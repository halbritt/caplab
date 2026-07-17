#!/usr/bin/env python3
"""Append and validate typed evaluation-gate defect events."""

from __future__ import annotations

import argparse
import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
from typing import Any

import jsonschema


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCHEMA = ROOT / "doctrine/evaluations/gate-defect-event.schema.json"
SCHEMA_VERSION = "evaluation-gate-defect-event/1"


class DefectLedgerError(ValueError):
    pass


def _canonical_sha256(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _timestamp(value: str | None) -> str:
    if value:
        return value
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def _schema() -> dict[str, Any]:
    value = json.loads(DEFAULT_SCHEMA.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise DefectLedgerError("defect_schema_not_object")
    return value


def _observation_basis(event: dict[str, Any]) -> dict[str, Any]:
    return {
        "gate": event["gate"],
        "candidate_sha256": event["candidate_sha256"],
        "baseline_sha256": event["baseline_sha256"],
        "config_sha256": event["config_sha256"],
        "violations": event["violations"],
    }


def load_ledger(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    validator = jsonschema.Draft202012Validator(
        _schema(), format_checker=jsonschema.FormatChecker()
    )
    events: list[dict[str, Any]] = []
    event_ids: set[str] = set()
    observations: dict[str, dict[str, Any]] = {}
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            raise DefectLedgerError(f"blank_ledger_line:{line_number}")
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            raise DefectLedgerError(f"invalid_json_line:{line_number}:{exc}") from exc
        if not isinstance(event, dict):
            raise DefectLedgerError(f"event_not_object:{line_number}")
        validator.validate(event)
        event_id = str(event["event_id"])
        if event_id in event_ids:
            raise DefectLedgerError(f"duplicate_event_id:{event_id}")
        event_ids.add(event_id)
        defect_id = str(event["defect_id"])
        if event["event_type"] == "observation":
            digest = _canonical_sha256(_observation_basis(event))
            if event["observation_sha256"] != digest:
                raise DefectLedgerError(f"observation_digest_mismatch:{event_id}")
            if event_id != f"obs-{digest[:16]}" or defect_id != f"gate-{digest[:16]}":
                raise DefectLedgerError(f"observation_identity_mismatch:{event_id}")
            if defect_id in observations:
                raise DefectLedgerError(f"duplicate_observation:{defect_id}")
            observations[defect_id] = event
        else:
            observation = observations.get(defect_id)
            if observation is None:
                raise DefectLedgerError(f"event_precedes_observation:{event_id}")
            if event["observation_event_id"] != observation["event_id"]:
                raise DefectLedgerError(f"observation_event_mismatch:{event_id}")
            if event["observation_sha256"] != observation["observation_sha256"]:
                raise DefectLedgerError(f"observation_digest_mismatch:{event_id}")
        events.append(event)
    return events


def _append(path: Path, event: dict[str, Any]) -> dict[str, Any]:
    jsonschema.Draft202012Validator(
        _schema(), format_checker=jsonschema.FormatChecker()
    ).validate(event)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        events = load_ledger(path)
        for existing in events:
            if existing["event_id"] != event["event_id"]:
                continue
            stable_existing = {
                key: value for key, value in existing.items() if key != "recorded_at"
            }
            stable_event = {
                key: value for key, value in event.items() if key != "recorded_at"
            }
            if stable_existing != stable_event:
                raise DefectLedgerError(
                    f"event_identity_collision:{event['event_id']}"
                )
            return existing
        handle.seek(0, os.SEEK_END)
        handle.write(json.dumps(event, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
        load_ledger(path)
        return event


def record_observation(
    path: Path,
    *,
    candidate: dict[str, Any],
    baseline: dict[str, Any],
    config: dict[str, Any],
    violations: list[str],
    recorded_at: str | None = None,
) -> dict[str, Any]:
    if not violations:
        raise DefectLedgerError("observation_requires_violation")
    basis = {
        "gate": "evaluation-regression",
        "candidate_sha256": _canonical_sha256(candidate),
        "baseline_sha256": _canonical_sha256(baseline),
        "config_sha256": _canonical_sha256(config),
        "violations": sorted(set(violations)),
    }
    digest = _canonical_sha256(basis)
    event = {
        "schema_version": SCHEMA_VERSION,
        "event_type": "observation",
        "event_id": f"obs-{digest[:16]}",
        "defect_id": f"gate-{digest[:16]}",
        "recorded_at": _timestamp(recorded_at),
        "assertion_type": "observation",
        **basis,
        "observation_sha256": digest,
    }
    return _append(path, event)


def _observation_for(path: Path, defect_id: str) -> dict[str, Any]:
    observations = [
        event
        for event in load_ledger(path)
        if event["event_type"] == "observation" and event["defect_id"] == defect_id
    ]
    if len(observations) != 1:
        raise DefectLedgerError(f"observation_not_found:{defect_id}")
    return observations[0]


def _related_id(prefix: str, event: dict[str, Any]) -> str:
    stable = {key: value for key, value in event.items() if key not in {"event_id", "recorded_at"}}
    return f"{prefix}-{_canonical_sha256(stable)[:16]}"


def record_diagnosis(
    path: Path,
    *,
    defect_id: str,
    summary: str,
    evidence: list[str],
    rivals_considered: list[str],
    diagnosed_by: str,
    recorded_at: str | None = None,
) -> dict[str, Any]:
    observation = _observation_for(path, defect_id)
    event = {
        "schema_version": SCHEMA_VERSION,
        "event_type": "diagnosis",
        "defect_id": defect_id,
        "observation_event_id": observation["event_id"],
        "observation_sha256": observation["observation_sha256"],
        "recorded_at": _timestamp(recorded_at),
        "assertion_type": "inference",
        "summary": summary,
        "evidence": sorted(set(evidence)),
        "rivals_considered": sorted(set(rivals_considered)),
        "diagnosed_by": diagnosed_by,
    }
    event["event_id"] = _related_id("diag", event)
    return _append(path, event)


def record_disposition(
    path: Path,
    *,
    defect_id: str,
    status: str,
    rationale: str,
    decided_by: str,
    authority: str,
    recorded_at: str | None = None,
) -> dict[str, Any]:
    observation = _observation_for(path, defect_id)
    event = {
        "schema_version": SCHEMA_VERSION,
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
    event["event_id"] = _related_id("disp", event)
    return _append(path, event)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("--ledger", type=Path, required=True)
    diagnose_parser = subparsers.add_parser("diagnose")
    diagnose_parser.add_argument("--ledger", type=Path, required=True)
    diagnose_parser.add_argument("--defect-id", required=True)
    diagnose_parser.add_argument("--summary", required=True)
    diagnose_parser.add_argument("--evidence", action="append", required=True)
    diagnose_parser.add_argument("--rival", action="append", required=True)
    diagnose_parser.add_argument("--diagnosed-by", required=True)
    diagnose_parser.add_argument("--recorded-at")
    dispose_parser = subparsers.add_parser("dispose")
    dispose_parser.add_argument("--ledger", type=Path, required=True)
    dispose_parser.add_argument("--defect-id", required=True)
    dispose_parser.add_argument(
        "--status",
        required=True,
        choices=["remediated", "deferred", "duplicate", "not-a-defect", "accepted-risk"],
    )
    dispose_parser.add_argument("--rationale", required=True)
    dispose_parser.add_argument("--decided-by", required=True)
    dispose_parser.add_argument("--authority", required=True)
    dispose_parser.add_argument("--recorded-at")
    args = parser.parse_args(argv)

    if args.command == "validate":
        events = load_ledger(args.ledger)
        print(f"evaluation defect ledger valid: {len(events)} event(s)")
        return 0
    if args.command == "diagnose":
        event = record_diagnosis(
            args.ledger,
            defect_id=args.defect_id,
            summary=args.summary,
            evidence=args.evidence,
            rivals_considered=args.rival,
            diagnosed_by=args.diagnosed_by,
            recorded_at=args.recorded_at,
        )
    else:
        event = record_disposition(
            args.ledger,
            defect_id=args.defect_id,
            status=args.status,
            rationale=args.rationale,
            decided_by=args.decided_by,
            authority=args.authority,
            recorded_at=args.recorded_at,
        )
    print(f"recorded {event['event_type']}: {event['event_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
