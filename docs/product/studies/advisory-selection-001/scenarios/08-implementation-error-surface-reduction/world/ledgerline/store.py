"""SQLite-backed ledger store."""

from __future__ import annotations

import sqlite3
from datetime import date
from pathlib import Path

from .records import Transaction

_SCHEMA = """
CREATE TABLE IF NOT EXISTS transactions (
    id           INTEGER PRIMARY KEY,
    posted       TEXT    NOT NULL,
    account      TEXT    NOT NULL,
    amount_cents INTEGER NOT NULL,
    memo         TEXT    NOT NULL DEFAULT ''
)
"""


class LedgerStore:
    """Append-only transaction store used by the nightly import."""

    def __init__(self, db_path: Path | str) -> None:
        self._conn = sqlite3.connect(db_path)
        self._conn.execute(_SCHEMA)
        self._conn.commit()

    def add(self, txn: Transaction) -> None:
        self._conn.execute(
            "INSERT INTO transactions (posted, account, amount_cents, memo)"
            " VALUES (?, ?, ?, ?)",
            (txn.posted.isoformat(), txn.account, txn.amount_cents, txn.memo),
        )
        self._conn.commit()

    def count(self) -> int:
        (n,) = self._conn.execute("SELECT COUNT(*) FROM transactions").fetchone()
        return n

    def transactions_for(self, account: str) -> list[Transaction]:
        rows = self._conn.execute(
            "SELECT posted, account, amount_cents, memo FROM transactions"
            " WHERE account = ? ORDER BY posted, id",
            (account,),
        ).fetchall()
        return [
            Transaction(
                posted=date.fromisoformat(posted),
                account=account_,
                amount_cents=cents,
                memo=memo,
            )
            for posted, account_, cents, memo in rows
        ]

    def close(self) -> None:
        self._conn.close()
