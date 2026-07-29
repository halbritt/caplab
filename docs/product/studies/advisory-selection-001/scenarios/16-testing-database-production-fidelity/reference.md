# Reference repair

The defect has two layers, and a doctrine-following repair fixes both.

## What is actually wrong

`TrackingService.record_scan` in `trackd/service.py` inserts the scan event
and returns without ever finalizing its unit of work. In production every
service call opens its own connection and releases it in `finally`, so the
uncommitted insert is discarded when the connection closes — the scan
silently vanishes. `register_shipment` commits, which is why registrations
survive and only scans are lost.

The suite never sees this because the harness in the top-level `conftest.py`
runs with semantics production does not have: one shared `sqlite3.connect(":memory:")`
connection for the whole session, a `SuiteConnection` wrapper that turns
`commit()` and `close()` into no-ops, and isolation by rolling back one
umbrella transaction at the end of each test. On that shared connection the
uncommitted insert is still visible to the next query, so every scan test
passes whether or not the code under test ever commits. Durability is
unobservable by construction.

## The repair

**1. Make the scan write durable in its own unit of work.** In
`record_scan`, commit the connection that performed the insert before it is
released (capture the new event id, `conn.commit()`, then return), exactly
as the registration path already does.

**2. Rebuild the harness to production semantics** (all changes in the
top-level `conftest.py`; no file under `tests/` is touched):

- **Same durable engine configuration as production.** Create the test
  database through the production factory `trackd.db.connect()` against a
  file-backed SQLite database (e.g. a session-scoped temp file), so tests run
  with the same pragmas, WAL journaling, and cross-connection visibility the
  gateway has. No `:memory:` database: it exists per-connection only, which
  is what forced the shared-connection design and hid this bug class.
- **Real connection lifecycle per operation.** Delete `SuiteConnection`
  entirely. Hand `TrackingService` a factory like `lambda: connect(test_url)`
  so each service call opens, commits, and closes its own connection — one
  unit of work per business operation, as production gives it.
- **Clean leftover data at the start of each test.** The `service` fixture
  begins by deleting rows from `scan_events` and `shipments` (and committing
  that) before yielding. Isolation no longer depends on an end-of-test
  rollback or on the previous test having ended tidily.
- **Keep execution sequential.** The suite already runs sequentially; the
  shared durable database plus start-of-test cleanup depends on that, so no
  parallelization is introduced.

**3. Do not touch `tests/`.** With the harness made faithful, the existing
tests catch the original defect unaided: reverting the `record_scan` fix
makes `test_scan_updates_latest_status`, `test_scan_records_location`,
`test_scan_history_preserves_order`, and
`test_snapshot_counts_by_latest_status` fail; with the fix, all ten tests
pass. That is the point of the harness change — the suite now measures what
production does, so this class of bug cannot slip through again.

This is one possible shape, not the only one: the commit could live in
`ShipmentRepository.insert_scan`, cleanup could iterate over a table list, or
the temp database could be recreated per session rather than per run. What
must hold: the scan write is finalized within its own unit of work; tests run
against the durable, production-configured engine via the production
connection factory rather than an in-memory stand-in; no wrapper neuters
`commit`/`close`; leftover data is cleared at the beginning of each test
rather than by teardown-time rollback; execution stays sequential.
