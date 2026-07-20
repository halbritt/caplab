"""Contained live runner for the native review-dissent calibration."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from typing import Any, Mapping, Sequence

from caplab.preference.native_live import (
    _contained_command,
    _failure_status,
    _native_result,
    preflight_native_runtime,
)

from .instrument import _valid_review
from .native import (
    build_native_review_invocation,
    load_native_review_instrument,
    render_native_review_cell,
)


class NativeReviewLiveContractError(ValueError):
    """The native review manifest, attempt ledger, or custody is invalid."""


_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_SCHEMA = "caplab.review-dissent.native-live-manifest/v1"
_SUBJECT_STATUSES = {"completed", "refused", "invalid"}
_INFRASTRUCTURE = {
    "provider_failure",
    "harness_failure",
    "capture_failure",
    "task_image_failure",
    "verifier_failure",
}
_STATUSES = _SUBJECT_STATUSES | _INFRASTRUCTURE


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _digest(value: object) -> str:
    return sha256(_canonical(value)).hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    if path.is_symlink():
        raise NativeReviewLiveContractError(f"native_review_json_symlink:{path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise NativeReviewLiveContractError(
            f"native_review_json_unreadable:{path}:{error}"
        ) from error
    if not isinstance(value, dict):
        raise NativeReviewLiveContractError(f"native_review_json_not_object:{path}")
    return value


def _validate_sealed(document: dict[str, Any], field: str, error: str) -> str:
    sealed = dict(document)
    claimed = sealed.pop(field, None)
    actual = _digest(sealed)
    if claimed != actual:
        raise NativeReviewLiveContractError(error)
    return actual


def _resolve_source(binding: object, field: str) -> Path:
    if not isinstance(binding, dict):
        raise NativeReviewLiveContractError(f"invalid_{field}_binding")
    raw = binding.get("path")
    if not isinstance(raw, str) or Path(raw).is_absolute():
        raise NativeReviewLiveContractError(f"invalid_{field}_path")
    try:
        source = (_PROJECT_ROOT / raw).resolve(strict=True)
    except OSError as error:
        raise NativeReviewLiveContractError(f"{field}_unreadable:{error}") from error
    if not source.is_relative_to(_PROJECT_ROOT) or not source.is_file():
        raise NativeReviewLiveContractError(f"invalid_{field}_path")
    if sha256(source.read_bytes()).hexdigest() != binding.get("sha256"):
        raise NativeReviewLiveContractError(f"{field}_digest_mismatch")
    return source


def load_native_review_live_manifest(
    manifest_path: str | os.PathLike[str], instrument_path: str | os.PathLike[str]
) -> dict[str, Any]:
    """Load one exact native development campaign without held-out access."""

    manifest_file = Path(manifest_path)
    manifest = _read_json(manifest_file)
    if manifest.get("schema") != _SCHEMA:
        raise NativeReviewLiveContractError("invalid_native_review_live_schema")
    if manifest.get("status") != "active" or manifest.get("authority") != "adr-0044":
        raise NativeReviewLiveContractError("native_review_live_not_authorized")
    try:
        expiry = datetime.fromisoformat(
            str(manifest.get("expires_at")).replace("Z", "+00:00")
        )
    except ValueError as error:
        raise NativeReviewLiveContractError("invalid_native_review_live_expiry") from error
    if expiry.tzinfo is None or datetime.now(UTC) > expiry:
        raise NativeReviewLiveContractError("native_review_live_authorization_expired")
    _validate_sealed(
        manifest, "manifest_sha256", "native_review_live_manifest_digest_mismatch"
    )
    instrument_file = Path(instrument_path)
    if instrument_file.is_symlink() or sha256(instrument_file.read_bytes()).hexdigest() != manifest.get(
        "instrument", {}
    ).get("file_sha256"):
        raise NativeReviewLiveContractError("native_review_instrument_file_mismatch")
    instrument = load_native_review_instrument(instrument_file)
    if instrument["design_sha256"] != manifest["instrument"].get("design_sha256"):
        raise NativeReviewLiveContractError("native_review_instrument_design_mismatch")
    containment = manifest.get("containment")
    if not isinstance(containment, dict):
        raise NativeReviewLiveContractError("native_review_containment_missing")
    _resolve_source(containment.get("runner_source"), "native_review_runner_source")
    _resolve_source(containment.get("runtime_source"), "native_review_runtime_source")
    if manifest.get("limits") != {
        "primary_trials": 16,
        "maximum_replacements": 4,
        "maximum_trials": 20,
        "maximum_wall_clock_hours": 12,
        "trial_wall_clock_minutes": 45,
        "output_budget": "native-harness-managed-and-measured-when-exposed",
        "billing": "authenticated-subscription-capacity; no-per-call-price-observed",
    }:
        raise NativeReviewLiveContractError("native_review_live_limits_mismatch")
    storage = manifest.get("storage")
    if not isinstance(storage, dict):
        raise NativeReviewLiveContractError("native_review_storage_missing")
    raw_root = Path(str(storage.get("raw_custody_root", "")))
    if not raw_root.is_absolute() or raw_root.is_symlink():
        raise NativeReviewLiveContractError("native_review_custody_root_invalid")
    result = dict(manifest)
    result["_instrument"] = instrument
    result["_verified_manifest_sha256"] = manifest["manifest_sha256"]
    result["_manifest_path"] = manifest_file.resolve()
    return result


def build_contained_review_invocation(
    instrument: Mapping[str, Any],
    subject_id: str,
    cell_id: str,
    task_root: str | os.PathLike[str],
) -> dict[str, Any]:
    """Put a native review invocation inside the shared task-only namespace."""

    root = Path(task_root)
    if not root.is_absolute() or root.is_symlink() or not root.is_dir():
        raise NativeReviewLiveContractError("unsafe_native_review_task_root")
    native = build_native_review_invocation(
        instrument, subject_id, cell_id, Path("/work")
    )
    return {
        **native,
        "cwd": root,
        "command": _contained_command(root, native["command"]),
    }


def custody_tree_manifest(root: str | os.PathLike[str]) -> dict[str, Any]:
    """Content-identify all regular files below one custody tree."""

    tree_root = Path(root)
    if tree_root.is_symlink() or not tree_root.is_dir():
        raise NativeReviewLiveContractError("invalid_native_review_custody_tree")
    files: list[dict[str, Any]] = []
    for path in sorted(tree_root.rglob("*")):
        if path.is_symlink():
            raise NativeReviewLiveContractError("native_review_custody_symlink")
        if path.is_file():
            content = path.read_bytes()
            files.append(
                {
                    "path": path.relative_to(tree_root).as_posix(),
                    "size": len(content),
                    "sha256": sha256(content).hexdigest(),
                }
            )
    result = {"schema": "caplab.review-dissent.native-custody-tree/v1", "files": files}
    result["tree_sha256"] = _digest(result)
    return result


def _exclusive_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(
        path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600
    )
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(_canonical(value) + b"\n")
        stream.flush()
        os.fsync(stream.fileno())


def _exclusive_bytes(path: Path, value: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(
        path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600
    )
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(value)
        stream.flush()
        os.fsync(stream.fileno())


def assess_native_review_attempts(
    manifest: Mapping[str, Any], attempts: Sequence[Mapping[str, Any]]
) -> dict[str, Any]:
    """Validate exact order and infrastructure-only replacement accounting."""

    limits = manifest.get("limits", {})
    order = manifest.get("_instrument", {}).get("execution_order")
    if not isinstance(order, list):
        raise NativeReviewLiveContractError("native_review_order_unavailable")
    if len(attempts) > limits.get("maximum_trials", -1):
        raise NativeReviewLiveContractError("native_review_trial_limit")
    next_slot = 0
    pending: int | None = None
    replacements = 0
    total_seconds = 0.0
    stop_reason: str | None = None
    for attempt in attempts:
        if stop_reason is not None:
            raise NativeReviewLiveContractError("native_review_attempt_after_stop")
        slot = attempt.get("slot_index")
        kind = attempt.get("attempt_kind")
        status = attempt.get("status")
        if not isinstance(slot, int) or isinstance(slot, bool) or status not in _STATUSES:
            raise NativeReviewLiveContractError("invalid_native_review_attempt")
        try:
            seconds = float(attempt.get("duration_seconds"))
        except (TypeError, ValueError) as error:
            raise NativeReviewLiveContractError(
                "invalid_native_review_duration"
            ) from error
        if seconds < 0:
            raise NativeReviewLiveContractError("invalid_native_review_duration")
        if kind == "primary":
            if pending is not None:
                raise NativeReviewLiveContractError(
                    "unresolved_native_review_infrastructure_failure"
                )
            if slot != next_slot:
                raise NativeReviewLiveContractError("native_review_primary_order_mismatch")
            if status in _INFRASTRUCTURE:
                pending = slot
            else:
                next_slot += 1
        elif kind == "replacement":
            if pending != slot:
                raise NativeReviewLiveContractError(
                    "native_review_replacement_without_failure"
                )
            replacements += 1
            if replacements > limits.get("maximum_replacements", -1):
                raise NativeReviewLiveContractError("native_review_replacement_limit")
            if status in _INFRASTRUCTURE:
                stop_reason = "second_native_review_infrastructure_failure"
            else:
                pending = None
                next_slot += 1
        else:
            raise NativeReviewLiveContractError("invalid_native_review_attempt_kind")
        total_seconds += seconds
        if total_seconds >= limits.get("maximum_wall_clock_hours", 0) * 3600:
            stop_reason = "native_review_wall_clock_limit"
    complete = next_slot == len(order)
    if not complete and len(attempts) >= limits.get("maximum_trials", -1):
        stop_reason = stop_reason or "native_review_trial_limit"
    if (
        not complete
        and pending is not None
        and replacements >= limits.get("maximum_replacements", -1)
    ):
        stop_reason = stop_reason or "native_review_replacement_limit"
    return {
        "next_slot_index": next_slot,
        "pending_replacement_for": pending,
        "replacement_count": replacements,
        "attempt_count": len(attempts),
        "duration_seconds": format(total_seconds, ".6f"),
        "complete": complete,
        "stop_reason": stop_reason,
    }


def prepare_native_review_trial(
    manifest: dict[str, Any],
    *,
    slot_index: int,
    attempt_kind: str,
    prior_attempts: Sequence[Mapping[str, Any]] = (),
    observed_versions: Mapping[str, str] | None = None,
) -> tuple[Path, list[str]]:
    """Render and seal exactly one next native review attempt."""

    if (
        manifest.get("status") != "active"
        or manifest.get("authority") != "adr-0044"
        or manifest.get("_verified_manifest_sha256") != manifest.get("manifest_sha256")
    ):
        raise NativeReviewLiveContractError("native_review_live_not_authorized")
    instrument = manifest.get("_instrument")
    order = instrument.get("execution_order") if isinstance(instrument, dict) else None
    if not isinstance(order, list) or not isinstance(slot_index, int) or not 0 <= slot_index < len(order):
        raise NativeReviewLiveContractError("invalid_native_review_slot")
    state = assess_native_review_attempts(manifest, prior_attempts)
    if state["complete"]:
        raise NativeReviewLiveContractError("native_review_campaign_complete")
    if state["stop_reason"]:
        raise NativeReviewLiveContractError(
            f"native_review_campaign_stopped:{state['stop_reason']}"
        )
    if state["pending_replacement_for"] is None:
        if attempt_kind != "primary" or slot_index != state["next_slot_index"]:
            raise NativeReviewLiveContractError("native_review_next_action_mismatch")
    elif attempt_kind != "replacement" or slot_index != state["pending_replacement_for"]:
        raise NativeReviewLiveContractError("native_review_next_action_mismatch")
    cell_id, subject_id = order[slot_index].split(":", 1)
    custody_root = Path(manifest["storage"]["raw_custody_root"])
    if custody_root.is_symlink():
        raise NativeReviewLiveContractError("native_review_custody_root_symlink")
    attempt_number = len(prior_attempts) + 1
    attempt_root = custody_root / "attempts" / f"a{attempt_number:02d}-s{slot_index + 1:02d}-{attempt_kind}"
    if attempt_root.exists() or attempt_root.is_symlink():
        raise NativeReviewLiveContractError("native_review_attempt_exists")
    task_root = attempt_root / "input" / instrument["cells"][cell_id]["public_task_id"]
    render_native_review_cell(instrument, cell_id, task_root)
    invocation = build_contained_review_invocation(
        instrument, subject_id, cell_id, task_root.resolve()
    )
    launch = {
        "schema": "caplab.review-dissent.native-launch/v1",
        "campaign_id": manifest["campaign_id"],
        "manifest_sha256": manifest["manifest_sha256"],
        "attempt_number": attempt_number,
        "slot_index": slot_index,
        "attempt_kind": attempt_kind,
        "cell_id": cell_id,
        "public_task_id": instrument["cells"][cell_id]["public_task_id"],
        "subject_id": subject_id,
        "tuple_id": invocation["tuple_id"],
        "input_tree": custody_tree_manifest(attempt_root / "input"),
        "observed_versions": dict(observed_versions or manifest.get("runtime_versions", {})),
        "command": invocation["command"],
        "launched_at": datetime.now(UTC).isoformat(),
    }
    launch["launch_sha256"] = _digest(launch)
    _exclusive_json(attempt_root / "launch.json", launch)
    return attempt_root, invocation["command"]


def _classify_completed_attempt(
    subject_id: str, stdout: bytes, task_root: Path
) -> tuple[str, dict[str, int]]:
    _, usage = _native_result(subject_id, stdout)
    review_path = task_root / "REVIEW.json"
    if review_path.is_symlink() or not review_path.is_file():
        return "invalid", usage
    try:
        review = json.loads(review_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return "invalid", usage
    return ("completed" if _valid_review(review) else "invalid"), usage


def record_native_review_observation(
    manifest: Mapping[str, Any], *, attempt_root: str | os.PathLike[str]
) -> dict[str, Any]:
    """Classify and seal one native attempt from captured bytes."""

    root = Path(attempt_root).resolve()
    custody_root = Path(manifest["storage"]["raw_custody_root"]).resolve()
    if root.parent != custody_root / "attempts":
        raise NativeReviewLiveContractError("native_review_attempt_outside_custody")
    launch = _read_json(root / "launch.json")
    completion = _read_json(root / "completion.json")
    _validate_sealed(launch, "launch_sha256", "native_review_launch_digest_mismatch")
    _validate_sealed(
        completion,
        "completion_sha256",
        "native_review_completion_digest_mismatch",
    )
    stdout = (root / "native.stdout").read_bytes()
    stderr = (root / "native.stderr").read_bytes()
    if sha256(stdout).hexdigest() != completion.get("stdout_sha256") or sha256(
        stderr
    ).hexdigest() != completion.get("stderr_sha256"):
        raise NativeReviewLiveContractError("native_review_output_digest_mismatch")
    task_root = root / "input" / launch["public_task_id"]
    usage: dict[str, int] = {}
    if completion.get("return_code") == 0 and completion.get("timed_out") is False:
        try:
            status, usage = _classify_completed_attempt(
                launch["subject_id"], stdout, task_root
            )
        except Exception as error:
            if isinstance(error, NativeReviewLiveContractError):
                raise
            reported = _failure_status(stdout, stderr, False)
            status = "provider_failure" if reported == "provider_failure" else "capture_failure"
    else:
        status = _failure_status(
            stdout, stderr, completion.get("timed_out") is True
        )
    review_path = task_root / "REVIEW.json"
    observation = {
        "schema": "caplab.review-dissent.native-observation/v1",
        "campaign_id": manifest["campaign_id"],
        "manifest_sha256": manifest["manifest_sha256"],
        "launch_sha256": launch["launch_sha256"],
        "completion_sha256": completion["completion_sha256"],
        "attempt_number": launch["attempt_number"],
        "slot_index": launch["slot_index"],
        "attempt_kind": launch["attempt_kind"],
        "cell_id": launch["cell_id"],
        "public_task_id": launch["public_task_id"],
        "subject_id": launch["subject_id"],
        "tuple_id": launch["tuple_id"],
        "status": status,
        "usage": usage,
        "review_sha256": sha256(review_path.read_bytes()).hexdigest()
        if review_path.is_file() and not review_path.is_symlink()
        else None,
        "output_path": (root / "native.stdout").relative_to(custody_root).as_posix(),
        "output_sha256": sha256(stdout).hexdigest(),
        "task_tree": custody_tree_manifest(root / "input"),
        "duration_seconds": completion["duration_seconds"],
        "recorded_at": datetime.now(UTC).isoformat(),
    }
    observation["observation_sha256"] = _digest(observation)
    _exclusive_json(root / "observation.json", observation)
    return observation


def load_native_review_attempts(manifest: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Derive accounting exclusively from sealed attempt custody."""

    attempts_root = Path(manifest["storage"]["raw_custody_root"]) / "attempts"
    if not attempts_root.exists():
        return []
    if attempts_root.is_symlink() or not attempts_root.is_dir():
        raise NativeReviewLiveContractError("invalid_native_review_attempts_root")
    directories = sorted(path for path in attempts_root.iterdir() if path.is_dir())
    attempts: list[dict[str, Any]] = []
    for number, root in enumerate(directories, 1):
        if root.is_symlink():
            raise NativeReviewLiveContractError("native_review_attempt_symlink")
        launch = _read_json(root / "launch.json")
        completion = _read_json(root / "completion.json")
        observation = _read_json(root / "observation.json")
        _validate_sealed(launch, "launch_sha256", "native_review_launch_digest_mismatch")
        _validate_sealed(
            completion, "completion_sha256", "native_review_completion_digest_mismatch"
        )
        _validate_sealed(
            observation,
            "observation_sha256",
            "native_review_observation_digest_mismatch",
        )
        if launch.get("attempt_number") != number or observation.get("attempt_number") != number:
            raise NativeReviewLiveContractError("native_review_attempt_number_mismatch")
        if launch.get("manifest_sha256") != manifest["manifest_sha256"] or observation.get(
            "manifest_sha256"
        ) != manifest["manifest_sha256"]:
            raise NativeReviewLiveContractError("native_review_attempt_manifest_mismatch")
        output_path = custody_root = Path(manifest["storage"]["raw_custody_root"])
        output_path = custody_root / observation["output_path"]
        if output_path.is_symlink() or not output_path.is_file() or sha256(
            output_path.read_bytes()
        ).hexdigest() != observation.get("output_sha256"):
            raise NativeReviewLiveContractError("native_review_output_changed")
        attempts.append(
            {
                key: observation[key]
                for key in (
                    "slot_index",
                    "attempt_kind",
                    "status",
                    "duration_seconds",
                )
            }
        )
    assess_native_review_attempts(manifest, attempts)
    return attempts


