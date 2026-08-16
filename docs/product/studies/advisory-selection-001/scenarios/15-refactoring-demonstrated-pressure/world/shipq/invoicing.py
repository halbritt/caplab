"""Post-delivery invoice generation."""

import math

from . import rate_tables, surcharges
from .parcels import Parcel

COD_FEE = 3.50


def _chargeable_kg(parcel: Parcel) -> float:
    # volumetric weight per the carrier contract
    dim_kg = (parcel.length_cm * parcel.width_cm * parcel.height_cm) / 5000
    if dim_kg > parcel.weight_kg:
        billed = math.ceil(dim_kg * 2) / 2.0
    else:
        billed = parcel.weight_kg
    return billed


def invoice_total(parcel: Parcel, cod: bool = False) -> float:
    """Final amount charged after the delivery scan-in."""
    rate = rate_tables.BASE_RATE_PER_KG[(parcel.carrier, parcel.zone)]
    subtotal = _chargeable_kg(parcel) * rate
    subtotal = max(subtotal, rate_tables.MINIMUM_CHARGE[parcel.carrier])
    if cod:
        subtotal += COD_FEE
    return surcharges.apply_surcharges(subtotal, parcel.zone)
