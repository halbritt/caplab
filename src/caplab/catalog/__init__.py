"""Shared-catalog discovery and prospective-preparation validation.

Quartermaster publishes configured catalog routes and projects them for this
consumer. Nothing here builds a Binding, admits a native tuple, authorizes an
effect or qualifies a model; see docs/product/contracts/catalog-selection-v1.md.
"""

from caplab.catalog.discovery import discover
from caplab.catalog.preparation import (
    retain_selection,
    select_entry,
    validate_against_spec,
)
from caplab.catalog.projection import (
    CatalogSelectionError,
    Projection,
    load_projection,
)

__all__ = [
    "CatalogSelectionError",
    "Projection",
    "discover",
    "load_projection",
    "retain_selection",
    "select_entry",
    "validate_against_spec",
]
