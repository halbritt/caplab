---
id: plan-agent-capability-lab-v0
artifact_type: implementation-plan
title: Agent Capability Lab v0
status: proposed
owner: repository-maintainers
created: 2026-07-15
updated: 2026-07-15
supersedes: []
superseded_by: null
source_artifacts:
  - spec-agent-capability-lab
source_decision: adr-0002
baseline: 97380767e4517d991b3118c738922ba43f2448af
authorization_record: null
authorized_scope: []
change_types:
  - change-feature-implementation
  - change-architectural-restructuring
  - change-migration
  - change-operational-hardening
---

# Agent Capability Lab v0

Status interpretation: this plan projects the selected CAPLAB v0 contract into
dependency-ordered work. The exact Study 001 experiment and v0 evidence
governance are selected in ADRs 0004 and 0005. The Study 001 capability card is
selected in ADR 0006. The plan remains proposed and is not ready for
implementation: the runtime shape, exact physical namespaces and adapters, and
live Postgres and object-store fitness remain unresolved. The owner's
instructions on 2026-07-15 authorized preparation of this plan, its governing
decision records, the capability-card selection, and matching Plane projections
only. They did not authorize implementation, datastore changes, evidence
retention or import, model calls, dataset export, training, verification, or
acceptance.

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

**Observation:** baseline
`97380767e4517d991b3118c738922ba43f2448af` contains the decided CAPLAB
specification and ADR, but no CAPLAB implementation plan. Both source records
have empty `related_plans` lists. **Evidence:** Git status, product index, the
source records, and the plan directory inspected on 2026-07-15.

**Observation:** On 2026-07-15 the repository owner selected the exact C9 Luna
B-versus-V confirmation as Study 001 and selected the v0 evidence-governance
boundary. ADRs 0004 and 0005 record those decisions. Neither decision authorizes
implementation or evidence admission.

**Observation:** `PYTHONDONTWRITEBYTECODE=1 make doctrine-check` passed at the
baseline. **Limit:** this verifies the doctrine and generated documentation
surfaces; it is not a CAPLAB runtime or storage check.

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
Read-only inspection may include the historical checkout-retries artifacts,
system Postgres configuration, local S3-compatible service, and backup and
restore surfaces.

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
  operational metadata, Git as authority for frozen research and governing
  records, and Plane as a regenerable projection;
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
| P4 | CAPLAB-22 | Round-trip one synthetic sealed attempt | P3 | Verified model-free Postgres/S3/Git path |
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

Prefer a CLI-first batch path unless current evidence earns a service. Record
the interface, module boundaries, Postgres schema and role, S3 namespace,
dependency changes, migrations, retention, rollback, verification, expiry,
stop conditions, and exact work-item and path scope. Promote this plan to
`ready` only after the decision is complete; promote it to `authorized` only
when the owner separately exercises bounded implementation authority.

### P4 — Round-trip one synthetic sealed attempt

Using non-sensitive fixtures, carry layered identities and one sealed
assignment through immutable object storage, transactional metadata, retrieval,
and hash verification. Enforce stable operation identities at durable effect
boundaries so retries are idempotent and overwrite or identity substitution is
refused. Keep default repository checks hermetic; use a separately invoked local
integration gate for the real stores.

Rollback removes only authorized CAPLAB-created synthetic state and preserves
the evidence needed to verify what was removed.

### P5 — Fail closed and recover the synthetic attempt

Exercise missing and altered objects, locator drift, duplicate submission,
interrupted transactions, manifest mismatch, invalid and ambiguous attempts,
backup restore, orphan detection, and authorized purge. Invalid attempts remain
auditable as invalid-attempt observations but cannot become subject-behavior
outcomes or inference-bearing trial observations. Recovery must reproduce
content identities and the selected operational state.

### P6 — Register Study 001 without rewriting history

Ingest only inputs bound by the P0 decision and verified preservation manifest.
Link layered identities, assignments, attempts, outcome records, object
locators, and one frozen registration manifest end to end. Preserve historical
content and timestamps. Missing or mismatched evidence stops registration; no
model call occurs.

### P7 — Recompute the frozen Study 001 result

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
| Store assumptions are wrong | Isolation, backup, recovery, or purge proof fails | Keep plan proposed; reopen runtime shape before authorization | repository owner and system owner |
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

No CAPLAB implementation, migration, runtime verification, inference, export,
or v0 acceptance record exists yet. The selected Study 001 capability card and
its decision are linked at P2; add later execution and assertion records only
after the corresponding owner records each distinct event.

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
