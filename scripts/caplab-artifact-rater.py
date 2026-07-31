#!/usr/bin/env python3
"""Select, run, and evaluate an append-only artifact-rater calibration."""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from caplab.artifact_rater import (
    CalibrationError,
    build_artifact_prompt,
    build_calibration_manifest,
    build_judgment_schema,
    evaluate_calibration,
    extract_thread_id,
    read_rollout_attestation,
    validate_judgment,
)


def _json_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


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
    _write_new(path, _json_bytes(value))


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _save_idempotent(path: Path, value: object) -> None:
    encoded = _json_bytes(value)
    if path.exists():
        if path.read_bytes() != encoded:
            raise CalibrationError(f"refusing to replace different evidence: {path}")
        return
    _write_new(path, encoded)


def _attempt_number(slot_root: Path) -> int:
    existing = [
        int(path.name.removeprefix("attempt-"))
        for path in slot_root.glob("attempt-[0-9][0-9][0-9]")
        if path.name.removeprefix("attempt-").isdigit()
    ]
    return max(existing, default=0) + 1


def _find_rollout(thread_id: str, timeout_seconds: float = 10.0) -> Path:
    sessions = Path.home() / ".codex" / "sessions"
    deadline = time.monotonic() + timeout_seconds
    while True:
        matches = sorted(sessions.glob(f"**/*{thread_id}*.jsonl"))
        if matches:
            return matches[-1]
        if time.monotonic() >= deadline:
            raise CalibrationError(f"cannot locate persisted rollout for {thread_id}")
        time.sleep(0.1)


def _rater_metadata(output_root: Path, model: str, effort: str) -> dict[str, Any]:
    version = subprocess.run(
        ["codex", "--version"],
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    ).stdout.strip()
    path = output_root / "rater.json"
    stable = {
        "schema_version": "caplab-artifact-rater/1",
        "native_harness": "codex",
        "model": model,
        "effort": effort,
        "version": version,
        "sandbox": "read-only",
        "ignore_user_config": True,
        "ignore_rules": True,
        "output_schema": "exact-boolean-object",
    }
    if path.exists():
        existing = _load_json(path)
        for key, value in stable.items():
            if existing.get(key) != value:
                raise CalibrationError(f"rater metadata mismatch at {key}: {path}")
        return existing
    metadata = {
        **stable,
        "created_at": datetime.now(UTC).isoformat(),
    }
    _write_new_json(path, metadata)
    return metadata


def _recover_completed_attempt(
    attempt_root: Path,
    accepted_path: Path,
    entry: dict[str, Any],
    model: str,
    effort: str,
) -> bool:
    """Accept a preserved successful call after a local parser correction."""
    record_path = attempt_root / "record.json"
    if not record_path.is_file() or (attempt_root / "recovery.json").exists():
        return False
    record = _load_json(record_path)
    if (
        record.get("return_code") != 0
        or record.get("model") != model
        or record.get("effort") != effort
        or record.get("diff_sha256") != entry["diff_sha256"]
    ):
        return False
    last_message_path = attempt_root / "last-message.txt"
    events_path = attempt_root / "events.jsonl"
    if not last_message_path.is_file() or not events_path.is_file():
        return False

    judgment = validate_judgment(
        json.loads(last_message_path.read_text(encoding="utf-8")),
        entry["code_ids"],
    )
    thread_id = extract_thread_id(events_path.read_text(encoding="utf-8"))
    source_rollout = _find_rollout(thread_id)
    attestation = read_rollout_attestation(source_rollout, thread_id)
    if attestation["model"] != model or attestation["effort"] != effort:
        raise CalibrationError(
            f"attested tuple mismatch: {attestation['model']}/{attestation['effort']}"
        )
    custody_rollout = attempt_root / "rollout.jsonl"
    if not custody_rollout.exists():
        shutil.copyfile(source_rollout, custody_rollout)
    attestation["source_rollout_path"] = attestation.pop("rollout_path")
    attestation["custody_rollout_sha256"] = _sha256(custody_rollout)
    recovery = {
        "schema_version": "caplab-artifact-rater-recovery/1",
        "recovered_at": datetime.now(UTC).isoformat(),
        "reason": "original parser did not read turn_context attestation",
        "original_record_sha256": _sha256(record_path),
        "thread_id": thread_id,
        "attestation": attestation,
        "last_message_sha256": _sha256(last_message_path),
    }
    _write_new_json(attempt_root / "recovery.json", recovery)
    accepted = {
        "schema_version": "caplab-artifact-rater-judgment/1",
        "slot": entry["slot"],
        "scenario": entry["scenario"],
        "model": model,
        "effort": effort,
        "thread_id": thread_id,
        "diff_sha256": entry["diff_sha256"],
        "prompt_sha256": record["prompt_sha256"],
        "judgment": judgment,
        "attempt": attempt_root.name,
        "recovered_from_preserved_attempt": True,
    }
    _write_new_json(accepted_path, accepted)
    return True


