from decimal import Decimal

import pytest

from quoteflow.express import quote_express
from quoteflow.models import Parcel


def parcel(weight="2", postcode="3000", **kwargs):
    return Parcel(weight_kg=Decimal(weight), destination_postcode=postcode, **kwargs)


def test_metro_base_rate_includes_handling():
    quote = quote_express(parcel("2"))
    assert quote.transport == Decimal("17.60")
    assert quote.total == Decimal("17.60")


def test_oversize_fee_added():
    quote = quote_express(parcel("2", length_cm=130))
    assert quote.surcharges == Decimal("12.00")
    assert quote.total == Decimal("29.60")


def test_promo_discount_on_metro_quote():
    quote = quote_express(parcel("5"), promo_code="WELCOME10")
    assert quote.discount == Decimal("2.47")
    assert quote.total == Decimal("22.18")


def test_rejects_overweight_parcel():
    with pytest.raises(ValueError):
        quote_express(parcel("30.5"))
