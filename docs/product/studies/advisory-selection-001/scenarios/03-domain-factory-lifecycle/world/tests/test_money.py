from decimal import Decimal

import pytest

from vouchercore.errors import CurrencyMismatch, InvalidAmount
from vouchercore.money import Money, MoneyFactory


def test_create_normalises_amount_and_currency():
    m = MoneyFactory.create("50", "eur")
    assert m == Money(Decimal("50.00"), "EUR")


def test_create_rounds_to_cents():
    assert MoneyFactory.create("19.999", "EUR").amount == Decimal("20.00")


def test_create_rejects_negative_amounts():
    with pytest.raises(InvalidAmount):
        MoneyFactory.create("-1.00", "EUR")


def test_create_rejects_unknown_currency():
    with pytest.raises(InvalidAmount):
        MoneyFactory.create("5.00", "XXX")


def test_create_rejects_garbage():
    with pytest.raises(InvalidAmount):
        MoneyFactory.create("fifty", "EUR")


def test_minus_same_currency():
    m = MoneyFactory.create("50.00", "EUR").minus(MoneyFactory.create("20.00", "EUR"))
    assert m.amount == Decimal("30.00")


def test_minus_rejects_currency_mix():
    with pytest.raises(CurrencyMismatch):
        MoneyFactory.create("50.00", "EUR").minus(MoneyFactory.create("20.00", "USD"))
