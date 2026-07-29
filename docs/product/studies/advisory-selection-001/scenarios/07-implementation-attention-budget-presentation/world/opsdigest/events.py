"""Check-event model shared by the recorder CLI and the digest renderer."""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime

STATUSES = ("ok", "warn", "crit")


@dataclass(frozen=True)
class CheckEvent:
    """One check result from one host at one moment.

    Timestamps are timezone-aware UTC throughout; the fleet spans three
    regions and naive stamps have burned us before.
    """

    timestamp: datetime
    host: str
    check: str
    status: str
    message: str = ""

    def __post_init__(self) -> None:
        if self.status not in STATUSES:
            raise ValueError(f"unknown status {self.status!r}")
        if self.timestamp.tzinfo is None:
            raise ValueError("timestamp must be timezone-aware")

    def to_json(self) -> str:
        return json.dumps(
            {
                "ts": self.timestamp.isoformat(),
                "host": self.host,
                "check": self.check,
                "status": self.status,
                "message": self.message,
            },
            separators=(",", ":"),
        )

    @classmethod
    def from_json(cls, line: str) -> "CheckEvent":
        raw = json.loads(line)
        return cls(
            timestamp=datetime.fromisoformat(raw["ts"]),
            host=raw["host"],
            check=raw["check"],
            status=raw["status"],
            message=raw.get("message", ""),
        )
