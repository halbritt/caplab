"""Posting workflow: validation plus statement assembly."""

from __future__ import annotations

from datetime import date

from ledgerlib.models import Account, Money, Posting, Statement
from ledgerlib.policy import CategoryRules
from ledgerlib.store import SqliteStore


class Ledger:
    """Front door for writes: opens accounts, records postings, builds
    monthly statements."""

    def __init__(
        self, store: SqliteStore, rules: CategoryRules | None = None
    ) -> None:
        self._store = store
        self._rules = rules or CategoryRules()

    def open_account(
        self, account_id: str, name: str, currency: str = "USD"
    ) -> Account:
        account = Account(account_id, name, currency)
        self._store.add_account(account)
        return account

    def post(
        self,
        account_id: str,
        amount: Money,
        category: str,
        posted_on: date,
        memo: str = "",
    ) -> Posting:
        # Raises UnknownAccountError for postings against missing accounts.
        self._store.get_account(account_id)
        cleaned = self._rules.normalize(category)
        return self._store.add_posting(
            account_id, amount, cleaned, posted_on, memo
        )

    def statement(self, year: int, month: int) -> Statement:
        lines = tuple(self._store.postings_in_month(year, month))
        return Statement(year=year, month=month, lines=lines)
