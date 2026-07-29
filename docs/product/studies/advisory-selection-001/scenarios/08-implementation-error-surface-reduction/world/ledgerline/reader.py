"""Discovery and reading of export files in the incoming directory."""

from __future__ import annotations

import csv
from pathlib import Path


def find_exports(incoming: Path) -> list[Path]:
    """All export files in the incoming directory, in a stable order."""
    return sorted(p for p in incoming.glob("*.csv") if p.is_file())


def read_rows(path: Path) -> list[dict[str, str | None]]:
    """Read one export file as a list of dict rows.

    Banks occasionally ship a truncated or oddly encoded file; a bad file
    should not take down the whole nightly run, so an unreadable file just
    contributes no rows.
    """
    try:
        with path.open(newline="", encoding="utf-8") as fh:
            return list(csv.DictReader(fh))
    except (OSError, UnicodeDecodeError):
        return []
