---
id: adr-0010
artifact_type: architecture-decision-record
title: CAPLAB P5 corrective continuation
status: decided
decision_owner: repository-owner
decision_authority: repository-ownership
created: 2026-07-16
decided_at: 2026-07-16
supersedes: []
superseded_by: null
affected_contexts:
  - agent-capability-lab
  - caplab-runtime
  - caplab-custody
  - proximal-backup
related_specs:
  - spec-agent-capability-lab
related_plans:
  - plan-agent-capability-lab-v0
related_receipts:
  - caplab-p5-execution-2026-07-16
  - caplab-p5-verification-2026-07-16
---

# CAPLAB P5 corrective continuation

Status interpretation: after the independent P5 failure was reported together
with the requirement for a newly frozen owner-authorized corrective campaign,
the repository owner instructed the executor to `proceed` on 2026-07-16. That
instruction authorizes the correction and remaining P5 effects below through
`2026-07-23T23:59:59Z`.

This decision does not accept the failed campaign, rewrite its records, admit
historical Study 001 evidence, authorize CAPLAB-24/P6 or CAPLAB-25/P7, run a
model, export data, train a model, or accept CAPLAB.

## Observations and inference

**Observation:** campaign `caplab-p5-recovery-2026-07-16` durably registered
operation `op-p5-recovery-0001`, then stopped when validation returned
`MetadataMismatch: migration runtime commit differs from provenance`.
Independent verification returned FAIL. The P5 registration and matching
Garage and `/nvr` bytes remain quarantined with access disabled. P4 remains
unchanged. **Evidence:** the P5
[`execution`](../records/caplab-p5-execution-2026-07-16.md) and
[`verification`](../records/caplab-p5-verification-2026-07-16.md) records.

**Observation:** the retained migration ledger has the expected filenames and
file hashes. Migration `0001` records the P4 commit that applied it, while
migration `0002` records the P5 commit that applied it. The retained P5
manifest names the original P5 runtime commit and both migration file hashes.

**Observation:** a production-regression test reproduced the failure through
`RegistrationService.verify`. The test passes when validation treats each
ledger `runtime_commit` as the applied-by Git identity and leaves comparison
with the explicitly expected current provenance to reconciliation. The
standing reconciliation test still rejects current-runtime provenance drift.

**Inference:** the all-rows-equal predicate conflated two identities: the
commit that applied each forward migration and the runtime commit retained in
one registration request. Byte corruption, locator substitution, migration
file drift, and request substitution remain contradicted by the preserved
hashes. The smallest repair is to preserve the two identities separately and
remove only the invalid equality.

## Decision and authorization

**Decision:** select corrective campaign
`caplab-p5-corrective-2026-07-16`.

**Owner and authority:** the repository owner under repository ownership,
exercised by the instruction `proceed` after receiving the P5 FAIL and
corrective-campaign requirement.

The original data identity remains unchanged:

| Field | Frozen value |
|---|---|
| Data campaign | `caplab-p5-recovery-2026-07-16` |
| Operation | `op-p5-recovery-0001` |
| Request SHA-256 | `4164a5d4febd4f429158d5917a15ae303392ecf1d9d6a57e84ae9a731282b229` |
| Content SHA-256 | `a1ac9f819a8a9e330290910b1049e70fe1a2a73a7ee98068a5fd9fe0c0d8b43d` |
| Manifest SHA-256 | `77acb678e5fa2d99374ba5a2e5841a043d904333a7718612fd3b0153a057f1b4` |
| Registered runtime commit | `c82b5512661c537db06f725af70198eccc818358` |
| Original authorization SHA-256 | `e8cd172af19cb631ba6814a3fd57c7b91f381cd799de862d9bd277b6ef68d34f` |

Before the first corrective host effect, the executor must freeze:

- the clean corrected CAPLAB commit as `executor_source_commit`;
- the clean Proximal corrective host-surface commit;
- this authorization document's SHA-256;
- the unchanged data identities above;
- the live disabled-quarantine state and P4 control;
- a new root-only execution directory and verified manifest; and
- a fresh independent verifier who did not implement or execute the repair.

