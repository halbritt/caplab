#!/usr/bin/env python3
"""Shared execution-mode contract for Books evaluation artifacts."""

from __future__ import annotations


VALID_EVALUATION_MODES = frozenset({"live", "replay"})


class EvaluationModeError(ValueError):
    pass


def require_evaluation_mode(expected: str, artifact_mode: object) -> None:
    """Reject undeclared, unknown, or mismatched evaluation artifact modes."""
    if expected not in VALID_EVALUATION_MODES:
        raise EvaluationModeError(f"unknown_execution_mode:{expected}")
    if artifact_mode not in VALID_EVALUATION_MODES:
        raise EvaluationModeError(f"unknown_artifact_mode:{artifact_mode}")
    if artifact_mode != expected:
        raise EvaluationModeError(
            f"mode_mismatch:expected={expected}:artifact={artifact_mode}"
        )
