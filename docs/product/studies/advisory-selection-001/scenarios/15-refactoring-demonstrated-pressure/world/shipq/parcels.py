"""Parcel domain objects shared across quoting and invoicing."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Parcel:
    carrier: str        # carrier code, e.g. "DPX" or "ARO"
    zone: int           # destination pricing zone (1-3)
    weight_kg: float    # actual scale weight
    length_cm: float
    width_cm: float
    height_cm: float

    def volume_cm3(self) -> float:
        return self.length_cm * self.width_cm * self.height_cm
