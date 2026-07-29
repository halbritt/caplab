from catalog.search_index import SearchIndex


def _item(item_id, name, description="", tags=()):
    return {
        "id": item_id,
        "name": name,
        "description": description,
        "tags": list(tags),
        "price_cents": 0,
        "updated_at": 0.0,
    }


def test_lookup_matches_any_word():
    index = SearchIndex()
    index.upsert(_item("sku-1", "wireless earbuds"))
    assert index.lookup("earbuds") == ["sku-1"]
    assert index.lookup("wireless charger") == ["sku-1"]


def test_upsert_replaces_previous_words():
    index = SearchIndex()
    index.upsert(_item("sku-1", "wireless earbuds"))
    index.upsert(_item("sku-1", "bluetooth earbuds"))
    assert index.lookup("bluetooth") == ["sku-1"]
    assert index.lookup("wireless") == []


def test_remove_drops_item():
    index = SearchIndex()
    index.upsert(_item("sku-1", "espresso grinder"))
    index.remove("sku-1")
    assert index.lookup("espresso") == []


def test_remove_unknown_id_is_harmless():
    index = SearchIndex()
    index.remove("ghost")
    assert index.lookup("anything") == []


def test_index_survives_reopen(tmp_path):
    path = str(tmp_path / "search.json")
    index = SearchIndex(path)
    index.upsert(_item("sku-1", "wireless earbuds"))
    reopened = SearchIndex(path)
    assert reopened.lookup("earbuds") == ["sku-1"]


def test_lookup_ranks_fuller_matches_first():
    index = SearchIndex()
    index.upsert(_item("sku-1", "steel water bottle"))
    index.upsert(_item("sku-2", "steel pan"))
    assert index.lookup("steel bottle") == ["sku-1", "sku-2"]
