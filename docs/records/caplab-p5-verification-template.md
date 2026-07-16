# CAPLAB P5 independent verification template

Status: verification template; contains no verification result or CAPLAB
acceptance.

Verifier: a different fresh agent or named human assigned before the first
live fault.

## Frozen criteria

Record the criteria and identities received before live execution: ADR 0009,
authorization binding, source and host commits, fixture and operation
identities, backup and isolated restore identities, P4 control, expected
tombstone, execution-root path, and `SHA256SUMS`.

## Read-only observations

Independently compare the execution manifest, direct `.rc` receipts, store
inventories, restored database, migration ledger, P4 control, P5 registration
and recovery identities, dependency refusal, final purge tombstone, absence
of live P5 application and byte state, removed isolated restore, disabled P5
credentials and identities, and clean host phase.

For every observation, retain its command or method, locator, UTC time, and
relevant content hash. If raw evidence is unavailable, label the aggregate as
not independently verified.

## Verification result

Return `PASS` only if every mandatory ADR 0009 criterion is independently
supported. Otherwise return `FAIL` with each unmet or contradicted criterion
and the observed residual state.

This verification can pass or fail CAPLAB-23/P5. It cannot accept CAPLAB,
authorize CAPLAB-24/P6, or redefine the frozen criteria.
