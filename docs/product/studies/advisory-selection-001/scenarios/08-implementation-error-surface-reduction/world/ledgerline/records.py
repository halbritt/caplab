"""Row-to-domain translation for imported bank transactions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from .amounts import parse_amount


@dataclass(frozen=True, slots=True)
class Transaction:
    posted: date
    account: str
    amount_cents: int
    memo: str


def parse_row(row: dict[str, str | None]) -> Transaction | None:
    """Turn one CSV row into a Transaction.

    Real exports are messy: repeated header lines, footer totals, and even
    promotional text show up as "rows". Anything that does not look like a
    transaction is skipped so one junk line never spoils a whole file.
    """
    try:
        account = (row["account"] or "").strip()
        if not account:
            raise ValueError("account is blank")
        return Transaction(
            posted=date.fromisoformat((row["date"] or "").strip()),
            account=account,
            amount_cents=parse_amount(row["amount"]),
            memo=(row.get("memo") or "").strip(),
        )
    except Exception:
        return None
