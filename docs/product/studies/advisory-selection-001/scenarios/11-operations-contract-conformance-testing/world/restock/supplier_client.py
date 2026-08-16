"""HTTP client for the Nordvik Supply availability API (v2).

The endpoint reference this client was written against is vendored at
docs/supplier-api-v2.md.
"""

from restock.config import SupplierConfig
from restock.models import AvailabilityRecord


class SupplierApiError(RuntimeError):
    """Raised when the supplier API returns a non-success response."""


class SupplierClient:
    def __init__(self, transport, config: SupplierConfig):
        self._transport = transport
        self._config = config

    def fetch_availability(self, warehouse: str) -> list[AvailabilityRecord]:
        """Fetch every availability page for one warehouse."""
        records: list[AvailabilityRecord] = []
        page: int | None = 1
        while page is not None:
            payload = self._get_page(warehouse, page)
            for entry in payload["items"]:
                records.append(AvailabilityRecord(**entry))
            page = payload["next_page"]
        return records

    def _get_page(self, warehouse: str, page: int) -> dict:
        response = self._transport.get(
            f"{self._config.base_url}/availability",
            params={"warehouse": warehouse, "page": page},
            headers={"X-Api-Key": self._config.api_key},
        )
        if response.status != 200:
            raise SupplierApiError(
                f"availability request for {warehouse} failed: HTTP {response.status}"
            )
        return response.json()
