from restock.models import AvailabilityRecord
from restock.store import InventoryStore


def make_record(**overrides):
    base = dict(
        sku="NV-0001",
        quantity=5,
        unit_price_cents=999,
        warehouse="OSL",
        discount_pct=0.0,
        restock_eta=None,
    )
    base.update(overrides)
    return AvailabilityRecord(**base)


def test_upsert_then_get_roundtrip():
    store = InventoryStore()
    record = make_record(restock_eta="2026-08-01")
    assert store.upsert(record) == "added"
    assert store.get("NV-0001", "OSL") == record


def test_upsert_identical_record_reports_unchanged():
    store = InventoryStore()
    store.upsert(make_record())
    assert store.upsert(make_record()) == "unchanged"


def test_upsert_changed_quantity_reports_updated():
    store = InventoryStore()
    store.upsert(make_record())
    assert store.upsert(make_record(quantity=9)) == "updated"
    assert store.get("NV-0001", "OSL").quantity == 9


def test_skus_are_scoped_to_warehouse():
    store = InventoryStore()
    store.upsert(make_record())
    store.upsert(make_record(sku="NV-0002", warehouse="GOT"))
    assert store.skus_for_warehouse("OSL") == {"NV-0001"}


def test_delete_removes_record():
    store = InventoryStore()
    store.upsert(make_record())
    store.delete("NV-0001", "OSL")
    assert store.get("NV-0001", "OSL") is None
