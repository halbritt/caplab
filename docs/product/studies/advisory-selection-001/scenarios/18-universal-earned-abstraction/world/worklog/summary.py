"""Aggregation of raw entries into a per-project report table."""
from __future__ import annotations

from .models import Entry

COLUMNS = ["project", "hours", "entries", "last_day"]


def summarize(entries: list[Entry]) -> tuple[list[str], list[dict]]:
    """Collapse entries into one row per project.

    Returns ``(columns, rows)`` where each row is a plain dict keyed by
    column name. Hours are rounded to two decimals; rows are sorted by
    project name so reports are stable run to run.
    """
    acc: dict[str, dict] = {}
    for entry in entries:
        bucket = acc.setdefault(
            entry.project, {"hours": 0.0, "entries": 0, "last_day": entry.day}
        )
        bucket["hours"] += entry.hours
        bucket["entries"] += 1
        if entry.day > bucket["last_day"]:
            bucket["last_day"] = entry.day
    rows = [
        {
            "project": project,
            "hours": round(acc[project]["hours"], 2),
            "entries": acc[project]["entries"],
            "last_day": acc[project]["last_day"].isoformat(),
        }
        for project in sorted(acc)
    ]
    return list(COLUMNS), rows
