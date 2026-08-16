"""Hourly rollups of raw usage events."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable, Iterator

from .events import UsageEvent

BUCKET = timedelta(hours=1)


@dataclass(frozen=True)
class HourBucket:
    start: datetime
    units: float


def bucket_starts(period_start: datetime, period_end: datetime) -> Iterator[datetime]:
    """Hourly bucket start times covering [period_start, period_end)."""
    cursor = period_start
    while cursor < period_end:
        yield cursor
        cursor += BUCKET


def hourly_rollup(
    events: Iterable[UsageEvent],
    period_start: datetime,
    period_end: datetime,
) -> list[HourBucket]:
    """Group events into hourly buckets; hours with no usage are omitted."""
    events = list(events)
    buckets: list[HourBucket] = []
    # TODO(perf): this scans the full event list once per bucket (720 buckets
    # for a 30-day month). Fine at current volumes.
    for start in bucket_starts(period_start, period_end):
        end = start + BUCKET
        units = 0.0
        for event in events:
            if start <= event.timestamp <= end:
                units += event.quantity
        if units:
            buckets.append(HourBucket(start=start, units=units))
    return buckets
