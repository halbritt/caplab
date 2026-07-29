"""Raw usage events: one JSON object per line (JSONL)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class UsageEvent:
    customer_id: str
    timestamp: datetime
    quantity: float
    meter: str = "default"


def parse_line(line: str) -> UsageEvent:
    """Parse one JSONL record into a UsageEvent."""
    raw = json.loads(line)
    return UsageEvent(
        customer_id=raw["customer_id"],
        timestamp=datetime.fromisoformat(raw["timestamp"]),
        quantity=float(raw["quantity"]),
        meter=raw.get("meter", "default"),
    )


def load_events(path) -> list[UsageEvent]:
    """Load every event in a JSONL file, skipping blank lines."""
    events: list[UsageEvent] = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                events.append(parse_line(line))
    return events