def _score_entry(
    entry: dict[str, Any],
    manifest: dict[str, Any],
    output_root: Path,
    model: str,
    effort: str,
    timeout_seconds: int,
) -> tuple[str, bool, str]:
    slot = entry["slot"]
    slot_root = output_root / "scores" / slot
    accepted_path = slot_root / "accepted.json"
    if accepted_path.exists():
        accepted = _load_json(accepted_path)
        validate_judgment(accepted.get("judgment"), entry["code_ids"])
        if (
            accepted.get("model") != model
            or accepted.get("effort") != effort
            or accepted.get("diff_sha256") != entry["diff_sha256"]
        ):
            raise CalibrationError(f"accepted evidence mismatch for {slot}")
        return slot, True, "already accepted"

    for prior_attempt in sorted(slot_root.glob("attempt-[0-9][0-9][0-9]"), reverse=True):
        try:
            if _recover_completed_attempt(
                prior_attempt, accepted_path, entry, model, effort
            ):
                return slot, True, f"recovered {prior_attempt.name}"
        except (CalibrationError, json.JSONDecodeError, OSError):
            continue

    attempt_root = slot_root / f"attempt-{_attempt_number(slot_root):03d}"
    attempt_root.mkdir(parents=True, exist_ok=False)
    campaign_root = Path(manifest["campaign_root"])
    scenario_root = Path(manifest["scenario_root"])
    diff_path = campaign_root / "attempts" / slot / "diff.patch"
    if _sha256(diff_path) != entry["diff_sha256"]:
        raise CalibrationError(f"diff changed after manifest freeze: {slot}")
    diff = diff_path.read_text(encoding="utf-8")
    prompt = build_artifact_prompt(
        scenario_root / entry["scenario"] / "codes.json", diff
    )
    schema = build_judgment_schema(entry["code_ids"])
    prompt_path = attempt_root / "prompt.txt"
    schema_path = attempt_root / "schema.json"
    events_path = attempt_root / "events.jsonl"
    stderr_path = attempt_root / "stderr.txt"
    last_message_path = attempt_root / "last-message.txt"
    _write_new(prompt_path, prompt.encode("utf-8"))
    _write_new_json(schema_path, schema)

    with tempfile.TemporaryDirectory(prefix="caplab-rater-") as empty_directory:
        command = [
            "codex",
            "exec",
            "--ignore-user-config",
            "--ignore-rules",
            "--strict-config",
            "--sandbox",
            "read-only",
            "--cd",
            empty_directory,
            "--skip-git-repo-check",
            "--model",
            model,
            "--config",
            f'model_reasoning_effort="{effort}"',
            "--output-schema",
            str(schema_path),
            "--json",
            "--output-last-message",
            str(last_message_path),
            "-",
        ]
        started_at = datetime.now(UTC).isoformat()
        try:
            completed = subprocess.run(
                command,
                input=prompt,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
            )
            return_code = completed.returncode
            events = completed.stdout
            stderr = completed.stderr
        except subprocess.TimeoutExpired as error:
            return_code = 124
            events = error.stdout or ""
            stderr = (error.stderr or "") + f"\nTimed out after {timeout_seconds}s\n"
    _write_new(events_path, events.encode("utf-8"))
    _write_new(stderr_path, stderr.encode("utf-8"))

    record: dict[str, Any] = {
        "schema_version": "caplab-artifact-rater-attempt/1",
        "slot": slot,
        "model": model,
        "effort": effort,
        "started_at": started_at,
        "finished_at": datetime.now(UTC).isoformat(),
        "return_code": return_code,
        "command": command[:-1] + ["<prompt-on-stdin>"],
        "prompt_sha256": _sha256(prompt_path),
        "schema_sha256": _sha256(schema_path),
        "events_sha256": _sha256(events_path),
        "stderr_sha256": _sha256(stderr_path),
        "diff_sha256": entry["diff_sha256"],
        "accepted": False,
    }
    try:
        if return_code != 0:
            raise CalibrationError(f"Codex exited {return_code}")
        if not last_message_path.is_file():
            raise CalibrationError("Codex did not write a final message")
        judgment = validate_judgment(
            json.loads(last_message_path.read_text(encoding="utf-8")),
            entry["code_ids"],
        )
        thread_id = extract_thread_id(events)
        source_rollout = _find_rollout(thread_id)
        attestation = read_rollout_attestation(source_rollout, thread_id)
        if attestation["model"] != model or attestation["effort"] != effort:
            raise CalibrationError(
                "attested tuple mismatch: "
                f"{attestation['model']}/{attestation['effort']}"
            )
        custody_rollout = attempt_root / "rollout.jsonl"
        shutil.copyfile(source_rollout, custody_rollout)
        attestation["source_rollout_path"] = attestation.pop("rollout_path")
        attestation["custody_rollout_sha256"] = _sha256(custody_rollout)
        record.update(
            {
                "accepted": True,
                "thread_id": thread_id,
                "last_message_sha256": _sha256(last_message_path),
                "attestation": attestation,
            }
        )
        accepted = {
            "schema_version": "caplab-artifact-rater-judgment/1",
            "slot": slot,
            "scenario": entry["scenario"],
            "model": model,
            "effort": effort,
            "thread_id": thread_id,
            "diff_sha256": entry["diff_sha256"],
            "prompt_sha256": record["prompt_sha256"],
            "judgment": judgment,
            "attempt": attempt_root.name,
        }
        _write_new_json(accepted_path, accepted)
        message = "accepted"
        success = True
    except (CalibrationError, json.JSONDecodeError, OSError) as error:
        record["failure"] = str(error)
        message = str(error)
        success = False
    _write_new_json(attempt_root / "record.json", record)
    return slot, success, message


