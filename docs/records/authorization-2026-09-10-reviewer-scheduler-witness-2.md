# Complete the pinned scheduler dependency closure

Under ADR 0026, authorize a new private custody
`reviewer-ranking-001/development/scheduler-witness-2`, with the same four
source revisions, witness, seven conditions, criteria, limits and isolation
as [the first authorization](authorization-2026-09-10-reviewer-scheduler-witness.md).
Preserve `scheduler-witness-1` unchanged: all four module-verification
preflights failed before compilation or execution because the isolated mount
omitted yaml.v3's `check.v1` dependency.

Include the existing cached source and module metadata for
`gopkg.in/check.v1@v0.0.0-20161208181325-20d25e280405`, already named in the
historical `go.sum`, along with the two existing dependencies. Pin all bytes
and require Go's module verification before each compilation. No download,
dependency upgrade or target source change is authorized. Copy the exact
source trees again into the new custody, preserving hashes and provenance.

The first attempt's frozen criteria and Go witness hashes must match the new
attempt before execution. These are new consumed-once compilation/execution
slots; no old attempt is replayed or relabeled. Expiry: consumption or
2026-09-11T00:00:00Z. All prior no-provider, no-live-graph, no-ranking and
historical-preservation boundaries continue to apply.
