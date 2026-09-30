"""Shared fixtures for the retrieval runner tests (not a test module).

`StubArtifacts` follows the coordinator's published `RunArtifacts` interface so
the runner can be tested before the real artifact store is integrated: it seals
`plan.json` first, appends each attempt durably to `attempts.jsonl`, keeps raw
bytes separate, and writes `report.json` on `finish`. The fixture retrievers are
deterministic, provider-free commands.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import textwrap
from pathlib import Path

from caplab.retrieval import contracts, metrics

REPORT_SCHEMA = "caplab-retrieval-report/1"


class StubArtifacts:
    instances: list = []

    def __init__(self, output, spec, *, provenance=None):
        self.output = Path(output)
        self.output.mkdir(parents=True)  # Raises FileExistsError for a reused directory.
        self.spec = spec
        self.provenance = provenance
        self.calls = []
        self.attempts = []
        self.registered = {}
        self.finished = False
        (self.output / "plan.json").write_bytes(contracts.canonical_json({
            "spec": spec, "spec_digest": contracts.spec_digest(spec),
            "roster": contracts.assignments(spec), "provenance": provenance}))
        self.calls.append("plan")
        type(self).instances.append(self)

    def pending_assignments(self):
        done = {a["assignment_id"] for a in self.attempts}
        return [row for row in contracts.assignments(self.spec) if row["assignment_id"] not in done]

    def register_bytes(self, name, payload, *, media_type="application/octet-stream"):
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,255}", name):
            raise ValueError(f"invalid artifact name {name!r}")
        if name in self.registered and self.registered[name] != payload:
            raise ValueError(f"{name!r} is already registered with other bytes")
        self.calls.append(("register", name))
        self.registered[name] = payload
        return {"name": name, "declared_media_type": media_type, "sha256": hashlib.sha256(payload).hexdigest(),
                "byte_count": len(payload)}

    def record_attempt(self, attempt, *, raw=None):
        attempt = contracts.validate_attempt(attempt, self.spec)
        for role in (raw or {}):
            if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", role):
                raise ValueError(f"invalid raw role {role!r}")
        if any(a["assignment_id"] == attempt["assignment_id"] for a in self.attempts):
            raise ValueError(f"assignment {attempt['assignment_id']} is already recorded")
        self.calls.append(("attempt", attempt["assignment_id"], attempt["status"]))
        with (self.output / "attempts.jsonl").open("ab") as handle:
            handle.write(contracts.canonical_json(attempt) + b"\n")
            handle.flush()
            os.fsync(handle.fileno())
        for key, payload in (raw or {}).items():
            folder = self.output / "raw" / attempt["assignment_id"].replace(":", "__")
            folder.mkdir(parents=True, exist_ok=True)
            (folder / key).write_bytes(payload)
        self.attempts.append(attempt)
        return attempt

    def finish(self):
        self.calls.append("finish")
        self.finished = True
        # The real store's vocabulary: only a missing assignment is incomplete; any attempt that is
        # not `ok` (error, timeout, interrupted, not_started) is a failure.
        if self.pending_assignments():
            status = "incomplete"
        elif any(a["status"] != "ok" for a in self.attempts):
            status = "completed_with_failures"
        else:
            status = "complete"
        report = {"schema_version": REPORT_SCHEMA, "spec_digest": contracts.spec_digest(self.spec),
                  "run": {"status": status}, "summary": metrics.summarize(self.spec, self.attempts),
                  "provenance": self.provenance}
        data = contracts.canonical_json(report)
        (self.output / "report.json").write_bytes(data)
        return {"status": status, "complete": status == "complete", "run": report["run"], "report": report,
                "manifest_sha256": hashlib.sha256(data).hexdigest(), "output": str(self.output),
                "report_path": str(self.output / "report.json")}


# ---------------------------------------------------------------- spec

CORPUS = [
    {"id": "n-restart", "body": "Restart the billing worker with systemctl restart billing-worker after a deploy."},
    {"id": "n-backup", "body": "The nightly ledger database backup runs at two in the morning and keeps seven copies."},
    {"id": "n-cert", "body": "Rotate the TLS certificate with certbot renew and then reload nginx."},
    {"id": "n-cert-old", "body": "Old certificate rotation used a manual openssl step.", "supersede_with": "n-cert"},
    {"id": "n-local", "body": "Local note: the billing worker password lives in the private vault.", "shareable": False},
    {"id": "n-other", "body": "Restart the analytics worker in the other project with kubectl.", "repo": "other-collection"},
    {"id": "n-noise-1", "body": "Office plants are watered on Fridays by the facilities team."},
    {"id": "n-noise-2", "body": "The quarterly offsite agenda is posted on the team calendar."},
]
QUERIES = [
    {"id": "q-restart", "text": "how do I restart the billing worker", "relevant_ids": ["n-restart"],
     "forbidden_ids": ["n-local"]},
    {"id": "q-backup", "text": "when does the ledger backup run", "relevant_ids": ["n-backup"]},
    {"id": "q-cert", "text": "rotate the tls certificate", "relevant_ids": ["n-cert"], "forbidden_ids": ["n-cert-old"]},
    {"id": "q-none", "text": "what is the office wifi password", "relevant_ids": [], "forbidden_ids": ["n-local"],
     "stratum": "no-answer"},
]


def command_arm(arm_id, script):
    return {"id": arm_id, "adapter": "command", "configuration": {"argv": [sys.executable, str(script)]}}


def make_spec(arms, *, seeds=(0,), cutoffs=(1, 3), timeout_seconds=10, queries=None, corpus=None,
              experiment_id="runner-fixture"):
    return {"schema_version": "caplab-retrieval-spec/1", "experiment_id": experiment_id,
            "corpus": corpus or CORPUS, "queries": queries or QUERIES, "arms": arms,
            "cutoffs": list(cutoffs), "seeds": list(seeds), "timeout_seconds": timeout_seconds}


# ---------------------------------------------------------------- fixture retrievers

PRELUDE = """
import json, os, sys, time
request = json.loads(sys.stdin.read())
corpus = request["corpus"]
tokens = lambda text: {w.strip(".,:;").lower() for w in text.split()}
query = tokens(request["query"])
def score(note):
    return len(query & tokens(note["body"]))
