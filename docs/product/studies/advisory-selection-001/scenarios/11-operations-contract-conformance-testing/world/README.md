# restock

Nightly replenishment sync for warehouse stock levels. Pulls per-warehouse
availability from the Nordvik Supply v2 API and mirrors it into a local
SQLite snapshot that the purchasing dashboard reads.

## Layout

- `restock/supplier_client.py` — Nordvik API client (the endpoint reference
  this was written against is vendored at `docs/supplier-api-v2.md`)
- `restock/transport.py` — thin HTTP layer, stubbed out in tests
- `restock/sync.py` — fetch and reconcile one warehouse
- `restock/store.py` — SQLite snapshot store
- `restock/cli.py` — entry point; cron runs `python -m restock.cli OSL GOT`
  nightly at 02:10

## Running

```bash
NORDVIK_API_KEY=... python -m restock.cli OSL GOT
```

## Tests

```bash
python3 -m pytest -q
```
