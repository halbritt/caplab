# Execution and verification records

Execution records state what an authorized executor changed. Verification
records independently compare those effects with frozen criteria. Neither is
acceptance.

CAPLAB-22/P4 produced separate records for campaign
`caplab-p4-roundtrip-2026-07-15`:

- [`caplab-p4-execution-2026-07-15.md`](caplab-p4-execution-2026-07-15.md)
  records the authorized effects and quarantine state; and
- [`caplab-p4-verification-2026-07-15.md`](caplab-p4-verification-2026-07-15.md)
  records the independent PASS by `caplab22_verifier`.

Neither record accepts CAPLAB or authorizes P5.

CAPLAB-23/P5 proposal preparation produced a static-first
[`failure-mode audit`](../../CAPLAB_FAILURE_MODE_AUDIT_CODEX_2026-07-16.md).
The audit records current recovery gaps; it is not an execution or verification
record and does not authorize the proposed campaign.

The selected P5 implementation includes
[`execution`](caplab-p5-execution-template.md) and
[`independent verification`](caplab-p5-verification-template.md) templates.
They are empty contracts, not observations or evidence that P5 has run.

CAPLAB-23/P5 then produced separate records for campaign
`caplab-p5-recovery-2026-07-16`:

- [`caplab-p5-execution-2026-07-16.md`](caplab-p5-execution-2026-07-16.md)
  records the post-effect provenance stop, access disablement, and quarantined
  registration; and
- [`caplab-p5-verification-2026-07-16.md`](caplab-p5-verification-2026-07-16.md)
  records the independent **FAIL** because mandatory recovery, backup, restore,
  dependency, purge, tombstone, and final-absence criteria were not completed.

The safe stop and quarantine do not pass P5, accept CAPLAB, or authorize P6.

ADR 0010 then authorized a distinct corrective continuation without changing
the original P5 data identity:

- [`caplab-p5-corrective-execution-2026-07-16.md`](caplab-p5-corrective-execution-2026-07-16.md)
  records successful exact replay, recovery drills, non-destructive Restic
  check, and post-registration backup, followed by the mandatory stop when the
  frozen isolated-restore helper could not start Debian's externally
  configured PostgreSQL cluster; and
- [`caplab-p5-corrective-verification-2026-07-16.md`](caplab-p5-corrective-verification-2026-07-16.md)
  records the fresh independent **FAIL** because the restored database was not
  queryable and dependency refusal, purge, tombstone, restore removal, and
  final P5 absence remain unmet.

The corrective safe stop also does not pass P5, accept CAPLAB, or authorize
P6.

ADR 0011 authorized one narrower isolated-restore correction:

- [`caplab-p5-isolated-restore-execution-2026-07-16.md`](caplab-p5-isolated-restore-execution-2026-07-16.md)
  records actual use of the dedicated target configuration, HBA, socket, and
  loopback port, followed by the recovery-time `max_wal_senders` refusal and
  preserved safe stop; and
- [`caplab-p5-isolated-restore-verification-2026-07-16.md`](caplab-p5-isolated-restore-verification-2026-07-16.md)
  records independent **FAIL** for the correction and **PASS** for protecting
  the live cluster.

The one retry is consumed. The stopped target remains preserved, and another
retry, target removal, purge, and P6 require a new owner decision.

ADR 0012 authorized the recovery-compatible `max_wal_senders` correction and
one further isolated retry:

- [`caplab-p5-recovery-compatibility-execution-2026-07-17.md`](caplab-p5-recovery-compatibility-execution-2026-07-17.md)
  records successful recovery past the prior compatibility blocker, actual
  HBA rejection, and the safe stop caused by a promotion-readiness race; and
- [`caplab-p5-recovery-compatibility-verification-2026-07-17.md`](caplab-p5-recovery-compatibility-verification-2026-07-17.md)
  records independent **FAIL** for the correction and **PASS** for protecting
  the live cluster.

ADR 0012's retry is consumed. The new stopped target remains preserved, and
another retry, target removal, purge, and P6 require a new owner decision.

ADR 0013 then authorized the fixed promotion-readiness wait and one final
isolated retry:

- [`caplab-p5-promotion-readiness-execution-2026-07-17.md`](caplab-p5-promotion-readiness-execution-2026-07-17.md)
  records the real `t` then `f` promotion wait, restored P4/P5 identity
  queries, guarded stop, and exact isolated-target removal; and
- [`caplab-p5-promotion-readiness-verification-2026-07-17.md`](caplab-p5-promotion-readiness-verification-2026-07-17.md)
  records independent **PASS** for the correction and **PASS** for protecting
  the live cluster.

The promotion-readiness blocker is removed, but P5 still has closure
`1|1|0|0`. No dependency, byte deletion, purge, tombstone, P6, or acceptance
was authorized or performed.
