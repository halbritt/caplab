from shipq.invoicing import invoice_total
from shipq.parcels import Parcel
from shipq.quotes import quote_total


def test_dense_parcel_invoice_matches_quote():
    p = Parcel("DPX", 1, 12.0, 30, 20, 20)
    assert invoice_total(p) == quote_total(p)


def test_dense_parcel_invoice_amount():
    p = Parcel("DPX", 1, 12.0, 30, 20, 20)
    assert invoice_total(p) == 53.68


def test_cod_fee_added():
    p = Parcel("DPX", 1, 12.0, 30, 20, 20)
    assert invoice_total(p, cod=True) == 57.4


def test_minimum_charge_floor():
    p = Parcel("ARO", 2, 0.5, 10, 10, 10)
    assert invoice_total(p) == 9.32


def test_remote_zone_surcharge_included():
    p = Parcel("ARO", 3, 4.0, 20, 15, 10)
    assert invoice_total(p) == 37.41
