"""JSON Lines backend.

Rides the shared pipeline: each cell becomes a ``"key": "value"`` pair and
:meth:`format_row` closes the pairs into an object, which keeps this backend
as small as the CSV one.
"""
from __future__ import annotations

from .base import BaseExporter, register, text


@register
class JsonlExporter(BaseExporter):
    format_name = "jsonl"

    def format_cell(self, column: str, value: object) -> str:
        return f'"{column}": "{text(value)}"'

    def format_row(self, cells: list[str]) -> str:
        return "{" + ", ".join(cells) + "}"
