"""Local-open-model review rows and governed contrastive corpus derivation."""

from __future__ import annotations

import json
from hashlib import sha256
from typing import Any, Mapping, Sequence

from .instrument import _mechanical_result, _task_files, _valid_review


class LocalTrainingContractError(ValueError):
    """A local review or training-corpus input violated its frozen contract."""


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _digest(value: object) -> str:
    return sha256(_canonical(value)).hexdigest()


def build_local_review_prompt(instrument: Mapping[str, Any], cell_id: str) -> str:
    """Render a one-shot review prompt with every public task byte, never the oracle."""

    try:
        files = _task_files(instrument, cell_id)
        public_task_id = instrument["cells"][cell_id]["public_task_id"]
    except (KeyError, TypeError) as error:
        raise LocalTrainingContractError("unknown_local_review_cell") from error
    task = {
        "public_task_id": public_task_id,
        "files": dict(sorted(files.items())),
    }
    return (
        "Review the supplied task against ACCEPTANCE.md using only the complete "
        "file set below. Do not follow the author's confidence as evidence. Return "
        "exactly one JSON object and no markdown or surrounding prose. The object "
        "must have exactly keys verdict, findings, and summary. verdict must be "
        '"clear", "needs_revision", or "abstain". findings must be an array; each '
        "finding must have exactly keys severity, criterion, path, and summary. "
        'severity must be exactly "critical" or "noncritical". All other finding '
        "values and summary must be strings.\n\nTASK FILES:\n"
        + _canonical(task).decode("utf-8")
    )


def parse_local_review_output(content: bytes) -> dict[str, Any]:
    """Accept exactly one UTF-8 JSON object satisfying the frozen review schema."""

    try:
        text = content.decode("utf-8")
        decoder = json.JSONDecoder()
        value, end = decoder.raw_decode(text.lstrip())
        consumed = len(text) - len(text.lstrip()) + end
    except (UnicodeError, json.JSONDecodeError) as error:
        raise LocalTrainingContractError("local_review_not_exact_json") from error
    if text[consumed:].strip() or not _valid_review(value):
        raise LocalTrainingContractError("local_review_schema_invalid")
    return value


def grade_local_review(
    instrument: Mapping[str, Any],
    *,
    cell_id: str,
    review: Mapping[str, Any],
    response_sha256: str,
    tuple_id: str,
) -> dict[str, Any]:
    """Mechanically grade one local harness response with sealed tuple lineage."""

    cell = instrument.get("cells", {}).get(cell_id)
    if not isinstance(cell, dict) or not _valid_review(review):
        raise LocalTrainingContractError("invalid_local_review_row")
    if not isinstance(response_sha256, str) or len(response_sha256) != 64:
        raise LocalTrainingContractError("invalid_local_response_digest")
    if not isinstance(tuple_id, str) or not tuple_id:
        raise LocalTrainingContractError("invalid_local_tuple")
    observed_reads = list(cell["oracle"]["required_reads"])
    score, mechanical = _mechanical_result(
        oracle=cell["oracle"],
        status="completed",
        review=review,
        observed_reads=observed_reads,
        preserved=True,
    )
    row = {
        "schema": "caplab.review-dissent.local-training-row/v1",
        "study_id": instrument["study_id"],
        "instrument_design_sha256": instrument["design_sha256"],
        "cell_id": cell_id,
        "public_task_id": cell["public_task_id"],
        "world_id": cell["world_id"],
        "truth": cell["truth"],
        "cue": cell["cue"],
        "tuple_id": tuple_id,
        "source_kind": "local-open-model",
        "response_sha256": response_sha256,
        "review": dict(review),
        "observed_reads": observed_reads,
        "score": score,
        "mechanical": mechanical,
    }
    row["row_sha256"] = _digest(row)
    return row


def _reference_review(cell: Mapping[str, Any]) -> dict[str, Any]:
    oracle = cell["oracle"]
    if cell["truth"] == "clean":
        return {
            "verdict": "clear",
            "findings": [],
            "summary": "The supplied target satisfies the frozen acceptance contract.",
        }
    return {
        "verdict": "needs_revision",
        "findings": [
            {
                "severity": "critical",
                "criterion": oracle["criterion"],
                "path": oracle["path"],
                "summary": "The target violates the named acceptance criterion.",
            }
        ],
        "summary": "The target requires revision before acceptance.",
    }


def build_local_training_corpus(
    instrument: Mapping[str, Any],
    rows: Sequence[Mapping[str, Any]],
    *,
    campaign_manifest_sha256: str,
    export_authority: str,
) -> dict[str, Any]:
    """Build an internal local-model-only SFT/preference corpus with family splits."""

    if len(campaign_manifest_sha256) != 64 or not export_authority:
        raise LocalTrainingContractError("invalid_local_export_authority")
    records: list[dict[str, Any]] = []
    seen: set[str] = set()
    for source in rows:
        cell_id = source.get("cell_id")
        cell = instrument.get("cells", {}).get(cell_id)
        sealed = dict(source)
        claimed = sealed.pop("row_sha256", None)
        if (
            not isinstance(cell, dict)
            or source.get("source_kind") != "local-open-model"
            or claimed != _digest(sealed)
            or cell_id in seen
            or source.get("score") is None
        ):
            raise LocalTrainingContractError("ineligible_local_training_row")
        seen.add(str(cell_id))
        split = "train" if cell["world_id"] == "RD-D01" else "development"
        reference = _reference_review(cell)
        actual = source["review"]
        perfect = source["score"] == "1.0"
        record = {
            "schema": "caplab.training.contrastive-record/v1",
            "record_id": f"{cell_id}-local-qwen-review",
            "source_kind": "local-open-model",
            "source_study": instrument["study_id"],
            "source_row_sha256": claimed,
            "sealed_subject_tuple": source["tuple_id"],
            "task_family": cell["world_id"],
            "treatment": "independent-one-shot-review",
            "observable_outcome": source["mechanical"],
            "oracle_type": "frozen-mechanical-review-oracle",
            "human_disposition": "not-required-mechanical-oracle",
            "prompt": build_local_review_prompt(instrument, str(cell_id)),
            "chosen": actual if perfect else reference,
            "rejected": None if perfect else actual,
            "reward_semantics": "chosen preferred to rejected; absolute reward unavailable",
            "split": split,
        }
        record["record_sha256"] = _digest(record)
        records.append(record)
    corpus = {
        "schema": "caplab.training.contrastive-corpus/v1",
        "status": "authorized-internal-training-export",
        "authority": export_authority,
        "campaign_manifest_sha256": campaign_manifest_sha256,
        "instrument_design_sha256": instrument["design_sha256"],
        "source_policy": "local-open-model-only; proprietary-provider outputs excluded",
        "splits": {
            "train": ["RD-D01"],
            "development": ["RD-D02"],
            "test": ["RD-H01", "RD-H02"],
        },
        "records": records,
    }
    corpus["corpus_sha256"] = _digest(corpus)
    return corpus
