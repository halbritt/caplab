"""Exchange-rate reference data.

Treasury publishes a daily reference-rate file (CSV): one row per currency
per publication date, ``currency,valid_from,rate``, where ``rate`` is EUR per
one unit of ``currency``.  A row is effective from its ``valid_from`` date
until a later row for the same currency supersedes it.  The file is
append-only; history is never rewritten.
"""

from __future__ import annotations

import csv
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path


class RateLookupError(KeyError):
    """No effective rate for the requested currency at the requested time."""


# Snapshot memo: building a snapshot means parsing the treasury file, which
# is not free, so keep computed snapshots keyed by (file, as_of) for the
# lifetime of the process.
_SNAPSHOTS: dict[tuple[str, datetime], dict[str, Decimal]] = {}


def rates_as_of(rates_path: str | Path, as_of: datetime) -> dict[str, Decimal]:
    """Return the map of currency -> effective EUR rate at ``as_of``."""
    key = (str(rates_path), as_of)
    cached = _SNAPSHOTS.get(key)
    if cached is not None:
        return cached
    rows = _read_rate_rows(rates_path)
    snapshot = _effective_snapshot(rows, as_of.date())
    _SNAPSHOTS[key] = snapshot
    return snapshot


def convert(amount: Decimal, currency: str, snapshot: dict[str, Decimal]) -> Decimal:
    """Convert ``amount`` of ``currency`` to EUR, quantized to cents."""
    try:
        rate = snapshot[currency]
    except KeyError:
        raise RateLookupError(currency) from None
    return (amount * rate).quantize(Decimal("0.01"))


def _read_rate_rows(rates_path: str | Path) -> list[tuple[str, date, Decimal]]:
    rows: list[tuple[str, date, Decimal]] = []
    with open(rates_path, newline="") as fh:
        for rec in csv.DictReader(fh):
            rows.append(
                (
                    rec["currency"],
                    date.fromisoformat(rec["valid_from"]),
                    Decimal(rec["rate"]),
                )
            )
    return rows


def _effective_snapshot(
    rows: list[tuple[str, date, Decimal]], on: date
) -> dict[str, Decimal]:
    """Pick, per currency, the newest row whose valid_from is on or before ``on``."""
    best: dict[str, tuple[date, Decimal]] = {}
    for currency, valid_from, rate in rows:
        if valid_from > on:
            continue
        prev = best.get(currency)
        if prev is None or valid_from > prev[0]:
            best[currency] = (valid_from, rate)
    return {currency: rate for currency, (_, rate) in best.items()}
