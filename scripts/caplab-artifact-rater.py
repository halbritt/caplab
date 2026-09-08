#!/usr/bin/env python3
"""Select, run, and evaluate an append-only artifact-rater calibration."""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
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
    build_scoring_manifest,
    evaluate_calibration,
    derive_artifact_judgment,
    preserve_rollout_attestation,
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
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as output:
            output.write(_json_bytes(value))
            output.flush()
            os.fsync(output.fileno())
        os.link(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


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


class PublicationError(CalibrationError):
    """Preserved work needs publication repair, not another native invocation."""


def _publish_validated_attempt(
    attempt_root: Path, accepted_path: Path, entry: dict[str, Any],
    model: str, effort: str, record: dict[str, Any], record_bytes: bytes,
) -> bool:
    if record.get("validated") is False:
        return False
    if record.get("validated") is not True or record.get("return_code") != 0 or record.get("timed_out") is True:
        raise PublicationError("invalid prepared attempt validation state")
    try:
        derived = derive_artifact_judgment(
            (attempt_root / "events.jsonl").read_bytes(),
            (attempt_root / "last-message.txt").read_bytes(), entry["code_ids"],
        )
        if derived["derivation"] != record["judgment_derivation"]:
            raise CalibrationError("preserved judgment derivation changed")
        if derived["derivation"]["events_sha256"] != record["events_sha256"]:
            raise CalibrationError("preserved event stream changed")
        for filename, key in (("prompt.txt", "prompt_sha256"), ("schema.json", "schema_sha256"),
                              ("stderr.txt", "stderr_sha256")):
            if _sha256(attempt_root / filename) != record[key]:
                raise CalibrationError(f"preserved {filename} changed")
        attestation = read_rollout_attestation(attempt_root / "rollout.jsonl", derived["thread_id"])
        if not isinstance(record.get("attestation"), dict):
            raise CalibrationError("preserved attestation is missing")
        if any(record["attestation"].get(key) != value for key, value in attestation.items()):
            raise CalibrationError("preserved rollout attestation changed")
        candidate = record["judgment_candidate"]
        if not isinstance(candidate, dict):
            raise CalibrationError("preserved judgment candidate is malformed")
        expected = {
            "slot": entry["slot"], "scenario": entry["scenario"], "model": model,
            "effort": effort, "diff_sha256": entry["diff_sha256"],
            "thread_id": derived["thread_id"], "judgment": derived["judgment"],
            "judgment_derivation": derived["derivation"], "attempt": attempt_root.name,
            "prompt_sha256": record["prompt_sha256"],
        }
        if any(candidate.get(key) != value for key, value in expected.items()):
            raise CalibrationError("preserved judgment candidate changed")
        if attestation["model"] != model or attestation["effort"] != effort:
            raise CalibrationError("preserved native tuple differs from requested tuple")
        if (attempt_root / "record.json").read_bytes() != record_bytes:
            raise CalibrationError("prepared attempt record changed during publication")
    except (CalibrationError, KeyError) as error:
        raise PublicationError(f"cannot publish preserved attempt: {error}") from error
    _write_new_json(accepted_path, {
        **candidate, "attempt_record_sha256": hashlib.sha256(record_bytes).hexdigest(),
    })
    return True


def _recover_completed_attempt(
    attempt_root: Path,
    accepted_path: Path,
    entry: dict[str, Any],
    model: str,
    effort: str,
) -> bool:
    """Accept a preserved successful call after a local parser correction."""
    record_path = attempt_root / "record.json"
    if not record_path.is_file():
        raise PublicationError(f"partial attempt requires disposition: {attempt_root}")
    record_bytes = record_path.read_bytes()
    try:
        record = json.loads(record_bytes)
    except (ValueError, UnicodeError) as error:
        raise PublicationError("preserved attempt record is unreadable") from error
    if not isinstance(record, dict):
        raise PublicationError("preserved attempt record is not an object")
    if record.get("schema_version") == "caplab-artifact-rater-attempt/2":
        return _publish_validated_attempt(
            attempt_root, accepted_path, entry, model, effort, record, record_bytes,
        )
    if record.get("schema_version") not in (None, "caplab-artifact-rater-attempt/1"):
        raise PublicationError("unsupported preserved attempt schema")
    recovery_path = attempt_root / "recovery.json"
    existing = None
    if recovery_path.exists():
        try:
            existing = _load_json(recovery_path)
        except (ValueError, UnicodeError) as error:
            raise PublicationError("existing recovery receipt is unreadable") from error
        if not isinstance(existing, dict):
            raise PublicationError("existing recovery receipt is not an object")
    if (
        record.get("return_code") != 0
        or record.get("model") != model
        or record.get("effort") != effort
        or record.get("diff_sha256") != entry["diff_sha256"]
    ):
        if existing is not None:
            raise PublicationError("recovery receipt belongs to a different attempt identity")
        return False
    last_message_path = attempt_root / "last-message.txt"
    events_path = attempt_root / "events.jsonl"
    if not last_message_path.is_file() or not events_path.is_file():
        if existing is not None:
            raise PublicationError("recovery receipt has missing source evidence")
        return False

    try:
        derived = derive_artifact_judgment(
            events_path.read_bytes(), last_message_path.read_bytes(), entry["code_ids"],
        )
        judgment, thread_id = derived["judgment"], derived["thread_id"]
        custody_rollout = attempt_root / "rollout.jsonl"
        if existing is not None:
            observed = read_rollout_attestation(custody_rollout, thread_id)
            attestation = existing.get("attestation")
            if not isinstance(attestation, dict) or any(
                attestation.get(key) != observed[key]
                for key in ("thread_id", "model", "effort", "cli_version", "rollout_sha256")
            ):
                raise CalibrationError("recovery rollout differs from its receipt")
        else:
            source_rollout = _find_rollout(thread_id)
            attestation = preserve_rollout_attestation(source_rollout, custody_rollout, thread_id)
        if attestation["model"] != model or attestation["effort"] != effort:
            raise CalibrationError(
                f"attested tuple mismatch: {attestation['model']}/{attestation['effort']}"
            )
    except CalibrationError as error:
        if existing is not None:
            raise PublicationError(f"cannot resume preserved recovery: {error}") from error
        raise
    recovery = {
        "schema_version": "caplab-artifact-rater-recovery/1",
        "recovered_at": datetime.now(UTC).isoformat(),
        "reason": "original parser did not read turn_context attestation",
        "original_record_sha256": hashlib.sha256(record_bytes).hexdigest(),
        "thread_id": thread_id,
        "attestation": attestation,
        "last_message_sha256": derived["derivation"]["last_message_sha256"],
        "judgment_derivation": derived["derivation"],
    }
    if existing is not None:
        if any(existing.get(key) != value for key, value in recovery.items() if key != "recovered_at"):
            raise PublicationError("existing recovery receipt differs from preserved evidence")
    else:
        _write_new_json(recovery_path, recovery)
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
        "judgment_derivation": derived["derivation"],
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
        if "attempt_record_sha256" in accepted:
            attempt_name = accepted.get("attempt")
            if not isinstance(attempt_name, str) or Path(attempt_name).name != attempt_name:
                raise PublicationError("invalid published attempt locator")
            record_bytes = (slot_root / attempt_name / "record.json").read_bytes()
            record = json.loads(record_bytes)
            candidate = {key: value for key, value in accepted.items() if key != "attempt_record_sha256"}
            if (hashlib.sha256(record_bytes).hexdigest() != accepted["attempt_record_sha256"]
                    or record.get("validated") is not True
                    or record.get("judgment_candidate") != candidate):
                raise PublicationError("published judgment does not match its attempt record")
        return slot, True, "already accepted"

    for prior_attempt in sorted(slot_root.glob("attempt-[0-9][0-9][0-9]"), reverse=True):
        try:
            if _recover_completed_attempt(
                prior_attempt, accepted_path, entry, model, effort
            ):
                return slot, True, f"recovered {prior_attempt.name}"
        except (PublicationError, OSError) as error:
            return slot, False, str(error)
        except (CalibrationError, json.JSONDecodeError):
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
        timed_out = False
        try:
            completed = subprocess.run(
                command,
                input=prompt.encode("utf-8"),
                capture_output=True,
                timeout=timeout_seconds,
            )
            return_code = completed.returncode
            events = completed.stdout
            stderr = completed.stderr
        except subprocess.TimeoutExpired as error:
            return_code = 124
            timed_out = True
            events = error.stdout or b""
            stderr = error.stderr or b""
    _write_new(events_path, events)
    _write_new(stderr_path, stderr)

    record: dict[str, Any] = {
        "schema_version": "caplab-artifact-rater-attempt/2",
        "slot": slot,
        "model": model,
        "effort": effort,
        "started_at": started_at,
        "finished_at": datetime.now(UTC).isoformat(),
        "return_code": return_code,
        "timed_out": timed_out,
        "timeout_seconds": timeout_seconds,
        "command": command[:-1] + ["<prompt-on-stdin>"],
        "prompt_sha256": _sha256(prompt_path),
        "schema_sha256": _sha256(schema_path),
        "events_sha256": _sha256(events_path),
        "stderr_sha256": _sha256(stderr_path),
        "diff_sha256": entry["diff_sha256"],
        "validated": False,
    }
    try:
        if timed_out:
            raise CalibrationError(f"Codex timed out after {timeout_seconds}s")
        if return_code != 0:
            raise CalibrationError(f"Codex exited {return_code}")
        if not last_message_path.is_file():
            raise CalibrationError("Codex did not write a final message")
        derived = derive_artifact_judgment(
            events, last_message_path.read_bytes(), entry["code_ids"],
        )
        judgment, thread_id = derived["judgment"], derived["thread_id"]
        source_rollout = _find_rollout(thread_id)
        custody_rollout = attempt_root / "rollout.jsonl"
        attestation = preserve_rollout_attestation(source_rollout, custody_rollout, thread_id)
        if attestation["model"] != model or attestation["effort"] != effort:
            raise CalibrationError(
                "attested tuple mismatch: "
                f"{attestation['model']}/{attestation['effort']}"
            )
        record.update(
            {
                "thread_id": thread_id,
                "last_message_sha256": derived["derivation"]["last_message_sha256"],
                "judgment_derivation": derived["derivation"],
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
            "judgment_derivation": derived["derivation"],
            "attempt": attempt_root.name,
        }
        record["validated"] = True
        record["judgment_candidate"] = accepted
    except (CalibrationError, json.JSONDecodeError, OSError) as error:
        record["failure"] = str(error)
        message = str(error)
    _write_new_json(attempt_root / "record.json", record)
    if not record["validated"]:
        return slot, False, message
    try:
        _publish_validated_attempt(
            attempt_root, accepted_path, entry, model, effort, record, _json_bytes(record),
        )
    except (PublicationError, OSError) as error:
        return slot, False, str(error)
    return slot, True, "accepted"


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


def command_select_all(arguments: argparse.Namespace) -> int:
    manifest = build_scoring_manifest(
        arguments.campaign_root,
        arguments.scenario_root,
    )
    _save_idempotent(arguments.output, manifest)
    print(f"selected {len(manifest['entries'])} behavioral attempts")
    return 0


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

    select_all = subparsers.add_parser("select-all")
    select_all.add_argument("--campaign-root", type=Path, required=True)
    select_all.add_argument("--scenario-root", type=Path, required=True)
    select_all.add_argument("--output", type=Path, required=True)
    select_all.set_defaults(function=command_select_all)

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
