# CAPLAB P5 recovery surface

This package implements the separately authorized CAPLAB-23/P5 custody
surface selected by
[ADR 0009](../../../docs/decisions/adr-0009-caplab-p5-failure-and-recovery-campaign.md).
It does not widen `caplab.runtime`: the ordinary P4 CLI still exposes no fault,
replacement, removal, or purge command.

The P5 CLI is `python -m caplab.recovery`. Its live configuration is fixed at
`/etc/caplab-p5/recovery.toml`, its campaign expires at
`2026-07-23T23:59:59Z`, and its effect commands accept only the frozen P5
identity in that root-custodied file. The bootstrap-only `identity` command
derives the exact request, content, manifest, identity-layer, migration,
fixture, dependency-lock, and authorization-document hashes before live
configuration is installed.

The package owns four bounded responsibilities:

- verified recovery between the exact Garage object and `/nvr` copy;
- separately typed invalid or ambiguous attempt observations containing no
  subject-outcome fields;
- orphan inventory across durable requests, registrations, both byte stores,
  retained dependencies, and purge tombstones; and
- one guarded PostgreSQL purge function reached only through an exact pending
  custody request.

The forward `0002_p5_recovery_custody.sql` migration keeps tables append-only
for ordinary roles. It grants no table-level delete privilege. Its
`SECURITY DEFINER` function is owned by the `NOLOGIN` CAPLAB owner and refuses
unknown, expired, cross-campaign, mismatched, shared, or dependency-bearing
state before deleting one exact P5 application-row closure transactionally.

Live fault and purge execution remains governed by ADR 0009. In particular,
the P4 registration is read-only control state; both P5 byte copies must be
staged before removal; database purge is refused until both live P5 bytes are
absent; every command outcome receives a direct numeric `.rc` receipt in the
root-only execution directory; and a different fresh agent or named human
must verify restore and purge before P5 can pass.
