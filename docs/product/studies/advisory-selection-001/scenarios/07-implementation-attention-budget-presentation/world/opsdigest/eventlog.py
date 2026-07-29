"""Append-only JSONL store for check events.

The log is the system of record: every check result ever observed lands
here, one JSON object per line, in arrival order. Nothing else in the
tool is allowed to invent or discard history; the only sanctioned
rewrite is retention pruning, driven by the operator via the CLI.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable, List

from .events import CheckEvent


class EventLog:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def append(self, event: CheckEvent) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(event.to_json() + "\n")

    def read_all(self) -> List[CheckEvent]:
        if not self.path.exists():
            return []
        with self.path.open("r", encoding="utf-8") as fh:
            return [CheckEvent.from_json(line) for line in fh if line.strip()]

    def read_since(self, cutoff: datetime) -> List[CheckEvent]:
        return [e for e in self.read_all() if e.timestamp >= cutoff]

    def rewrite(self, events: Iterable[CheckEvent]) -> None:
        """Replace the log contents atomically. Retention pruning only."""
        tmp = self.path.with_suffix(".tmp")
        with tmp.open("w", encoding="utf-8") as fh:
            for event in events:
                fh.write(event.to_json() + "\n")
        tmp.replace(self.path)

    def prune(self, keep_days: int, now: datetime | None = None) -> int:
        """Drop events older than the retention window. Returns count dropped."""
        now = now or datetime.now(timezone.utc)
        cutoff = now - timedelta(days=keep_days)
        events = self.read_all()
        kept = [e for e in events if e.timestamp >= cutoff]
        self.rewrite(kept)
        return len(events) - len(kept)
