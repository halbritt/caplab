"""Comma-separated backend."""
from __future__ import annotations

from .base import BaseExporter, register, text


@register
class CsvExporter(BaseExporter):
    format_name = "csv"
    delimiter = ","

    def begin(self, columns: list[str]) -> str:
        return self.format_row([self._escape(column) for column in columns])

    def format_cell(self, column: str, value: object) -> str:
        return self._escape(text(value))

    def format_row(self, cells: list[str]) -> str:
        return self.delimiter.join(cells)

    def _escape(self, cell: str) -> str:
        if self.delimiter in cell or '"' in cell or "\n" in cell:
            return '"' + cell.replace('"', '""') + '"'
        return cell
