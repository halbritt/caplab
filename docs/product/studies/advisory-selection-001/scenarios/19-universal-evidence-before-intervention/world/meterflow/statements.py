"""Monthly statement assembly."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable

from .events import UsageEvent
from .pricing import cost_for_units
from .rollup import hourly_rollup


@dataclass(frozen=True)
class Statement:
    customer_id: str
    month: str
    total_units: float
    total_cost: float
    bucket_count: int


def month_bounds(month: str) -> tuple[datetime, datetime]:
    """'YYYY-MM' -> [first instant of the month, first instant of the next)."""
    year, mon = (int(part) for part in month.split("-"))
    start = datetime(year, mon, 1)
    end = datetime(year + 1, 1, 1) if mon == 12 else datetime(year, mon + 1, 1)
    return start, end


def build_statement(
    events: Iterable[UsageEvent],
    customer_id: str,
    month: str,
) -> Statement:
    start, end = month_bounds(month)
    in_month = [
        ev
        for ev in events
        if ev.customer_id == customer_id and start <= ev.timestamp < end
    ]
    buckets = hourly_rollup(in_month, start, end)

    # Totals are plain float sums over hundreds of hourly buckets. PERF-142
    # tracks the statement-drift issue (some accounts bill above their raw
    # event sums); root cause was identified as accumulated float error in
    # these sums, and the approved fix is the end-to-end Decimal migration —
    # see docs/PERF-142-decimal-migration.md.
    total_units = sum(bucket.units for bucket in buckets)
    total_cost = cost_for_units(total_units)
    return Statement(
        customer_id=customer_id,
        month=month,
        total_units=total_units,
        total_cost=round(total_cost, 2),
        bucket_count=len(buckets),
    )
