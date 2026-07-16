# CAPLAB P5 execution record template

Status: execution template; contains no execution observation, verification,
or acceptance.

## Frozen authority and identities

Record the ADR 0009 content hash, authorization-binding hash, authorization
expiry, CAPLAB source commit, Proximal host-surface commit, independent
verifier identity, fixture and payload hashes, dependency lock, migration
ledger, host manifest, unit files, operation identity, all content and
manifest identities, the selected pgBackRest backup, and isolated restore
target.

## Preconditions

Record direct observations for clean source trees, active authorization,
disabled P4 campaign identities, unchanged P4 control, available rollback
staging, completed restic backup, adequate storage, active services, exact
roles and grants, and verifier readiness.

## Effects and observations

For every command, retain sanitized command text, UTC start and finish time,
stdout, structured stderr, and a direct numeric `.rc` file. Link before and
after PostgreSQL, Garage, and `/nvr` inventories. Keep invalid and ambiguous
attempt observations separate from subject outcomes.

Record the controlled interruption, missing and altered source drills,
restores, reconciliations, backup lock, non-destructive restic check,
pgBackRest backup and isolated restore, dependency-refusing purge rehearsal,
byte staging and removal, guarded database purge, tombstone, credential and
identity disablement, and unchanged P4 control.

## Stop or quarantine

If any ADR 0009 stop condition occurs, record the exact observation, completed
effects, stabilization or rollback action, remaining P5 state, revoked
access, cleanup plan, and quarantine location. Do not label partial execution
as verification.

## Manifest

Record the root-only execution directory, its verified `SHA256SUMS`, and the
method used to verify the manifest.
