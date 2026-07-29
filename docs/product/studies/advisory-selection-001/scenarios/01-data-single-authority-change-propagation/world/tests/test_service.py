import pytest

from catalog.maintenance import rebuild_index
from catalog.search_index import SearchIndex
from catalog.service import CatalogService
from catalog.store import CatalogStore


@pytest.fixture
def service(tmp_path):
    store = CatalogStore(str(tmp_path / "catalog.db"))
    index = SearchIndex(str(tmp_path / "search.json"))
    return CatalogService(store, index)


def test_created_item_is_searchable(service):
    service.create_item(
        "sku-1",
        "wireless earbuds",
        description="noise cancelling",
        price_cents=4999,
        tags=["audio"],
    )
    assert [r["id"] for r in service.search("wireless")] == ["sku-1"]


def test_search_returns_current_fields(service):
    service.create_item("sku-1", "wireless earbuds", price_cents=4999)
    service.update_item("sku-1", price_cents=3999)
    (result,) = service.search("earbuds")
    assert result["price_cents"] == 3999


def test_rename_updates_what_matches(service):
    service.create_item("sku-1", "wireless earbuds")
    service.update_item("sku-1", name="bluetooth earbuds")
    assert [r["id"] for r in service.search("bluetooth")] == ["sku-1"]
    assert service.search("wireless") == []


def test_deleted_item_leaves_search(service):
    service.create_item("sku-1", "espresso grinder")
    service.delete_item("sku-1")
    assert service.search("espresso") == []


def test_search_honours_limit(service):
    for n in range(5):
        service.create_item(f"sku-{n}", "steel pan")
    assert len(service.search("steel", limit=3)) == 3


def test_rebuilt_index_matches_live_search(tmp_path):
    store = CatalogStore(str(tmp_path / "catalog.db"))
    index = SearchIndex(str(tmp_path / "search.json"))
    service = CatalogService(store, index)
    service.create_item("sku-1", "wireless earbuds", tags=["audio"])
    service.create_item("sku-2", "espresso grinder")
    service.create_item("sku-3", "steel water bottle")
    service.update_item("sku-1", name="bluetooth earbuds")
    service.delete_item("sku-2")

    fresh = SearchIndex(str(tmp_path / "fresh.json"))
    rebuild_index(store, fresh)
    rebuilt = CatalogService(store, fresh)
    for query in ("bluetooth", "espresso", "steel bottle", "wireless"):
        assert [r["id"] for r in rebuilt.search(query)] == [
            r["id"] for r in service.search(query)
        ]
