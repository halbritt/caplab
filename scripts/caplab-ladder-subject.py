#!/usr/bin/env python3
"""Run one append-only advisory ladder subject attempt through native Codex."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from caplab.artifact_rater import (
    CalibrationError,
    extract_thread_id,
    read_rollout_attestation,
)
from caplab.ladder_subject import (
    NativeSubjectError,
    classify_subject_attempt,
    subject_slot,
    validate_ladder_subject,
)


def _write_new(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as output:
            output.write(data)
    except BaseException:
        path.unlink(missing_ok=True)
        raise


def _write_new_json(path: Path, value: object) -> None:
    _write_new(
        path, (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")
    )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _find_rollout(thread_id: str, timeout_seconds: float = 10.0) -> Path:
    sessions = Path.home() / ".codex" / "sessions"
    deadline = time.monotonic() + timeout_seconds
    while True:
        matches = sorted(sessions.glob(f"**/*{thread_id}*.jsonl"))
        if matches:
            return matches[-1]
        if time.monotonic() >= deadline:
            raise NativeSubjectError(f"cannot locate native rollout for {thread_id}")
        time.sleep(0.1)


def _run_git(world: Path, *arguments: str, capture: bool = False) -> str:
    completed = subprocess.run(
        ["git", "-C", str(world), *arguments],
        check=True,
        capture_output=capture,
        text=True,
        timeout=60,
    )
    return completed.stdout if capture else ""


def run(arguments: argparse.Namespace) -> int:
    # The frozen ladder is complete. Reopening it requires a new authorization
    # and a sealed provider launcher/runtime bundle; the historical runner
    # inherited ambient process state and therefore cannot prove exact identity.
    raise NativeSubjectError(
        "native_ladder_execution_closed: completed campaign has no sealed "
        "provider launcher bundle"
    )


def _run_historical_ladder_attempt(arguments: argparse.Namespace) -> int:
    """Preserve the completed campaign mechanics behind the closed boundary."""
    slot = subject_slot(
        arguments.scenario,
        arguments.arm,
        arguments.model,
        arguments.effort,
        arguments.trial,
        arguments.replacement,
    )
    command_prefix = [
        "codex",
        "exec",
        "-m",
        arguments.model,
        "-c",
        f"model_reasoning_effort={arguments.effort}",
    ]
    # ADR 0039 requires this refusal before an attempt directory is prepared.
    validate_ladder_subject(
        arguments.policy,
        arguments.tuple_policy,
        arguments.model,
        arguments.effort,
        command_prefix,
    )
    version = subprocess.run(
        ["codex", "--version"],
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    ).stdout.strip()

    output = arguments.campaign_root / "attempts" / slot
    if (output / "episode.json").is_file():
        episode = json.loads((output / "episode.json").read_text(encoding="utf-8"))
        if (
            episode.get("model") == arguments.model
            and episode.get("effort") == arguments.effort
            and episode.get("scenario") == arguments.scenario
            and episode.get("arm") == arguments.arm
        ):
            print(f"{slot}: already recorded")
            return 0
        raise NativeSubjectError(f"existing slot identity mismatch: {slot}")
    if output.exists():
        raise NativeSubjectError(f"partial attempt requires adjudication: {output}")
    output.mkdir(parents=True)

    scenario = arguments.scenario_root / arguments.scenario
    source_world = scenario / "world"
    if not source_world.is_dir():
        raise NativeSubjectError(f"missing scenario world: {source_world}")
    world = output / "world"
    shutil.copytree(source_world, world)
    _run_git(world, "init", "-q")
    _run_git(world, "add", "-A")
    subprocess.run(
        [
            "git",
            "-C",
            str(world),
            "-c",
            "user.email=caplab@invalid",
            "-c",
            "user.name=CAPLAB",
            "commit",
            "-q",
            "-m",
            "baseline",
        ],
        check=True,
        timeout=60,
    )

    task = (scenario / "TASK.md").read_text(encoding="utf-8")
    if arguments.arm == "injection":
        injection = (
            arguments.campaign_root / "render" / f"{arguments.scenario}.injection.md"
        ).read_text(encoding="utf-8")
        prompt = f"{injection}\n\n---\n\n{task}"
    else:
        prompt = task
    prompt_path = output / "prompt.txt"
    _write_new(prompt_path, prompt.encode("utf-8"))

    events_path = output / "native.stdout"
    stderr_path = output / "native.stderr"
    command = [
        *command_prefix,
        "--json",
        "--dangerously-bypass-approvals-and-sandbox",
        prompt,
    ]
    started_at = datetime.now(UTC).isoformat()
    start = time.monotonic()
    try:
        completed = subprocess.run(
            command,
            cwd=world,
            capture_output=True,
            text=True,
            timeout=arguments.timeout,
        )
        return_code = completed.returncode
        events = completed.stdout
        stderr = completed.stderr
    except subprocess.TimeoutExpired as error:
        return_code = 124
        events = error.stdout or ""
        stderr = (error.stderr or "") + f"\nTimed out after {arguments.timeout}s\n"
    duration = int(time.monotonic() - start)
    _write_new(events_path, events.encode("utf-8"))
    _write_new(stderr_path, stderr.encode("utf-8"))

    _run_git(world, "add", "-A")
    diff = _run_git(world, "diff", "--cached", capture=True)
    write_set_text = _run_git(world, "diff", "--cached", "--name-only", capture=True)
    diff_path = output / "diff.patch"
    write_set_path = output / "write_set.txt"
    _write_new(diff_path, diff.encode("utf-8"))
    _write_new(write_set_path, write_set_text.encode("utf-8"))
    write_set = [line for line in write_set_text.splitlines() if line]

    attested_model = attested_effort = thread_id = None
    pin_ok = False
    attestation_failure = None
    try:
        thread_id = extract_thread_id(events)
        source_rollout = _find_rollout(thread_id)
        attestation = read_rollout_attestation(source_rollout, thread_id)
        attested_model = attestation["model"]
        attested_effort = attestation["effort"]
        pin_ok = (
            attested_model == arguments.model and attested_effort == arguments.effort
        )
        shutil.copyfile(source_rollout, output / "rollout.jsonl")
    except (CalibrationError, NativeSubjectError, OSError) as error:
        attestation_failure = str(error)

    disposition, infrastructure_reason = classify_subject_attempt(
        events, return_code, write_set, pin_ok=pin_ok
    )
    if attestation_failure and disposition == "infrastructure":
        infrastructure_reason = attestation_failure
    episode: dict[str, Any] = {
        "slot": slot,
        "scenario": arguments.scenario,
        "arm": arguments.arm,
        "model": arguments.model,
        "effort": arguments.effort,
        "trial": arguments.trial,
        "replacement": arguments.replacement,
        "native_harness": "codex",
        "native_harness_version": version,
        "command": command_prefix,
        "rc": return_code,
        "duration_s": duration,
        "started_at": started_at,
        "finished_at": datetime.now(UTC).isoformat(),
        "disposition": disposition,
        "infra_reason": infrastructure_reason,
        "thread_id": thread_id,
        "attested_model": attested_model,
        "attested_effort": attested_effort,
        "pin_ok": pin_ok,
        "write_set": write_set,
        "attempted": (None if disposition == "infrastructure" else bool(write_set)),
        "prompt_sha256": _sha256(prompt_path),
        "diff_sha256": _sha256(diff_path),
        "events_sha256": _sha256(events_path),
        "stderr_sha256": _sha256(stderr_path),
        "policy_sha256": _sha256(arguments.policy),
        "tuple_policy_sha256": _sha256(arguments.tuple_policy),
    }
    if (output / "rollout.jsonl").is_file():
        episode["rollout_sha256"] = _sha256(output / "rollout.jsonl")
    _write_new_json(output / "episode.json", episode)
    print(f"{slot}: {disposition}")
    return 1 if disposition == "infrastructure" else 0


def parser() -> argparse.ArgumentParser:
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("--campaign-root", type=Path, required=True)
    argument_parser.add_argument("--scenario-root", type=Path, required=True)
    argument_parser.add_argument("--policy", type=Path, required=True)
    argument_parser.add_argument("--tuple-policy", type=Path, required=True)
    argument_parser.add_argument("--scenario", required=True)
    argument_parser.add_argument("--arm", choices=("none", "injection"), required=True)
    argument_parser.add_argument("--model", required=True)
    argument_parser.add_argument("--effort", required=True)
    argument_parser.add_argument("--trial", type=int, required=True)
    argument_parser.add_argument("--replacement", type=int)
    argument_parser.add_argument("--timeout", type=int, default=1200)
    return argument_parser


def main() -> int:
    try:
        return run(parser().parse_args())
    except (
        NativeSubjectError,
        CalibrationError,
        OSError,
        json.JSONDecodeError,
        subprocess.SubprocessError,
    ) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
