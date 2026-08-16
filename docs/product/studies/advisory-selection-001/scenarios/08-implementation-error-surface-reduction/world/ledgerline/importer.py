"""Orchestration of one nightly import run."""

from __future__ import annotations

from pathlib import Path

from .reader import find_exports, read_rows
from .records import parse_row
from .store import LedgerStore


def run_import(incoming: Path, store: LedgerStore) -> tuple[int, int]:
    """Import every export file found in *incoming*.

    Returns ``(files_seen, transactions_imported)``.
    """
    files = find_exports(incoming)
    imported = 0
    for path in files:
        for row in read_rows(path):
            txn = parse_row(row)
            if txn is None:
                continue
            store.add(txn)
            imported += 1
    return len(files), imported
