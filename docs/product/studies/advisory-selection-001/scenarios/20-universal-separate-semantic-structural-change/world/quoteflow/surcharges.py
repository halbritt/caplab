"""Destination and size surcharges (2025 rate card)."""

from decimal import Decimal

from .models import Parcel

REMOTE_PREFIXES = ("08", "09")
REMOTE_AREA_FEE = Decimal("7.50")

OVERSIZE_LIMIT_CM = 120
OVERSIZE_FEE = Decimal("12.00")


def is_remote(postcode: str) -> bool:
    return postcode.startswith(REMOTE_PREFIXES)


def is_oversize(parcel: Parcel) -> bool:
    longest = max(parcel.length_cm, parcel.width_cm, parcel.height_cm)
    return longest > OVERSIZE_LIMIT_CM


def surcharge_total(parcel: Parcel) -> Decimal:
    total = Decimal("0.00")
    if is_remote(parcel.destination_postcode):
        total += REMOTE_AREA_FEE
    if is_oversize(parcel):
        total += OVERSIZE_FEE
    return total


def fuel_levy(transport: Decimal) -> Decimal:
    # Deprecated: the 2025 rate card folded the fuel levy into the per-kg
    # rates. Keep until the invoicing job (invoices repo, >= 2024-12) stops
    # importing it, then delete.
    return (transport * Decimal("0.08")).quantize(Decimal("0.01"))
