"""Checkout-time price quoting."""

import math

from . import rate_tables, surcharges
from .parcels import Parcel

# 2026-04: DPX rate notice #713 cut the volumetric divisor from 5000 to 4000.
DIM_DIVISOR = 4000


def _billable_weight_kg(parcel: Parcel) -> float:
    """Greater of scale weight and volumetric weight, rounded up to 0.5 kg."""
    volumetric_kg = parcel.volume_cm3() / DIM_DIVISOR
    return max(parcel.weight_kg, math.ceil(volumetric_kg * 2) / 2.0)


def quote_total(parcel: Parcel) -> float:
    """Price shown to the customer at checkout."""
    rate = rate_tables.BASE_RATE_PER_KG[(parcel.carrier, parcel.zone)]
    subtotal = _billable_weight_kg(parcel) * rate
    subtotal = max(subtotal, rate_tables.MINIMUM_CHARGE[parcel.carrier])
    return surcharges.apply_surcharges(subtotal, parcel.zone)
