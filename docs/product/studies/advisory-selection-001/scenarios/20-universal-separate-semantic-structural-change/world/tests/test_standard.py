from decimal import Decimal

import pytest

from quoteflow.models import Parcel
from quoteflow.standard import quote_standard


def parcel(weight="2", postcode="3000", **kwargs):
    return Parcel(weight_kg=Decimal(weight), destination_postcode=postcode, **kwargs)


def test_metro_base_rate():
    quote = quote_standard(parcel("2"))
    assert quote.transport == Decimal("7.15")
    assert quote.total == Decimal("7.15")


def test_weight_charge_scales_per_kg():
    assert quote_standard(parcel("10")).transport == Decimal("15.95")


def test_remote_area_fee_added():
    quote = quote_standard(parcel("2", postcode="0872"))
    assert quote.surcharges == Decimal("7.50")
    assert quote.total == Decimal("14.65")


def test_promo_discount_on_metro_quote():
    quote = quote_standard(parcel("10"), promo_code="SAVE15")
    assert quote.discount == Decimal("2.39")
    assert quote.total == Decimal("13.56")


def test_rejects_overweight_parcel():
    with pytest.raises(ValueError):
        quote_standard(parcel("31"))
