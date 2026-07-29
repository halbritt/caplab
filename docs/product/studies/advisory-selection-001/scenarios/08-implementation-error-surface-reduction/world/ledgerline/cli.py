"""Command-line entry point for the nightly import."""

from __future__ import annotations

import argparse
from pathlib import Path

from .importer import run_import
from .store import LedgerStore


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="ledgerline",
        description="Import bank CSV exports into the ledger store.",
    )
    parser.add_argument("incoming", type=Path, help="directory of export files")
    parser.add_argument(
        "--db",
        type=Path,
        default=Path("ledger.db"),
        help="path to the ledger database (default: ./ledger.db)",
    )
    args = parser.parse_args(argv)

    store = LedgerStore(args.db)
    try:
        files, imported = run_import(args.incoming, store)
    finally:
        store.close()

    print(f"Imported {imported} transactions from {files} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
