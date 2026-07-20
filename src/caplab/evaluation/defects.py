"""Append-only typed records for CAPLAB evaluation-gate defects."""

from __future__ import annotations

import datetime as dt
import fcntl
import json
import os
import re
from collections.abc import Mapping, Sequence
from pathlib import Path
from types import MappingProxyType
from typing import Any, TextIO

from caplab.runtime.canonical import CanonicalizationError, canonical_json, sha256_hex

from .snapshot import EvaluationGateResult


DEFECT_SCHEMA = "caplab-evaluation-gate-defect-event/1"
SHA256 = re.compile(r"^[0-9a-f]{64}$")
DISPOSITIONS = frozenset(
    {"remediated", "deferred", "duplicate", "not-a-defect", "accepted-risk"}
)


class DefectLedgerError(ValueError):
    """A defect event or ledger violates its append-only contract."""


def _freeze(value: Any) -> Any:
    if isinstance(value, dict):
        return MappingProxyType({key: _freeze(child) for key, child in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(child) for child in value)
    return value


def _digest(value: Any) -> str:
    try:
        return sha256_hex(canonical_json(value))
    except CanonicalizationError as error:
        raise DefectLedgerError("noncanonical_defect_event") from error


def _timestamp(value: str | None) -> str:
    if value is None:
        instant = dt.datetime.now(dt.timezone.utc)
    else:
        if not isinstance(value, str):
            raise DefectLedgerError(f"invalid_recorded_at:{value}")
        try:
            instant = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as error:
            raise DefectLedgerError(f"invalid_recorded_at:{value}") from error
        if instant.tzinfo is None or instant.utcoffset() != dt.timedelta(0):
            raise DefectLedgerError(f"recorded_at_must_be_utc:{value}")
    return instant.astimezone(dt.timezone.utc).isoformat(timespec="seconds").replace(
        "+00:00", "Z"
    )


def _require_exact_keys(
    value: Mapping[str, Any],
    expected: frozenset[str],
    location: str,
) -> None:
    if set(value) != expected:
        raise DefectLedgerError(
            f"invalid_shape:{location}:"
            f"missing={sorted(expected - set(value))}:"
            f"extra={sorted(set(value) - expected)}"
        )


def _observation_basis(event: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "gate": event["gate"],
        "candidate_sha256": event["candidate_sha256"],
        "baseline_sha256": event["baseline_sha256"],
        "policy_sha256": event["policy_sha256"],
        "violations": event["violations"],
    }


def _validate_observation(event: Mapping[str, Any], line_number: int) -> None:
    expected = frozenset(
        {
            "schema_version",
            "event_type",
            "event_id",
            "defect_id",
            "recorded_at",
            "assertion_type",
            "gate",
            "candidate_sha256",
            "baseline_sha256",
            "policy_sha256",
            "violations",
            "observation_sha256",
        }
    )
    _require_exact_keys(event, expected, f"ledger[{line_number}]")
    if event["schema_version"] != DEFECT_SCHEMA:
        raise DefectLedgerError(f"unsupported_event_schema:{line_number}")
    if event["event_type"] != "observation" or event["assertion_type"] != "observation":
        raise DefectLedgerError(f"invalid_observation_type:{line_number}")
    _timestamp(event["recorded_at"])
    if event["gate"] != "caplab-evaluation-snapshot":
        raise DefectLedgerError(f"invalid_gate:{line_number}")
    for name in (
        "candidate_sha256",
        "baseline_sha256",
        "policy_sha256",
        "observation_sha256",
    ):
        if not isinstance(event[name], str) or not SHA256.fullmatch(event[name]):
            raise DefectLedgerError(f"invalid_digest:{line_number}:{name}")
    violations = event["violations"]
    if (
        not isinstance(violations, Sequence)
        or isinstance(violations, (str, bytes))
        or not violations
        or any(not isinstance(item, str) or not item for item in violations)
        or list(violations) != sorted(set(violations))
    ):
        raise DefectLedgerError(f"invalid_observation_violations:{line_number}")
    digest = _digest(_observation_basis(event))
    if event["observation_sha256"] != digest:
        raise DefectLedgerError(f"observation_digest_mismatch:{line_number}")
    if event["event_id"] != f"obs-{digest[:16]}":
        raise DefectLedgerError(f"observation_event_identity_mismatch:{line_number}")
    if event["defect_id"] != f"gate-{digest[:16]}":
        raise DefectLedgerError(f"defect_identity_mismatch:{line_number}")


def _validate_text_list(value: Any, location: str) -> None:
    if (
        not isinstance(value, Sequence)
        or isinstance(value, (str, bytes))
        or not value
        or any(not isinstance(item, str) or not item for item in value)
        or list(value) != sorted(set(value))
    ):
        raise DefectLedgerError(f"invalid_text_list:{location}")


def _related_basis(event: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in event.items()
        if key not in {"event_id", "recorded_at"}
    }


def _validate_related(event: Mapping[str, Any], line_number: int) -> None:
    common = {
        "schema_version",
        "event_type",
        "event_id",
        "defect_id",
        "observation_event_id",
        "observation_sha256",
        "recorded_at",
        "assertion_type",
    }
    event_type = event.get("event_type")
    if event_type == "inference":
        expected = frozenset(
            common | {"summary", "evidence", "rivals", "inferred_by"}
        )
        prefix, assertion_type = "inf", "inference"
    elif event_type == "disposition":
        expected = frozenset(
            common | {"status", "rationale", "decided_by", "authority"}
        )
        prefix, assertion_type = "disp", "decision"
    else:
        raise DefectLedgerError(f"unknown_event_type:{line_number}:{event_type}")
    _require_exact_keys(event, expected, f"ledger[{line_number}]")
    if event["schema_version"] != DEFECT_SCHEMA:
        raise DefectLedgerError(f"unsupported_event_schema:{line_number}")
    if event["assertion_type"] != assertion_type:
        raise DefectLedgerError(f"invalid_assertion_type:{line_number}")
    _timestamp(event["recorded_at"])
    if not isinstance(event["observation_sha256"], str) or not SHA256.fullmatch(
        event["observation_sha256"]
    ):
        raise DefectLedgerError(f"invalid_observation_digest:{line_number}")
    expected_event_id = f"{prefix}-{_digest(_related_basis(event))[:16]}"
    if event["event_id"] != expected_event_id:
        raise DefectLedgerError(f"related_event_identity_mismatch:{line_number}")
    if event_type == "inference":
        for name in ("summary", "inferred_by"):
            if not isinstance(event[name], str) or not event[name]:
                raise DefectLedgerError(f"invalid_inference_field:{line_number}:{name}")
        _validate_text_list(event["evidence"], f"ledger[{line_number}].evidence")
        _validate_text_list(event["rivals"], f"ledger[{line_number}].rivals")
    else:
        if not isinstance(event["status"], str) or event["status"] not in DISPOSITIONS:
            raise DefectLedgerError(f"invalid_disposition_status:{line_number}")
        for name in ("rationale", "decided_by", "authority"):
            if not isinstance(event[name], str) or not event[name]:
                raise DefectLedgerError(f"invalid_disposition_field:{line_number}:{name}")


def _validate_event(event: Mapping[str, Any], line_number: int) -> None:
    if event.get("event_type") == "observation":
        _validate_observation(event, line_number)
    else:
        _validate_related(event, line_number)


def _read_events(handle: TextIO) -> list[dict[str, Any]]:
    handle.seek(0)
    events: list[dict[str, Any]] = []
    event_ids: set[str] = set()
    observations: dict[str, dict[str, Any]] = {}
    for line_number, line in enumerate(handle, 1):
        if not line.strip():
            raise DefectLedgerError(f"blank_ledger_line:{line_number}")
        try:
            event = json.loads(line)
        except json.JSONDecodeError as error:
            raise DefectLedgerError(f"invalid_json_line:{line_number}") from error
        if not isinstance(event, dict):
            raise DefectLedgerError(f"event_not_object:{line_number}")
        _validate_event(event, line_number)
        if event["event_id"] in event_ids:
            raise DefectLedgerError(f"duplicate_event_id:{event['event_id']}")
        event_ids.add(event["event_id"])
        if event["event_type"] == "observation":
            if event["defect_id"] in observations:
                raise DefectLedgerError(f"duplicate_observation:{event['defect_id']}")
            observations[event["defect_id"]] = event
        else:
            observation = observations.get(event["defect_id"])
            if observation is None:
                raise DefectLedgerError(f"event_precedes_observation:{event['event_id']}")
            if event["observation_event_id"] != observation["event_id"]:
                raise DefectLedgerError(f"observation_event_mismatch:{event['event_id']}")
            if event["observation_sha256"] != observation["observation_sha256"]:
                raise DefectLedgerError(f"observation_digest_mismatch:{event['event_id']}")
        events.append(event)
    return events


def _refuse_symlink_components(path: Path) -> None:
    current = path
    while current != current.parent:
        if current.exists() and current.is_symlink():
            raise DefectLedgerError(f"ledger_path_is_symlink:{current}")
        current = current.parent


def _fsync_directory(path: Path) -> None:
    flags = os.O_RDONLY
    if hasattr(os, "O_DIRECTORY"):
        flags |= os.O_DIRECTORY
    try:
        descriptor = os.open(path, flags)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
    except OSError as error:
        raise DefectLedgerError(f"ledger_directory_fsync_failed:{path}") from error


def load_defect_ledger(path: Path) -> tuple[Mapping[str, Any], ...]:
    """Load and validate every event without modifying the ledger."""

    _refuse_symlink_components(path)
    if not path.exists():
        return ()
    try:
        with path.open("r", encoding="utf-8") as handle:
            return tuple(_freeze(event) for event in _read_events(handle))
    except OSError as error:
        raise DefectLedgerError(f"unreadable_ledger:{path}") from error


def _append_event(path: Path, event: dict[str, Any]) -> Mapping[str, Any]:
    _validate_event(event, 0)
    _refuse_symlink_components(path)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        raise DefectLedgerError(f"unwritable_ledger_parent:{path.parent}") from error
    created = not path.exists()
    flags = os.O_APPEND | os.O_CREAT | os.O_RDWR
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags, 0o600)
    except OSError as error:
        raise DefectLedgerError(f"unwritable_ledger:{path}") from error
    with os.fdopen(descriptor, "a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        events = _read_events(handle)
        for existing in events:
            if existing["event_id"] != event["event_id"]:
                continue
            stable_existing = {k: v for k, v in existing.items() if k != "recorded_at"}
            stable_event = {k: v for k, v in event.items() if k != "recorded_at"}
            if stable_existing != stable_event:
                raise DefectLedgerError(f"event_identity_collision:{event['event_id']}")
            return _freeze(existing)
        handle.write(canonical_json(event).decode("utf-8") + "\n")
        handle.flush()
        os.fsync(handle.fileno())
        if created:
            _fsync_directory(path.parent)
        _read_events(handle)
    return _freeze(event)


def record_gate_observation(
    path: Path,
    *,
    result: EvaluationGateResult,
    recorded_at: str | None = None,
) -> Mapping[str, Any]:
    """Append one digest-bound observation for a failed snapshot gate."""

    if result.passed or not result.violations:
        raise DefectLedgerError("observation_requires_failed_gate")
    basis = {
        "gate": "caplab-evaluation-snapshot",
        "candidate_sha256": result.candidate_sha256,
        "baseline_sha256": result.baseline_sha256,
        "policy_sha256": result.policy_sha256,
        "violations": list(result.violations),
    }
    digest = _digest(basis)
    event = {
        "schema_version": DEFECT_SCHEMA,
        "event_type": "observation",
        "event_id": f"obs-{digest[:16]}",
        "defect_id": f"gate-{digest[:16]}",
        "recorded_at": _timestamp(recorded_at),
        "assertion_type": "observation",
        **basis,
        "observation_sha256": digest,
    }
    return _append_event(path, event)


def _observation_for(path: Path, defect_id: str) -> Mapping[str, Any]:
    matches = [
        event
        for event in load_defect_ledger(path)
        if event["event_type"] == "observation" and event["defect_id"] == defect_id
    ]
    if len(matches) != 1:
        raise DefectLedgerError(f"observation_not_found:{defect_id}")
    return matches[0]


def _related_event_id(prefix: str, event: Mapping[str, Any]) -> str:
    return f"{prefix}-{_digest(_related_basis(event))[:16]}"


def _normalize_texts(value: Sequence[str], location: str) -> list[str]:
    if (
        not isinstance(value, Sequence)
        or isinstance(value, (str, bytes))
        or not value
        or any(not isinstance(item, str) or not item for item in value)
    ):
        raise DefectLedgerError(f"invalid_text_list:{location}")
    return sorted(set(value))


def record_defect_inference(
    path: Path,
    *,
    defect_id: str,
    summary: str,
    evidence: Sequence[str],
    rivals: Sequence[str],
    inferred_by: str,
    recorded_at: str | None = None,
) -> Mapping[str, Any]:
    """Append an inference linked to one observed gate defect."""

    observation = _observation_for(path, defect_id)
    event = {
        "schema_version": DEFECT_SCHEMA,
        "event_type": "inference",
        "defect_id": defect_id,
        "observation_event_id": observation["event_id"],
        "observation_sha256": observation["observation_sha256"],
        "recorded_at": _timestamp(recorded_at),
        "assertion_type": "inference",
        "summary": summary,
        "evidence": _normalize_texts(evidence, "inference.evidence"),
        "rivals": _normalize_texts(rivals, "inference.rivals"),
        "inferred_by": inferred_by,
    }
    event["event_id"] = _related_event_id("inf", event)
    return _append_event(path, event)


def record_defect_disposition(
    path: Path,
    *,
    defect_id: str,
    status: str,
    rationale: str,
    decided_by: str,
    authority: str,
    recorded_at: str | None = None,
) -> Mapping[str, Any]:
    """Append an authorized decision linked to one observed gate defect."""

    observation = _observation_for(path, defect_id)
    event = {
        "schema_version": DEFECT_SCHEMA,
        "event_type": "disposition",
        "defect_id": defect_id,
        "observation_event_id": observation["event_id"],
        "observation_sha256": observation["observation_sha256"],
        "recorded_at": _timestamp(recorded_at),
        "assertion_type": "decision",
        "status": status,
        "rationale": rationale,
        "decided_by": decided_by,
        "authority": authority,
    }
    event["event_id"] = _related_event_id("disp", event)
    return _append_event(path, event)
