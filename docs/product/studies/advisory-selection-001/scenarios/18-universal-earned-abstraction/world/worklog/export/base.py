"""Shared exporter pipeline.

A backend subclasses :class:`BaseExporter`, implements the cell/row hooks,
and decorates itself with :func:`register`. The shared :meth:`render` drives
iteration, the header, and line assembly, so a typical backend is only a
screenful of code. The hook split anticipates the TSV, XML, and fixed-width
backends on the roadmap, which should only differ at the cell and row level.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

_REGISTRY: dict[str, type["BaseExporter"]] = {}


def register(cls: type["BaseExporter"]) -> type["BaseExporter"]:
    """Class decorator: make a backend available by its ``format_name``."""
    _REGISTRY[cls.format_name] = cls
    return cls


def text(value: object) -> str:
    """Canonical text form of a cell value, shared by every backend."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


class BaseExporter(ABC):
    """Template for tabular report backends."""

    format_name: str = ""

    def __init__(self, **options: object) -> None:
        # Backend-specific tuning (delimiters, date styles, ...). No current
        # backend takes options, but the slot keeps the constructor signature
        # stable for the ones that will.
        self.options = options

    def render(self, columns: list[str], rows: list[dict]) -> str:
        out: list[str] = []
        header = self.begin(columns)
        if header is not None:
            out.append(header)
        for row in rows:
            cells = [self.format_cell(column, row[column]) for column in columns]
            out.append(self.format_row(cells))
        tail = self.end()
        if tail is not None:
            out.append(tail)
        return "\n".join(out) + "\n"

    def begin(self, columns: list[str]) -> str | None:
        """Optional leading line (e.g. a header row)."""
        return None

    @abstractmethod
    def format_cell(self, column: str, value: object) -> str:
        """Text form of one cell."""

    @abstractmethod
    def format_row(self, cells: list[str]) -> str:
        """Assemble formatted cells into one output line."""

    def end(self) -> str | None:
        """Optional trailing line (e.g. a footer or closing tag)."""
        return None
