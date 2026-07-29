from decimal import Decimal

import pytest

from quoteflow.promo import UnknownPromoCode, resolve_discount


def test_codes_are_case_insensitive():
    assert resolve_discount("save15") == Decimal("0.15")


def test_known_codes():
    assert resolve_discount("WELCOME10") == Decimal("0.10")
    assert resolve_discount("BULK20") == Decimal("0.20")


def test_unknown_code_is_rejected():
    with pytest.raises(UnknownPromoCode):
        resolve_discount("SAVE99")
