"""Append-only movement log.

The ledger is the audit source of truth: statements are rendered from the
entry stream, never from the wallet record.
"""

from __future__ import annotations

from .models import LedgerEntry


class Ledger:
    def __init__(self) -> None:
        self._entries: list[LedgerEntry] = []

    def record(self, entry: LedgerEntry) -> None:
        self._entries.append(entry)

    def entries_for(self, wallet_id: str) -> list[LedgerEntry]:
        return [e for e in self._entries if e.wallet_id == wallet_id]

    def statement(self, wallet_id: str) -> str:
        lines = [f"statement for {wallet_id}"]
        for e in self.entries_for(wallet_id):
            lines.append(
                f"{e.at:%Y-%m-%d %H:%M}  {e.kind:<12} "
                f"{e.amount_cents:>8}  {e.balance_after_cents:>8}  {e.memo}"
            )
        return "\n".join(lines)
