"""Shared fail-closed classification for Books evaluation outcomes."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


TAXONOMY_PATH = (
    Path(__file__).resolve().parents[1] / "evaluations/error-taxonomy.json"
)
TAXONOMY: dict[str, Any] = json.loads(TAXONOMY_PATH.read_text(encoding="utf-8"))
UNKNOWN = str(TAXONOMY["unknown_status_policy"])


def classify_entailment(verdict: str) -> str:
    return str(TAXONOMY["entailment_verdicts"].get(verdict, UNKNOWN))


def classify_scenario_exit(returncode: int) -> str:
    return str(TAXONOMY["scenario_exit_codes"].get(str(returncode), UNKNOWN))


def score_eligible(outcome_class: str) -> bool:
    definition = TAXONOMY["outcome_classes"].get(outcome_class)
    return bool(definition and definition["score_eligible"])
