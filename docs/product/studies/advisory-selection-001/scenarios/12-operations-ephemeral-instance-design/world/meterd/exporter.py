"""Daily usage export for billing.

Billing picks up one CSV per day from the export directory on the
shared volume.
"""

from __future__ import annotations

import csv
from pathlib import Path

from meterd.store import MeteringStore


def write_daily_export(
    store: MeteringStore, day: str, out_dir: str | Path
) -> Path:
    """Write ``usage-<day>.csv`` and return its path."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"usage-{day}.csv"
    tmp = out_path.with_suffix(".csv.tmp")
    with open(tmp, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["customer", "total"])
        for customer, total in store.rollups_for_day(day):
            writer.writerow([customer, f"{total:.3f}"])
    tmp.replace(out_path)
    return out_path
