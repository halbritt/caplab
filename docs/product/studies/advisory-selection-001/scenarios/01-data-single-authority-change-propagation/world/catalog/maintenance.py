"""Operator helpers behind `python -m catalog.cli`."""

from __future__ import annotations

from .search_index import SearchIndex
from .store import CatalogStore


def rebuild_index(store: CatalogStore, index: SearchIndex) -> int:
    """Rebuild the search index to match the item store, item by item.

    Returns the number of items indexed.
    """
    live = {item["id"]: item for item in store.all_items()}
    for item_id in sorted(index.known_ids() - set(live)):
        index.remove(item_id)
    for item in live.values():
        index.upsert(item)
    return len(live)
