"""SQLite persistence for ledgerlib.

The store is deliberately thin: schema management plus typed reads and
writes. Business rules live in ledgerlib.ledger.
"""

from __future__ import annotations

import sqlite3
from datetime import date
from pathlib import Path

from ledgerlib.errors import DuplicateAccountError, UnknownAccountError
from ledgerlib.models import Account, Money, Posting

_SCHEMA = """
CREATE TABLE IF NOT EXISTS accounts (
    account_id TEXT PRIMARY KEY,
    name       TEXT NOT NULL,
    currency   TEXT NOT NULL DEFAULT 'USD'
);
CREATE TABLE IF NOT EXISTS postings (
    posting_id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id TEXT NOT NULL REFERENCES accounts(account_id),
    cents      INTEGER NOT NULL,
    currency   TEXT NOT NULL,
    category   TEXT NOT NULL,
    posted_on  TEXT NOT NULL,
    memo       TEXT NOT NULL DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_postings_posted_on ON postings (posted_on);
"""


class SqliteStore:
    """Storage backend used by Ledger and ReportBuilder."""

    def __init__(self, path: str | Path) -> None:
        self._conn = sqlite3.connect(str(path))
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")

    def migrate(self) -> None:
        self._conn.executescript(_SCHEMA)
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    # -- accounts ----------------------------------------------------------

    def add_account(self, account: Account) -> None:
        try:
            self._conn.execute(
                "INSERT INTO accounts (account_id, name, currency)"
                " VALUES (?, ?, ?)",
                (account.account_id, account.name, account.currency),
            )
            self._conn.commit()
        except sqlite3.IntegrityError as exc:
            raise DuplicateAccountError(account.account_id) from exc

    def get_account(self, account_id: str) -> Account:
        row = self._conn.execute(
            "SELECT account_id, name, currency FROM accounts"
            " WHERE account_id = ?",
            (account_id,),
        ).fetchone()
        if row is None:
            raise UnknownAccountError(account_id)
        return Account(row["account_id"], row["name"], row["currency"])

    # -- postings ----------------------------------------------------------

    def add_posting(
        self,
        account_id: str,
        amount: Money,
        category: str,
        posted_on: date,
        memo: str = "",
    ) -> Posting:
        cur = self._conn.execute(
            "INSERT INTO postings"
            " (account_id, cents, currency, category, posted_on, memo)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (
                account_id,
                amount.cents,
                amount.currency,
                category,
                posted_on.isoformat(),
                memo,
            ),
        )
        self._conn.commit()
        return Posting(
            posting_id=cur.lastrowid,
            account_id=account_id,
            amount=amount,
            category=category,
            posted_on=posted_on,
            memo=memo,
        )

    def postings_in_month(self, year: int, month: int) -> list[Posting]:
        prefix = f"{year:04d}-{month:02d}-"
        rows = self._conn.execute(
            "SELECT * FROM postings WHERE posted_on LIKE ?"
            " ORDER BY posted_on, posting_id",
            (prefix + "%",),
        ).fetchall()
        return [self._row_to_posting(r) for r in rows]

    def postings_for_account(self, account_id: str) -> list[Posting]:
        rows = self._conn.execute(
            "SELECT * FROM postings WHERE account_id = ?"
            " ORDER BY posted_on, posting_id",
            (account_id,),
        ).fetchall()
        return [self._row_to_posting(r) for r in rows]

    @staticmethod
    def _row_to_posting(row: sqlite3.Row) -> Posting:
        return Posting(
            posting_id=row["posting_id"],
            account_id=row["account_id"],
            amount=Money(row["cents"], row["currency"]),
            category=row["category"],
            posted_on=date.fromisoformat(row["posted_on"]),
            memo=row["memo"],
        )
