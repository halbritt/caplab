"""Complete the private fate gate locally after artifact recovery."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from .contract import ContractError
from .evaluate import side
from .runtime import training_config


def _read_bytes(path: Path) -> bytes:
    try:
        return path.read_bytes()
    except OSError as exc:
        raise ContractError(f"could not read {path}: {exc}") from exc


def _json_lines(path: Path, data: bytes) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        lines = data.decode("utf-8").splitlines()
    except UnicodeDecodeError as exc:
        raise ContractError(f"{path} is not UTF-8") from exc
    for line_number, line in enumerate(lines, start=1):
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ContractError(
                f"{path} line {line_number} is not valid JSON"
            ) from exc
        if not isinstance(row, dict):
            raise ContractError(f"{path} line {line_number} is not a JSON object")
        rows.append(row)
    return rows


def score_fate(
    *, results_path: Path, analysis_path: Path, eval_source_path: Path
) -> dict[str, Any]:
    config = training_config()["quality_gate"]
    evaluation_policy = config["epoch_one_full"]
    analysis_policy = config.get("local_fate_analysis")
    if not isinstance(analysis_policy, dict):
        raise ContractError("quality policy has no pinned local fate analysis")
    expected_count = evaluation_policy["examples"]
    eval_source_bytes = _read_bytes(eval_source_path)
    analysis_bytes = _read_bytes(analysis_path)
    results_bytes = _read_bytes(results_path)
    eval_source_sha256 = hashlib.sha256(eval_source_bytes).hexdigest()
    analysis_sha256 = hashlib.sha256(analysis_bytes).hexdigest()
    results_sha256 = hashlib.sha256(results_bytes).hexdigest()
    if eval_source_sha256 != evaluation_policy["source_sha256"]:
        raise ContractError("evaluation source hash does not match the authorized policy")
    if analysis_sha256 != analysis_policy.get("source_sha256"):
        raise ContractError("analysis source hash does not match the authorized policy")

    examples = _json_lines(eval_source_path, eval_source_bytes)
    if len(examples) != expected_count:
        raise ContractError(
            f"expected {expected_count} authorized evaluation examples, "
            f"found {len(examples)}"
        )
    expected_dispatch_ids: list[str] = []
    for example in examples:
        metadata = example.get("meta")
        dispatch_id = (
            metadata.get("dispatch_id") if isinstance(metadata, dict) else None
        )
        if not isinstance(dispatch_id, str) or not dispatch_id:
            raise ContractError("authorized evaluation example has no dispatch ID")
        expected_dispatch_ids.append(dispatch_id)
    if len(set(expected_dispatch_ids)) != expected_count:
        raise ContractError("authorized evaluation dispatch IDs are not unique")

    try:
        analysis_document = json.loads(analysis_bytes)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ContractError("analysis is not valid UTF-8 JSON") from exc
    reviews = (
        analysis_document.get("reviews")
        if isinstance(analysis_document, dict)
        else None
    )
    if not isinstance(reviews, list):
        raise ContractError("analysis has no reviews list")
    fate: dict[str, str] = {}
    seen_analysis_dispatch_ids: set[str] = set()
    for review in reviews:
        if not isinstance(review, dict):
            raise ContractError("analysis review is not a JSON object")
        dispatch_id = review.get("dispatch_id")
        if not isinstance(dispatch_id, str) or not dispatch_id:
            raise ContractError("analysis review has no dispatch ID")
        if dispatch_id in seen_analysis_dispatch_ids:
            raise ContractError(f"analysis dispatch ID is duplicated: {dispatch_id}")
        seen_analysis_dispatch_ids.add(dispatch_id)
        disposition = review.get("fate")
        if isinstance(disposition, str):
            fate[dispatch_id] = disposition

    rows = _json_lines(results_path, results_bytes)
    result_dispatch_ids = [row.get("dispatch_id") for row in rows]
    if result_dispatch_ids != expected_dispatch_ids:
        raise ContractError(
            "result dispatch IDs do not match the authorized evaluation source"
        )

    missing_fates = [
        dispatch_id
        for dispatch_id in expected_dispatch_ids
        if fate.get(dispatch_id) not in {"final", "revised"}
    ]
    if missing_fates:
        raise ContractError(
            f"authorized evaluation examples lack usable fate records: "
            f"{missing_fates[:3]}"
        )

    scored = []
    for row in rows:
        verdict_side = side(row.get("verdict"))
        if verdict_side is None:
            continue
        disposition = fate[row["dispatch_id"]]
        scored.append(
            verdict_side == ("accepting" if disposition == "final" else "refusing")
        )

    legal_baseline = config["strictly_beat"]["verdict_legal"]
    required_min_fate_scored = next(
        count
        for count in range(expected_count + 1)
        if count / expected_count > legal_baseline
    )
    verdict_legal_passed = len(scored) >= required_min_fate_scored
    agreement = sum(scored) / len(scored) if scored else None
    fate_baseline = config["strictly_beat"]["fate_agreement"]
    fate_agreement_passed = agreement is not None and agreement > fate_baseline
    dispatch_ids_sha256 = hashlib.sha256(
        json.dumps(
            expected_dispatch_ids,
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode()
    ).hexdigest()
    receipt = {
        "protocol": "striatum-local-fate-gate/2",
        "results_sha256": results_sha256,
        "analysis_sha256": analysis_sha256,
        "eval_source_sha256": eval_source_sha256,
        "analysis_policy_path": analysis_policy.get("source_path"),
        "eval_source_policy_path": evaluation_policy.get("source_path"),
        "authorized_dispatch_ids_sha256": dispatch_ids_sha256,
        "results_count": len(rows),
        "matched_fate_records": expected_count,
        "fate_scored": len(scored),
        "required_min_fate_scored": required_min_fate_scored,
        "verdict_legal": len(scored) / expected_count,
        "verdict_legal_baseline": legal_baseline,
        "verdict_legal_passed": verdict_legal_passed,
        "fate_agreement": agreement,
        "baseline": fate_baseline,
        "fate_agreement_passed": fate_agreement_passed,
        "passed": verdict_legal_passed and fate_agreement_passed,
    }
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--analysis", type=Path, required=True)
    parser.add_argument("--eval-source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    receipt = score_fate(
        results_path=args.results,
        analysis_path=args.analysis,
        eval_source_path=args.eval_source,
    )
    args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    if not receipt["verdict_legal_passed"]:
        raise ContractError(
            "legal verdict count did not strictly beat the 35B baseline: "
            f"required at least {receipt['required_min_fate_scored']}, "
            f"found {receipt['fate_scored']}"
        )
    if not receipt["fate_agreement_passed"]:
        raise ContractError("fate agreement did not strictly beat the 35B baseline")


if __name__ == "__main__":
    main()
