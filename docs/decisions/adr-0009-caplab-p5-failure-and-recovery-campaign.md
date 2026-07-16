---
id: adr-0009
artifact_type: architecture-decision-record
title: CAPLAB P5 bounded failure and recovery campaign
status: proposed
decision_owner: repository-owner
decision_authority: repository-ownership
created: 2026-07-16
decided_at: null
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
related_receipts: []
---

# CAPLAB P5 bounded failure and recovery campaign

Status interpretation: the repository owner instructed the agent to handle the
next Plane items in dependency order. That authorizes CAPLAB-23 investigation,
proposal preparation, and tracker handling. It does not select an unseen fault
matrix or authorize deletion, corruption, restore, purge, historical evidence
admission, or P6. This proposal remains unselected until the owner explicitly
authorizes it as written or records revisions.

## Decision question and scope

Should CAPLAB implement and execute campaign
`caplab-p5-recovery-2026-07-16` through `2026-07-23T23:59:59Z` to qualify
failure detection, recovery, backup restore, orphan custody, and exact purge
using a new P5-only synthetic identity while preserving the quarantined P4
registration as an unchanged control?

This proposal governs CAPLAB-23/P5 only. It does not admit or inspect
historical Study 001 evidence, authorize CAPLAB-24/P6 or CAPLAB-25/P7, make a
capability inference, run a model, export data, train a model, verify its own
restore or purge, accept CAPLAB, or change Striatum.

## Observations and evidence

**Observation:** CAPLAB-22/P4 passed independent verification and left one
synthetic registration quarantined with runtime access disabled. The P4 object,
`/nvr` copy, application rows, cleanup plan, lifecycle state, and preserved
execution root remain evidence. P4 did not authorize a fault, restore, source
loss, deletion, or purge. **Evidence:** the P4
[`execution`](../records/caplab-p4-execution-2026-07-15.md) and
[`verification`](../records/caplab-p4-verification-2026-07-15.md) records.

**Observation:** the current registration service claims an operation in
PostgreSQL, writes and verifies Garage, writes and verifies `/nvr`, then
finalizes registration in PostgreSQL. A failure before finalization can leave
an incomplete request and byte copies. Replaying the identical request can
complete it. Reconciliation detects missing, mismatched, incomplete, locator,
manifest, and provenance state but does not repair it. **Evidence:**
`src/caplab/runtime/registration.py`, its adapters, and
`tests/test_runtime.py`.

**Observation:** the P4 runtime and host controller have no fault, restore,
object-delete, copy-delete, application-row-delete, or purge command. Migration
`0001_runtime_core.sql` rejects ordinary update and delete on CAPLAB v0
application tables. The cleanup plan applies nothing. **Evidence:** the runtime
CLI, storage adapters, migration, custody module, and the Proximal P4 host
contract.

**Observation:** `restic-prune.service` remains failed from 2026-07-01. During
the 2026-07-16 observation interval, the daily restic backup remained active
for several hours. The backup and prune units use the same repository and have
no shared serialization mechanism. The historical journal no longer preserves
the failure text. **Inference:** schedule overlap is a credible cause and a
future risk, but remote, credential, repository, or storage failure remain
credible rivals. **Evidence:** read-only systemd state and unit definitions.

The detailed current-behavior trace is in
[`CAPLAB_FAILURE_MODE_AUDIT_CODEX_2026-07-16.md`](../../CAPLAB_FAILURE_MODE_AUDIT_CODEX_2026-07-16.md).

## Recommendation and alternatives

**Recommendation:** select a separate P5 campaign and host surface. Keep the P4
runtime, controller, state, and retained registration unchanged as a control.
Use a new non-sensitive P5 operation and payload for every live fault,
recovery, and purge effect.

Rejected alternatives:

- faulting or purging the P4 registration would destroy the only preserved P4
  control and exceed its authorization;
- adding P5 delete or fault commands to the frozen P4 controller would violate
  its repository contract;
- qualifying only hermetic adapters would not verify the selected PostgreSQL,
  Garage, `/nvr`, and backup boundaries;
- manually changing live rows or disabling append-only triggers would bypass
  the custody contract; and
- proceeding directly to Study 001 would promote unverified recovery targets
  into an admission decision.

## Proposed decision and authorization

If selected, the repository owner authorizes the exact campaign below.

### Campaign identity, time, and roles

