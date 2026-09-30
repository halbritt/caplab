"""Isolated real-Cairn retrieval adapter.

An arm supplies an exact Cairn `binary` and the `checkout` it was built from.
The adapter refuses the run unless the binary's embedded revision equals the
checkout's HEAD and both are unmodified. It then runs Cairn's own
`scripts/trial-task-eval.sh -- COMMAND`, which owns a disposable PostgreSQL
cluster (Unix socket only, removed on exit), and the command it runs is this
module: the *store host*. The host loads the corpus through Cairn's public CLI
with one CAPLAB-owned procedure for every arm, serves a new API on a private
socket, and reports readiness. The adapter then measures real searches through
the hosted-agent interface with an environment that has no database access.

CAPLAB contains no PostgreSQL lifecycle of its own. The wrapper comes from the
arm's checkout, or from CAPLAB_RETRIEVAL_LIFECYCLE_WRAPPER for a checkout that
predates the `--` command mode; either way its hash is pinned.

Nothing here can reach a production database, socket or profile: the wrapper and
host run with a rebuilt environment, and every path they use lies under the
store's own temporary directory or the wrapper's private cluster.

Host protocol (JSON lines): the adapter writes one request on the host's stdin;
the host answers `{"ready": ...}` or `{"error": ...}`, then runs until its stdin
closes or it receives SIGTERM, stops the API and exits.
"""

from __future__ import annotations

import concurrent.futures
import contextlib
import hashlib
import json
import os
import queue
import secrets
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
import uuid
from pathlib import Path

from caplab.retrieval import contracts
from caplab.retrieval.runner import (Adapter, AdapterCleanupError, AdapterError, Completed, Outcome, bounded_run,
                                     file_sha256, scrubbed_env, text_tail)

TASK = "caplab-retrieval"
SEARCH_TOKENS = 64_000  # Available context per page; each page has its own budget.
MAX_PAGES = 100
STORE_COMMAND_TIMEOUT = 120
READY_TIMEOUT = 900
HOST_EXIT_TIMEOUT = 90  # After the host's stdin closes: stop the API, then the wrapper removes the cluster.
HOST_TERM_TIMEOUT = 60  # After SIGTERM to the host's process group, before SIGKILL.
LOG_LIMIT = 1 << 20
WRAPPER = "scripts/trial-task-eval.sh"
WRAPPER_ENV = "CAPLAB_RETRIEVAL_LIFECYCLE_WRAPPER"
ROOT_PREFIX = "caplab-rtv-"
CLUSTER_PREFIX = "/tmp/cairn-task-eval-pg."  # The wrapper's cluster root; its `socket` directory is exported.
SRC_ROOT = Path(__file__).resolve().parents[2]


def _strict_json(data: bytes):
    def refuse(token):
        raise ValueError(f"non-finite JSON number {token}")

    return json.loads(data.decode("utf-8"), parse_constant=refuse)


def _ok(done: Completed, what: str) -> Completed:
    if done.timed_out or done.returncode != 0:
        raise AdapterError("store_failed", f"{what} failed", {
            "exit_code": done.returncode, "timed_out": done.timed_out,
            "stderr_tail": text_tail(done.stderr), "stdout_tail": text_tail(done.stdout)})
    return done


# ---------------------------------------------------------------- store host (runs under the wrapper)

class ExternalCluster:
    """The cluster owned by Cairn's wrapper. This process uses it and never starts or stops it."""

    def __init__(self, environ=None):
        environ = os.environ if environ is None else environ
        socket, pg_bin = environ.get("CAIRN_TASK_EVAL_PG", ""), environ.get("CAIRN_TASK_EVAL_PG_BIN", "")
        if not socket or not pg_bin or not socket.startswith(CLUSTER_PREFIX) or not Path(socket).is_dir():
            raise AdapterError("store_unsafe", "the store host must run under Cairn's trial-task-eval.sh, "
                                               "which owns the disposable cluster")
        self.socket, self.pg_bin = Path(socket), Path(pg_bin)
        self.root = self.socket.parent

    def create_database(self, name: str) -> str:
        done = bounded_run([self.pg_bin / "createdb", "-h", self.socket, name],
                           env=scrubbed_env(self.root), timeout=STORE_COMMAND_TIMEOUT)
        _ok(done, "createdb")
        return f"host={self.socket} dbname={name} sslmode=disable"

    def version(self) -> str:
        done = bounded_run([self.pg_bin / "pg_ctl", "--version"], env=scrubbed_env(self.root), timeout=30)
        return done.stdout.decode().strip() if done.returncode == 0 else "unknown"

    def log(self) -> bytes:
        path = self.root / "postgres.log"
        return path.read_bytes()[-LOG_LIMIT:] if path.is_file() else b""


