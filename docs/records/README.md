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

ADR 0014 then authorized exact P5 purge completion and gated P6 admission:

- [`caplab-p5-purge-execution-2026-07-17.md`](caplab-p5-purge-execution-2026-07-17.md)
  records the dependency refusal, matching release, staged exact-byte
  deletion, guarded transaction, tombstone, disablement, and cleanup; and
- [`caplab-p5-purge-verification-2026-07-17.md`](caplab-p5-purge-verification-2026-07-17.md)
  records independent **PASS** for ADR 0014 Stage A and CAPLAB-23/P5.

P5 is complete and the P6 predecessor gate is open under ADR 0014 only. This
does not authorize P7 or accept CAPLAB.

ADR 0014 Stage B then produced separate CAPLAB-24/P6 records:

- [`caplab-p6-admission-execution-2026-07-17.md`](caplab-p6-admission-execution-2026-07-17.md)
  records the exact restricted source inventory, content-addressed two-store
  admission, append-only relational links, idempotent replay, and role
  disablement; and
- [`caplab-p6-admission-verification-2026-07-17.md`](caplab-p6-admission-verification-2026-07-17.md)
  records the independent **PASS** for the 684-record, 325-byte-identity,
  20-assignment Study 001 registration.

P6 is complete. ADR 0017 approved the exact
[`P7 live continuation proposal`](caplab-p7-live-continuation-proposal-2026-07-18.md).
The resulting
[`stopped execution record`](caplab-p7-live-attempt-2026-07-18.md) observes
that Garage 2.3 response-shape verification stopped the run before either
recomputation, followed by complete access disablement and preservation. The
[`exact retry proposal`](caplab-p7-live-retry-proposal-2026-07-18.md) was
approved by ADR 0018. The resulting
[`stopped retry record`](caplab-p7-live-retry-attempt-2026-07-19.md) observes
that an added password-representation assertion stopped before either
recomputation, followed by complete access disablement and preservation. The
[`exact second retry proposal`](caplab-p7-live-retry-2-proposal-2026-07-19.md)
binds the versioned readiness repair and was approved unchanged by ADR 0020.
The resulting
[`stopped second-retry record`](caplab-p7-live-second-retry-attempt-2026-07-19.md)
observes that the first recomputation stopped at the identity-safe JSON-decimal
boundary, followed by complete access disablement and preservation. ADR 0020 is
consumed. Capability inference, export, publication, training, purge, another
live retry, independent verification, and CAPLAB acceptance remain unavailable
and unauthorized.

ADR 0016 Stage A then produced the
[`P7 JSON-decimal identity repair`](caplab-p7-json-decimal-repair-2026-07-19.md).
The regression reproduced the second retry's live failure before the one-line
boundary repair and passes afterward with the complete repository gate. The
[`exact third retry proposal`](caplab-p7-live-retry-3-proposal-2026-07-19.md)
binds the repaired CAPLAB and prepared Proximal commits. It awaits a new owner
decision; preparation alone does not authorize installation or live access.
ADR 0021 records the repository owner's conditional approval after confirming
the repair and complete gate pass, and authorizes that proposal unchanged.
The resulting
[`stopped third-retry record`](caplab-p7-live-third-retry-attempt-2026-07-19.md)
observes that the controller refused a symlinked venv interpreter before state
or access creation. Independent controls prove access remained disabled and all
protected state unchanged. ADR 0021 is consumed; the owner's instruction to
`retry again` requires an exact runtime-custody correction before live effects.

ADR 0016 Stage A then produced the
[`regular-file runtime custody repair`](caplab-p7-runtime-custody-repair-2026-07-19.md).
The [`exact fourth-retry proposal`](caplab-p7-live-retry-4-proposal-2026-07-19.md)
binds that correction, and ADR 0022 records the owner's `retry again`
instruction as authority for one exact corrected execution.
The resulting
[`P7 execution record`](caplab-p7-live-recomputation-execution-2026-07-20.md)
reports two byte-identical recomputations, a byte-identical historical match,
complete aggregate disablement, and matching preservation controls. P7 is
complete; this execution is not independent verification or acceptance.

ADR 0016 Stage A also produced the
[`P8 and P10 implementation record`](caplab-p8-p10-stage-a-implementation-2026-07-18.md).
The deterministic profile-proposal and candidate-manifest boundaries are
implemented and pass the repository gate. This is implementation preparation,
not execution of P8 or P10. The P7 observation is now available for those
deterministic checkpoints. Human inference, eligibility, export, independent
verification, and acceptance remain separate gates.

CAPLAB-39 produced the
[`repository migration record`](caplab-39-repository-migration-2026-07-19.md).
It records the verified bundles, joined histories, preserved branches, GitHub
rename, local compatibility redirect, and retained recovery checkout. The
migration changes repository identity and topology; it does not accept CAPLAB
or authorize any pending study, inference, export, or training gate.
