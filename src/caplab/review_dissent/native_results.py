"""Normalization and calibration result for native review-dissent attempts."""

from __future__ import annotations

import argparse
import json
import os
from collections import Counter, defaultdict
from hashlib import sha256
from pathlib import Path
from typing import Any, Mapping, Sequence

from .instrument import _valid_review
from .native import build_native_review_capture
from .native_live import (
    _read_json,
    assess_native_review_attempts,
    load_native_review_attempts,
    load_native_review_live_manifest,
)


class NativeReviewResultContractError(ValueError):
    """Native review normalization or result lineage failed."""


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _digest(value: object) -> str:
    return sha256(_canonical(value)).hexdigest()


def _exclusive_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(
        path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600
    )
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(_canonical(value) + b"\n")
        stream.flush()
        os.fsync(stream.fileno())


def _group_key(row: Mapping[str, Any], dimensions: tuple[str, ...]) -> str:
    return "|".join(f"{dimension}={row[dimension]}" for dimension in dimensions)


def summarize_native_review_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Aggregate development calibration rows without rescuing invalid reviews."""

    status_counts = Counter(str(row.get("status")) for row in rows)
    outcome_counts = Counter(str(row.get("outcome")) for row in rows)
    score_counts = Counter(
        str(row["score"]) for row in rows if row.get("score") is not None
    )
    schema_valid = sum(row.get("review_schema_valid") is True for row in rows)
    score_eligible = sum(row.get("score") is not None for row in rows)
    grouped: dict[str, Any] = {}
    for dimensions in (
        ("subject_id",),
        ("truth",),
        ("cue",),
        ("world_id",),
        ("subject_id", "truth"),
        ("subject_id", "cue"),
    ):
        buckets: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
        for row in rows:
            buckets[_group_key(row, dimensions)].append(row)
        grouped["+".join(dimensions)] = {
            key: {
                "slots": len(bucket),
                "schema_valid": sum(
                    item.get("review_schema_valid") is True for item in bucket
                ),
                "score_eligible": sum(item.get("score") is not None for item in bucket),
                "score_bands": dict(
                    sorted(
                        Counter(
                            str(item["score"])
                            for item in bucket
                            if item.get("score") is not None
                        ).items()
                    )
                ),
            }
            for key, bucket in sorted(buckets.items())
        }
    if len(rows) != 16:
        conclusion = "incomplete"
        comparison_status = "not-estimable"
    elif schema_valid != 16 or score_eligible != 16:
        conclusion = "instrument-not-calibrated"
        comparison_status = "not-estimable"
    else:
        conclusion = "instrument-calibrated"
        comparison_status = "development-descriptive-only"
    return {
        "counts": {
            "primary_slots": len(rows),
            "review_schema_valid": schema_valid,
            "score_eligible": score_eligible,
            "statuses": dict(sorted(status_counts.items())),
            "outcomes": dict(sorted(outcome_counts.items())),
            "score_bands": dict(sorted(score_counts.items())),
        },
        "groups": grouped,
        "conclusion": conclusion,
        "comparison_status": comparison_status,
    }


def _severity_values(review: object) -> list[str]:
    if not isinstance(review, dict) or not isinstance(review.get("findings"), list):
        return []
    values: list[str] = []
    for finding in review["findings"]:
        if isinstance(finding, dict) and isinstance(finding.get("severity"), str):
            values.append(finding["severity"])
    return values


def normalize_native_review_campaign(manifest: Mapping[str, Any]) -> dict[str, Any]:
    """Normalize all sealed primaries and write one development result."""

    attempts = load_native_review_attempts(manifest)
    state = assess_native_review_attempts(manifest, attempts)
    if not state["complete"] or state["pending_replacement_for"] is not None:
        raise NativeReviewResultContractError("native_review_campaign_incomplete")
    instrument = manifest.get("_instrument")
    if not isinstance(instrument, dict):
        raise NativeReviewResultContractError("native_review_instrument_missing")
    raw_root = Path(manifest["storage"]["raw_custody_root"])
    normalization_root = raw_root / "normalization"
    repository_root = Path(instrument["_project_root"]) / manifest["storage"][
        "normalized_repository_root"
    ]
    if normalization_root.exists() or normalization_root.is_symlink():
        raise NativeReviewResultContractError("native_review_normalization_exists")
    if repository_root.exists() or repository_root.is_symlink():
        raise NativeReviewResultContractError("native_review_result_exists")

    rows: list[dict[str, Any]] = []
    capture_hashes: dict[str, str] = {}
    severity_counts: Counter[str] = Counter()
    directories = sorted((raw_root / "attempts").iterdir())
    for expected_number, attempt_root in enumerate(directories, 1):
        launch = _read_json(attempt_root / "launch.json")
        observation = _read_json(attempt_root / "observation.json")
        if launch.get("attempt_number") != expected_number or launch.get(
            "attempt_kind"
        ) != "primary":
            raise NativeReviewResultContractError("unexpected_native_review_attempt")
        cell_id = launch["cell_id"]
        subject_id = launch["subject_id"]
        task_root = attempt_root / "input" / launch["public_task_id"]
        native_jsonl = (attempt_root / "native.stdout").read_bytes()
        capture = build_native_review_capture(
            instrument,
            cell_id=cell_id,
            subject_id=subject_id,
            task_root=task_root,
            native_jsonl=native_jsonl,
            status=observation["status"],
            observation_sha256=observation["observation_sha256"],
            campaign_manifest_sha256=manifest["manifest_sha256"],
        )
        relative = f"captures/{cell_id}/{subject_id}.json"
        _exclusive_json(normalization_root / relative, capture)
        capture_hashes[relative] = capture["capture_sha256"]
        review: object = None
        review_path = task_root / "REVIEW.json"
        if review_path.is_file() and not review_path.is_symlink():
            try:
                review = json.loads(review_path.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, json.JSONDecodeError):
                review = None
        severities = _severity_values(review)
        severity_counts.update(severities)
        cell = instrument["cells"][cell_id]
        row = {
            "attempt_number": expected_number,
            "slot_index": launch["slot_index"],
            "cell_id": cell_id,
            "public_task_id": launch["public_task_id"],
            "subject_id": subject_id,
            "tuple_id": launch["tuple_id"],
            "world_id": cell["world_id"],
            "truth": cell["truth"],
            "cue": cell["cue"],
            "status": observation["status"],
            "outcome": capture["outcome"],
            "score": capture["mechanical"]["score"],
            "review_schema_valid": _valid_review(review),
            "observed_severity_values": severities,
            "review_sha256": observation["review_sha256"],
            "observation_sha256": observation["observation_sha256"],
            "capture_sha256": capture["capture_sha256"],
            "qualitative_disposition": "unavailable-mechanically-invalid-review-schema",
        }
        rows.append(row)

    capture_manifest = {
        "schema": "caplab.review-dissent.native-capture-manifest/v1",
        "campaign_id": manifest["campaign_id"],
        "manifest_sha256": manifest["manifest_sha256"],
        "native_instrument_design_sha256": instrument["design_sha256"],
        "captures": dict(sorted(capture_hashes.items())),
    }
    capture_manifest["capture_manifest_sha256"] = _digest(capture_manifest)
    _exclusive_json(normalization_root / "capture-manifest.json", capture_manifest)
    summary = summarize_native_review_rows(rows)
    result = {
        "schema": "caplab.review-dissent.native-development-result/v1",
        "campaign_id": manifest["campaign_id"],
        "manifest_sha256": manifest["manifest_sha256"],
        "native_instrument_design_sha256": instrument["design_sha256"],
        "capture_manifest_sha256": capture_manifest["capture_manifest_sha256"],
        "attempt_accounting": state,
        "rows": rows,
        "summary": summary,
        "observed_severity_vocabulary": dict(sorted(severity_counts.items())),
        "failure_explanation": (
            "The native prompt required a severity field but did not state the "
            "frozen critical or noncritical enum. Both native harnesses emitted "
            "ordinary severity labels, so no review satisfied the exact schema."
        ),
        "qualitative_disposition_status": "unavailable-no-schema-valid-review",
        "heldout_status": "sealed-unopened",
        "claim_ceiling": "development calibration on these synthetic review worlds only",
    }
    result["result_sha256"] = _digest(result)
    _exclusive_json(repository_root / "result.json", result)
    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m caplab.review_dissent.native_results"
    )
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--instrument", required=True, type=Path)
    args = parser.parse_args(argv)
    manifest = load_native_review_live_manifest(args.manifest, args.instrument)
    result = normalize_native_review_campaign(manifest)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