The recovery configuration must name both `executor_source_commit` and
`registration_runtime_commit`. Registration replay and reconciliation use the
registered commit so the immutable request remains byte-identical. Migration
execution and host source verification use the corrected executor commit. The
configuration also binds this authorization and the superseded ADR 0009
authorization hash.

### Authorized corrective sequence

The executor may:

1. commit and install the regression-tested validation correction;
2. update the separate Proximal P5 surface to recognize only the exact
   disabled quarantine state and the two source identities above;
3. recreate temporary P5 operator, verifier, and Garage credentials under the
   existing expiry and role boundaries;
4. replay the exact registered request and require successful idempotent
   registration verification and reconciliation;
5. complete ADR 0009 live-sequence steps 5 through 12: Garage and `/nvr`
   missing and altered recovery, non-destructive Restic check, exact
   post-registration pgBackRest backup, isolated restore, dependency-refusing
   purge rehearsal, staged byte removal, guarded database purge, tombstone,
   disablement, and final P4 control verification; and
6. preserve the original failed roots and a separate corrective execution
   root. Evidence from the two campaigns may be verified together but must not
   be merged or rewritten.

The earlier wrong-role, invalid, ambiguous, interruption, orphan, and
changed-request observations need not be repeated. Their preserved receipts
remain part of P5 verification. A repeated destructive effect requires a new
reason and must still remain inside ADR 0009.

### Stop conditions

Stop and restore disabled quarantine on:

- source, authorization, request, manifest, migration-file, P4 control, or
  live-state drift;
- any replay that is not idempotent or any reconciliation mismatch;
- inability to restore the good P5 bytes before the next destructive step;
- backup, isolated-restore, dependency, purge, or tombstone failure;
- an unavailable fresh verifier;
- any need to rewrite the retained request or manifest, alter P4, stop the live
  PostgreSQL cluster, run destructive Restic prune, admit historical evidence,
  or widen the campaign.

After a post-effect stop, revoke P5 access, preserve both good byte copies when
the database still references them, emit a non-applying cleanup plan, and keep
CAPLAB-23 In Progress. Do not continue to P6.

## Verification and advancement gate

The fresh independent verifier must assess the original and corrective
evidence roots against ADR 0009 and this decision. P5 passes only if every
mandatory criterion is supported, the purge tombstone is present, P5 live
state is absent, P5 access is disabled, the isolated restore is removed, and
P4 is unchanged.

A PASS is verification, not acceptance. It removes the P5 predecessor blocker
but does not authorize P6. Study 001 admission still requires a separate
durable authorization naming the exact historical evidence and admission
effects.

## Doctrine advisory provenance

The correction used evidenced packet `pkt-af0d437e5bb22fb9`, packet content
SHA-256
`af0d437e5bb22fb967ba6e0e45ffafe2b472a8d2eb0ff567f5be7c931f5721f5`,
retriever `retriever-20c2013aa294d1fa`, doctrine
`doctrine-f630427242460c1e`, and corpus
`corpus-2026-07-12-d2ea7b94a1ce`.

Material guidance applied here is repository-contract precedence, evidence
before intervention, a separate defect-repair checkpoint, preservation of
unlisted behavior, and authority-bounded action. The incident record, live
quarantine observation, static validation path, red/green regression, and
owner instruction supplied the material evidence.

Generic obligations about mutable ownership, text normalization, async
timing, annotation cost, and resource cleanup are nonmaterial because this
repair changes one synchronous validation predicate and adds no new resource
or text boundary. Live reversibility and verification remain intentionally
unmet until this campaign executes.

## Reopening conditions

Reopen this decision if the exact quarantined identity is unavailable, the
correction requires a migration or stored-manifest rewrite, P4 changes, the
remaining ADR 0009 sequence cannot finish before expiry, or P6 scope is needed.
