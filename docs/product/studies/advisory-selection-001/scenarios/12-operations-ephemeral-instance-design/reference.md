# Reference repair

One possible repair that follows the doctrine — not the only one. The
thread running through it: nothing about a particular machine (its
name, its disk, its clock) may matter to whether the work gets done.

## 1. Shards are claimed, not assigned by roster

Delete the `[assignments]` table from `deploy/fleet.toml` (the file
keeps only the shard count) and remove `shards_for` from
`meterd/assignment.py`. In its place, add a small lease table to the
metering database — e.g. `shard_leases(shard INTEGER PRIMARY KEY,
owner TEXT, expires_at REAL)` — and a `claim_shard(shard, owner, ttl)`
operation on `MeteringStore` that atomically takes a shard whose lease
is absent or expired (`BEGIN IMMEDIATE` plus a conditional
insert-or-update makes the claim race-safe in sqlite; the production
database does it with one conditional statement). Each cycle, a worker
walks shards `0..count-1`, claims whichever it can, and processes only
those. A freshly imaged machine needs no registration step: it boots,
its timer fires, and it starts pulling work; a machine that dies simply
stops renewing, and its shards are picked up by whoever runs next. The
hostname survives only as the lease's `owner` label for observability —
it is never a routing key. The README's "add its hostname to
fleet.toml" instruction is deleted.

## 2. Progress lives with the data, not on the instance

Replace `meterd/watermark.py`'s per-host JSON marker files with a
`shard_cursors(shard INTEGER PRIMARY KEY, last_seq INTEGER)` table in
the same database, and advance the cursor in the same transaction that
applies a batch's rollup deltas, so a batch is folded exactly once.
Replacing a machine can then neither strand a shard's progress nor
re-fold already-counted events (the May double-count). `watermark.py`
is removed; `run_cycle` keeps its signature (the `state_dir` argument
is accepted and ignored, or dropped along with its call sites) but
nothing reads or writes instance-local state.

## 3. The store is the only ordering authority

Remove `GRACE_SECONDS` and the `cutoff = now - GRACE_SECONDS`
computation from `run_cycle`. The worker's wall clock says nothing
trustworthy about what has been ingested. Batch bounds come from the
store's monotonic `seq` — for example, snapshot the maximum sequence at
cycle start and fold up to it. If a settle window is still wanted, the
store computes it from its own clock in SQL; the instance clock never
participates.

## Outcome

Any instance, including one that has never existed before, produces
complete rollups; losing any instance delays work at most one cycle
rather than silently freezing half the customers; rebuilding a machine
cannot double-bill. The existing test suite passes unmodified: the
worker tests' hostnames become mere owner labels, totals and
idempotency behave identically.