| Field | Proposed value |
|---|---|
| Checkpoint | `CAPLAB-23` / P5 only |
| Campaign | `caplab-p5-recovery-2026-07-16` |
| Authorization expiry | `2026-07-23T23:59:59Z` |
| Executor | primary Codex agent acting as the named CAPLAB and host delegate |
| Restore and purge verifier | a different fresh agent or named human, assigned before the first live fault |
| Live namespaces | existing `caplab` database, `caplab_v0` schema, `caplab-v0` bucket, and `/nvr/caplab/v0`, limited to new P5 identities |
| Control | the exact P4 registration and its preserved artifacts, read-only throughout P5 |

The executor may implement the campaign in standalone CAPLAB and a new
Proximal P5 host-integration directory. The existing Proximal
`caplab-runtime/**` P4 subsystem may receive documentation links only; its
commands, campaign, expiry, source pin, lifecycle state, and installed files
remain unchanged.

Before the first live effect, the executor must freeze and record:

- the clean standalone CAPLAB implementation commit;
- the clean Proximal P5 host-surface commit;
- dependency-lock, migration, fixture, host-manifest, and unit-file hashes;
- the exact P5 operation ID, content SHA-256, object key, local-copy key,
  manifest SHA-256, and identity SHA-256;
- the selected pgBackRest backup identity and isolated restore target;
- the exact purge authorization document hash; and
- the independent verifier identity.

Any drift after that freeze stops the campaign.

### Repository implementation boundary

The selected implementation may add:

- `src/caplab/recovery/**` for explicit verifier reports, source-loss recovery,
  orphan inventory, and custody checks;
- a forward-only `0002` migration for P5 custody requests, purge tombstones,
  and one guarded database purge procedure;
- hermetic and separately gated local integration tests for the P5 matrix;
- P5-only non-sensitive fixtures;
- P5 execution and verification record templates; and
- a separate Proximal P5 host surface for temporary custodian identity,
  campaign expiry, isolated PostgreSQL restore, Garage and `/nvr` staging,
  backup serialization, inventory, disablement, and exact cleanup.

The ordinary `caplab.runtime` writer, reader, and verifier commands remain
non-destructive. Purge and fault operations are not added to their public CLI.
The P5 custodian surface accepts only the frozen campaign and exact
authorization identity and expires with the campaign.

### Hermetic failure matrix

The repository gate must first prove, without live service effects:

1. missing and altered Garage objects fail verification and retrieval;
2. missing and altered `/nvr` copies fail verification and retrieval;
3. locator, manifest, migration-ledger, and runtime-provenance substitution
   fail closed;
4. duplicate replay is idempotent and a changed operation request is refused
   before new effects;
5. interruption after either byte write and before final metadata remains
   incomplete and can be retried without rewriting bytes;
6. invalid and ambiguous attempts produce separately typed
   invalid-attempt observations and cannot populate subject-outcome fields;
7. orphan inventory distinguishes incomplete requests, unreferenced objects,
   unreferenced copies, and registered dependencies;
8. purge refuses an unknown identity, mismatched authorization hash, retained
   dependency, P4 identity, or non-P5 campaign; and
9. every expected refusal has a direct numeric `.rc` receipt in addition to
   structured stderr.

### Live P5 sequence

The live campaign may perform these effects only after the frozen source,
identity, expiry, verifier, and rollback checks pass:

1. Keep the P4 campaign disabled. Capture an independent control inventory and
   verify the P4 registration before any P5 mutation.
2. Create one new P5 synthetic registration with distinct operation and
   content identities. Capture PostgreSQL, Garage, and `/nvr` inventories.
3. Exercise wrong-role, duplicate, changed-request, invalid, and ambiguous
   calls. Preserve stdout, stderr, direct numeric status receipts, and
   unchanged verifier-owned inventories.
4. Run one controlled P5 interruption after both byte copies are verified but
   before final PostgreSQL registration. Prove incomplete metadata and orphan
   detection, then replay the identical request to completion.
5. Stage the exact P5 Garage object in a root-custodied temporary recovery area,
   remove it from Garage, prove verification and retrieval fail with
   `ObjectMismatch`, restore it from the matching `/nvr` copy, and reconcile
   every identity.
6. Replace the P5 Garage object with non-identical bytes, prove mismatch, then
   restore and reconcile it from `/nvr`.
7. Atomically move only the P5 `/nvr` copy into the recovery area, prove
   `CopyMismatch`, restore it from Garage, and reconcile. Repeat with
   non-identical local bytes.
8. Do not interrupt the currently running restic backup. After it completes,
   install a shared blocking lock for the backup and prune services, preserve
   the next failure output if either command fails, and run a non-destructive
   restic repository check. A destructive `restic prune` is outside this
   campaign unless the owner separately names it.
