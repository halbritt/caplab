"""Runtime configuration for the supplier integration."""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class SupplierConfig:
    base_url: str
    api_key: str
    timeout_s: float = 10.0


def from_env() -> SupplierConfig:
    """Build config from the environment; NORDVIK_API_KEY is required."""
    return SupplierConfig(
        base_url=os.environ.get("NORDVIK_BASE_URL", "https://api.nordviksupply.com/v2"),
        api_key=os.environ["NORDVIK_API_KEY"],
        timeout_s=float(os.environ.get("NORDVIK_TIMEOUT_S", "10")),
    )
