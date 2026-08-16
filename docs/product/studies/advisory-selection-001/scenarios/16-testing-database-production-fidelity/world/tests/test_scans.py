import pytest

from trackd.errors import InvalidStatusError, UnknownShipmentError


def test_scan_updates_latest_status(service):
    service.register_shipment("PKG-200", "orion", "reno-dc")
    event_id = service.record_scan("PKG-200", "in_transit", "Reno sort hub")
    assert event_id >= 1
    assert service.latest_status("PKG-200") == "in_transit"


def test_scan_history_preserves_order(service):
    service.register_shipment("PKG-201", "atlas", "slc-dc")
    service.record_scan("PKG-201", "in_transit", "SLC hub")
    service.record_scan("PKG-201", "out_for_delivery", "Provo depot")
    service.record_scan("PKG-201", "delivered", "front porch")
    history = service.scan_history("PKG-201")
    assert [event["status"] for event in history] == [
        "in_transit",
        "out_for_delivery",
        "delivered",
    ]


def test_scan_records_location(service):
    service.register_shipment("PKG-202", "orion", "reno-dc")
    service.record_scan("PKG-202", "in_transit", "Reno sort hub")
    summary = service.shipment_summary("PKG-202")
    assert summary["status"] == "in_transit"
    assert summary["last_location"] == "Reno sort hub"


def test_scan_for_unknown_shipment_raises(service):
    with pytest.raises(UnknownShipmentError):
        service.record_scan("PKG-NOPE", "in_transit", "nowhere")


def test_unrecognized_status_is_rejected(service):
    service.register_shipment("PKG-203", "orion", "reno-dc")
    with pytest.raises(InvalidStatusError):
        service.record_scan("PKG-203", "teleported", "area 51")
