"""Domain records for worklog."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class Entry:
    """One logged block of work."""

    day: date
    project: str
    hours: float
    note: str = ""

    def __post_init__(self) -> None:
        if not self.project.strip():
            raise ValueError("project must be non-empty")
        if not 0 < self.hours <= 24:
            raise ValueError(f"hours out of range: {self.hours}")

    @classmethod
    def parse(cls, record: dict) -> "Entry":
        """Build an Entry from one decoded log record."""
        try:
            return cls(
                day=date.fromisoformat(record["day"]),
                project=str(record["project"]),
                hours=float(record["hours"]),
                note=str(record.get("note", "")),
            )
        except KeyError as exc:
            raise ValueError(f"missing field: {exc.args[0]}") from None
