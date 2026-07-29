"""Category rules applied when postings enter the ledger."""

from __future__ import annotations

from collections.abc import Iterable

from ledgerlib.errors import UnknownCategoryError


class CategoryRules:
    """Normalises and validates posting categories.

    A plain in-process object so callers can extend the allowed set per
    ledger (e.g. a project-specific category) without touching storage.
    """

    DEFAULT_CATEGORIES = frozenset(
        {"travel", "meals", "office", "software", "utilities", "equipment"}
    )

    def __init__(self, extra: Iterable[str] = ()) -> None:
        self._allowed = frozenset(
            self.DEFAULT_CATEGORIES | {c.strip().lower() for c in extra}
        )

    def normalize(self, category: str) -> str:
        cleaned = category.strip().lower()
        if cleaned not in self._allowed:
            raise UnknownCategoryError(category)
        return cleaned
