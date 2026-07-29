"""Command-line entry point: python -m restock.cli OSL GOT"""

import argparse
import sys

from restock import config
from restock.store import InventoryStore
from restock.supplier_client import SupplierClient
from restock.sync import sync_warehouse
from restock.transport import UrllibTransport


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="restock-sync",
        description="Sync warehouse availability from Nordvik Supply into the local snapshot.",
    )
    parser.add_argument("warehouses", nargs="+", help="warehouse codes, e.g. OSL GOT")
    parser.add_argument("--db", default="restock.sqlite3", help="path to the snapshot database")
    args = parser.parse_args(argv)

    cfg = config.from_env()
    client = SupplierClient(UrllibTransport(cfg.timeout_s), cfg)
    store = InventoryStore(args.db)
    for warehouse in args.warehouses:
        summary = sync_warehouse(client, store, warehouse)
        print(
            f"{summary.warehouse}: +{summary.added} ~{summary.updated}"
            f" ={summary.unchanged} -{summary.removed}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
