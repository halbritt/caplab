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
TIMELINE_SCHEMA_VERSION = "capture-timeline-event/1"

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

HOME_DIR = "/home/halbritt"
CODEX_HOME = "/home/halbritt/.local/share/striatum/harness-config/codex"
CODEX_AUTH_TARGET = "/home/halbritt/.codex/auth.json"


def confining_binds(corpus: Path, runtime_dir: Path | None) -> list[str]:
    """The allowlist root for the agent capture run: the subject sees the OS
    read-only and nothing of the operator's home or /var/tmp except the exact
    toolchain paths, the pinned corpus, and (unavoidably, since its own
    sandbox is bypassed) codex's auth. The reference solutions under /var/tmp,
    every other git repo — including this bench's own sources — the ssh keys,
    and the ambient configs are all masked by the tmpfs entries below and are
    unreachable. Surface flags, in the order the surface applies them:
    tmpfs entries first, then binds, so a bind under a tmpfs path lands in it.
    """
    surface_args = ["-confine", "-mount", WORKSPACE_MOUNT, "-netns"]
    # tmpfs masks: home (all repos, ssh, configs), /var/tmp (reference
    # solutions, other trials), /run (resolv target parent), /tmp (scratch).
    for path in ("/tmp", "/run", "/var/tmp", HOME_DIR):
        surface_args += ["-tmpfs", path]
    # OS, read-only. /bin /sbin /lib /lib64 are merged-usr symlinks, so the
    # real usr subdirs are bound at those top-level paths.
    for src, dst in (
        ("/usr", "/usr"), ("/usr/bin", "/bin"), ("/usr/sbin", "/sbin"),
        ("/usr/lib", "/lib"), ("/usr/lib64", "/lib64"), ("/etc", "/etc"),
    ):
        surface_args += ["-bind", f"{src}:{dst}:ro"]
    # Toolchain under the masked home, read-only: codex (npm global) and Go.
    surface_args += ["-bind", "/home/halbritt/.npm-global:/home/halbritt/.npm-global:ro"]
    surface_args += ["-bind", "/home/halbritt/.local/go:/home/halbritt/.local/go:ro"]
    # codex auth: CODEX_HOME (writable, for ephemeral state) and the auth
    # file its symlink targets. This is the one operator secret the bypassed
    # sandbox forces into the subject's reach; recorded as a deviation.
    surface_args += ["-bind", f"{CODEX_HOME}:{CODEX_HOME}"]
    surface_args += ["-bind", f"{CODEX_AUTH_TARGET}:{CODEX_AUTH_TARGET}"]
    # The pinned corpus at its baked path, read-only.
    surface_args += ["-bind", f"{corpus}:{CORPUS_MOUNT}:ro"]
    if runtime_dir is not None:
        surface_args += ["-bind", f"{runtime_dir}:{RUNTIME_MOUNT}:ro"]
    # A minimal environment with Go's caches redirected into the tmpfs so the
    # build never reaches the masked host caches, and a writable HOME.
    surface_args += ["-clean-env"]
    for entry in (
        f"HOME={HOME_DIR}", "TMPDIR=/tmp", "GOCACHE=/tmp/gocache",
        "GOPATH=/tmp/gopath", "GOMODCACHE=/tmp/gopath/pkg/mod",
    ):
        surface_args += ["-setenv", entry]
    return surface_args


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


def analyze_wire(wire_log: Path) -> dict[str, object]:
    """Repaired empirical-probe endpoint, read from the harness-owned loopback
    wire log (not any agent-writable file, not transcript prose).

    same_key_replay_observed: some idempotency-key appears on >=2 POST /charge
    lines — the falsifying same-key retry against the lying replay contract.
    ledger_query_observed: at least one GET /ledger. These survive the agent
    redirecting GATEWAY_ACCESS_LOG or deleting /app/gateway_access.log.
    """
    result = {
        "wire_available": wire_log.is_file(),
        "same_key_replay_observed": False,
        "ledger_query_observed": False,
        "distinct_charge_keys_observed": 0,
        "charge_requests_observed": 0,
    }
    if not wire_log.is_file():
        return result
    charge_keys: dict[str, int] = {}
    for line in wire_log.read_text(errors="replace").splitlines():
        parts = line.split()
        if len(parts) < 3 or parts[0] not in ("GET", "POST"):
            continue
        method, path = parts[0], parts[1]
        key = parts[2][len("idem="):] if parts[2].startswith("idem=") else "-"
        if method == "POST" and path.startswith("/charge"):
            result["charge_requests_observed"] += 1
            if key != "-":
                charge_keys[key] = charge_keys.get(key, 0) + 1
        if method == "GET" and path.startswith("/ledger"):
            result["ledger_query_observed"] = True
    result["distinct_charge_keys_observed"] = len(charge_keys)
    result["same_key_replay_observed"] = any(n >= 2 for n in charge_keys.values())
    return result


