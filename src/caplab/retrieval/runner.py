"""Run a sealed retrieval experiment: every (arm, query, seed) assignment once.

`run_experiment(spec, output)` validates and normalizes the spec, pins each
arm's inputs, seals the plan in a new `RunArtifacts` output, then executes the
sealed roster in order. Each attempt is recorded the moment it finishes, so an
error or interruption leaves durable evidence: the interrupted assignment is
recorded as `interrupted` and every assignment not yet run as `not_started`.
A failing adapter is a recorded failure. No response is ever substituted.

Adapters see only what a retriever would see: the query text, the corpus notes,
the seed and the requested depth. Relevance and forbidden labels stay in the
spec and are used only by scoring.
"""

from __future__ import annotations

import contextlib
import hashlib
import json
import os
import platform
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Mapping

from caplab.retrieval import contracts

REQUEST_SCHEMA = "caplab-retrieval-request/1"
RESPONSE_SCHEMA = "caplab-retrieval-response/1"
MAX_OUTPUT_BYTES = 16 << 20
ERROR_TEXT_BYTES = 2_000
_RESPONSE_KEYS = {"schema_version", "ranked_ids", "delivered_ids", "observation"}
_ENV_ALLOWED = ("PATH", "LANG", "LC_ALL", "LC_CTYPE", "TZ")


class AdapterError(Exception):
    """A classified adapter failure; the runner records it as an error attempt."""

    def __init__(self, code: str, message: str, detail: dict | None = None):
        super().__init__(f"{code}: {message}")
        self.code, self.message, self.detail = code, message, dict(detail or {})

    def as_error(self) -> dict:
        return {"code": self.code, "message": self.message[:ERROR_TEXT_BYTES], **self.detail}


class AdapterCleanupError(Exception):
    """An adapter could not fully release its resources. `evidence` is still kept."""

    def __init__(self, message: str, evidence: dict | None = None):
        super().__init__(message)
        self.message, self.evidence = message, dict(evidence or {})


class RunnerCleanupError(Exception):
    """Cleanup failed, so the run was left unfinished rather than reported as a success.

    Every attempt and all retained evidence are in `output`; `verify_run(output,
    allow_unfinished=True)` can read them. Measured retrieval results are not altered.
    """

    code = "cleanup_failed"

    def __init__(self, output: Path, failures: dict):
        self.output, self.failures = Path(output), dict(failures)
        super().__init__("cleanup failed for " + "; ".join(f"arm {arm}: {msg}" for arm, msg in self.failures.items())
                         + f"; the run at {output} was left unfinished")


@dataclass
class Outcome:
    """What an adapter observed for one assignment, before contract validation."""

    status: str = "ok"  # ok, error or timeout; the runner owns interrupted and not_started
    ranked_ids: list = field(default_factory=list)
    delivered_ids: list | None = None  # None: delivery was not observed; never inferred from rank
    error: dict | None = None
    observation: dict = field(default_factory=dict)
    raw: dict = field(default_factory=dict)  # exact request/response bytes for separate artifacts
    latency_ns: int | None = None  # the adapter's own measurement; the runner times the call if None


class Adapter:
    """One arm's retrieval system. `pin` is cheap and runs before the plan is sealed."""

    def pin(self) -> dict:
        """Identity of the inputs the arm depends on. Raise AdapterError to refuse the run."""
        return {}

    def open(self) -> None:
        """Acquire resources after the plan is sealed. Raise AdapterError if unavailable."""

    def retrieve(self, query: dict, seed: int, cutoff: int, timeout: float) -> Outcome:
        raise NotImplementedError

    def close(self) -> dict:
        """Release resources; return run-level evidence as {name: bytes}.

        Raise AdapterCleanupError (carrying the evidence) if anything could not be released.
        """
        return {}

    def unreleased(self) -> list:
        """What an `open` that failed or was interrupted could not release; empty when nothing is held.

        `close` is not called for an arm that never opened, so this is how such a leak reaches the runner.
        """
        return []


# ---------------------------------------------------------------- subprocess

def scrubbed_env(home: Path) -> dict:
    """A minimal environment: no inherited credentials, CAIRN_* settings or profiles."""
    env = {key: os.environ[key] for key in _ENV_ALLOWED if key in os.environ}
    env.update(HOME=str(home), TMPDIR=str(home), PYTHONDONTWRITEBYTECODE="1")
    return env


@dataclass
class Completed:
    returncode: int | None
    stdout: bytes
    stderr: bytes
    timed_out: bool
    truncated: bool
    elapsed_ns: int


