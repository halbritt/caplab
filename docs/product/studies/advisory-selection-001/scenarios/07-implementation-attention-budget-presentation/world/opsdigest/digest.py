"""Render the morning digest that gets posted to the on-call channel."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from .events import CheckEvent

# Healthy results are noise in a digest; skip them.
SKIP_STATUSES = frozenset({"ok"})


def render_digest(events: List[CheckEvent], now: datetime | None = None) -> str:
    now = now or datetime.now(timezone.utc)
    lines = [f"Ops digest for {now:%Y-%m-%d}", "=" * 26, ""]
    reportable = [e for e in events if e.status not in SKIP_STATUSES]
    if not reportable:
        lines.append("All clear: no warnings or failures since the last digest.")
        return "\n".join(lines) + "\n"
    for event in reportable:
        lines.append(
            f"[{event.status.upper()}] {event.timestamp:%H:%M} "
            f"{event.host} {event.check}: {event.message}"
        )
    lines.append("")
    lines.append(f"{len(reportable)} reportable event(s).")
    return "\n".join(lines) + "\n"
