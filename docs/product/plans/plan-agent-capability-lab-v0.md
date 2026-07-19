---
id: plan-agent-capability-lab-v0
artifact_type: implementation-plan
title: Agent Capability Lab v0
status: authorized
owner: repository-maintainers
created: 2026-07-15
updated: 2026-07-18
supersedes: []
superseded_by: null
source_artifacts:
  - spec-agent-capability-lab
source_decision: adr-0002
baseline_repository: halbritt/books
baseline: 97380767e4517d991b3118c738922ba43f2448af
authorization_record: adr-0007
authorization_records:
  - adr-0007
  - adr-0009
  - adr-0010
  - adr-0014
  - adr-0015
  - adr-0016
  - adr-0017
authorized_scope:
  - CAPLAB-22/P4
  - CAPLAB-23/P5
  - src/caplab/runtime/**
  - tests/test_runtime.py
  - tests/fixtures/runtime/**
  - tests/integration/test_runtime_local.py
  - docs/records/caplab-p4-execution-2026-07-15.md
  - docs/records/caplab-p4-verification-2026-07-15.md
  - proximal:caplab-runtime/**
  - postgres:caplab/caplab_v0
  - garage:caplab-v0
  - /nvr/caplab/v0
  - adr-0009 bounded P5 effects
  - adr-0010 corrective P5 continuation
  - adr-0014 exact P5 purge completion and restricted P6 admission
  - adr-0015 P5 frozen executor source worktree correction
  - CAPLAB-24/P6
  - src/caplab/admission/**
  - tests/test_admission.py
  - tests/fixtures/admission/**
  - tests/integration/test_admission_local.py
  - docs/records/caplab-p5-purge-*
  - docs/records/caplab-p6-*
  - proximal:caplab-p6/**
  - adr-0016 Stage A model-free backlog-drain implementation
  - CAPLAB-25/P7 implementation preparation
  - CAPLAB-26/P8 implementation preparation
  - CAPLAB-28/P10 implementation preparation
  - src/caplab/recomputation/**
  - src/caplab/profile/**
  - src/caplab/training_candidates/**
change_types:
  - change-feature-implementation
  - change-architectural-restructuring
  - change-migration
  - change-operational-hardening
---

# Agent Capability Lab v0

Status interpretation: ADRs 0004 through 0008 select Study 001, evidence
governance, the capability card, the CLI runtime, and the standalone repository.
The repository owner authorized only CAPLAB-22/P4 through
`2026-07-22T23:59:59Z` and delegated CAPLAB decision authority on 2026-07-15.
P4 executed and passed independent verification. The repository owner selected
ADR 0009 and authorized its bounded P5 implementation and effects through
`2026-07-23T23:59:59Z`. The first P5 execution failed independent
verification and left the exact P5 state quarantined. ADR 0010 records the
owner's instruction to proceed with a corrective continuation under the same
expiry. ADR 0014 authorizes exact P5 purge completion and, only after an
independent P5 PASS, restricted P6 admission through
`2026-07-24T23:59:59Z`. ADR 0016 authorizes model-free implementation
preparation for P7, P8, and P10 through `2026-07-25T23:59:59Z`; live P7 data
access remains unavailable until a separate continuation binds the exact
executor and temporary read-only runtime. ADR 0017 now authorizes that exact
P7 continuation through `2026-07-25T23:59:59Z`. Human inference, eligibility,
export, independent verification, model calls, training, and acceptance remain
unauthorized. P8 and P10 now have hermetic deterministic implementations, but
their actual Study 001 outputs remain unavailable until authorized live P7
produces the bound observation.

## Objective and authority boundary

Deliver the smallest complete CAPLAB product slice: register one exactly
identified historical checkout-retries experiment as Study 001, reconstruct
and recompute it through the selected systems of record, emit one bounded
capability profile and one separately authorized training-eligible export,
prove unsupported broader claims unavailable, independently verify the slice,
and present it to the repository owner for acceptance.

The governing product contract is
[`spec-agent-capability-lab`](../specs/spec-agent-capability-lab.md); the selected
architecture is [`adr-0002`](../../decisions/adr-0002-agent-capability-lab-v0.md).
Neither record authorizes implementation. Plane work-item state is a planning
projection and cannot select Study 001, authorize work, record a human
inference, verify an outcome, or accept v0.

Authority is deliberately reacquired at the boundary where it is needed:

- the repository owner or a durably named delegate selects Study 001, the
  capability card, evidence governance, and the runtime shape;
- a separate authorization record names the exact repository, Postgres, S3,
  migration, retention, rollback, verification, and expiry scope for each
  executable campaign;
- a named human makes the Study 001 capability inference and training-
  eligibility decision;
- dataset export receives its own authorization; and
- an independent verifier records verification before the repository owner
  records acceptance or rejection.

## Current-state evidence and assumptions

**Observation:** `halbritt/books` baseline
`97380767e4517d991b3118c738922ba43f2448af` contains the decided CAPLAB
specification and ADR, but no CAPLAB implementation plan. Both source records
have empty `related_plans` lists. **Evidence:** Git status, product index, the
source records, and the plan directory inspected on 2026-07-15.

**Observation:** On 2026-07-15 the repository owner selected the exact C9 Luna
B-versus-V confirmation as Study 001 and selected the v0 evidence-governance
boundary. ADRs 0004 and 0005 record those decisions. Neither decision authorizes
implementation or evidence admission.

**Observation:** `PYTHONDONTWRITEBYTECODE=1 make doctrine-check` passed in the
source repository at the original baseline. **Limit:** that historical check
is source provenance, not a standalone CAPLAB runtime or storage check. CAPLAB's
current repository gate is `make check`; Doctrine retrieval, when used, remains
external advisory evidence.

**Observation before this plan's tracker projection:** the existing CAPLAB Plane
project contained CAPLAB-1 through CAPLAB-17. CAPLAB-1 recorded the
selected contract and was Done. CAPLAB-2 through CAPLAB-17 were Backlog
projections of the rejected earlier charter: among other mismatches, they pooled
checkout-retries experiments, used an overloaded subject tuple, and put later
preference, Striatum, and training work inside the active queue. **Evidence:**
live Plane inventory before reconciliation on 2026-07-15. The status log records
the resulting current projection.

**Inference:** retaining those items as the active queue would make two
incompatible plans appear current. Rewriting their meanings would obscure the
planning history. The replacement queue should therefore use new work items;
the old items should remain inspectable in `Cancelled` with a supersession
comment.

Assumptions to test before implementation:

- the selected C9 evidence passes the artifact-specific privacy, licensing, and
  credential disposition required before admission;
- system Postgres and the locally scoped S3-compatible store can support
  dedicated CAPLAB namespaces, credentials, backup, restore, retention, and
  purge rules;
- a model-free, CLI-first vertical slice is sufficient for v0; and
- the selected historical evidence can support a bounded capability inference
  and training-eligible examples. If it cannot, v0 must preserve that result as
  unavailable rather than manufacture a claim or dataset.

## Scope, non-goals, and change classification

This plan covers CAPLAB-owned code, tests, migrations, documentation, and local
runtime namespaces only after a separate authorization record names them.
Future checkpoints may authorize read-only inspection of historical
checkout-retries artifacts. P4 does not. P4 read-only inspection is limited to
the system Postgres configuration, local S3-compatible service, backup and
restore surfaces, and the synthetic fixture it creates.

The work classes stay separate:

- **feature:** study registration, reconstruction, recomputation, profile, and
  export behavior;
- **architecture:** layered identities and one authority per kind of state;
- **migration:** creation and removal of CAPLAB-owned Postgres and S3 state;
- **operational hardening:** integrity, idempotence, recovery, redaction, audit,
  and purge behavior; and
- **documentation:** decisions, capability cards, manifests, verification, and
  acceptance records.

Out of scope for v0 are new model calls, preference studies, multi-family
Striatum qualification, scheduler-policy changes, fine-tuning, checkpoint
deployment, a global leaderboard, public raw evidence, a second operational
database, a daemon, a UI, and a public API. Those are not implicitly authorized
by completing any checkpoint here.

## Preservation boundaries

Every checkpoint preserves:

- historical tasks, treatments, trial order, results, corrections, failures,
  stopping rules, timestamps, and claim scope;
- original evidence bytes and verified content identities;
- separate model, agent-configuration, administration, trial-context,
  assignment, attempt, and analysis identities;
- S3 as authority for immutable evidence bytes, Postgres as authority for live
  operational metadata, standalone CAPLAB Git as authority for governing code,
  decisions, manifests, and verification records, `halbritt/books` Git as the
  source authority for unadmitted historical research, and Plane as a
  regenerable projection;
- mechanical observations separately from human-owned judgments, inferences,
  decisions, authorization, verification, and acceptance;
- privacy, license, credential, retention, purge, and backup boundaries; and
- the target systems' authority: CAPLAB cannot alter Striatum policy or claim
  scheduler, deployment, or acceptance authority.

Registration cannot rewrite a historical record or retroactively authorize its
retention. A missing object, hash mismatch, locator substitution, database-to-
manifest disagreement, missing human judgment, or absent authorization fails
closed. A recomputation discrepancy is quarantined for investigation; it is not
permission to change the historical result.

## Dependency map

```text
P0 ──┬──> P2 ──┐
     │         │
P1 ──┴────────> P3 -> P4 -> P5 -> P6 -> P7 -> P8 -> P9 ──┐
                       │              └────> P10 -> P11 ───┤
                       │                          └─> P12 ─┤ (when authorized)
                       └─────────────────────────────────> P13 -> P14
```

P0 and P1 may proceed independently. P10 may begin after P2 and P7 without
waiting for the capability inference at P9. Human-owned gates are not AFK work,
even when all mechanical inputs are ready.

Two stopped outcomes are part of the plan rather than implementation failures:

- if P0 finds no admissible Study 001 candidate, record that decision and stop;
  P2 through P14 remain unavailable. Substituting another v0 slice requires the
  repository owner to reopen the governing specification and ADR; and
- if P11 selects no training-eligible examples, P12 is not run. P13 verifies
  that no export occurred and records the v0 export criterion as unmet. P14 may
  then record revision or rejection, but not acceptance.

## Checkpoints and Plane projection

All replacement work items begin in `Backlog`. `Ready`, `In Progress`, or a
completed dependency does not authorize the next item. Each executable item
must cite the durable authorization record that covers it.

| ID | Plane item | Purpose | Depends on | Principal output |
|---|---|---|---|---|
| P0 | CAPLAB-18 | Bind the exact historical Study 001 | CAPLAB-1 | Git-recorded selection decision or no-admissible-candidate decision |
| P1 | CAPLAB-19 | Decide CAPLAB v0 evidence governance | CAPLAB-1 | Current runtime facts and owner governance decision |
| P2 | CAPLAB-20 | Select the Study 001 capability card | P0 | Versioned, owner-selected capability card |
| P3 | CAPLAB-21 | Select the runtime shape and authorize a bounded campaign | P0, P1, P2 | Runtime decision and bounded authorization record |
| P4 | CAPLAB-22 | Round-trip one synthetic sealed attempt | P3 | Verified model-free Postgres/Garage/NVR path |
| P5 | CAPLAB-23 | Fail closed and recover the synthetic attempt | P4 | Integrity, fault, backup, restore, and purge evidence |
| P6 | CAPLAB-24 | Register Study 001 without rewriting history | P0, P1, P5 | Frozen Study 001 registration manifest |
| P7 | CAPLAB-25 | Recompute the frozen Study 001 result | P6 | Content-addressed recomputation record |
| P8 | CAPLAB-26 | Emit a bounded Study 001 capability-profile proposal | P2, P7 | Study-local profile with broader claims unavailable |
| P9 | CAPLAB-27 | Make or decline the Study 001 capability inference | P8 | Named human inference or refusal record |
| P10 | CAPLAB-28 | Derive a governed training-candidate set | P2, P7 | Candidate manifest; no eligibility or export |
| P11 | CAPLAB-29 | Select training eligibility and decide whether to authorize one export | P1, P10 | Human eligibility decision and, when selected, export authorization |
| P12 | CAPLAB-30 | Materialize the authorized training-eligible export | P11 authorization | Verified immutable dataset bundle and manifest |
| P13 | CAPLAB-33 | Independently verify the integrated CAPLAB v0 slice | P5, P7, P8, P9, P11; P12 when authorized | Independent verification record |
| P14 | CAPLAB-34 | Accept or reject CAPLAB v0 | P13 | Repository-owner acceptance decision |

### P0 — Bind the exact historical Study 001

The repository owner selected C9 in
[`adr-0004`](../../decisions/adr-0004-caplab-study-001-selection.md). The
decision fixes the experiment identity and exclusions but does not admit,
retain, import, or register evidence.

Prepare a candidate dossier from preserved artifacts, including the exact
preregistration, result, task and world identities, preservation manifest,
content hashes, and current availability. Label aggregate-only or missing raw
evidence. A repository owner or durably named delegate selects exactly one
experiment, or records that no candidate is admissible. The Git decision grants
no implementation or retention authority and excludes adjacent experiments.

Stop if a manifest cannot be verified, evidence has to be rewritten, or the
selection owner is absent.

### P1 — Decide CAPLAB v0 evidence governance

The repository owner selected the v0 governance boundary in
[`adr-0005`](../../decisions/adr-0005-caplab-v0-evidence-governance.md). The
decision fixes policy and fitness targets but creates no datastore state and
does not verify the selected services.

Inspect, without mutation, the exact local Postgres and S3-compatible runtime,
versions, backup and restore boundary, credential owner, feasible dedicated
namespaces, and purge owner. The owner then selects data classes, purposes,
access roles, retention periods, redaction and licensing checks, purge triggers,
restore authority, and sanitized Plane projection rules. The decision contains
no credentials and creates no datastore state.

Stop if the available services cannot meet the selected isolation, recovery,
or retention contract. Reopen the architecture if operating both stores is
disproportionate.

### P2 — Select the Study 001 capability card

The repository owner selected version 0.1.0 of
[`caplab-study-001-explicit-verification-elicited-harm-avoidance`](../capability-cards/caplab-study-001-explicit-verification-elicited-harm-avoidance.md)
in [`adr-0006`](../../decisions/adr-0006-caplab-study-001-capability-card-selection.md).
The exact review bytes define the construct, intended population, direct
observables, controls, rivals, falsifiers, exclusions, missingness, scoring,
human-owned judgments, and promotion gates. Selection establishes the
measurement contract; it records no capability inference and grants no P3
implementation authority.

### P3 — Select the runtime shape and authorize a bounded campaign

ADR 0007 selects the CLI-first batch path, interface, Postgres schema and roles,
S3 namespace, dependency, migration, retention, rollback, verification,
expiry, and stop contracts. ADR 0008 moves repository ownership to standalone
CAPLAB. The owner separately exercised bounded CAPLAB-22/P4 authority.

### P4 — Round-trip one synthetic sealed attempt

Using non-sensitive fixtures, carry layered identities and one sealed
assignment through content-addressed object storage with overwrite checks,
transactional metadata, retrieval, and hash verification. Enforce stable
operation identities at durable effect boundaries so retries are idempotent
and overwrite or identity substitution is refused. Keep default repository
checks hermetic; use a separately invoked local integration gate for the real
stores.

Before the first synthetic S3 or NVR object or synthetic application row,
rollback may remove only newly created bootstrap resources. After that
boundary, rollback revokes credentials, disables peer identities, emits a
content-identified cleanup plan, and quarantines synthetic state. P4 does not
authorize live evidence-object or synthetic application-row deletion.

P4 executed and independently verified PASS on 2026-07-15. The
[`execution record`](../../records/caplab-p4-execution-2026-07-15.md) preserves
the effects, deviations, artifacts, and quarantine boundary; the
[`verification record`](../../records/caplab-p4-verification-2026-07-15.md)
records the separate verifier's observations and bounded numeric-status gap.
This completes P4 verification only. It is not acceptance and does not
authorize P5.

### P5 — Fail closed and recover the synthetic attempt

Exercise missing and altered objects, locator drift, duplicate submission,
interrupted transactions, manifest mismatch, invalid and ambiguous attempts,
backup restore, orphan detection, and authorized purge. Invalid attempts remain
auditable as invalid-attempt observations but cannot become subject-behavior
outcomes or inference-bearing trial observations. Recovery must reproduce
content identities and the selected operational state.

### P6 — Register Study 001 without rewriting history

P6 executed under ADR 0014 and received independent **PASS** on 2026-07-17.
The frozen restricted registration manifest is
`d2d4f821146c3f39e6726133c383807ec9f6051834e74fbd3a5f33aae8ef148e`:
684 evidence records, 325 unique content identities, and exact 20/20/20
assignment-attempt-outcome links. Temporary writer and verifier access is
disabled. This completion does not authorize P7.

Ingest only inputs bound by the P0 decision and verified preservation manifest.
Link layered identities, assignments, attempts, outcome records, object
locators, and one frozen registration manifest end to end. Preserve historical
content and timestamps. Missing or mismatched evidence stops registration; no
model call occurs.

### P7 — Recompute the frozen Study 001 result

ADR 0017's exact live attempt stopped during reader-ready verification before
either recomputation. Aggregate disablement passed and all preserved controls
remain unchanged. The stopped execution is
[`caplab-p7-live-attempt-2026-07-18`](../../records/caplab-p7-live-attempt-2026-07-18.md).
The causal Garage 2.3 response-shape repair is pushed, but the
[`exact retry proposal`](../../records/caplab-p7-live-retry-proposal-2026-07-18.md)
awaits a new owner decision. P7 remains incomplete.

Resolve registered immutable evidence through Postgres locators, apply the
frozen analysis and missingness rules, and reproduce the selected normalized
result byte for byte. Bind inputs, code, output, and failure classifications in
a content-addressed result manifest. A deterministic mismatch is reported and
quarantined rather than repaired by rewriting history. The output is an
observation or estimate, not a capability inference.

### P8 — Emit a bounded Study 001 capability-profile proposal

Bind the selected card, exact population, recomputed result, uncertainty,
missingness, failures, and credible rivals. Mechanically show cross-task
capability, universal ranking, preference, and Striatum placement as
unavailable. The profile remains a proposal pending the human inference gate.

### P9 — Make or decline the Study 001 capability inference

A named human reviews the observations, card, profile scope, rivals, and missing
evidence, then records a bounded inference, a narrower inference, or a refusal
to infer. Preserve that record as content-addressed evidence distinct from
technical verification and final v0 acceptance.

### P10 — Derive a governed training-candidate set

Derive candidate examples only from evidence-valid observations with complete
trial, outcome, label or reward, verifier, and required human-disposition
lineage. Exclude provider and infrastructure failures, compromised instruments,
ambiguous judgments, and leaked cases. Keep task families and scenario
templates together for split purposes. The output is a candidate manifest, not
an eligibility decision, export, or training corpus.

### P11 — Select training eligibility and decide whether to authorize one export

A named human selects exact example identities under privacy, license, quality,
provenance, and family-safe split rules, or records that no example is eligible.
When examples are selected, the owner separately authorizes the destination,
maximum size, retention, expiry, purge, and stop conditions. The record excludes
model calls, fine-tuning, deployment, public release, and later exports. A
no-eligible-example decision leaves P12 unavailable and the v0 export criterion
unmet.

### P12 — Materialize the authorized training-eligible export

Run only when P11 authorizes an export. Export exactly the authorized examples
to an immutable dataset bundle and frozen manifest with complete lineage. Prove
that unauthorized examples, mutable Postgres state, and changed locators cannot
influence the output. This checkpoint performs no model execution or training.

### P13 — Independently verify the integrated CAPLAB v0 slice

An executor independent of implementation runs a clean replay from Study 001
inputs through registration, result, and profile. When P11 authorized an
export, the replay includes P12 and its dataset bundle. When P11 selected no
eligible examples, verify that no export occurred and record the required v0
criterion as unmet. Verify database and object recovery; valid, invalid,
missing, tampered, and ambiguous fixtures; claim-scope refusal; and family-safe
split enforcement. Record residual failures. Verification does not claim
acceptance.

### P14 — Accept or reject CAPLAB v0

The repository owner reviews the independent verification record, human
capability inference, export decision, residual risks, and stop conditions, then
records acceptance, conditional acceptance, revision, or rejection. Acceptance
is available only when every v0 criterion, including the authorized export,
passed independent verification. Otherwise the owner records revision or
rejection. No disposition grants preference-study, model-call, Striatum-routing,
fine-tuning, deployment, or subsequent-export authority.

## Verification plan

Verification layers remain distinct:

1. **Document and manifest structure:** schema checks, stable identities,
   reciprocal links, and reproducible hashes.
2. **Hermetic behavior:** model-free unit, component, property, and fixture
   tests for valid, invalid, missing, tampered, ambiguous, duplicate, and
   interrupted cases.
3. **Local-store integration:** explicitly invoked tests against the dedicated
   Postgres and S3 namespaces, including transaction boundaries, object
   immutability, backup, restore, reconciliation, and purge.
4. **Historical reconstruction:** byte and hash verification from the selected
   Study 001 inputs through the recomputed normalized result.
5. **Claim and split enforcement:** independent tests that unsupported claims
   remain unavailable and task-family or scenario-lineage leakage is refused.
6. **Human gates:** named capability inference, eligibility decision, and final
   acceptance remain human records, not test output.

Every executable checkpoint records its command, environment, version, result,
and retained evidence locator. Passing one layer cannot promote the assertion
owned by another.

## Risks and mitigations

| Failure mode | Early signal | Mitigation | Residual owner |
|---|---|---|---|
| No historical experiment is admissible as Study 001 | Candidate lacks raw inputs or verified manifest | Record no selection; repair preservation under separate authority or reopen the specification and ADR before substituting the v0 slice | repository owner |
| Mutable metadata becomes inference authority | Result depends on an unsealed row or locator | Require frozen manifests and byte verification; fail closed on disagreement | implementation owner, then independent verifier |
| Registration rewrites history or retention | Imported timestamp, outcome, rule, or byte differs | Compare before write; stop and quarantine any mismatch | Study 001 decision owner |
| Store assumptions are wrong | Isolation, backup, recovery, or purge proof fails | Stop P4 and reopen ADR 0007 or its authorization with the exact failed condition | repository owner and system owner |
| Human assertions are synthesized | Automation populates a human identity or verdict | Require authenticated human record and reject inferred ownership | assertion owner |
| Profile overgeneralizes | One-study evidence produces cross-task or placement output | Mechanically render broader claims unavailable | capability-card owner |
| Training leakage or invalid rows enter export | Scenario relatives cross splits or lineage is incomplete | Family-safe grouping and fail-closed eligibility checks | eligibility decision owner |
| Plane becomes a second authority | Tracker text differs from Git or retained evidence | Treat Plane as regenerable projection; link authoritative records | repository maintainers |

## Stop, escalation, and rollback conditions

Stop before any material mutation when the exact authorization record, target
namespace, retention rule, rollback path, or acceptance owner is absent. Stop
on identity or hash drift, unverifiable preservation, unexpected historical
mutation, credential exposure, public-projection redaction failure, or a failed
store integrity or recovery gate. Stop before paid or local model inference,
fine-tuning, Striatum changes, public evidence publication, or a second export;
none is part of v0 authorization.

Rollback returns to the last independently verified checkpoint. Remove only
CAPLAB-created projections or state named by the authorization and retention
decision. Preserve source study evidence, decision records, manifests, failure
records, and enough audit evidence to verify rollback. Prefer safe forward when
deletion authority or retention semantics are uncertain.

## Deferred work

- blinded Fable-versus-GPT preference measurement;
- additional task families and cross-task capability promotion;
- Striatum pass profiles, lane-fit reports, and scheduler-policy decisions;
- actual fine-tuning, held-out checkpoint evaluation, and deployment;
- public collaboration beyond sanitized Plane summaries; and
- daemon, UI, API, global ranking, or multi-backend support.

These become eligible only through new plans and evidence appropriate to their
claims. They are not standing work authorized by this queue.

## Execution, verification, and acceptance records

P4 has separate execution and PASS verification records. P5 preserves its
stopped and corrective failure records plus the ADR 0013 correction PASS and
ADR 0014 exact-purge PASS. CAPLAB-23 is complete and the P6 predecessor gate is
open. No Study 001 registration,
recomputation, capability inference, export, integrated verification, or v0
acceptance record exists.

Planning projection: Plane project `CAPLAB`, with active replacement work items
CAPLAB-18 through CAPLAB-30 and CAPLAB-33 through
CAPLAB-34. CAPLAB-2 through CAPLAB-17 are retained as cancelled history from
the superseded planning interpretation. CAPLAB-31 and CAPLAB-32 are retained as
cancelled correction history after a conditional dependency was repaired by
replacement because the Plane connector could not remove the original relation.

## Status log

- **2026-07-15 — proposed.** The repository owner instructed the agent to
  create the implementation plan and populate Plane. The plan projects the
  selected CAPLAB v0 boundary and reconciles the stale queue. Implementation
  remains unauthorized.
- **2026-07-15 — final-review correction.** Clarified that only plan preparation
  and tracker projection were authorized, changed the capability-card gate to
  selection, narrowed the invalid-attempt claim, and added stopped branches for
  no admissible study and no eligible export. Plane items CAPLAB-31 and
  CAPLAB-32 were cancelled and replaced by CAPLAB-33 and CAPLAB-34 because the
  connector could not remove the superseded dependency relation.
- **2026-07-15 — P0 selected.** The repository owner selected the exact C9 Luna
  B-versus-V confirmation as Study 001 in ADR 0004. Selection does not admit or
  register its evidence.
- **2026-07-15 — P1 selected.** The repository owner selected CAPLAB v0 evidence
  governance in ADR 0005. The plan remains proposed pending P2 and P3; no
  implementation or datastore mutation is authorized.
- **2026-07-15 — P2 selected.** The repository owner selected the exact version
  0.1.0 Study 001 capability card in ADR 0006. The plan remains proposed pending
  P3; no implementation, evidence admission, capability inference, model call,
  export, training, verification, or acceptance is authorized.
- **2026-07-15 — P3 proposal prepared.** The repository owner authorized
  CAPLAB-21 discovery and proposal preparation. Proposed ADR 0007 names the
  CLI runtime and an exact P4 synthetic campaign. The plan remains proposed and
  unauthorized until the owner selects, revises, or declines that proposal and
  separately exercises the bounded P4 authority it contains.
- **2026-07-15 — P3 selected and P4 authorized.** The repository owner selected
  ADR 0007 at books commit
  `cdbb5120d1d450763fca2a8aca172f6308413440`, authorized CAPLAB-22/P4 through
  `2026-07-22T23:59:59Z`, and delegated CAPLAB decision authority. ADR 0008
  records the owner's correction that CAPLAB is a standalone repository. No P5
  or later effect is authorized.
- **2026-07-15 — P4 executed and independently verified.** One model-free
  synthetic operation completed registration, idempotent replay, changed-input
  refusal, retrieval, reconciliation, cleanup-plan generation, quarantine, and
  access disablement. The separate `caplab22_verifier` recorded PASS with a
  bounded preservation gap: the three numeric status-2 values were asserted by
  the live shell but not retained as direct numeric receipts. No P5 action or
  CAPLAB acceptance occurred.
- **2026-07-16 — P5 proposal prepared.** The repository owner instructed the
  agent to handle CAPLAB-23, CAPLAB-24, and CAPLAB-25 in dependency order.
  CAPLAB-23 moved into investigation and proposal preparation. The failure-mode
  audit and proposed ADR 0009 name a P5-only synthetic campaign, preserve P4 as
  a control, and require exact owner selection before live fault, restore,
  deletion, or purge effects. P6 and P7 remain gated and unauthorized.
- **2026-07-16 — P5 selected and authorized.** The repository owner explicitly
  authorized ADR 0009 as written. Campaign
  `caplab-p5-recovery-2026-07-16` may implement and execute only its named
  P5-only fault, recovery, backup, isolated restore, orphan, and guarded-purge
  effects through `2026-07-23T23:59:59Z`. P4 remains an unchanged control.
  Independent restore and purge verification is required before P5 can pass;
  P6 and P7 remain unauthorized.
- **2026-07-16 — P5 failed and received corrective authority.** The first
  campaign stopped after durable registration because validation conflated
  per-migration applied-by commits with the registration runtime commit. A
  fresh verifier returned FAIL. The executor disabled access and preserved the
  exact registration and good bytes in quarantine. After receiving that result
  and the requirement for a newly frozen campaign, the repository owner
  instructed the executor to proceed. ADR 0010 authorizes the narrow source
  correction and remaining ADR 0009 sequence under a separate evidence root.
  P6 and P7 remain unauthorized.
- **2026-07-17 — P5 restore blocker removed and ordered P5/P6 authority
  recorded.** ADR 0013's isolated restore correction passed independently and
  removed its isolated target without touching the live cluster. The owner
  then explicitly authorized the restated boundary. ADR 0014 reopens only the
  exact frozen P5 purge and authorizes restricted P6 admission of the
  manifest-bound Study 001 evidence after a fresh independent P5 PASS. P7,
  recomputation, model calls, inference, export, training, and acceptance
  remain unauthorized.
- **2026-07-17 — P5 frozen source-worktree correction.** ADR 0014's first
  read-only preflight refused the advancing shared CAPLAB checkout because it
  no longer equaled the older frozen executor commit. ADR 0015 selects a
  dedicated clean linked worktree at that exact commit and preserves the
  original equality and cleanliness gates. No P5 data or host mutation
  preceded this correction.
- **2026-07-17 — P5 completed.** The exact dependency rehearsal refused with
  SQLSTATE `P5004`; the matching release cleared it; both exact P5 byte copies
  were staged and removed; the guarded transaction removed only the P5
  application closure and retained its tombstone; and access was disabled.
  Fresh independent verification returned PASS. CAPLAB-23 is complete and ADR
  0014 Stage B/P6 is open. P7 and all later authority remain unavailable.
- **2026-07-17 — P6 completed.** The restricted admission froze manifest
  `d2d4f821146c3f39e6726133c383807ec9f6051834e74fbd3a5f33aae8ef148e`
  with 684 records, 325 unique content identities, and exact 20/20/20 links.
  Fresh independent verification returned PASS and all temporary access was
  disabled. CAPLAB-24 is complete; this result did not authorize P7.
- **2026-07-18 — backlog-drain Stage A authorized.** The repository owner
  instructed the agent to work the CAPLAB backlog and clarified that the goal
  is to drain it. ADR 0016 authorizes model-free implementation preparation for
  CAPLAB-25/P7, CAPLAB-26/P8, and CAPLAB-28/P10 through
  `2026-07-25T23:59:59Z`. Live registered-evidence access still requires a
  separate exact continuation. Human inference, eligibility, export,
  independent verification, model calls, training, and acceptance remain
  separately gated.
- **2026-07-18 — P8 and P10 Stage A implemented.** The P8 service binds the
  selected card and P7 observation into a proposal with human inference and
  broader claims unavailable. The P10 service binds sealed trial, outcome,
  verifier, label, and human-disposition lineage into family-grouped candidates
  whose eligibility remains unavailable. This is implementation preparation,
  not execution of either checkpoint; both still depend on the pending live P7
  continuation.
- **2026-07-18 — exact P7 live continuation approved.** The repository owner
  instructed the agent to `approve the exact P7 live continuation`. ADR 0017
  authorizes the proposal's frozen CAPLAB and Proximal commits, one temporary
  read-only reader identity, two byte-identical recomputations, mandatory
  aggregate revocation, preservation checks, and exact evidence root through
  `2026-07-25T23:59:59Z`. All later human and acceptance gates remain separate.
- **2026-07-18 — exact P7 attempt stopped.** The installed controller rejected
  Garage 2.3 bucket identity metadata during ready verification before either
  recomputation. Aggregate disablement removed the key and credential, restored
  `NOLOGIN`, and left zero sessions or processes; whole-schema, cluster, P4,
  P6, Garage-summary, and `/nvr` controls remained unchanged. A narrow tested
  controller repair is pushed at Proximal
  `8c45e62a22cf5c7e566df2d4510b49742f39b6ac`, and a new exact retry proposal
  awaits the owner's decision. ADR 0017 does not authorize that retry.
- **2026-07-19 — exact P7 live retry approved.** The repository owner replied
  `approved` to the exact retry proposal. ADR 0018 authorizes one retry using
  pushed Proximal commit
  `8c45e62a22cf5c7e566df2d4510b49742f39b6ac`, preserved failed-attempt
  evidence, the unchanged frozen CAPLAB source and P6 admission, two exact
  recomputations, mandatory aggregate disablement, and fresh preservation
  evidence through `2026-07-25T23:59:59Z`. Later human and acceptance gates
  remain separate.