def bounded_run(argv: list, *, stdin: bytes = b"", cwd: Path | None = None, env: Mapping | None = None,
                timeout: float, limit: int | None = None) -> Completed:
    """Run a command in its own session with a wall-clock timeout and capped output.

    On timeout, output overflow or interruption, the whole process group is killed.
    """
    limit = MAX_OUTPUT_BYTES if limit is None else limit
    start = time.monotonic_ns()
    proc = subprocess.Popen([str(a) for a in argv], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, cwd=cwd, env=dict(env) if env is not None else None,
                            start_new_session=True)
    buffers = {"out": bytearray(), "err": bytearray()}
    overflow = threading.Event()

    def kill():
        with contextlib.suppress(ProcessLookupError, PermissionError):
            os.killpg(proc.pid, signal.SIGKILL)

    def pump(stream, key):
        buf = buffers[key]
        while True:
            chunk = stream.read1(65536)
            if not chunk:
                return
            room = limit - len(buf)
            if room > 0:
                buf += chunk[:room]
            if len(chunk) > room:
                overflow.set()
                kill()
                return

    def feed():
        with contextlib.suppress(BrokenPipeError, OSError, ValueError):
            proc.stdin.write(stdin)
        with contextlib.suppress(BrokenPipeError, OSError, ValueError):
            proc.stdin.close()

    threads = [threading.Thread(target=pump, args=(proc.stdout, "out"), daemon=True),
               threading.Thread(target=pump, args=(proc.stderr, "err"), daemon=True),
               threading.Thread(target=feed, daemon=True)]
    for thread in threads:
        thread.start()
    timed_out = False
    try:
        try:
            proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            kill()
            proc.wait()
    except BaseException:
        kill()
        proc.wait()
        raise
    finally:
        kill()  # Reap any descendant still holding the group, then the pipes.
        for thread in threads:
            thread.join(timeout=5)
        for stream in (proc.stdin, proc.stdout, proc.stderr):
            with contextlib.suppress(OSError, ValueError):
                stream.close()
    return Completed(proc.returncode, bytes(buffers["out"]), bytes(buffers["err"]), timed_out,
                     overflow.is_set(), time.monotonic_ns() - start)


def text_tail(data: bytes, limit: int = ERROR_TEXT_BYTES) -> str:
    return data[-limit:].decode("utf-8", "replace")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return "sha256:" + digest.hexdigest()


# ---------------------------------------------------------------- command adapter

def _strict_json(data: bytes) -> Any:
    def refuse(token):
        raise ValueError(f"non-finite JSON number {token}")

    return json.loads(data.decode("utf-8"), parse_constant=refuse)