def respond(ranked, **extra):
    print(json.dumps(dict(schema_version="caplab-retrieval-response/1", ranked_ids=ranked, **extra)))
"""

RETRIEVERS = {
    # Token overlap, best first.
    "good": "respond([n['id'] for n in sorted(corpus, key=lambda n: (-score(n), n['id']))],"
            " observation={'method': 'token-overlap'})",
    # The same scores, worst first: a deliberately bad retriever.
    "bad": "respond([n['id'] for n in sorted(corpus, key=lambda n: (score(n), n['id']))])",
    "empty": "respond([])",
    "failing": "sys.stderr.write('retriever exploded'); sys.exit(3)",
    "slow": "time.sleep(60)",
    "malformed": "print('this is not json')",
    "nan": "print('{\"schema_version\": \"caplab-retrieval-response/1\", \"ranked_ids\": [], \"observation\": {\"x\": NaN}}')",
    "wrong_schema": "print(json.dumps(dict(schema_version='other/9', ranked_ids=[])))",
    "extra_field": "print(json.dumps(dict(schema_version='caplab-retrieval-response/1', ranked_ids=[], gold=[1])))",
    "duplicate": "respond([corpus[0]['id'], corpus[0]['id']])",
    "unknown": "respond(['no-such-note'])",
    "not_list": "respond('n-restart')",
    "flood": "sys.stdout.write('x' * 5_000_000)",
    "echo_env": "respond([], observation={'env': sorted(os.environ), 'cwd': os.getcwd()})",
    "echo_request": "respond([], observation={'request_keys': sorted(request), 'note_keys': sorted({k for n in corpus for k in n})})",
    "seeded": "respond([n['id'] for n in sorted(corpus, key=lambda n: (n['id'] != corpus[request['seed'] % len(corpus)]['id'], n['id']))])",
    "grandchild": "import subprocess; subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(120)']); time.sleep(60)",
}


def write_retriever(directory, name):
    path = Path(directory) / f"{name}.py"
    path.write_text(PRELUDE + textwrap.dedent(RETRIEVERS[name]) + "\n")
    return path


def read_attempts(output):
    lines = (Path(output) / "attempts.jsonl").read_text().splitlines()
    return [json.loads(line) for line in lines]


# ---------------------------------------------------------------- fake Cairn (hermetic adapter tests)

FAKE_CAIRN = r'''#!/usr/bin/env python3
"""A fake `cairn` binary speaking the CLI protocol the adapter uses, with injectable faults."""
import json, os, socket, sys, time, uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONFIG = json.loads((HERE / "fake-cairn.json").read_text())
ARGV = sys.argv[1:]

def log():
    entry = {"argv": ARGV, "env": {k: v for k, v in os.environ.items()}, "cwd": os.getcwd()}
    with open(CONFIG["log"], "a") as handle:
        handle.write(json.dumps(entry) + "\n")

def out(data, ok=True, status="OK", **extra):
    print(json.dumps(dict(schema="cairn.response/1", ok=ok, status=status, data=data, **extra)))

def flag(name, default=None):
    return ARGV[ARGV.index(name) + 1] if name in ARGV else default

def notes_dir():
    path = Path(os.environ["CAIRN_HOME"]) / "notes"
    path.mkdir(exist_ok=True)
    return path

def load():
    # One file per note: seeding runs in parallel, so a shared file would race.
    return {p.stem: json.loads(p.read_text()) for p in notes_dir().glob("*.json")}

def tokens(text):
    return {w.strip(".,:;?").lower() for w in text.split()}

log()
command = ARGV[0]
if command == "version":
    data = dict(vcs_revision=CONFIG["revision"], vcs_modified=CONFIG.get("modified", False),
                module_version="v0.0.0-fake", go_version="go-fake")
    data = {k: v for k, v in data.items() if not (k == "vcs_revision" and CONFIG.get("unstamped"))
            and not (k == "vcs_modified" and CONFIG.get("no_modified_flag"))}
    out(data)
elif command == "migrate":
    time.sleep(CONFIG.get("migrate_sleep", 0))
    if CONFIG.get("migrate_fail"):
        out({}, ok=False, status="INTERNAL", message="migration failed")
        sys.exit(1)
    out({})
elif command == "remember":
    body = sys.stdin.read()
    record_id = str(uuid.uuid5(uuid.NAMESPACE_URL, flag("--request-id")))
    # Jitter scrambles the completion order of concurrent inserts; write time is taken afterwards, as
    # Cairn's store does, so only a sequential loader produces write times in corpus order.
    time.sleep(CONFIG.get("remember_jitter", 0) * (int(record_id[:6], 16) % 97) / 97)
    (notes_dir() / (record_id + ".json")).write_text(json.dumps(
        dict(body=body, repo=flag("--repo"), shareable="--shareable" in ARGV, superseded=False, written=time.time_ns())))
    out(dict(record_id=record_id, version=1))
elif command == "preview-retract":
    out(dict(version=1, preview_id="preview-" + ARGV[1]))
elif command == "supersede":
    request = json.loads(sys.stdin.read())
    path = notes_dir() / (request["record_id"] + ".json")
    note = json.loads(path.read_text())
    note["superseded"] = True
    path.write_text(json.dumps(note))
    out(dict(record_id=request["record_id"]))
elif command == "serve":
    if CONFIG.get("serve_fail"):
        print("fake api: cannot listen", flush=True)
        sys.exit(1)
    path = flag("--socket")
    sock = socket.socket(socket.AF_UNIX)
    sock.bind(path)
    print("fake api listening", path, "worker" if "--semantic-stream-command" in ARGV else "no-worker", flush=True)
    time.sleep(3600)
elif command == "agent" and "search" in ARGV:
    query = ARGV[-1]
    offset = int(flag("--offset", 0))
    semantic = "--semantic" in ARGV
    mode = CONFIG.get("search", {})
    if query == "readiness probe":
        mode = {k: v for k, v in mode.items() if k in ("semantic_state", "probe_garbage")}
        if mode.get("probe_garbage"):
            print("the probe answered with prose")
            sys.exit(0)
    if mode.get("sleep"):
        time.sleep(mode["sleep"])
    if mode.get("garbage"):
        print("not json at all")
        sys.exit(0)
    if mode.get("error"):
        out({}, ok=False, status="INVALID_REQUEST", message="fake refusal")
        sys.exit(2)
    repo = flag("--repo")
    scored = []
    for record_id, note in load().items():
        if note["superseded"] or not note["shareable"] or note["repo"] != repo:
            continue
        score = len(tokens(query) & tokens(note["body"]))
        if score:
            scored.append((-score, -note["written"], record_id))  # Ties: newest write first, as Cairn does.
    ranked = [record_id for *_, record_id in sorted(scored)]
    size = mode.get("page_size", 100)
    page = ranked[offset:offset + size]
    data = dict(index=[dict(record_id=r) for r in page], status="READY", ranking="binary-idf-scope-recency/1",
                omitted={"NO_LEXICAL_MATCH": len(load()) - len(ranked), "OPTIONAL_BUDGET": 0})
    if mode.get("unknown_record"):
        data["index"].append(dict(record_id="00000000-0000-0000-0000-00000000dead"))
    if offset + size < len(ranked):
        data["page"] = dict(next_offset=offset if mode.get("stall") else offset + size)
    if semantic:
        state = mode.get("semantic_state", "unavailable")
        if mode.get("flip_state_on_offset") is not None and offset >= mode["flip_state_on_offset"]:
            state = "unavailable"
        data["discovery"] = dict(state=state)
        if state == "ready":
            data["discovery"].update(model_sha256="m" * 64, algorithm="fake-embed/1")
        else:
            data["status"], data["ranking"] = "DEGRADED_NO_EMBEDDINGS", "lexical-scope-recency/4"
    out(data)
else:
    out({}, ok=False, status="INVALID_REQUEST", message="unexpected " + " ".join(ARGV))
    sys.exit(2)
'''


FAKE_WRAPPER = r"""#!/usr/bin/env bash
# A fake scripts/trial-task-eval.sh: the `--` command mode, with injectable faults.
set -euo pipefail
mode=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1])).get("mode", "ok"))' "__CONFIG__")
if [[ "$mode" == "old" || "${1:-}" != "--" ]]; then
    echo "trial_task_eval.py: error: argument command: invalid choice: '${1:-}'" >&2
    exit 2
