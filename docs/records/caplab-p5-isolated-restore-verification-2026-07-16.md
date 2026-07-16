# CAPLAB-23/P5 isolated-restore correction verification

Result: **FAIL for the correction; PASS for the live-cluster safety
boundary**.

Fresh verifier `/root/caplab_p5_isolated_verifier` completed a read-only
assessment on 2026-07-16. The preserved report SHA-256 is
`12f505328bf202e5f22907cd62f37fa54e900f4bc4097733e6f03732a893276f`.
The verifier did not implement or execute the correction.

## Supported observations

- Exact backup `20260712-010203F_20260716-195901D` restored successfully.
- The dedicated configuration, rejecting HBA, loopback port `55435`, and
  target socket were actually used.
- Recovery refused `max_wal_senders = 0` because the backup required at least
  the primary value `10`; the isolated postmaster then shut down.
- The stopped target and root state are preserved without a PID or listener.
- The live cluster retained the same data directory, port, PID, start time,
  active state, P4 control, P5 retained control, roles, local bytes, and
  credential absence.

## Verification judgment

**FAIL for ADR 0011's correction:** the restored database never became
queryable. Restored migrations, P4 control, P5 registration, manifests, and
content identities were therefore not verified. No interim queryable-state
report exists, the guarded stop helper did not transition state to `stopped`,
and the target was not removed.

**PASS for the safety boundary:** the isolated instance addressed only its
dedicated target, socket, HBA, and loopback port. It shut itself down after the
recovery refusal. Independent final checks proved the live PostgreSQL cluster
and CAPLAB controls were unchanged.

## Recommendation and residual authority

**Recommendation, not a decision or authorization:** a new bounded decision
could evaluate a recovery-compatible `max_wal_senders` value while retaining
the proven target, socket, HBA, live-identity, one-retry, and independent
verification gates. Another defect remains credible until recovery completes.

The ADR 0011 retry is consumed. Another retry, target removal, dependency
creation, byte deletion, purge, tombstone, P6, P7, model work, evidence
admission, and acceptance remain unauthorized.

