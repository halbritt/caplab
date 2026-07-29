"""Item CRUD plus search — the surface the web app and the CLI both use."""

from __future__ import annotations

from itertools import islice

from .search_index import SearchIndex
from .store import CatalogStore, ItemNotFound


class CatalogService:
    """Front door for catalog reads and edits."""

    def __init__(self, store: CatalogStore, index: SearchIndex):
        self.store = store
        self.index = index

    def create_item(
        self,
        item_id: str,
        name: str,
        description: str = "",
        price_cents: int = 0,
        tags=(),
    ) -> dict:
        item = self.store.create(
            item_id, name, description=description, price_cents=price_cents, tags=tags
        )
        self.index.upsert(item)
        return item

    def update_item(self, item_id: str, **fields) -> dict:
        item = self.store.update(item_id, **fields)
        self.index.upsert(item)
        return item

    def delete_item(self, item_id: str) -> None:
        self.store.delete(item_id)
        self.index.remove(item_id)

    def get_item(self, item_id: str) -> dict:
        return self.store.get(item_id)

    def search(self, query: str, limit: int = 20) -> list[dict]:
        def hydrated():
            for item_id in self.index.lookup(query):
                try:
                    yield self.store.get(item_id)
                except ItemNotFound:
                    continue  # the index can briefly know ids the store no longer has

        return list(islice(hydrated(), limit))