def command_select(arguments: argparse.Namespace) -> int:
    manifest = build_calibration_manifest(
        arguments.campaign_root,
        arguments.scenario_root,
        seed=arguments.seed,
        per_scenario=arguments.per_scenario,
    )
    _save_idempotent(arguments.output, manifest)
    print(f"selected {len(manifest['entries'])} calibration attempts")
    return 0


def command_run(arguments: argparse.Namespace) -> int:
    manifest = _load_json(arguments.manifest)
    arguments.output_root.mkdir(parents=True, exist_ok=True)
    _rater_metadata(arguments.output_root, arguments.model, arguments.effort)
    _save_idempotent(arguments.output_root / "manifest.json", manifest)
    results: list[tuple[str, bool, str]] = []
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=arguments.workers
    ) as executor:
        futures = [
            executor.submit(
                _score_entry,
                entry,
                manifest,
                arguments.output_root,
                arguments.model,
                arguments.effort,
                arguments.timeout,
            )
            for entry in manifest["entries"]
        ]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            results.append(result)
            print(f"{result[0]}: {result[2]}", flush=True)
    failures = [result for result in results if not result[1]]
    print(f"accepted {len(results) - len(failures)}/{len(results)}")
    return 1 if failures else 0


def command_evaluate(arguments: argparse.Namespace) -> int:
    manifest = _load_json(arguments.manifest)
    judgments = {}
    for entry in manifest["entries"]:
        accepted = _load_json(
            arguments.output_root / "scores" / entry["slot"] / "accepted.json"
        )
        judgments[entry["slot"]] = accepted["judgment"]
    result = evaluate_calibration(manifest, judgments)
    result["model"] = arguments.model
    result["effort"] = arguments.effort
    _save_idempotent(arguments.output_root / "calibration-result.json", result)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["passed"] else 2


def parser() -> argparse.ArgumentParser:
    argument_parser = argparse.ArgumentParser()
    subparsers = argument_parser.add_subparsers(dest="command", required=True)

    select = subparsers.add_parser("select")
    select.add_argument("--campaign-root", type=Path, required=True)
    select.add_argument("--scenario-root", type=Path, required=True)
    select.add_argument("--seed", type=int, required=True)
    select.add_argument("--per-scenario", type=int, required=True)
    select.add_argument("--output", type=Path, required=True)
    select.set_defaults(function=command_select)

    run = subparsers.add_parser("run")
    run.add_argument("--manifest", type=Path, required=True)
    run.add_argument("--output-root", type=Path, required=True)
    run.add_argument("--model", required=True)
    run.add_argument("--effort", required=True)
    run.add_argument("--workers", type=int, default=4)
    run.add_argument("--timeout", type=int, default=900)
    run.set_defaults(function=command_run)

    evaluate = subparsers.add_parser("evaluate")
    evaluate.add_argument("--manifest", type=Path, required=True)
    evaluate.add_argument("--output-root", type=Path, required=True)
    evaluate.add_argument("--model", required=True)
    evaluate.add_argument("--effort", required=True)
    evaluate.set_defaults(function=command_evaluate)
    return argument_parser


def main() -> int:
    arguments = parser().parse_args()
    try:
        return arguments.function(arguments)
    except (CalibrationError, OSError, json.JSONDecodeError, subprocess.SubprocessError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
