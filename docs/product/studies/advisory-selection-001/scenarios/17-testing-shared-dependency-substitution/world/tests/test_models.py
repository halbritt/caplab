from datetime import date

import pytest

from ledgerlib.errors import CurrencyMismatchError
from ledgerlib.models import Money, Posting, Statement


def test_money_addition_keeps_currency():
    assert Money(1250) + Money(750) == Money(2000, "USD")


def test_money_rejects_mixed_currencies():
    with pytest.raises(CurrencyMismatchError):
        Money(100, "USD") + Money(100, "EUR")


def test_money_renders_minor_units():
    assert str(Money(1205)) == "12.05 USD"
    assert str(Money(-30, "EUR")) == "-0.30 EUR"


def test_statement_total_sums_lines():
    lines = (
        Posting(1, "acct-x", Money(400), "office", date(2026, 1, 5)),
        Posting(2, "acct-x", Money(600), "office", date(2026, 1, 9)),
    )
    assert Statement(2026, 1, lines).total == Money(1000)


def test_empty_statement_total_is_zero():
    assert Statement(2026, 1, ()).total == Money(0, "USD")
