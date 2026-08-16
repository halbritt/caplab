"""Local telemetry buffering.

Terminals produce small telemetry events (card reads, reboots, printer
faults). Events are buffered on the device and shipped with the next
check-in rather than sent one by one.
"""

from __future__ import annotations

from typing import Any


class TelemetryBuffer:
    """Bounded FIFO buffer of telemetry events."""

    def __init__(self, batch_size: int, max_events: int = 10_000) -> None:
        if batch_size < 1:
            raise ValueError("batch_size must be at least 1")
        self._batch_size = batch_size
        self._max_events = max_events
        self._events: list[dict[str, Any]] = []
        self.dropped = 0

    def __len__(self) -> int:
        return len(self._events)

    def record(self, event: dict[str, Any]) -> None:
        """Add one event, dropping the oldest if the buffer is at capacity."""
        if len(self._events) >= self._max_events:
            self._events.pop(0)
            self.dropped += 1
        self._events.append(event)

    def take_batch(self) -> list[dict[str, Any]]:
        """Remove and return up to ``batch_size`` of the oldest events."""
        batch = self._events[: self._batch_size]
        del self._events[: self._batch_size]
        return batch

    def requeue(self, events: list[dict[str, Any]]) -> None:
        """Put an unshipped batch back at the front of the buffer."""
        self._events[:0] = events
