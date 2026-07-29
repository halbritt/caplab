from shipq.parcels import Parcel
from shipq.quotes import quote_total


def test_dense_parcel_billed_by_scale_weight():
    # 12000 cm3 of volume is well under 12 kg of scale weight
    p = Parcel("DPX", 1, 12.0, 30, 20, 20)
    assert quote_total(p) == 53.68


def test_bulky_parcel_billed_by_volume():
    # 40000 cm3 -> 10.0 kg volumetric, dominates the 2.0 kg scale weight
    p = Parcel("DPX", 1, 2.0, 50, 40, 20)
    assert quote_total(p) == 44.73


def test_minimum_charge_floor():
    p = Parcel("ARO", 2, 0.5, 10, 10, 10)
    assert quote_total(p) == 9.32


def test_remote_zone_surcharge_included():
    p = Parcel("ARO", 3, 4.0, 20, 15, 10)
    assert quote_total(p) == 37.41