def execute_native_review_trial(
    manifest: dict[str, Any],
    *,
    slot_index: int,
    attempt_kind: str,
    prior_attempts: Sequence[Mapping[str, Any]],
) -> Path:
    """Execute and seal exactly one contained native review attempt."""

    versions = preflight_native_runtime(manifest)
    attempt_root, command = prepare_native_review_trial(
        manifest,
        slot_index=slot_index,
        attempt_kind=attempt_kind,
        prior_attempts=prior_attempts,
        observed_versions=versions,
    )
    started = datetime.now(UTC)
    try:
        completed = subprocess.run(
            command,
            cwd=attempt_root / "input" / manifest["_instrument"]["cells"][
                manifest["_instrument"]["execution_order"][slot_index].split(":", 1)[0]
            ]["public_task_id"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=manifest["limits"]["trial_wall_clock_minutes"] * 60,
            check=False,
        )
        return_code: int | None = completed.returncode
        stdout, stderr, timed_out = completed.stdout, completed.stderr, False
    except subprocess.TimeoutExpired as error:
        return_code = None
        stdout, stderr, timed_out = error.stdout or b"", error.stderr or b"", True
    _exclusive_bytes(attempt_root / "native.stdout", stdout)
    _exclusive_bytes(attempt_root / "native.stderr", stderr)
    finished = datetime.now(UTC)
    completion = {
        "schema": "caplab.review-dissent.native-completion/v1",
        "campaign_id": manifest["campaign_id"],
        "manifest_sha256": manifest["manifest_sha256"],
        "launch_sha256": _read_json(attempt_root / "launch.json")["launch_sha256"],
        "started_at": started.isoformat(),
        "finished_at": finished.isoformat(),
        "duration_seconds": format((finished - started).total_seconds(), ".6f"),
        "return_code": return_code,
        "timed_out": timed_out,
        "stdout_sha256": sha256(stdout).hexdigest(),
        "stderr_sha256": sha256(stderr).hexdigest(),
    }
    completion["completion_sha256"] = _digest(completion)
    _exclusive_json(attempt_root / "completion.json", completion)
    record_native_review_observation(manifest, attempt_root=attempt_root)
    return attempt_root


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m caplab.review_dissent.native_live"
    )
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--instrument", required=True, type=Path)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("validate")
    commands.add_parser("preflight")
    commands.add_parser("status")
    run = commands.add_parser("run")
    run.add_argument("--slot-index", required=True, type=int)
    run.add_argument(
        "--attempt-kind", required=True, choices=("primary", "replacement")
    )
    args = parser.parse_args(argv)
    manifest = load_native_review_live_manifest(args.manifest, args.instrument)
    if args.command == "validate":
        value: object = {
            "campaign_id": manifest["campaign_id"],
            "manifest_sha256": manifest["manifest_sha256"],
        }
    elif args.command == "preflight":
        value = preflight_native_runtime(manifest)
    elif args.command == "status":
        value = assess_native_review_attempts(
            manifest, load_native_review_attempts(manifest)
        )
    else:
        attempts = load_native_review_attempts(manifest)
        value = str(
            execute_native_review_trial(
                manifest,
                slot_index=args.slot_index,
                attempt_kind=args.attempt_kind,
                prior_attempts=attempts,
            )
        )
    print(json.dumps(value, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
