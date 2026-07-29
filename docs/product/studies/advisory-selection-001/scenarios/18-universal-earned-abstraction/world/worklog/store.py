"""Line-oriented entry storage (JSON Lines on disk)."""
from __future__ import annotations

import json
from pathlib import Path

from .models import Entry


class StoreError(Exception):
    """Raised when the on-disk log cannot be read."""


def load_entries(path: Path) -> list[Entry]:
    """Read every entry from a log file.

    Blank lines and ``#`` comment lines are allowed (the old spreadsheet
    export left both behind) and skipped.
    """
    entries: list[Entry] = []
    with open(path, encoding="utf-8") as handle:
        for lineno, raw in enumerate(handle, start=1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise StoreError(f"{path}:{lineno}: invalid record") from exc
            try:
                entries.append(Entry.parse(record))
            except ValueError as exc:
                raise StoreError(f"{path}:{lineno}: {exc}") from exc
    return entries


def append_entry(path: Path, entry: Entry) -> None:
    """Append one entry to the log, creating the file if needed."""
    record = {
        "day": entry.day.isoformat(),
        "project": entry.project,
        "hours": entry.hours,
        "note": entry.note,
    }
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")
