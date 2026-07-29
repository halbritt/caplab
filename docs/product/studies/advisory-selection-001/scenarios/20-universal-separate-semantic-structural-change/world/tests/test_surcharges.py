from decimal import Decimal

from quoteflow.models import Parcel
from quoteflow.surcharges import is_oversize, is_remote, surcharge_total


def test_remote_postcode_detection():
    assert is_remote("0872")
    assert is_remote("0900")
    assert not is_remote("3000")


def test_oversize_detection_uses_longest_side():
    assert is_oversize(Parcel(weight_kg=Decimal("1"), width_cm=125))
    assert not is_oversize(Parcel(weight_kg=Decimal("1"), length_cm=120))


def test_remote_and_oversize_fees_stack():
    boxy = Parcel(
        weight_kg=Decimal("1"), length_cm=140, destination_postcode="0900"
    )
    assert surcharge_total(boxy) == Decimal("19.50")