class CommandAdapter(Adapter):
    """A retriever run as one argv per assignment: request JSON on stdin, response JSON on stdout.

    Each call gets an empty working directory and a minimal environment. Nonzero
    exit, timeout, oversized output and malformed or contract-violating
    responses are classified failures.

    Pinned files (the executable and every argv entry that is a file) are re-checked before
    the arm opens (by hash) and before every call (by size, modification time and inode,
    re-hashed on any change); a file that differs from the sealed plan is a `pin_changed`
    failure, never a silent run of other bytes. Limits: this is detection, not custody. A file
    can still change between the check and the exec, and anything the program loads that is not
    named in argv (libraries, imported modules, data files) is not pinned.
    """

    def __init__(self, arm: dict, spec: dict):
        self.arm = arm["id"]
        self.argv = list(arm["configuration"]["argv"])
        self.corpus = spec["corpus"]
        self._pinned: dict = {}  # path -> (sha256, stat signature) at pin time

    @staticmethod
    def _signature(path: Path) -> tuple:
        info = Path(path).stat()
        return info.st_size, info.st_mtime_ns, info.st_ino

    def _verify_files(self, *, full: bool) -> None:
        for path, (digest, signature) in self._pinned.items():
            try:
                current = self._signature(path)
                changed = (full or current != signature) and file_sha256(path) != digest
            except OSError as exc:
                raise AdapterError("pin_changed", f"pinned file {path} can no longer be read: {exc}") from None
            if changed:
                raise AdapterError("pin_changed", f"pinned file {path} no longer matches the sealed plan",
                                   {"path": str(path)})
            self._pinned[path] = (digest, current)  # Same bytes (for example touched): keep the new signature.

    def open(self) -> None:
        self._verify_files(full=True)

    def pin(self) -> dict:
        executable = shutil.which(self.argv[0]) if not os.path.dirname(self.argv[0]) else self.argv[0]
        if not executable or not Path(executable).is_file() or not os.access(executable, os.X_OK):
            raise AdapterError("command_unavailable", f"{self.argv[0]!r} is not an executable file")
        files = {}
        self._pinned = {}
        for index, part in enumerate(self.argv):
            path = Path(executable if index == 0 else part)
            if path.is_file() and path.stat().st_size <= 256 << 20:
                digest = file_sha256(path)
                files[f"argv[{index}]"] = {"path": str(path.resolve()), "sha256": digest}
                self._pinned[path] = (digest, self._signature(path))
        return {"adapter": "command", "argv": self.argv, "files": files}

    def request(self, query: dict, seed: int, cutoff: int) -> bytes:
        # Gold labels (relevant_ids, forbidden_ids, stratum) never enter the request.
        return contracts.canonical_json({"schema_version": REQUEST_SCHEMA, "query_id": query["id"],
                                         "query": query["text"], "seed": seed, "corpus": self.corpus,
                                         "cutoff": cutoff})

    def retrieve(self, query: dict, seed: int, cutoff: int, timeout: float) -> Outcome:
        self._verify_files(full=False)
        request = self.request(query, seed, cutoff)
        with tempfile.TemporaryDirectory(prefix="caplab-cmd-") as scratch:
            done = bounded_run(self.argv, stdin=request, cwd=Path(scratch), env=scrubbed_env(Path(scratch)),
                               timeout=timeout)
        raw = {"request": request, "stdout": done.stdout, "stderr": done.stderr}
        observation = {"adapter": "command", "exit_code": done.returncode, "cutoff_requested": cutoff,
                       "request_bytes": len(request), "stdout_bytes": len(done.stdout),
                       "stderr_bytes": len(done.stderr), "output_truncated": done.truncated}

        def failure(status, code, message, **detail):
            return Outcome(status=status, error={"code": code, "message": message, **detail},
                           observation=observation, raw=raw, latency_ns=done.elapsed_ns)

        if done.timed_out:
            return failure("timeout", "timeout", f"no response within {timeout} seconds", timeout_seconds=timeout)
        if done.truncated:
            return failure("error", "output_too_large", f"output exceeded {MAX_OUTPUT_BYTES} bytes")
        if done.returncode != 0:
            code = "killed_by_signal" if done.returncode < 0 else "nonzero_exit"
            return failure("error", code, f"exit status {done.returncode}", exit_code=done.returncode,
                           stderr_tail=text_tail(done.stderr))
        try:
            response = _strict_json(done.stdout)
        except (UnicodeDecodeError, ValueError, RecursionError) as exc:
            return failure("error", "malformed_response", f"stdout is not one JSON document: {exc}",
                           stdout_head=text_tail(done.stdout[:ERROR_TEXT_BYTES]))
        if not isinstance(response, dict) or set(response) - _RESPONSE_KEYS:
            return failure("error", "schema_mismatch", "response must be an object with only "
                           + ", ".join(sorted(_RESPONSE_KEYS)))
        if response.get("schema_version") != RESPONSE_SCHEMA or "ranked_ids" not in response:
            return failure("error", "schema_mismatch", f"schema_version must be {RESPONSE_SCHEMA!r} "
                           "and ranked_ids is required", schema_version=response.get("schema_version"))
        reported = response.get("observation", {})
        if not isinstance(reported, dict):
            return failure("error", "schema_mismatch", "observation must be an object")
        delivered = response.get("delivered_ids")
        for name, value in (("ranked_ids", response["ranked_ids"]), ("delivered_ids", delivered)):
            if (value is not None or name == "ranked_ids") and not isinstance(value, list):
                return failure("error", "schema_mismatch", f"{name} must be an array of note IDs")
        # The retriever's own observation stays separate from what the runner measured.
        observation["reported"] = reported
        return Outcome(ranked_ids=response["ranked_ids"], delivered_ids=delivered,
                       observation=observation, raw=raw, latency_ns=done.elapsed_ns)


def build_adapter(arm: dict, spec: dict) -> Adapter:
    if arm["adapter"] == "command":
        return CommandAdapter(arm, spec)
    from caplab.retrieval import cairn  # Deferred: only real Cairn arms need it.

    return cairn.CairnAdapter(arm, spec)


# ---------------------------------------------------------------- experiment

HARNESS_MODULES = ("contracts", "metrics", "artifacts", "report", "compare", "runner", "cairn")


