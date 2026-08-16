"""Decides when the next control-plane check-in happens.

Check-ins land on wall-clock interval boundaries: with the default
600 s interval every device reports at ...:00, :10, :20 and so on.
Ops asked for this early on so that per-interval dashboard buckets
line up exactly across the whole fleet.
"""

from __future__ import annotations

import math


def next_sync_time(now: float, interval_seconds: float) -> float:
    """Return the epoch timestamp of the next check-in after ``now``.

    The result is the next multiple of ``interval_seconds`` strictly
    after ``now``, which keeps every device's reporting buckets
    comparable on the fleet dashboard.
    """
    if interval_seconds <= 0:
        raise ValueError("interval_seconds must be positive")
    return (math.floor(now / interval_seconds) + 1) * interval_seconds


def seconds_until(now: float, target: float) -> float:
    """How long to wait until ``target``, clamped at zero for late callers."""
    return max(0.0, target - now)