fi
shift
root="$(mktemp -d /tmp/cairn-task-eval-pg.XXXXXXXX)"
mkdir "$root/socket"
{ echo "root $root"; echo "pgbin ${CAIRN_PG_BIN:-}"; env | sed 's/^/env /'; } >> "__RUNS__"
echo "fake postgres log" > "$root/postgres.log"
cleanup() { rm -rf -- "$root"; }
[[ "$mode" == "leak_cluster" || "$mode" == "stubborn" ]] || trap cleanup EXIT
export CAIRN_TASK_EVAL_PG="$root/socket" CAIRN_TASK_EVAL_PG_BIN="__PGBIN__"
child=
trap '[[ -z "$child" ]] || kill -TERM "$child" 2>/dev/null || true' TERM INT
"$@" <&0 &
child=$!
status=0
wait "$child" || status=$?
while kill -0 "$child" 2>/dev/null; do wait "$child" || status=$?; done
if [[ "$mode" == "stubborn" ]]; then trap '' TERM; while :; do sleep 1; done; fi  # Ignores SIGTERM: needs SIGKILL.
if [[ "$mode" == "cleanup_status" ]]; then echo "cleanup failed: fake wrapper status" >&2; status=1; fi  # As Cairn's does.
exit "$status"
"""

FAKE_CREATEDB = ("#!/bin/sh\nif [ -e \"$(dirname \"$0\")/createdb-fails\" ]; then "
                 "echo 'createdb: fake failure' >&2; exit 1; fi\nexit 0\n")
FAKE_PG_CTL = "#!/bin/sh\n[ \"$1\" = --version ] && echo 'pg_ctl (PostgreSQL) 99.0'\nexit 0\n"


def make_fake_lifecycle(directory):
    """Fake PostgreSQL client binaries and the wrapper text for a fake checkout.

    Returns (wrapper text, mode config path, run log path); the run log lists the cluster roots the
    wrapper created so a test can check that exactly those are gone.
    """
    directory = Path(directory)
    pg_bin = directory / "pgbin"
    pg_bin.mkdir()
    for name, body in (("createdb", FAKE_CREATEDB), ("pg_ctl", FAKE_PG_CTL)):
        (pg_bin / name).write_text(body)
        (pg_bin / name).chmod(0o755)
    config = directory / "fake-wrapper.json"
    config.write_text(json.dumps({"mode": "ok"}))
    runs = directory / "wrapper-runs"
    text = FAKE_WRAPPER.replace("__CONFIG__", str(config)).replace("__PGBIN__", str(pg_bin)).replace("__RUNS__", str(runs))
    return text, config, runs


def wrapper_log(runs, kind):
    """The values the fake wrapper logged for `kind` (`root`, `pgbin` or `env`)."""
    runs = Path(runs)
    lines = runs.read_text().splitlines() if runs.exists() else []
    return [line.split(" ", 1)[1] if " " in line else "" for line in lines if line.split(" ", 1)[0] == kind]


def wrapper_roots(runs):
    """Every cluster root the fake wrapper created, in order."""
    return wrapper_log(runs, "root")


def make_git_checkout(directory, wrapper=None):
    """A tiny committed git repository (optionally with scripts/trial-task-eval.sh); returns (path, HEAD)."""
    import subprocess
    path = Path(directory) / "checkout"
    path.mkdir()
    if wrapper is not None:
        (path / "scripts").mkdir()
        (path / "scripts" / "trial-task-eval.sh").write_text(wrapper)
        (path / "scripts" / "trial-task-eval.sh").chmod(0o755)
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
    for command in (["init", "-q"], ["config", "commit.gpgsign", "false"]):
        subprocess.run(["git", "-C", str(path), *command], check=True, env=env)
    (path / "README").write_text("fixture\n")
    subprocess.run(["git", "-C", str(path), "add", "-A"], check=True, env=env)
    subprocess.run(["git", "-C", str(path), "commit", "-q", "-m", "fixture"], check=True, env=env)
    head = subprocess.run(["git", "-C", str(path), "rev-parse", "HEAD"], check=True, capture_output=True,
                          text=True).stdout.strip()
    return path, head


def write_fake_cairn(directory, head, **config):
    """Write the fake binary beside its config; returns (binary, invocation log path)."""
    directory = Path(directory)
    log = directory / "invocations.jsonl"
    (directory / "fake-cairn.json").write_text(json.dumps(dict(config, revision=head, log=str(log))))
    binary = directory / "cairn"
    binary.write_text(FAKE_CAIRN)
    binary.chmod(0o755)
    return binary, log


def read_invocations(log):
    return [json.loads(line) for line in Path(log).read_text().splitlines()] if Path(log).exists() else []
