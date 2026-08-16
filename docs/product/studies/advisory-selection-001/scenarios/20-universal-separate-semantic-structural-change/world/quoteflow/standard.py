"""Quoting for the standard (road) service.

Business rules: docs/pricing-rules.md.
"""

from decimal import Decimal, ROUND_HALF_UP

from . import tariffs
from .models import Parcel, Quote
from .promo import resolve_discount
from .surcharges import surcharge_total

_CENT = Decimal("0.01")


def _round(amount: Decimal) -> Decimal:
    return amount.quantize(_CENT, rounding=ROUND_HALF_UP)


def _validate(parcel: Parcel) -> None:
    if parcel.weight_kg <= 0:
        raise ValueError("weight must be positive")
    if parcel.weight_kg > tariffs.MAX_WEIGHT_KG:
        raise ValueError(
            f"standard service takes parcels up to {tariffs.MAX_WEIGHT_KG} kg"
        )


def quote_standard(parcel: Parcel, promo_code: str | None = None) -> Quote:
    _validate(parcel)
    transport = _round(
        tariffs.STANDARD_FLAGFALL + tariffs.STANDARD_PER_KG * parcel.weight_kg
    )
    extras = surcharge_total(parcel)
    subtotal = transport + extras
    if promo_code:
        discount = _round(subtotal * resolve_discount(promo_code))
    else:
        discount = Decimal("0.00")
    return Quote(
        service="standard",
        transport=transport,
        surcharges=extras,
        discount=discount,
        total=_round(subtotal - discount),
    )
