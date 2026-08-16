# meterd

Nightly usage metering for the billing pipeline.

Ingest (a separate service) appends usage events to the metering
database. Customers are spread across 8 shards (`shard_of` in
`meterd/assignment.py`), and each night a systemd timer on every
metering worker runs one rollup cycle (`python3 -m meterd.worker`) that
folds new events into the `rollups` table. `meterd/exporter.py` writes
the daily CSV that billing picks up.

## Storage layout

- `/srv/meterd` — the shared volume, mounted on every worker. The
  metering database (`meter.db`) lives here; every instance sees the
  same data. Ingest writes events into it, workers fold rollups into it.
- `/var/lib/meterd` — the worker's own disk. Per-shard progress markers
  (`meterd/watermark.py`) live here so a cycle can resume where the
  previous one stopped.

The sqlite backend in `meterd/store.py` mirrors the production schema
and is what the tests run against.

## Fleet layout

The metering fleet is two VMs, `meter-prod-a` and `meter-prod-b`.
`deploy/fleet.toml` records which host owns which shards; keeping the
slices fixed per host means cycles never contend for the same shard.

### Adding or replacing a worker

1. Image the VM from the current base image.
2. Add its hostname and shard slice to `deploy/fleet.toml`.
3. Deploy and enable the timer (`deploy/meterd-rollup.timer`).

## Running the tests

    python3 -m pytest -q
