"""Read-side summaries built directly over the store."""

from __future__ import annotations

from collections.abc import Iterable

from ledgerlib.models import Money
from ledgerlib.store import SqliteStore


class ReportBuilder:
    """Aggregations for dashboards and month-end review."""

    def __init__(self, store: SqliteStore) -> None:
        self._store = store

    def account_activity(
        self, account_id: str, year: int, month: int
    ) -> Money:
        """Total posted against one account in one calendar month."""
        account = self._store.get_account(account_id)
        total = Money.zero(account.currency)
        for posting in self._store.postings_for_account(account_id):
            if (
                posting.posted_on.year == year
                and posting.posted_on.month == month
            ):
                total = total + posting.amount
        return total

    def category_totals(
        self, year: int, month: int, account_ids: Iterable[str]
    ) -> dict[str, Money]:
        """Per-category totals for a month, limited to the given accounts."""
        wanted = set(account_ids)
        totals: dict[str, Money] = {}
        for posting in self._store.postings_in_month(year, month):
            if posting.account_id not in wanted:
                continue
            current = totals.get(
                posting.category, Money.zero(posting.amount.currency)
            )
            totals[posting.category] = current + posting.amount
        return totals