def _git_state(directory: Path) -> dict:
    """The harness checkout's commit and whether it is modified; unknown is stated, never guessed."""
    with tempfile.TemporaryDirectory(prefix="caplab-git-") as scratch:
        env = scrubbed_env(Path(scratch))
        env.update(GIT_OPTIONAL_LOCKS="0", GIT_CONFIG_NOSYSTEM="1")
        try:
            head = bounded_run(["git", "-C", directory, "rev-parse", "HEAD"], env=env, timeout=30)
            status = bounded_run(["git", "-C", directory, "status", "--porcelain"], env=env, timeout=60)
        except OSError as exc:
            return {"commit": None, "modified": None, "reason": f"git unavailable: {exc}"}
    if head.returncode != 0 or status.returncode != 0:
        return {"commit": None, "modified": None, "reason": "not a git checkout"}
    return {"commit": head.stdout.decode().strip(), "modified": bool(status.stdout.strip())}


def _runner_identity(artifacts_factory=None) -> dict:
    """Exact bytes of every harness module that determines the evidence and its scores.

    A module copied into a modified tree is still pinned by its hash; the checkout state
    is reported alongside and is never claimed clean when it is not.
    """
    modules = {}
    names = {f"caplab.retrieval.{name}" for name in HARNESS_MODULES}
    if artifacts_factory is not None:
        names.add(getattr(artifacts_factory, "__module__", ""))
    for name in sorted(names):
        path = getattr(sys.modules.get(name), "__file__", None)
        if path and Path(path).is_file():
            modules[name] = {"path": str(Path(path).resolve()), "sha256": file_sha256(Path(path))}
    here = Path(__file__).resolve().parent
    return {"module": "caplab.retrieval.runner", "modules": modules, "checkout": _git_state(here),
            "python": sys.version.split()[0], "platform": platform.platform()}


def _attempt_dict(item: dict, status: str, *, ranked=None, delivered=None, latency_ns=None, error=None,
                  observation=None) -> dict:
    # Values pass through untouched: coercing a malformed response (a string into characters,
    # say) would hide the violation from the contract check.
    return {"assignment_id": item["assignment_id"], "arm": item["arm"], "query_id": item["query_id"],
            "seed": item["seed"], "status": status, "ranked_ids": [] if ranked is None else ranked,
            "delivered_ids": delivered, "latency_ns": latency_ns, "error": error,
            "observation": {} if observation is None else observation}


def _finish_attempt(spec: dict, item: dict, outcome: Outcome, elapsed_ns: int) -> tuple[dict, dict]:
    """Turn an adapter outcome into a contract-valid attempt. Violations become recorded failures."""
    latency = outcome.latency_ns if outcome.latency_ns is not None else elapsed_ns
    attempt = _attempt_dict(item, outcome.status, ranked=outcome.ranked_ids, delivered=outcome.delivered_ids,
                            latency_ns=latency, error=outcome.error, observation=outcome.observation)
    try:
        return contracts.validate_attempt(attempt, spec), outcome.raw
    except contracts.ContractError as exc:
        # The response broke the contract (unknown or duplicate IDs, wrong types). Keep the
        # evidence as a failure; never repair or drop the response.
        error = {"code": "invalid_response", "message": exc.message[:ERROR_TEXT_BYTES],
                 "contract_code": exc.code, "path": exc.path}
        # Rejected observations can themselves violate the contract (overflow or nesting).
        # Keep their exact bytes in raw evidence, not in the replacement failure attempt.
        failed = _attempt_dict(item, "error", latency_ns=latency, error=error,
                               observation={"response_rejected": True})
        return contracts.validate_attempt(failed, spec), outcome.raw


def _unavailable(spec: dict, item: dict, exc: AdapterError) -> dict:
    attempt = _attempt_dict(item, "error", latency_ns=0, error=dict(exc.as_error(), code="adapter_unavailable",
                            cause=exc.code), observation={"adapter_unavailable": True})
    return contracts.validate_attempt(attempt, spec)


def _stop_attempts(spec: dict, remaining: list, started: dict | None, reason: str) -> list:
    """Attempts for an interrupted run: the running assignment, then every unstarted one."""
    attempts = []
    for item in remaining:
        if started is not None and item["assignment_id"] == started["item"]["assignment_id"]:
            latency = time.monotonic_ns() - started["t0"]
            attempt = _attempt_dict(item, "interrupted", latency_ns=latency,
                                    error={"code": "interrupted", "message": reason})
        else:
            attempt = _attempt_dict(item, "not_started")
        attempts.append(contracts.validate_attempt(attempt, spec))
    return attempts


@contextlib.contextmanager
def _sigterm_interrupts(state: dict):
    """Treat SIGTERM like Ctrl-C so the run records its evidence before exiting."""
    if threading.current_thread() is not threading.main_thread():
        yield
        return

    def handler(signum, frame):
        state["reason"] = "SIGTERM"
        raise KeyboardInterrupt

    previous = signal.signal(signal.SIGTERM, handler)
    try:
        yield
    finally:
        signal.signal(signal.SIGTERM, previous)


