"""Read-only reports for finance and support."""

from __future__ import annotations

import json
import sqlite3
from decimal import Decimal
from pathlib import Path


class Ledger:
    """Reports over the voucher database. Never writes."""

    def __init__(self, db_path: str | Path) -> None:
        self._conn = sqlite3.connect(str(db_path))
        self._conn.row_factory = sqlite3.Row

    def close(self) -> None:
        self._conn.close()

    def outstanding_total(self, currency: str = "EUR") -> Decimal:
        """Total liability: the sum of every active voucher's balance."""
        rows = self._conn.execute(
            "SELECT balance FROM vouchers WHERE status = 'active' AND currency = ?",
            (currency,),
        ).fetchall()
        return sum((Decimal(row["balance"]) for row in rows), Decimal("0.00"))

    def issuance_history(self, code: str) -> list[dict]:
        """Every issuance the audit log records for this code."""
        rows = self._conn.execute(
            "SELECT kind, at, details FROM audit_log"
            " WHERE voucher_code = ? AND kind = 'issued' ORDER BY entry_id",
            (code.strip().upper(),),
        ).fetchall()
        return [self._entry(row) for row in rows]

    def activity(self, code: str) -> list[dict]:
        """The full audit trail for this code, oldest first."""
        rows = self._conn.execute(
            "SELECT kind, at, details FROM audit_log"
            " WHERE voucher_code = ? ORDER BY entry_id",
            (code.strip().upper(),),
        ).fetchall()
        return [self._entry(row) for row in rows]

    @staticmethod
    def _entry(row: sqlite3.Row) -> dict:
        return {
            "kind": row["kind"],
            "at": row["at"],
            "details": json.loads(row["details"]),
        }
