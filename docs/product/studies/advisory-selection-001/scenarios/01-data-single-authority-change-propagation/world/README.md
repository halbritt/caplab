# shopfloor-catalog

Catalog core for the shopfloor storefront: the item store, the search index
that makes items findable, and a small operator CLI.

The storefront's web app (separate repo) imports
`catalog.service.CatalogService` and serves merchandiser edits and shopper
searches from multiple worker threads. This repo is the part operators touch
directly on the box.

## Layout

- `catalog/store.py` — SQLite-backed item store
- `catalog/search_index.py` — word index over item text, saved beside the DB
  so restarts keep search warm
- `catalog/text.py` — shared tokenizer
- `catalog/service.py` — item CRUD plus search; the surface everything uses
- `catalog/maintenance.py` — index rebuild helper
- `catalog/cli.py` — operator CLI (`python -m catalog.cli --help`)

## Tests

```bash
python3 -m pytest -q
```

## Operator notes

Data lives in `./data` by default (`--data-dir` or `CATALOG_DATA_DIR` to
override). If search looks off, `python -m catalog.cli rebuild` rebuilds the
search index from the item store.
