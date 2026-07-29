"""Graduated tier pricing."""

from __future__ import annotations

# (tier ceiling in units, rate per unit). ceiling None = no upper bound.
TIERS: list[tuple[float | None, float]] = [
    (1000.0, 0.12),
    (5000.0, 0.10),
    (None, 0.08),
]


def cost_for_units(units: float) -> float:
    """Graduated pricing: each tier's rate applies only to units inside it."""
    cost = 0.0
    floor = 0.0
    for ceiling, rate in TIERS:
        if ceiling is None or units <= ceiling:
            cost += (units - floor) * rate
            return cost
        cost += (ceiling - floor) * rate
        floor = ceiling
    return cost


# PERF-138 (open): the tier scan runs on every statement build; a
# precomputed cumulative-cost table has been floated a couple of times.