class CairnStore:
    """One disposable database, one API server and one hosted-agent identity under `root`."""

    def __init__(self, binary: Path, *, collection: str, label: str, worker: Path | None, root: Path, cluster):
        self.binary, self.collection, self.label, self.worker = Path(binary), collection, label, worker
        self.root, self.cluster = Path(root), cluster
        self.home = self.root / "home"
        self.socket = self.home / "api.sock"
        self.token_file = self.root / "agent.token"
        self.server = None
        self.ids: dict = {}  # corpus note ID -> record ID
        self.names: dict = {}  # record ID -> corpus note ID
        self.env: dict = {}

    def _build_env(self, dsn: str) -> dict:
        """Rebuild the environment from scratch: only the store's own paths, no CAIRN_* from outside."""
        if str(self.cluster.socket) not in dsn or not str(self.root).startswith("/tmp/" + ROOT_PREFIX):
            raise AdapterError("store_unsafe", "the database is not the wrapper's own disposable cluster")
        env = scrubbed_env(self.home)
        env.update(CAIRN_HOME=str(self.home), CAIRN_DATABASE_URL=dsn,
                   XDG_DATA_HOME=str(self.home / "xdg-data"), XDG_CONFIG_HOME=str(self.home / "xdg-config"),
                   XDG_STATE_HOME=str(self.home / "xdg-state"), XDG_CACHE_HOME=str(self.home / "xdg-cache"))
        return env

    def cairn(self, *args, stdin: bytes = b"", timeout: float = STORE_COMMAND_TIMEOUT) -> Completed:
        return bounded_run([self.binary, *args], stdin=stdin, cwd=self.root, env=self.env, timeout=timeout)

    def cairn_json(self, *args, payload: dict | None = None, timeout: float = STORE_COMMAND_TIMEOUT):
        done = self.cairn(*args, stdin=b"" if payload is None else json.dumps(payload).encode(), timeout=timeout)
        try:
            response = json.loads(done.stdout.decode()) if done.stdout else {}
        except (UnicodeDecodeError, ValueError):
            response = {}
        if done.timed_out or done.returncode != 0 or not response.get("ok"):
            raise AdapterError("store_failed", f"cairn {args[0]} failed", {
                "status": response.get("status"), "message": response.get("message"),
                "stderr_tail": text_tail(done.stderr), "stdout_tail": text_tail(done.stdout)})
        return response["data"]

    def provision(self, corpus: list) -> None:
        dsn = self.cluster.create_database("caplab_retrieval")
        self.home.mkdir(mode=0o700)
        self.env = self._build_env(dsn)
        _ok(self.cairn("migrate", timeout=300), "cairn migrate")
        token = secrets.token_urlsafe(32)
        self.token_file.write_text(token)
        self.token_file.chmod(0o600)
        identities = self.home / "identities.json"
        identities.write_text(json.dumps([{
            "token_sha256": hashlib.sha256(token.encode()).hexdigest(), "principal": f"agent:caplab-{self.label}",
            "repo": self.collection, "role": "agent", "destination": "hosted"}]))
        identities.chmod(0o600)
        self.seed(corpus)

    def remember(self, note: dict) -> None:
        args = ["remember", "--repo", note.get("repo", self.collection), "--kind", note.get("kind", "note"),
                "--stdin", "--request-id", str(uuid.uuid5(uuid.NAMESPACE_URL, f"caplab-retrieval:{self.collection}:{note['id']}"))]
        if note.get("shareable", True):
            args.insert(1, "--shareable")
        done = self.cairn(*args, stdin=note["body"].encode(), timeout=60)
        try:
            record_id = json.loads(done.stdout.decode())["data"]["record_id"]
        except (UnicodeDecodeError, ValueError, KeyError, TypeError):
            raise AdapterError("store_failed", f"could not load note {note['id']!r}", {
                "exit_code": done.returncode, "stderr_tail": text_tail(done.stderr),
                "stdout_tail": text_tail(done.stdout)}) from None
        self.ids[note["id"]] = record_id
        self.names[record_id] = note["id"]

    def seed(self, corpus: list, workers: int = 8) -> None:
        with concurrent.futures.ThreadPoolExecutor(workers) as pool:
            list(pool.map(self.remember, corpus))  # Re-raises the first failure.
        for note in corpus:
            if note.get("supersede_with"):
                self.supersede(note["id"], note["supersede_with"])

    def supersede(self, old: str, new: str) -> None:
        preview = self.cairn_json("preview-retract", self.ids[old])
        self.cairn_json("supersede", payload={
            "request_id": str(uuid.uuid4()), "record_id": self.ids[old], "expected_version": preview["version"],
            "replacement": {"record_id": self.ids[new], "version": 1}, "preview_id": preview["preview_id"],
            "reason": "caplab retrieval fixture: superseded note"})

    def start(self, timeout: float = 30) -> None:
        command = [self.binary, "serve", "--socket", self.socket]
        if self.worker:
            command += ["--semantic-stream-command", self.worker]
        self.api_log = (self.root / "api.log").open("wb")
        self.server = subprocess.Popen([str(c) for c in command], env=self.env, cwd=self.root,
                                       stdout=self.api_log, stderr=self.api_log, start_new_session=True)
        deadline = time.monotonic() + timeout
        while not self.socket.exists():
            if self.server.poll() is not None or time.monotonic() > deadline:
                raise AdapterError("api_unavailable", "the isolated API did not start",
                                   {"log_tail": self.log_tail("api.log")})
            time.sleep(0.05)

    def stop(self) -> None:
        if self.server is not None and self.server.poll() is None:
            with contextlib.suppress(ProcessLookupError, PermissionError):
                os.killpg(self.server.pid, signal.SIGTERM)
            try:
                self.server.wait(15)
            except subprocess.TimeoutExpired:
                with contextlib.suppress(ProcessLookupError, PermissionError):
                    os.killpg(self.server.pid, signal.SIGKILL)
                self.server.wait()
        self.server = None
        if getattr(self, "api_log", None):
            self.api_log.close()

    def log_tail(self, name: str) -> str:
        path = self.root / name
        return text_tail(path.read_bytes()) if path.is_file() else ""


