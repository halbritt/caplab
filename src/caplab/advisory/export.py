"""Deterministic advisory export for quartermaster ingestion.

`caplab-advisory-export/1` is deliberately a different document kind from the
qualification export: nothing in it can be mistaken for a qualification
Claim. It carries every ledger claim (or a filtered subset), sorted
deterministically, plus the construct catalog the claims reference.
"""

from __future__ import annotations

import json

from .claims import REVIEW_DEFECT_DISCRIMINATION, Ledger

DOCUMENT = "caplab-advisory-export/1"

CONSTRUCT_CATALOG = {
    REVIEW_DEFECT_DISCRIMINATION: {
        "description": (
            "Review defect discrimination, measured by matched-pair defect "
            "injection: a mechanically verified defect is planted in a known "
            "control at a known element; catch_rate is the refusing-verdict "
            "rate on mutants, false_alarm_rate the refusing rate on controls, "
            "discrimination their difference (zero for any constant "
            "reviewer), anchored_detection whether the review names the "
            "broken element (rescored from retained arms)."),
        "metrics": ["n_pairs", "n_distinct_cases", "catch_rate",
                    "false_alarm_rate", "discrimination", "anchored_detection",
                    "findings_per_mutant", "json_valid_mutant"],
        "oracle": "deterministic mechanical checkers on both arms",
    },
}


def export_document(ledger: Ledger) -> dict:
    claims = [{k: v for k, v in claim.items() if k != "_content_hash"}
              for claim in ledger.read()]
    claims.sort(key=lambda c: (c["subject"]["source_id"], c["construct"],
                               c["as_of"], c["claim_id"]))
    return {
        "document": DOCUMENT,
        "constructs": CONSTRUCT_CATALOG,
        "claims": claims,
        "notice": ("Advisory scored claims. No qualification decision, "
                   "availability, or ranking is expressed or implied."),
    }


def write_export(ledger: Ledger, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(export_document(ledger), f, ensure_ascii=False,
                  indent=2, sort_keys=True)
        f.write("\n")
