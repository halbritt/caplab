"""SQLite persistence for vouchers, plus the append-only audit log."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

from vouchercore.errors import VoucherNotFound
from vouchercore.factory import VoucherFactory
from vouchercore.voucher import Voucher, VoucherStatus

_SCHEMA = """
CREATE TABLE IF NOT EXISTS vouchers (
    voucher_id TEXT PRIMARY KEY,
    code       TEXT NOT NULL,
    balance    TEXT NOT NULL,
    currency   TEXT NOT NULL,
    status     TEXT NOT NULL,
    issued_at  TEXT NOT NULL,
    expires_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_vouchers_code ON vouchers (code);
CREATE TABLE IF NOT EXISTS audit_log (
    entry_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    voucher_code TEXT NOT NULL,
    kind         TEXT NOT NULL,
    at           TEXT NOT NULL,
    details      TEXT NOT NULL
);
"""


class VoucherStore:
    """Owns the vouchers table and the audit log."""

    def __init__(self, db_path: str | Path) -> None:
        self._conn = sqlite3.connect(str(db_path))
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(_SCHEMA)
        self._factory = VoucherFactory()

    def close(self) -> None:
        self._conn.close()

    def exists(self, code: str) -> bool:
        row = self._conn.execute(
            "SELECT 1 FROM vouchers WHERE code = ? LIMIT 1",
            (code.strip().upper(),),
        ).fetchone()
        return row is not None

    def save(self, voucher: Voucher) -> None:
        self._conn.execute(
            """
            INSERT INTO vouchers
                (voucher_id, code, balance, currency, status, issued_at, expires_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(voucher_id) DO UPDATE SET
                balance    = excluded.balance,
                status     = excluded.status,
                expires_at = excluded.expires_at
            """,
            (
                voucher.voucher_id,
                voucher.code,
                str(voucher.balance.amount),
                voucher.balance.currency,
                voucher.status.value,
                voucher.issued_at.isoformat(),
                voucher.expires_at.isoformat(),
            ),
        )
        for event in voucher.pending_events:
            self._conn.execute(
                "INSERT INTO audit_log (voucher_code, kind, at, details)"
                " VALUES (?, ?, ?, ?)",
                (
                    voucher.code,
                    event["kind"],
                    event["at"],
                    json.dumps(event["details"]),
                ),
            )
        voucher.pending_events.clear()
        self._conn.commit()

    def load(self, code: str) -> Voucher:
        row = self._conn.execute(
            "SELECT * FROM vouchers WHERE code = ? ORDER BY rowid DESC LIMIT 1",
            (code.strip().upper(),),
        ).fetchone()
        if row is None:
            raise VoucherNotFound(f"no voucher with code {code!r}")
        voucher = self._factory.build(
            code=row["code"],
            amount=row["balance"],
            currency=row["currency"],
        )
        voucher.status = VoucherStatus(row["status"])
        voucher.expires_at = datetime.fromisoformat(row["expires_at"])
        return voucher
