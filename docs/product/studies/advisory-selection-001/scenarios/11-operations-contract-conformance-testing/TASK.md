# Nightly Nordvik sync is down

The nightly availability sync from Nordvik Supply has crashed on every run
since Friday. It aborts partway with a TypeError and writes nothing, so the
OSL and GOT snapshots the purchasing dashboard reads are five days stale.

Nordvik support says the only change on their side is that release 2.4 added
a `lead_time_days` field to availability items, and that additions like that
are allowed. Our test suite is green.

To reproduce: replay any current availability response through the client, or
run the sync against the Nordvik sandbox.

Expected: the sync completes and the snapshot updates. Actual: it crashes and
updates nothing.
