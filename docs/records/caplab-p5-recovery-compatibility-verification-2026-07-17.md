# CAPLAB-23/P5 recovery-compatibility verification

Result: **FAIL for the correction; PASS for the live-cluster safety
boundary**.

Fresh verifier `/root/caplab_p5_adr0012_preflight` completed a read-only final
assessment on 2026-07-17. The full preserved report SHA-256 is
`5cee24d03c0594b6c01cf5f55a370b385fa414c65a60ab915f7f8997c57d06de`.
The verifier did not implement or execute the correction.

## Supported observations

- Exact backup `20260712-010203F_20260716-195901D` restored 45.4 GB across
  11,608 files into the fixed isolated target.
- The target used its own configuration, HBA, ident, socket, and loopback port
  `55435`.
- Recovery accepted `max_wal_senders=10`, obtained WAL, reached consistency,
  and became available for read-only queries. The ADR 0011 compatibility
  failure did not recur.
- The real TCP probe was rejected by the target HBA. The HBA also explicitly
  rejects local and TCP physical replication.
- The helper sampled recovery state before PostgreSQL selected promotion
  timeline 2. Its combined identity check failed and the exit guard safely
  stopped the isolated postmaster.
- The preserved target is stopped in recovery with
  `max_wal_senders setting: 10`, no PID or listener, and `phase=starting`.
- The live cluster retained the exact data directory, port, PID, start time,
  active state, P4/P5 controls, roles, local bytes, and credential absence.

## Verification judgment

**FAIL for ADR 0012's correction:** `pg_ctl --wait start` returned when the
target reached queryable hot-standby readiness, not completed promotion. The
helper queried `pg_is_in_recovery()` during that interval, received the
recovery-state result, and failed its final identity gate. The target never
reached the helper's `ready` phase, and restored migrations, P4/P5 records,
manifests, content identities, and closure counts were not queried.

**PASS for the bounded `max_wal_senders` repair:** the effective target value
is `10`, and recovery advanced past the prior fatal incompatibility.

**PASS for the safety boundary:** the isolated restore addressed only its
fixed target, socket, and loopback port. The HBA rejected TCP access and
replication paths. The exit guard stopped only the verified isolated PID.
Independent checks prove the live cluster and CAPLAB controls are unchanged.

## Recommendation and residual authority

**Recommendation, not a decision or authorization:** a new bounded decision
could require an explicit wait for promotion to complete before running the
same settings, replication, TCP, identity, and content checks.

ADR 0012's retry is consumed. Its removal condition required a successful
interim queryable-state report, which does not exist. Another helper change,
retry, target or state removal, dependency creation, byte deletion, purge,
tombstone, P6, P7, model work, evidence admission, and acceptance remain
unauthorized.
