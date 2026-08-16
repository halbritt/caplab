def test_snapshot_counts_by_latest_status(service):
    service.register_shipment("PKG-300", "orion", "reno-dc")
    service.register_shipment("PKG-301", "orion", "reno-dc")
    service.register_shipment("PKG-302", "atlas", "slc-dc")
    service.record_scan("PKG-301", "in_transit", "Reno hub")
    service.record_scan("PKG-302", "in_transit", "SLC hub")
    service.record_scan("PKG-302", "delivered", "doorstep")
    snapshot = service.network_snapshot()
    assert snapshot == {"registered": 1, "in_transit": 1, "delivered": 1}


def test_snapshot_of_empty_network(service):
    assert service.network_snapshot() == {}
