import pytest

from catalog.store import CatalogStore, ItemNotFound


@pytest.fixture
def store(tmp_path):
    return CatalogStore(str(tmp_path / "catalog.db"))


def test_create_and_get_roundtrip(store):
    store.create(
        "sku-1",
        "wireless earbuds",
        description="noise cancelling",
        price_cents=4999,
        tags=["audio", "travel"],
    )
    item = store.get("sku-1")
    assert item["name"] == "wireless earbuds"
    assert item["price_cents"] == 4999
    assert item["tags"] == ["audio", "travel"]


def test_duplicate_id_is_rejected(store):
    store.create("sku-1", "earbuds")
    with pytest.raises(ValueError):
        store.create("sku-1", "earbuds again")


def test_update_touches_only_named_fields(store):
    store.create("sku-1", "earbuds", description="noise cancelling", price_cents=4999)
    item = store.update("sku-1", price_cents=3999)
    assert item["price_cents"] == 3999
    assert item["name"] == "earbuds"
    assert item["description"] == "noise cancelling"


def test_update_missing_item_raises(store):
    with pytest.raises(ItemNotFound):
        store.update("nope", name="anything")


def test_update_rejects_unknown_fields(store):
    store.create("sku-1", "earbuds")
    with pytest.raises(ValueError):
        store.update("sku-1", colour="red")


def test_delete_then_get_raises(store):
    store.create("sku-1", "earbuds")
    store.delete("sku-1")
    with pytest.raises(ItemNotFound):
        store.get("sku-1")


def test_all_items_sorted_by_id(store):
    store.create("sku-2", "second")
    store.create("sku-1", "first")
    assert [i["id"] for i in store.all_items()] == ["sku-1", "sku-2"]
