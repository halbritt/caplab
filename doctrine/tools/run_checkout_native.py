#!/usr/bin/env python3
"""Run one checkout-retries trial through the striatum workspace-capture seam.

The execution seam is striatum-next's `striatum-workspace-capture` binary:
this driver materializes the task's pinned `/app` baseline into a fresh
workspace, verifies the corpus against the task's pinned surface manifest,
invokes the capture surface (which runs the declared runtime inside a mount
namespace that presents the workspace at /app and the corpus at the baked
books path), then grades the captured tree with the task's own pristine
world-instrumented verifier. Contract:
docs/agent-judgment/native-capture-contract.md.

The driver never parses backend declarations, never builds harness argv, and
never touches the captured tree before the verifier reads it.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

CORPUS_MOUNT = "/home/halbritt/git/books"
RUNTIME_MOUNT = "/var/tmp/.bench-runtime"
WORKSPACE_MOUNT = "/app"
UNIFORM_MTIME = 946684800  # 2000-01-01, matching the shipped tree's uniform-metadata hygiene
RUNTIME_EVENT_FORMATS = ("none", "codex-jsonl")

# The verifier is loopback-only, so it runs inside its own network namespace:
# the fixed agent-facing ports (9090/8080) are occupied by host services, and
# the host's ephemeral-port churn intermittently steals the per-phase probe
# ports. A private namespace reproduces the container's clean network, which
# is the condition the verifier was validated under.
NETNS_WRAP = [
    "bwrap", "--die-with-parent", "--bind", "/", "/", "--dev", "/dev",
    "--proc", "/proc", "--unshare-user", "--uid", "0", "--gid", "0",
    "--cap-add", "CAP_NET_ADMIN", "--unshare-net", "--",
    "/bin/sh", "-c", 'ip link set lo up 2>/dev/null; exec "$@"', "netns-init",
]


def task_content_hash(task: Path) -> str:
    # The baked corpus is gitignored and pinned separately by its surface
    # manifest, so it is excluded here. Exclusion is by path components, not a
    # substring, so a sibling like environment/corpus-notes is not silently
    # exempted.
    corpus_prefix = ("environment", "corpus")
    digest = hashlib.sha256()
    for path in sorted(task.rglob("*")):
        rel = path.relative_to(task)
        if path.is_file() and rel.parts[: len(corpus_prefix)] != corpus_prefix:
            digest.update(rel.as_posix().encode())
            digest.update(b"\0")
            digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def verify_corpus(task: Path, corpus: Path) -> dict[str, object]:
    manifest = json.loads((task / "surface-corpus.manifest.json").read_text())
    if manifest["mount"] != CORPUS_MOUNT:
        raise SystemExit(f"surface manifest mounts {manifest['mount']}, driver binds {CORPUS_MOUNT}")
    mismatched = [
        rel
        for rel, want in manifest["files"].items()
        if not (corpus / rel).is_file()
        or hashlib.sha256((corpus / rel).read_bytes()).hexdigest() != want
    ]
    if mismatched:
        raise SystemExit(f"corpus does not match pinned surface: {mismatched[:5]}")
    extras = sorted(
        str(p.relative_to(corpus))
        for p in corpus.rglob("*")
        if p.is_file() and str(p.relative_to(corpus)) not in manifest["files"]
    )
    return {"surface_hash": manifest["surface_hash"], "corpus_extras": extras}


def materialize_workspace(task: Path, workspace: Path) -> None:
    shutil.copytree(task / "environment" / "app", workspace)
    for path in sorted(workspace.rglob("*")):
        if path.is_dir():
            path.chmod(0o755)
        else:
            path.chmod(0o644)
        os.utime(path, (UNIFORM_MTIME, UNIFORM_MTIME))
    os.utime(workspace, (UNIFORM_MTIME, UNIFORM_MTIME))
    # The container image ran `chmod +x /app/scripts/smoke.sh` after COPY.
    (workspace / "scripts" / "smoke.sh").chmod(0o755)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", type=Path, required=True, help="task dir (checkout-retries-v2 or -m1)")
    parser.add_argument("--declaration", type=Path, required=True, help="backend or fixture declaration")
    parser.add_argument("--corpus", type=Path, required=True, help="pinned corpus projection to bind at the baked path")
    parser.add_argument("--trial-dir", type=Path, required=True, help="trial output dir; must not exist")
    parser.add_argument("--capture-binary", default="striatum-workspace-capture")
    parser.add_argument("--runtime-dir", type=Path, help=f"dir bound ro at {RUNTIME_MOUNT} (fixture scripts)")
    parser.add_argument("--runtime-arg", action="append", default=[], help="passed through to the capture surface")
    parser.add_argument("--egress", action="store_true",
                        help="give the runtime outbound network (vendor-endpoint runtimes); loopback is always private")
    parser.add_argument("--runtime-events", choices=RUNTIME_EVENT_FORMATS, default="none",
                        help="runtime.log format, recorded for the stage summarizer")
    parser.add_argument("--timeout", type=int, default=1800)
    parser.add_argument("--prompt-file", type=Path,
                        help="prompt override (default: the task's instruction.md); used by the preregistered environment check")
    parser.add_argument("--expect-task-hash", help="refuse to run if the task content drifted")
    arguments = parser.parse_args()

    task = arguments.task.resolve()
    current_hash = task_content_hash(task)
    if arguments.expect_task_hash and arguments.expect_task_hash != current_hash:
        raise SystemExit(f"task hash drift: expected {arguments.expect_task_hash}, got {current_hash}")

    if arguments.trial_dir.exists():
        raise SystemExit(f"trial dir {arguments.trial_dir} already exists")
    trial = arguments.trial_dir
    trial.mkdir(parents=True)

    corpus_identity = verify_corpus(task, arguments.corpus.resolve())
    workspace = trial / "workspace"
    materialize_workspace(task, workspace)

    command = [
        arguments.capture_binary,
        "-declaration", str(arguments.declaration.resolve()),
        "-workspace", str(workspace),
        "-output", str(trial / "capture"),
        "-prompt-file", str((arguments.prompt_file or task / "instruction.md").resolve()),
        "-timeout", str(arguments.timeout),
        "-mount", WORKSPACE_MOUNT,
        "-netns",
        "-tmpfs", "/tmp",
        "-tmpfs", "/home/halbritt/git",
        "-bind", f"{arguments.corpus.resolve()}:{CORPUS_MOUNT}:ro",
    ]
    if arguments.egress:
        command += ["-netns-egress"]
    if arguments.runtime_dir:
        command += ["-bind", f"{arguments.runtime_dir.resolve()}:{RUNTIME_MOUNT}:ro"]
    for extra in arguments.runtime_arg:
        command += ["-runtime-arg", extra]

    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    capture = subprocess.run(command)
    capture_ok = capture.returncode in (0, 3)

    reward = None
    verifier_error = False
    if capture_ok:
        verifier_log = (trial / "verifier.log").open("w")
        verifier = subprocess.run(
            NETNS_WRAP + ["bash", str(task / "tests" / "test.sh")],
            env={**os.environ,
                 "CHECKOUT_APP_DIR": str(trial / "capture" / "workspace"),
                 "CHECKOUT_VERIFIER_LOGS": str(trial / "verifier")},
            stdout=verifier_log, stderr=subprocess.STDOUT,
        )
        verifier_log.close()
        verifier_error = verifier.returncode != 0
        reward_file = trial / "verifier" / "reward.txt"
        if reward_file.is_file():
            reward = float(reward_file.read_text().strip())

    provenance = {}
    provenance_file = trial / "capture" / "provenance.json"
    if provenance_file.is_file():
        provenance = json.loads(provenance_file.read_text())

    record = {
        "schema_version": "native-capture-trial/1",
        "task_name": task.name,
        "task_content_hash": current_hash,
        "declaration": str(arguments.declaration),
        "runtime_events": arguments.runtime_events,
        "started": started,
        "capture_exit": capture.returncode,
        "timed_out": capture.returncode == 3,
        "verifier_error": verifier_error,
        "reward": reward,
        "provenance": provenance,
        **corpus_identity,
    }
    (trial / "trial.json").write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")

    if not capture_ok:
        print(f"CAPTURE FAILED (exit {capture.returncode})", file=sys.stderr)
        return 1
    if verifier_error:
        print("VERIFIER ERROR (not a subject reward)", file=sys.stderr)
        return 1
    print(f"reward={reward}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
