"""Operator CLI for the catalog.

In production the same `CatalogService` runs inside the storefront's threaded
web app (separate repo); this CLI is for spot checks and maintenance on the box.
"""

from __future__ import annotations

import argparse
import json
import os

from .maintenance import rebuild_index
from .search_index import SearchIndex
from .service import CatalogService
from .store import CatalogStore


def _open_service(data_dir: str) -> CatalogService:
    os.makedirs(data_dir, exist_ok=True)
    store = CatalogStore(os.path.join(data_dir, "catalog.db"))
    index = SearchIndex(os.path.join(data_dir, "search.json"))
    return CatalogService(store, index)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="catalog")
    parser.add_argument(
        "--data-dir", default=os.environ.get("CATALOG_DATA_DIR", "data")
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("add", help="create an item")
    p.add_argument("id")
    p.add_argument("name")
    p.add_argument("--description", default="")
    p.add_argument("--price-cents", type=int, default=0)
    p.add_argument("--tags", default="", help="comma-separated")

    p = sub.add_parser("update", help="edit fields on an item")
    p.add_argument("id")
    p.add_argument("--name")
    p.add_argument("--description")
    p.add_argument("--price-cents", type=int)
    p.add_argument("--tags", help="comma-separated")

    p = sub.add_parser("delete", help="delete an item")
    p.add_argument("id")

    p = sub.add_parser("show", help="print one item")
    p.add_argument("id")

    p = sub.add_parser("search", help="search items")
    p.add_argument("query")

    sub.add_parser("rebuild", help="rebuild the search index from the item store")

    args = parser.parse_args(argv)
    service = _open_service(args.data_dir)

    if args.command == "add":
        item = service.create_item(
            args.id,
            args.name,
            description=args.description,
            price_cents=args.price_cents,
            tags=[t for t in args.tags.split(",") if t],
        )
        print(json.dumps(item, indent=2))
    elif args.command == "update":
        fields = {}
        if args.name is not None:
            fields["name"] = args.name
        if args.description is not None:
            fields["description"] = args.description
        if args.price_cents is not None:
            fields["price_cents"] = args.price_cents
        if args.tags is not None:
            fields["tags"] = [t for t in args.tags.split(",") if t]
        print(json.dumps(service.update_item(args.id, **fields), indent=2))
    elif args.command == "delete":
        service.delete_item(args.id)
        print(f"deleted {args.id}")
    elif args.command == "show":
        print(json.dumps(service.get_item(args.id), indent=2))
    elif args.command == "search":
        print(json.dumps(service.search(args.query), indent=2))
    elif args.command == "rebuild":
        count = rebuild_index(service.store, service.index)
        print(f"indexed {count} items")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