def _emit(value: dict) -> None:
    sys.stdout.write(json.dumps(value) + "\n")
    sys.stdout.flush()


def host_main() -> int:
    """Entry point for `scripts/trial-task-eval.sh -- python -m caplab.retrieval.cairn`."""
    stop = threading.Event()
    provisioning = {"active": True}

    def on_term(signum, frame):
        stop.set()
        if provisioning["active"]:
            raise KeyboardInterrupt

    signal.signal(signal.SIGTERM, on_term)
    store = None
    try:
        cluster = ExternalCluster()
        request = json.loads(sys.stdin.readline())
        store = CairnStore(Path(request["binary"]), collection=request["collection"], label=request["label"],
                           worker=Path(request["worker"]) if request.get("worker") else None,
                           root=Path(request["root"]), cluster=cluster)
        if not str(store.root).startswith("/tmp/" + ROOT_PREFIX) or not store.root.is_dir():
            raise AdapterError("store_unsafe", "the store root must be a directory created by the adapter")
        store.provision(request["corpus"])
        store.start()
        _emit({"ready": {"socket": str(store.socket), "token_file": str(store.token_file), "home": str(store.home),
                         "names": store.names, "pg_root": str(cluster.root), "pg_version": cluster.version()}})
    except AdapterError as exc:
        _emit({"error": exc.as_error()})
        code = 1
    except KeyboardInterrupt:
        _emit({"error": {"code": "interrupted", "message": "the store host was interrupted while provisioning"}})
        code = 1
    except BaseException as exc:  # Report, never crash silently: the adapter classifies this.
        _emit({"error": {"code": "host_failed", "message": f"{type(exc).__name__}: {exc}"[:2000]}})
        code = 1
    else:
        provisioning["active"] = False
        threading.Thread(target=lambda: (sys.stdin.read(), stop.set()), daemon=True).start()
        stop.wait()
        code = 0
    finally:
        if store is not None:
            store.stop()
            with contextlib.suppress(OSError):  # The wrapper removes its cluster directory right after us.
                (store.root / "postgres.log").write_bytes(store.cluster.log())
    if code == 0:
        _emit({"closed": True})
    return code


