import pytest

from trackd.errors import DuplicateShipmentError, UnknownShipmentError


def test_register_creates_shipment(service):
    service.register_shipment("PKG-100", "orion", "reno-dc")
    summary = service.shipment_summary("PKG-100")
    assert summary["tracking_id"] == "PKG-100"
    assert summary["carrier"] == "orion"
    assert summary["origin"] == "reno-dc"
    assert summary["status"] == "registered"
    assert summary["last_location"] is None


def test_duplicate_registration_is_rejected(service):
    service.register_shipment("PKG-101", "orion", "reno-dc")
    with pytest.raises(DuplicateShipmentError):
        service.register_shipment("PKG-101", "atlas", "slc-dc")


def test_summary_for_unknown_shipment_raises(service):
    with pytest.raises(UnknownShipmentError):
        service.shipment_summary("PKG-NOPE")
