"""Report export backends.

Public surface: :func:`render` and :func:`available_formats`. Backends
register themselves on import via the ``@register`` decorator in ``base``.
"""
from __future__ import annotations

from .base import _REGISTRY
from . import csv_exporter, jsonl_exporter  # noqa: F401  (registration side effect)


def available_formats() -> list[str]:
    return sorted(_REGISTRY)


def get_exporter(name: str, **options: object):
    try:
        cls = _REGISTRY[name]
    except KeyError:
        raise ValueError(f"unknown export format: {name!r}") from None
    return cls(**options)


def render(name: str, columns: list[str], rows: list[dict], **options: object) -> str:
    """Render a summary table in the named format."""
    return get_exporter(name, **options).render(columns, rows)