# ---------------------------------------------------------------- adapter

def _git(checkout: Path, *args) -> str:
    with tempfile.TemporaryDirectory(prefix="caplab-git-") as scratch:
        env = scrubbed_env(Path(scratch))
        env.update(GIT_OPTIONAL_LOCKS="0", GIT_CONFIG_NOSYSTEM="1")  # Reading must not touch the checkout.
        done = bounded_run(["git", "-C", checkout, *args], env=env, timeout=60)
    if done.returncode != 0:
        raise AdapterError("pin_unavailable", f"git {args[0]} failed in {checkout}", {"stderr_tail": text_tail(done.stderr)})
    return done.stdout.decode().strip()


class CairnAdapter(Adapter):
    """Measure real Cairn retrieval against a fresh disposable store.

    Seeds do not affect Cairn retrieval; the observation says so. `delivered_ids`
    stays unobserved: a search returns bounded previews in rank order and this
    adapter never pulls a body.
    """

    def __init__(self, arm: dict, spec: dict):
        config = arm["configuration"]
        self.arm, self.spec = arm["id"], spec
        self.binary, self.checkout = Path(config["binary"]), Path(config["checkout"])
        self.worker = Path(config["semantic_worker"]) if config.get("semantic_worker") else None
        self.semantic = config.get("semantic_mode", "off") == "on"
        self.collection = f"caplab-retrieval:{spec['experiment_id']}"
        self.wrapper: Path | None = None
        self.pinned: dict = {}
        self.host = None
        self.root: Path | None = None
        self.ready: dict = {}
        self.readiness: dict = {}
        self.agent_env: dict = {}
        self._lines: queue.Queue = queue.Queue()

    # -- identity

    def pin(self) -> dict:
        for what, path in (("binary", self.binary), ("semantic_worker", self.worker)):
            if path is not None and not (path.is_file() and os.access(path, os.X_OK)):
                raise AdapterError("pin_unavailable", f"{what} {path} is not an executable file")
        if not self.checkout.is_dir():
            raise AdapterError("pin_unavailable", f"checkout {self.checkout} is not a directory")
        with tempfile.TemporaryDirectory(prefix="caplab-ver-") as scratch:
            done = bounded_run([self.binary, "version"], env=scrubbed_env(Path(scratch)), timeout=60)
        try:
            version = json.loads(done.stdout.decode())["data"]
        except (UnicodeDecodeError, ValueError, KeyError, TypeError):
            raise AdapterError("pin_unavailable", "the binary did not report its build identity",
                               {"stderr_tail": text_tail(done.stderr)}) from None
        head = _git(self.checkout, "rev-parse", "HEAD")
        dirty = bool(_git(self.checkout, "status", "--porcelain"))
        problems = []
        if version.get("vcs_revision") != head:
            problems.append(f"binary revision {version.get('vcs_revision')!r} is not the checkout HEAD {head!r}")
        if version.get("vcs_modified") is not False:
            problems.append("the binary was built from a modified or unstamped tree")
        if dirty:
            problems.append("the checkout has uncommitted changes")
        if problems:
            raise AdapterError("pin_mismatch", "; ".join(problems), {
                "binary": str(self.binary), "checkout": str(self.checkout)})
        override = os.environ.get(WRAPPER_ENV)
        self.wrapper = Path(override) if override else self.checkout / WRAPPER
        if not self.wrapper.is_file():
            raise AdapterError("pin_unavailable", f"lifecycle wrapper {self.wrapper} not found; set {WRAPPER_ENV} "
                                                  "for a checkout without scripts/trial-task-eval.sh")
        pins = {"adapter": "cairn", "collection": self.collection,
                "binary": {"path": str(self.binary.resolve()), "sha256": file_sha256(self.binary),
                           "vcs_revision": version["vcs_revision"], "module_version": version.get("module_version"),
                           "go_version": version.get("go_version")},
                "checkout": {"path": str(self.checkout.resolve()), "head": head, "dirty": False},
                "lifecycle_wrapper": {"path": str(self.wrapper.resolve()), "sha256": file_sha256(self.wrapper),
                                      "from_environment": bool(override)},
                "semantic": {"mode": "on" if self.semantic else "off",
                             "worker": None if self.worker is None else {
                                 "path": str(self.worker.resolve()), "sha256": file_sha256(self.worker)}}}
        self.pinned = {"binary": pins["binary"]["sha256"], "head": head, "wrapper": pins["lifecycle_wrapper"]["sha256"]}
        return pins

    def _verify_unchanged(self) -> None:
        """The plan sealed these pins earlier; refuse if any input moved since."""
        if (file_sha256(self.binary) != self.pinned["binary"] or file_sha256(self.wrapper) != self.pinned["wrapper"]
                or _git(self.checkout, "rev-parse", "HEAD") != self.pinned["head"]):
            raise AdapterError("pin_changed", "the binary, wrapper or checkout changed after the plan was sealed")

    # -- lifecycle

    def open(self) -> None:
        self._verify_unchanged()
        self.root = Path(tempfile.mkdtemp(prefix=ROOT_PREFIX, dir="/tmp"))  # Short: Unix socket paths are capped.
        try:
            self._start_host()
            self._await_ready()
            self.agent_env = scrubbed_env(Path(self.ready["home"]))
            self.agent_env.update(CAIRN_HOME=self.ready["home"])  # No database URL: searches need none.
            self.readiness = self._probe()
        except BaseException as exc:
            problems = self._shutdown(graceful=False)
            tails = {"host_stderr_tail": self._tail("host.stderr"), "api_log_tail": self._tail("api.log")}
            if problems:
                tails["cleanup_problems"] = problems
            self._remove_root()
            if isinstance(exc, AdapterError):
                raise AdapterError(exc.code, exc.message, {**exc.detail, **tails}) from None
            raise

    def _tail(self, name: str) -> str:
        path = self.root / name if self.root else None
        return text_tail(path.read_bytes()) if path is not None and path.is_file() else ""

    def _start_host(self) -> None:
        env = scrubbed_env(self.root)
        env["PYTHONPATH"] = str(SRC_ROOT)
        pg_bin = os.environ.get("CAPLAB_RETRIEVAL_PG_BIN") or os.environ.get("CAIRN_PG_BIN")
        if pg_bin:
            env["CAIRN_PG_BIN"] = pg_bin  # Which PostgreSQL the wrapper uses; its own default is pg_config.
        with (self.root / "host.stderr").open("wb") as stderr:  # The child keeps its own descriptor.
            self.host = subprocess.Popen(
                ["bash", str(self.wrapper), "--", sys.executable, "-m", "caplab.retrieval.cairn"],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=stderr,
                env=env, cwd=self.root, start_new_session=True, text=True)
        self._lines = queue.Queue()
        threading.Thread(target=self._pump, daemon=True).start()
        request = {"binary": str(self.binary.resolve()), "collection": self.collection, "label": self.arm,
                   "worker": str(self.worker.resolve()) if self.worker else None, "root": str(self.root),
                   "corpus": self.spec["corpus"]}
        self.host.stdin.write(json.dumps(request) + "\n")
        self.host.stdin.flush()

    def _pump(self) -> None:
        for line in self.host.stdout:
            self._lines.put(line)
        self._lines.put(None)

    def _await_ready(self) -> None:
        deadline = time.monotonic() + READY_TIMEOUT
        while True:
            try:
                line = self._lines.get(timeout=max(0.1, min(1.0, deadline - time.monotonic())))
            except queue.Empty:
                if time.monotonic() > deadline:
                    raise AdapterError("host_timeout", f"the store was not ready within {READY_TIMEOUT} seconds") from None
                continue
            if line is None:
                self.host.wait()
                raise AdapterError("host_failed", "the lifecycle wrapper exited before the store was ready; the "
                                   "arm's checkout must support `scripts/trial-task-eval.sh -- COMMAND` "
                                   f"(or set {WRAPPER_ENV})", {"exit_code": self.host.returncode,
                                                                "stderr_tail": self._tail("host.stderr")})
            try:
                message = json.loads(line)
            except ValueError:
                continue  # Only protocol lines are JSON objects.
            if "error" in message:
                error = message["error"]
                raise AdapterError(error.get("code", "host_failed"), error.get("message", "the store host failed"),
                                   {k: v for k, v in error.items() if k not in ("code", "message")})
            if "ready" in message:
                self.ready = message["ready"]
                return

    def _probe(self) -> dict:
        """Observe, before any assignment, what the store does for the configured discovery mode."""
        done = self._search("readiness probe", offset=0, timeout=60)
        try:
            data = _strict_json(done.stdout)["data"]
        except (UnicodeDecodeError, ValueError, KeyError, TypeError):
            raise AdapterError("api_unavailable", "the isolated API did not answer a search",
                               {"stderr_tail": text_tail(done.stderr), "stdout_tail": text_tail(done.stdout)}) from None
        return {"semantic_requested": self.semantic, "worker_configured": self.worker is not None,
                "discovery": data.get("discovery"), "status": data.get("status"), "ranking": data.get("ranking"),
                "postgres": self.ready.get("pg_version")}

    def _search(self, query: str, *, offset: int, timeout: float) -> Completed:
        args = ["agent", "--socket", self.ready["socket"], "--token-file", self.ready["token_file"], "search",
                "--repo", self.collection, "--task", TASK, "--run", "rank-" + uuid.uuid4().hex[:12],
                "--tokens", str(SEARCH_TOKENS), "--offset", str(offset)]
        if self.semantic:
            args.append("--semantic")
        return bounded_run([self.binary, *args, "--", query], cwd=self.root, env=self.agent_env, timeout=timeout)

    def _shutdown(self, *, graceful: bool) -> list:
        """Stop the host and so the wrapper's cluster. Returns what could not be released."""
        problems: list = []
        host = self.host
        if host is None:
            return problems
        with contextlib.suppress(OSError, ValueError):
            host.stdin.close()
        try:
            if not graceful:
                raise subprocess.TimeoutExpired("host", 0)  # Do not wait politely after an interruption.
            host.wait(timeout=HOST_EXIT_TIMEOUT)
            if host.returncode != 0:
                # The host exits 0 after a clean stop, so the wrapper's own failure (for example a
                # cluster it could not stop or remove) is the only way to get here.
                problems.append(f"the lifecycle wrapper exited with status {host.returncode} after a clean stop: "
                                f"{self._tail('host.stderr')[-500:].strip()}")
        except subprocess.TimeoutExpired:
            if graceful:
                problems.append(f"the store host did not exit within {HOST_EXIT_TIMEOUT} seconds of stdin closing")
            with contextlib.suppress(ProcessLookupError, PermissionError):
                os.killpg(host.pid, signal.SIGTERM)
            try:
                host.wait(timeout=HOST_TERM_TIMEOUT)
            except subprocess.TimeoutExpired:
                problems.append(f"the wrapper did not exit within {HOST_TERM_TIMEOUT} seconds of SIGTERM; killed")
                with contextlib.suppress(ProcessLookupError, PermissionError):
                    os.killpg(host.pid, signal.SIGKILL)
                host.wait()
        with contextlib.suppress(OSError, ValueError):
            host.stdout.close()
        pg_root = self.ready.get("pg_root")
        if pg_root and Path(pg_root).exists():
            problems.append(f"the wrapper's cluster directory {pg_root} still exists; a postgres process may remain")
        self.host = None
        return problems

    def _remove_root(self) -> None:
        if self.root is not None and str(self.root).startswith("/tmp/" + ROOT_PREFIX):
            shutil.rmtree(self.root, ignore_errors=True)

    def close(self) -> dict:
        problems = self._shutdown(graceful=True)
        evidence = {}
        for name in ("api.log", "postgres.log", "host.stderr"):
            path = self.root / name if self.root else None
            if path is not None and path.is_file():
                evidence[name] = path.read_bytes()[-LOG_LIMIT:]
        evidence["readiness.json"] = contracts.canonical_json(self.readiness)
        self._remove_root()
        if problems:
            raise AdapterCleanupError("; ".join(problems), evidence)
        return evidence

    # -- measurement

    def retrieve(self, query: dict, seed: int, cutoff: int, timeout: float) -> Outcome:
        names, start, deadline = self.ready["names"], time.monotonic_ns(), time.monotonic() + timeout
        order: list = []
        raw: dict = {}
        pages: list = []
        offset, exhausted = 0, False

        def observation() -> dict:
            states = [p["state"] for p in pages]
            rankings = sorted({p["ranking"] for p in pages if p["ranking"]})
            discovery = next((p["discovery"] for p in pages if p["discovery"] is not None), None)
            omitted: dict = {}
            for p in pages:
                for key, value in p["omitted"].items():
                    omitted[key] = omitted.get(key, 0) + value
            state = states[0] if states else None
            return {"adapter": "cairn", "collection": self.collection, "seed_applied": False,
                    "latency_scope": "all search pages, including each CLI process start",
                    "exposure": "index previews only; no body was pulled",
                    "pages": len(pages), "response_bytes": sum(p["bytes"] for p in pages), "exhausted": exhausted,
                    "depth_requested": cutoff, "depth_returned": len(order), "rankings": rankings,
                    "status": sorted({p["status"] for p in pages if p["status"]}), "omitted": omitted,
                    "semantic": {"requested": self.semantic, "worker_configured": self.worker is not None,
                                 "state": state, "fallback": (state not in ("ready", "not_needed")) if self.semantic else None,
                                 "discovery": discovery}}

        def failure(status, code, message, **detail):
            return Outcome(status=status, error={"code": code, "message": message, **detail},
                           observation=observation(), raw=raw, latency_ns=time.monotonic_ns() - start)

        while len(order) < cutoff and len(pages) < MAX_PAGES:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return failure("timeout", "timeout", f"no complete answer within {timeout} seconds",
                               timeout_seconds=timeout)
            done = self._search(query["text"], offset=offset, timeout=remaining)
            name = f"search-page-{len(pages) + 1:03d}"
            raw[name + ".json"] = done.stdout
            if done.stderr:
                raw[name + ".stderr"] = done.stderr
            if done.timed_out:
                return failure("timeout", "timeout", f"no complete answer within {timeout} seconds",
                               timeout_seconds=timeout)
            try:
                response = _strict_json(done.stdout)
                data = response["data"] if response.get("ok") and done.returncode == 0 else None
            except (UnicodeDecodeError, ValueError, AttributeError, KeyError):
                return failure("error", "malformed_response", "search output was not one JSON document",
                               exit_code=done.returncode, stdout_head=text_tail(done.stdout[:2000]))
            if data is None:
                return failure("error", "search_failed", "Cairn refused or failed the search",
                               exit_code=done.returncode, cairn_status=response.get("status"),
                               cairn_message=response.get("message"), stderr_tail=text_tail(done.stderr))
            entries = data.get("index") or []
            discovery = data.get("discovery")
            pages.append({"bytes": len(done.stdout), "state": (discovery or {}).get("state"),
                          "ranking": data.get("ranking"), "status": data.get("status"), "discovery": discovery,
                          "omitted": {k: v for k, v in (data.get("omitted") or {}).items() if v}})
            if len(pages) > 1 and (pages[-1]["state"], pages[-1]["ranking"]) != (pages[0]["state"], pages[0]["ranking"]):
                # Cairn's own guidance: if fallback changes the ordering between pages, the pages are
                # not comparable. Stop at the first page that differs; never stitch them together.
                return failure("error", "discovery_changed", "discovery state or ranking changed between pages",
                               states=[p["state"] for p in pages], rankings=[p["ranking"] for p in pages])
            for entry in entries:
                note = names.get(entry.get("record_id"))
                if note is None:
                    return failure("error", "unknown_record", "Cairn returned a record that was not seeded",
                                   record_id=entry.get("record_id"))
                if note in order:
                    return failure("error", "duplicate_record", f"note {note!r} was returned twice")
                order.append(note)
            next_offset = (data.get("page") or {}).get("next_offset")
            if next_offset is None:
                exhausted = True
                break
            if not entries or not isinstance(next_offset, int) or next_offset <= offset:
                return failure("error", "paging_stalled", "the page cursor did not advance", next_offset=next_offset)
            offset = next_offset
        result = Outcome(ranked_ids=order[:cutoff], delivered_ids=None, raw=raw,
                         latency_ns=time.monotonic_ns() - start)
        result.observation = observation()
        return result


if __name__ == "__main__":
    sys.exit(host_main())
