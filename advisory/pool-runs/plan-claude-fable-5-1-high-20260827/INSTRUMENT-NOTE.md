# Instrument pin, and the four rows that predate it

`results.unpinned-v38.jsonl` holds the first four rows of this run, scored
against the LIVE instrument (oracle
`67ad30b6c57192fabd31019154328fedf3752ff68afc8bdb3be0db5aeb50cc69`, checks
registry `v38`, 38 resolvable check sets). They are kept as evidence and are
NOT part of the measurement: they were rendered from a different prompt (38
offered check sets, not 42) and scored by a different instrument than the
six subjects of `report-2026-08-27-planning-p2b.md`.

`results.jsonl` is the measurement, run against the pinned P2b instrument in
`~/.local/lib/caplab-instruments/plan-p2b-20260827/` (see its PROVENANCE.md):
oracle rebuilt from striatum-next `06cd940`, checks registry `v37`.
