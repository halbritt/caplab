from datetime import date

import pytest

from ledgerlib.errors import UnknownCategoryError
from ledgerlib.models import Money


def test_march_statement_lists_every_posting(ledger):
    ledger.open_account("acct-fleet", "Vehicle fleet")
    ledger.post("acct-fleet", Money(4500), "travel", date(2026, 3, 4), "van service")
    ledger.post("acct-fleet", Money(1200), "utilities", date(2026, 3, 11), "charging")
    ledger.post("acct-fleet", Money(8000), "equipment", date(2026, 3, 25), "tyres")
    statement = ledger.statement(2026, 3)
    assert len(statement.lines) == 3
    assert statement.total == Money(13700)


def test_statement_orders_postings_by_date(ledger):
    ledger.open_account("acct-lab", "Lab consumables")
    ledger.post("acct-lab", Money(900), "office", date(2026, 4, 20))
    ledger.post("acct-lab", Money(300), "office", date(2026, 4, 2))
    ledger.post("acct-lab", Money(650), "office", date(2026, 4, 9))
    statement = ledger.statement(2026, 4)
    assert [line.posted_on.day for line in statement.lines] == [2, 9, 20]


def test_post_normalizes_category_spelling(ledger):
    ledger.open_account("acct-annex", "Annex build-out")
    posting = ledger.post(
        "acct-annex", Money(2100), "  Equipment ", date(2026, 7, 3)
    )
    assert posting.category == "equipment"


def test_post_rejects_unknown_category(ledger):
    ledger.open_account("acct-archive", "Archive storage")
    with pytest.raises(UnknownCategoryError):
        ledger.post("acct-archive", Money(500), "yachts", date(2026, 7, 8))
