# trackd

Parcel scan tracking for the warehouse gateway.

`trackd` records shipments and the scan events that carriers post as parcels
move through the network. It runs as a small on-box service: scanner gateways
shell out to the CLI (or import `trackd.service`) once per scan.

## Production deployment

- Single gateway box per warehouse, systemd unit `trackd-gateway.service`.
- Storage is a file-backed SQLite database in WAL mode at
  `/var/lib/trackd/trackd.db` (override with `TRACKD_DATABASE_URL`,
  e.g. `sqlite:////var/lib/trackd/trackd.db`).
- Every scanner request is handled independently: each service call opens its
  own connection, does its work, and releases it. There is no long-lived
  connection or connection pool.

## CLI

```
python -m trackd register PKG-1042 --carrier orion --origin reno-dc
python -m trackd scan PKG-1042 in_transit "Reno sort hub"
python -m trackd status PKG-1042
python -m trackd history PKG-1042
python -m trackd snapshot
```

The CLI uses `sqlite:///trackd.db` in the current directory unless
`TRACKD_DATABASE_URL` is set. Schema is applied automatically on first use.

## Layout

- `trackd/db.py` — connection factory (URL parsing, pragmas, WAL).
- `trackd/schema.py` — DDL, idempotent.
- `trackd/repository.py` — SQL, no transaction management.
- `trackd/service.py` — application operations; one unit of work per call.
- `trackd/cli.py` — argparse front end.

## Tests

```
python -m pytest
```

The suite is fast and leaves nothing on disk; see `conftest.py` for the
shared database fixture.
