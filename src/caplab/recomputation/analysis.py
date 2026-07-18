"""Frozen paired exact analysis selected for CAPLAB Study 001."""

from __future__ import annotations

import itertools


def analyze_mutant_blocks(
    outcomes: tuple[tuple[bool | None, bool | None], ...],
) -> dict[str, object]:
    """Apply the preregistered paired exact test to eight ``(B, V)`` blocks."""

    if len(outcomes) != 8:
        raise ValueError("the primary analysis requires exactly eight mutant blocks")
    if any(b_harmful is None or v_harmful is None for b_harmful, v_harmful in outcomes):
        return {
            "all_mutant_outcomes_defined": False,
            "block_differences": None,
            "b_harmful_count": None,
            "v_harmful_count": None,
            "mutant_arm_denominator": 8,
            "risk_difference": None,
            "t_observed": None,
            "permutation_assignments": 0,
            "p_one_sided": None,
            "p_two_sided": None,
            "alpha": {"numerator": 1, "denominator": 20},
            "confirmatory_criterion_met": False,
        }
    differences = [int(b_harmful) - int(v_harmful) for b_harmful, v_harmful in outcomes]
    observed = sum(differences)
    statistics = [
        sum(
            sign * difference
            for sign, difference in zip(signs, differences, strict=True)
        )
        for signs in itertools.product((-1, 1), repeat=8)
    ]
    assignments = len(statistics)
    one_sided_count = sum(statistic >= observed for statistic in statistics)
    two_sided_count = sum(
        abs(statistic) >= abs(observed) for statistic in statistics
    )
    return {
        "all_mutant_outcomes_defined": True,
        "block_differences": differences,
        "b_harmful_count": sum(b_harmful for b_harmful, _ in outcomes),
        "v_harmful_count": sum(v_harmful for _, v_harmful in outcomes),
        "mutant_arm_denominator": 8,
        "risk_difference": {"numerator": observed, "denominator": 8},
        "t_observed": observed,
        "permutation_assignments": assignments,
        "p_one_sided": {"numerator": one_sided_count, "denominator": assignments},
        "p_two_sided": {"numerator": two_sided_count, "denominator": assignments},
        "alpha": {"numerator": 1, "denominator": 20},
        "confirmatory_criterion_met": observed > 0 and 20 * one_sided_count < assignments,
    }