9. Create an exact post-registration pgBackRest backup. Restore that backup
   into a new isolated PostgreSQL data directory and loopback port under
   `/var/tmp`, with no replacement or stop of the live cluster. Verify the
   restored migration ledger, P4 control, P5 registration, manifests, and
   content identities. Remove only the isolated restore after the independent
   verifier has preserved its report.
10. Generate an exact P5 cleanup plan. The guarded custody procedure must
    refuse purge while any external registration, result, claim, dataset, or
    campaign dependency exists.
11. Under the frozen purge authorization, stage the exact P5 bytes for crash
    recovery, delete only the P5 Garage object and `/nvr` copy, verify their
    absence, delete only the P5 application-row closure through the guarded
    custody procedure, and preserve a non-sensitive purge tombstone. If the
    database purge fails, restore both staged byte copies and stop.
12. Disable and remove the P5 custodian credentials and temporary identities.
    Independently verify the purge tombstone, absence of P5 live state, removal
    of the isolated restore, clean P5 host phase, and unchanged P4 control.

The guarded database procedure is owned by the `NOLOGIN` CAPLAB owner role and
may delete only the exact P5 operation closure named by a matching pending
custody request. It records the authorization hash and content identities in a
retained tombstone transaction. It refuses P4, unknown, cross-campaign, or
dependency-bearing state. The migration never creates a general table-delete
grant and never authorizes `DROP`, `TRUNCATE`, or trigger disablement.

### Evidence and verification contract

The executor preserves one root-only execution directory with:

- commands and sanitized environment identity;
- direct `.rc` receipts for every expected success and refusal;
- before and after inventories for all three stores;
- content hashes for every retained artifact;
- backup and isolated-restore identities;
- recovery, reconciliation, cleanup-plan, purge, disablement, and P4-control
  results; and
- a verified `SHA256SUMS` manifest.

The independent verifier starts from frozen criteria and read-only credentials
where possible. The verifier compares the execution root, live inventories,
restored database, purge tombstone, disabled P5 identities, and unchanged P4
control. Verification may return PASS or FAIL for P5; it cannot accept CAPLAB
or authorize P6.

### Stop and quarantine conditions

Stop before or during execution on:

- absent or expired authorization, source drift, dirty source, or missing
  verifier;
- any P4 control change;
- any target identity outside the frozen P5 closure;
- backup failure without preserved error output;
- mismatch between PostgreSQL, Garage, `/nvr`, fixture, or Git identities;
- inability to restore the good copy before the next destructive step;
- a purge dependency, guarded-procedure refusal, or incomplete tombstone;
- secret output, unexpected historical evidence, or public projection of a
  locator; or
- any need to stop the live PostgreSQL cluster, run destructive restic prune,
  alter another Garage object, or widen the campaign.

On a stop after the first P5 effect, revoke P5 access, restore staged P5 bytes
when the database still references them, emit a cleanup plan, preserve the
execution root, and quarantine P5 state. Do not repair history, touch P4, or
continue to P6.

## Doctrine advisory provenance

The proposal used doctrine packet `pkt-ac3ffbdff8ec270c`, content SHA-256
`ac3ffbdff8ec270ce021affe61009769c5e5f4ad42f725fcbcaefe3ac089c0ce`,
retriever `retriever-db7e43c1081abf3d`, doctrine
`doctrine-f630427242460c1e`, and corpus
`corpus-2026-07-12-d2ea7b94a1ce`. Material guidance applied here is repository
contract precedence, evidence before intervention, explicit atomicity scope,
structured cleanup, system-of-record boundaries, behavior preservation, and
authority-bounded action. Repository decisions remain authoritative.

Material evidence obligations were satisfied for user authority, repository
contracts, current mutation paths, data authority, atomicity, failure tests,
runtime backup state, and checkpoint verification. The packet's remaining
obligations about API abstraction, static typing, concurrency optimization,
normalization, non-ASCII representation, annotation cost, and performance were
classified nonmaterial because they cannot change this proposal's authority
ceiling, preservation boundary, or destructive stop rules. Live reversibility,
restore, and purge observations remain deliberately unmet until the selected
campaign executes; this proposal does not claim them.

## Owner selection required

**Recommendation:** authorize ADR 0009 as written.

Selection authorizes only the implementation and P5 effects named above through
the proposed expiry. It does not authorize historical evidence inspection or
admission, P6, P7, a model call, training, export, acceptance, or any effect not
listed here.
