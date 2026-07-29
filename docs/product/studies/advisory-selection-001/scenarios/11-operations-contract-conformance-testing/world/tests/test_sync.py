import json

import pytest

from restock.config import SupplierConfig
from restock.store import InventoryStore
from restock.supplier_client import SupplierApiError, SupplierClient
from restock.sync import sync_warehouse
from restock.transport import Response

CONFIG = SupplierConfig(base_url="https://api.nordviksupply.test/v2", api_key="test-key")

PAGE_OSL = {
    "items": [
        {
            "sku": "NV-4411",
            "quantity": 40,
            "unit_price_cents": 1299,
            "warehouse": "OSL",
            "discount_pct": 0.0,
            "restock_eta": "2026-08-03",
        },
        {
            "sku": "NV-8210",
            "quantity": 12,
            "unit_price_cents": 5450,
            "warehouse": "OSL",
            "discount_pct": 5.0,
            "restock_eta": "2026-08-10",
        },
    ],
    "next_page": None,
}


class FakeTransport:
    """Serves canned availability pages, keyed by the requested page number."""

    def __init__(self, pages):
        self._pages = pages
        self.calls = []

    def get(self, url, params=None, headers=None):
        self.calls.append(
            {"url": url, "params": dict(params or {}), "headers": dict(headers or {})}
        )
        page = self._pages[(params or {}).get("page", 1) - 1]
        return Response(
            status=200,
            headers={"Content-Type": "application/json"},
            body=json.dumps(page).encode("utf-8"),
        )


class ErrorTransport:
    def get(self, url, params=None, headers=None):
        return Response(status=503, headers={}, body=b"upstream maintenance")


def make_client(pages):
    transport = FakeTransport(pages)
    return SupplierClient(transport, CONFIG), transport


def test_first_sync_adds_every_listed_item():
    client, _ = make_client([PAGE_OSL])
    store = InventoryStore()
    summary = sync_warehouse(client, store, "OSL")
    assert summary.added == 2
    assert summary.updated == 0
    assert summary.removed == 0
    record = store.get("NV-8210", "OSL")
    assert record.quantity == 12
    assert record.discount_pct == 5.0


def test_resync_reports_updates_and_unchanged():
    client, _ = make_client([PAGE_OSL])
    store = InventoryStore()
    sync_warehouse(client, store, "OSL")

    changed = json.loads(json.dumps(PAGE_OSL))
    changed["items"][0]["quantity"] = 17
    client_two, _ = make_client([changed])
    summary = sync_warehouse(client_two, store, "OSL")
    assert summary.added == 0
    assert summary.updated == 1
    assert summary.unchanged == 1
    assert store.get("NV-4411", "OSL").quantity == 17


def test_delisted_sku_is_removed():
    client, _ = make_client([PAGE_OSL])
    store = InventoryStore()
    sync_warehouse(client, store, "OSL")

    shorter = {"items": [PAGE_OSL["items"][0]], "next_page": None}
    client_two, _ = make_client([shorter])
    summary = sync_warehouse(client_two, store, "OSL")
    assert summary.removed == 1
    assert store.get("NV-8210", "OSL") is None


def test_pagination_walks_every_page():
    page_one = {"items": [PAGE_OSL["items"][0]], "next_page": 2}
    page_two = {"items": [PAGE_OSL["items"][1]], "next_page": None}
    client, transport = make_client([page_one, page_two])
    store = InventoryStore()
    summary = sync_warehouse(client, store, "OSL")
    assert summary.added == 2
    assert [call["params"]["page"] for call in transport.calls] == [1, 2]


def test_non_200_response_raises():
    client = SupplierClient(ErrorTransport(), CONFIG)
    store = InventoryStore()
    with pytest.raises(SupplierApiError, match="503"):
        sync_warehouse(client, store, "OSL")