def run_experiment(spec: dict, output: Path, *, adapters: Mapping[str, Adapter] | None = None,
                   artifacts_factory: Callable | None = None) -> dict:
    """Execute every planned assignment once and return the finished run report.

    `output` must not exist (the artifact store refuses a reused directory). Contract
    errors and pin failures are raised before anything is created. After the plan is sealed, adapter failures, timeouts,
    malformed responses and interruption are recorded as attempts and the run
    still finishes with a report whose coverage shows what is missing.
    `adapters` and `artifacts_factory` are test seams.
    """
    spec = contracts.validate_spec(spec)
    output = Path(output)
    arms = {arm["id"]: (adapters or {}).get(arm["id"]) or build_adapter(arm, spec) for arm in spec["arms"]}
    if artifacts_factory is None:
        try:
            from caplab.retrieval.artifacts import RunArtifacts as artifacts_factory
        except ImportError as exc:
            raise RuntimeError("caplab.retrieval.artifacts (RunArtifacts) is required to record a run") from exc
    provenance = {"runner": _runner_identity(artifacts_factory), "spec_digest": contracts.spec_digest(spec),
                  "arms": {arm_id: adapter.pin() for arm_id, adapter in arms.items()}}
    artifacts = artifacts_factory(output, spec, provenance=provenance)

    roster = contracts.assignments(spec)
    queries = {query["id"]: query for query in spec["queries"]}
    cutoff, timeout = max(spec["cutoffs"]), spec["timeout_seconds"]
    recorded: set = set()
    cleanup_failures: dict = {}
    started: dict | None = None
    state: dict = {"reason": "KeyboardInterrupt"}

    def record(attempt: dict, raw: dict | None = None) -> None:
        artifacts.record_attempt(attempt, raw=raw or None)
        recorded.add(attempt["assignment_id"])

    try:
        with _sigterm_interrupts(state):
            for arm in spec["arms"]:
                adapter = arms[arm["id"]]
                items = [item for item in roster if item["arm"] == arm["id"]]
                try:
                    adapter.open()
                except AdapterError as exc:
                    for item in items:
                        record(_unavailable(spec, item, exc))
                    continue
                try:
                    for item in items:
                        started = {"item": item, "t0": time.monotonic_ns()}
                        try:
                            outcome = adapter.retrieve(queries[item["query_id"]], item["seed"], cutoff, timeout)
                        except AdapterError as exc:
                            outcome = Outcome(status="error", error=exc.as_error())
                        except Exception as exc:  # A crashed adapter is a recorded failure, not a fake result.
                            outcome = Outcome(status="error", error={
                                "code": "adapter_exception", "type": type(exc).__name__,
                                "message": str(exc)[:ERROR_TEXT_BYTES]})
                        attempt, raw = _finish_attempt(spec, item, outcome, time.monotonic_ns() - started["t0"])
                        record(attempt, raw)
                        started = None
                finally:
                    try:
                        evidence = adapter.close() or {}
                    except AdapterCleanupError as exc:
                        evidence = dict(exc.evidence, **{"close-error.txt": exc.message.encode()})
                        cleanup_failures[arm["id"]] = exc.message
                    except Exception as exc:
                        message = f"{type(exc).__name__}: {exc}"
                        evidence = {"close-error.txt": message.encode()}
                        cleanup_failures[arm["id"]] = message
                    for name, payload in evidence.items():
                        artifacts.register_bytes(f"arm.{arm['id']}.{name}", payload, media_type="text/plain")
    except KeyboardInterrupt:
        pending = [item for item in roster if item["assignment_id"] not in recorded]
        for attempt in _stop_attempts(spec, pending, started, f"run interrupted ({state['reason']})"):
            artifacts.record_attempt(attempt)
            recorded.add(attempt["assignment_id"])
    for arm_id, adapter in arms.items():
        problems = adapter.unreleased()  # For an arm whose open failed or was interrupted.
        if problems and arm_id not in cleanup_failures:
            cleanup_failures[arm_id] = "; ".join(problems)
            artifacts.register_bytes(f"arm.{arm_id}.close-error.txt", cleanup_failures[arm_id].encode(),
                                     media_type="text/plain")
    if cleanup_failures:
        # A run that leaked resources is not a successful run: leave it unfinished (no manifest), with
        # every attempt and the close evidence retained, and say so.
        raise RunnerCleanupError(output, cleanup_failures)
    return artifacts.finish()