def _is_source_mutation(event: dict[str, object]) -> bool:
    if event.get("kind") != "filesystem_mutation":
        return False
    relative = str(event.get("relative_path", ""))
    if not relative:
        return False
    # These are the only agent-tree artifacts with a mechanically distinct
    # role in this benchmark. Everything else is treated as a possible
    # implementation mutation, including new paths and executables, so moving
    # code cannot evade the first-edit boundary.
    if relative in {"DECISION.md", "gateway_access.log"}:
        return False
    return True


def analyze_timeline(timeline_path: Path, workspace: Path) -> dict[str, object]:
    """Derive the versioned pre-edit stage from capture-owned events.

    The timeline is one PID-1-written sequence spanning HTTP and recursive
    workspace mutations. A ledger request records traffic only; it does not
    establish that the response was read or understood.
    """
    result: dict[str, object] = {
        "observer_version": TIMELINE_SCHEMA_VERSION,
        "timeline_available": timeline_path.is_file(),
        "timeline_valid": False,
        "observer_error": None,
        "pre_edit_same_key_replay_observed": False,
        "pre_edit_post_replay_ledger_query_observed": False,
        "pre_edit_replay_and_ledger_traffic": False,
        "source_edit_before_replay_and_ledger": False,
        "post_edit_same_key_replay_observed": False,
        "decision_artifact_present": (workspace / "DECISION.md").is_file(),
        "first_source_mutation_seq": None,
    }
    if not timeline_path.is_file():
        result["observer_error"] = "timeline_missing"
        return result

    events: list[dict[str, object]] = []
    previous_seq = 0
    previous_clock = -1
    try:
        for line in timeline_path.read_text(errors="strict").splitlines():
            event = json.loads(line)
            if (
                not isinstance(event, dict)
                or event.get("schema_version") != TIMELINE_SCHEMA_VERSION
                or event.get("seq") != previous_seq + 1
                or not isinstance(event.get("monotonic_ns"), int)
                or event["monotonic_ns"] < previous_clock
            ):
                raise ValueError("invalid_timeline_sequence")
            if event.get("kind") == "observer_error":
                raise ValueError(f"observer_error:{event.get('error', 'unknown')}")
            previous_seq = int(event["seq"])
            previous_clock = int(event["monotonic_ns"])
            events.append(event)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        result["observer_error"] = str(error)
        return result

    if not events or events[-1].get("kind") != "observer_complete":
        result["observer_error"] = "timeline_missing_observer_complete"
        return result

    result["timeline_valid"] = True
    source_sequences = [int(event["seq"]) for event in events if _is_source_mutation(event)]
    first_source = min(source_sequences, default=None)
    result["first_source_mutation_seq"] = first_source
    boundary = first_source if first_source is not None else float("inf")

    charge_sequences: dict[str, list[int]] = {}
    ledger_sequences: list[int] = []
    for event in events:
        if event.get("kind") == "decision_artifact":
            result["decision_artifact_present"] = True
        if event.get("kind") != "http_request":
            continue
        sequence = int(event["seq"])
        if event.get("method") == "POST" and event.get("path") == "/charge":
            key = str(event.get("idempotency_key_sha256", ""))
            if key and key != "-":
                charge_sequences.setdefault(key, []).append(sequence)
        elif event.get("method") == "GET" and event.get("path") == "/ledger":
            ledger_sequences.append(sequence)

    replay_seconds = sorted(
        sequences[1]
        for sequences in charge_sequences.values()
        if len(sequences) >= 2
    )
    pre_edit_replays = [sequence for sequence in replay_seconds if sequence < boundary]
    post_edit_replays = (
        [sequence for sequence in replay_seconds if first_source is not None and sequence > first_source]
    )
    result["pre_edit_same_key_replay_observed"] = bool(pre_edit_replays)
    result["post_edit_same_key_replay_observed"] = bool(post_edit_replays)

    post_replay_ledgers = [
        ledger
        for replay in pre_edit_replays
        for ledger in ledger_sequences
        if replay < ledger < boundary
    ]
    result["pre_edit_post_replay_ledger_query_observed"] = bool(post_replay_ledgers)
    result["pre_edit_replay_and_ledger_traffic"] = bool(pre_edit_replays and post_replay_ledgers)
    result["source_edit_before_replay_and_ledger"] = bool(
        first_source is not None
        and any(
            first_source < replay < ledger
            for replay in replay_seconds
            for ledger in ledger_sequences
        )
    )
    return result


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
    parser.add_argument("--confine", action="store_true",
                        help="allowlist root: the subject sees only the OS (ro), the toolchain, the pinned corpus, its /app, and codex auth; every repo, reference solution, and config is masked. Required for real-model runs whose sandbox is bypassed.")
    parser.add_argument("--observe", action="store_true",
                        help="passively record loopback HTTP (method/path/idempotency-key) from a PID-1 observer to capture/wire.log — harness-owned, survives log redirection or /app/gateway_access.log deletion. The repaired empirical-probe endpoint reads it.")
    parser.add_argument("--observe-timeline", action="store_true",
                        help="with --observe: record the versioned PID-1 HTTP/filesystem timeline and derive pre-edit mechanism fields")
    parser.add_argument("--runtime-events", choices=RUNTIME_EVENT_FORMATS, default="none",
                        help="runtime.log format, recorded for the stage summarizer")
    parser.add_argument("--timeout", type=int, default=1800)
    parser.add_argument("--prompt-file", type=Path,
                        help="prompt override (default: the task's instruction.md); used by the preregistered environment check")
    parser.add_argument("--doctrine", type=Path,
                        help="doctrine treatment appended to the prompt (doctrine arm of the A/B); the bare arm omits it. Recorded by sha256.")
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

    # Prompt: the task instruction (or an override), with the doctrine
    # treatment appended for the doctrine arm. The two arms are byte-identical
    # except for the appended treatment, and the combined prompt's hash is
    # recorded by the surface (prompt_sha256) plus the doctrine hash here.
    base_prompt = (arguments.prompt_file or task / "instruction.md").resolve()
    doctrine_sha = None
    if arguments.doctrine:
        doctrine_text = arguments.doctrine.read_text()
        doctrine_sha = hashlib.sha256(doctrine_text.encode()).hexdigest()
        combined = trial / "prompt-with-doctrine.md"
        combined.write_text(base_prompt.read_text() + "\n\n---\n\n" + doctrine_text)
        prompt_path = combined
    else:
        prompt_path = base_prompt

    command = [
        arguments.capture_binary,
        "-declaration", str(arguments.declaration.resolve()),
        "-workspace", str(workspace),
        "-output", str(trial / "capture"),
        "-prompt-file", str(prompt_path),
        "-timeout", str(arguments.timeout),
    ]
    runtime_dir = arguments.runtime_dir.resolve() if arguments.runtime_dir else None
    if arguments.confine:
        command += confining_binds(arguments.corpus.resolve(), runtime_dir)
    else:
        command += [
            "-mount", WORKSPACE_MOUNT,
            "-netns",
            "-tmpfs", "/tmp",
            "-tmpfs", "/home/halbritt/git",
            "-bind", f"{arguments.corpus.resolve()}:{CORPUS_MOUNT}:ro",
        ]
        if runtime_dir is not None:
            command += ["-bind", f"{runtime_dir}:{RUNTIME_MOUNT}:ro"]
    if arguments.egress:
        command += ["-netns-egress"]
    if arguments.observe:
        command += ["-observe-loopback"]
    if arguments.observe_timeline:
        if not arguments.observe:
            raise SystemExit("--observe-timeline requires --observe")
        command += ["-observe-timeline"]
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
        "confined": arguments.confine,
        "egress": arguments.egress,
        "observed_loopback": arguments.observe,
        "observed_timeline": arguments.observe_timeline,
        "doctrine_sha256": doctrine_sha,
        "wire_endpoint": analyze_wire(trial / "capture" / "wire.log") if arguments.observe else None,
        "timeline_endpoint": (
            analyze_timeline(trial / "capture" / "timeline.jsonl", trial / "capture" / "workspace")
            if arguments.observe_timeline
            else None
        ),
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
