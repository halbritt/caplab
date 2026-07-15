---
id: adr-0005
artifact_type: architecture-decision-record
title: Agent Capability Lab v0 evidence governance
status: decided
decision_owner: repository-owner
decision_authority: repository-ownership
created: 2026-07-15
decided_at: 2026-07-15
supersedes: []
superseded_by: null
affected_contexts:
  - agent-capability-lab
  - caplab-evidence-governance
related_specs:
  - spec-agent-capability-lab
related_plans:
  - plan-agent-capability-lab-v0
related_receipts: []
---

# Agent Capability Lab v0 evidence governance

Status interpretation: the repository owner selected CAPLAB v0's evidence
governance on 2026-07-15. This decision fixes policy, systems-of-record roles,
recovery targets, retention, access, integrity, purge, disclosure, and Study
001 admission gates. It does not create a database, role, bucket, key, object,
backup, migration, retention effect, or implementation authorization.

## Decision question and scope

What evidence topology and governance rules should CAPLAB v0 use for Study 001
metadata, raw evidence, frozen research records, coordination projections,
backup, recovery, access, retention, purge, and admission?

This decision governs CAPLAB-owned v0 evidence. It does not select runtime
interfaces or adapters, physical names, schemas, migrations, credentials,
provider calls, a capability card, evidence eligibility, export, training,
verification, or final acceptance.

## Observations and evidence

**Observation:** ADR 0002 assigns distinct roles to local S3-compatible object
storage, system PostgreSQL, Git, and Plane, but deliberately leaves exact
governance and implementation unresolved. The CAPLAB plan makes governance P1
and requires a later P3 runtime and authorization decision. **Evidence:**
[`adr-0002`](adr-0002-agent-capability-lab-v0.md) and
[`plan-agent-capability-lab-v0`](../product/plans/plan-agent-capability-lab-v0.md).

**Observation:** A read-only host review found an existing PostgreSQL 17
cluster with local pgBackRest and encrypted off-site restic coverage, and an
existing S3-compatible Garage service whose v0 use would share a host,
administration, capacity, and recovery failure domain with other local
services. **Evidence:** runtime dossier SHA-256
`3fb84795d8816696c35ac9747782eba4bffdca9bd26b9b60a4621bc8f7ef8bca`.
This is a point-in-time observation, not a current health or recovery proof.

**Observation:** A bounded synthetic Garage qualification stopped before any
mutation because the review did not establish an already governed,
credential-safe S3 client path. No bucket, key, object, backup path, database,
credential, or service configuration was created or changed. Backup, restore,
idempotent replay, overwrite refusal, reconciliation, and purge were not
verified. **Evidence:** Plane comment external ID
`caplab-19-garage-qualification-blocked-2026-07-15` and qualification-report
SHA-256
`dff02698131cff0d01b9a1a72c5aa5d76fbbf8970546d22e3a7786f3f613dd3e`.

**Observation:** The repository owner accepted the governance recommendations
one decision at a time on 2026-07-15. CAPLAB-19's internal comments record the
selected PostgreSQL, backup, Garage, local-only recovery, retention, recovery,
access, integrity, accountability, audit, purge, disclosure, and Study 001
admission rules. Plane is a projection; this ADR is their durable record.

## Inferences, rivals, assumptions, and uncertainty

**Inference:** Using the existing PostgreSQL and Garage services with dedicated
CAPLAB namespaces is proportionate for v0 if registration fails closed until
the independent local copy, reconciliation, role isolation, backup, and restore
gates are demonstrated.

**Inference:** Defining evidence as registered only after both authoritative
Garage storage and a verified independent `/nvr` copy converts an otherwise
ambiguous upload into an explicit durability boundary. It does not solve total
host loss.

Rivals and uncertainty:

- SQLite would reduce service integration but would introduce a separate
  operational database and backup path despite an existing backed-up system
  PostgreSQL service;
- a filesystem-only evidence store would reduce adapter work but would not
  exercise the selected S3 evidence contract;
- off-host raw-evidence backup would improve host-loss recovery but would widen
  the v0 privacy and data-residency boundary;
- shared Garage remains single-host local infrastructure and is not WORM or
  Object Lock; application checks must earn the overwrite-refusal claim; and
- the selected recovery objectives remain targets until restore drills verify
  them under the actual configuration.

## Recommendation and alternatives

**Recommendation:** Use dedicated least-privileged CAPLAB namespaces in the
existing PostgreSQL and Garage services, keep sensitive raw evidence on-host,
require a verified independent `/nvr` copy before registration, and enforce the
retention, access, integrity, audit, purge, and disclosure rules below.

Alternatives were SQLite, filesystem-only evidence, off-host raw evidence, a
new service deployment, or no v0 implementation. The first four widen or alter
the selected product boundary. No implementation remains the correct response
until the later runtime and synthetic recovery gates are authorized and pass.

## Decision, owner, authority, and rationale

**Decision:** The repository owner selects the following CAPLAB v0 evidence
governance.

**Owner and authority:** repository owner under repository ownership. The owner
selected each recommendation on 2026-07-15 during the CAPLAB-19 governance
interview and authorized durable recording and implementation planning only.

**Rationale:** this topology reuses backed-up local services while keeping raw
evidence local and every durability, access, claim, and destructive transition
explicit. It makes failure observable and blocks dependent work instead of
manufacturing a stronger storage or recovery guarantee than the host can
currently prove.

### Systems of record and storage boundary

| Surface | Selected role and boundary |
|---|---|
| PostgreSQL | One dedicated `caplab` database in the existing PostgreSQL 17 cluster with least-privileged roles. PostgreSQL is authoritative for operational metadata and audit transitions, not raw prompts, trajectories, workspaces, credentials, or model output. The owner accepts the shared superuser and outage boundary for v0. |
| PostgreSQL backups | CAPLAB metadata may enter the existing local unencrypted pgBackRest repository and encrypted off-site restic repository. Live-row purge does not imply immediate physical-backup deletion; backup copies expire under their governing schedules. |
| Garage | One dedicated bucket with separate expiring least-privileged keys and a 1 GiB initial quota. Garage is authoritative for registered evidence bytes. Object keys are content-addressed; the application refuses non-identical replacement. Garage is not represented as WORM or Object Lock. The owner accepts its shared process, host, administration, capacity, and recovery failure domain for v0. |
| Independent raw-evidence copy | A verified application-level copy under `/nvr`, separate from the Garage object path. Raw prompts, trajectories, workspaces, logs, and model output remain on-host. This boundary deliberately provides no total-host-loss recovery. |
| Git | Standalone CAPLAB Git is authoritative for CAPLAB governing decisions, code and derivation identities, admitted manifests, approved aggregate results, content hashes, verification records, and non-sensitive purge tombstones. Before P6, `halbritt/books` Git remains the source authority for the selected historical research identities and records. Neither Git repository holds sensitive raw evidence. |
| Plane | Regenerable coordination projection only. It is never evidence, decision, authorization, purge, verification, or acceptance authority. |

### Registration and recovery objectives

Evidence is registered only after both the authoritative Garage object and its
byte-verified independent `/nvr` copy exist and reconciliation succeeds. If the
copy is absent or any required audit or recovery state is stale or failing, the
evidence remains unregistered and dependent work stops.

| State | Selected objective |
|---|---|
| PostgreSQL operational metadata | Target RPO no greater than 24 hours; target RTO no greater than one working day. |
| Registered evidence under Garage-object loss | Target RPO zero; target RTO no greater than one working day, using the verified independent local copy. |
| Total-host loss | Outside the v0 recovery guarantee; the owner explicitly accepts this residual risk. |

These are policy targets, not verified capabilities, until the separately
authorized restore drills pass.

### Retention and expiry

| Data class | Selected retention rule |
|---|---|
| Frozen inputs, raw attempts, verifier observations, and human dispositions | Retain while any registered result, capability claim, audit, training candidate, or dataset depends on them. After the final dependency ends, sensitive raw evidence receives a 12-month tail and then requires explicit renewal or an authorized purge. Review retained sensitive evidence annually. |
| Non-sensitive Git decisions, manifests, hashes, approved aggregates, and purge tombstones | Retain indefinitely. |
| Incidental operational logs | Retain 90 days unless promoted into registered evidence. |
| Privacy-, licensing-, or credential-affected material | May require earlier quarantine or purge under an explicit disposition. Credential-bearing material is quarantined and the credential is rotated. |
| Backup copies | Age out under their independently governed schedules only while remaining copies continue to satisfy the selected recovery objectives. Backup expiry is copy lifecycle, not live-evidence purge authorization. |

### Access, credentials, and accountability

| Role | Selected authority |
|---|---|
| Repository owner | Owns governance, exceptions, authorization, and acceptance. |
| Named host-system delegate | May perform database, role, bucket, key, backup, restore, rotation, and purge effects only under item-specific authorization. |
| Writer | May add a content-addressed object and matching metadata; may not overwrite or purge. |
| Recomputation reader | Read-only access to registered evidence required by one frozen analysis. |
| Independent verifier | Read-only evidence plus secret-free integrity and reconciliation outputs; cannot accept results. |
| Adjudicator | Only the evidence and private fields required for the named human judgment. |
| Export operator | No role exists until a separate export authorization creates and scopes one. |

Credentials remain outside Git and Plane, absent from command arguments and
logs, scoped to one role, and expired or rotated at the end of the v0 campaign.
Service accounts are execution identities, not decision owners.

Every authorized work item names its executor and verifier for backup, restore,
integrity review, credential rotation, redaction, or purge. One delegate may
perform several operational roles but may not verify their own restore or
purge. Purge always requires explicit repository-owner authorization and
separate verification. An unassigned required role blocks the operation.
Assignments are campaign-specific rather than permanent privileges.

### Integrity, reconciliation, and audit

1. Object identity is the byte-level SHA-256 and a content-addressed key.
2. A repeated write succeeds only when the existing bytes are identical.
3. A non-identical collision is refused and quarantined.
4. PostgreSQL metadata and locator, Garage bytes, Git manifest,
   derivation-code identity, and result hash must agree before registration,
   recomputation, inference, or export.
5. Reconcile at ingest, before every derived result, and after restoration.
6. A discrepancy blocks dependent operations for named review. Historical
   evidence is never repaired by rewriting it.
7. Check backup health automatically each day.
8. Run full manifest reconciliation weekly during active campaigns and monthly
   while idle.
9. Run model-free PostgreSQL and Garage restore drills quarterly and after
   material storage changes.
10. Review retained sensitive evidence annually.

### Purge semantics

- Every purge requires separate repository-owner authorization naming exact
  evidence identities.
- The authorized executor deletes only the named live PostgreSQL rows and
  Garage objects; a different verifier confirms the outcome.
- Git may retain a non-sensitive decision, content hash, tombstone, and audit
  fact.
- Plane's projection is corrected or removed but never acts as purge authority.
- Physical backup copies expire under their own schedules and are not reported
  as immediately removed by a live purge.
- When deletion conflicts with a scientific, audit, training, or dataset
  dependency, the owner must choose restricted retention or withdrawal of the
  dependent claim or dataset before purge.

### Plane and public-disclosure boundary

Plane may contain only:

- work-item key;
- non-sensitive title and status;
- Git decision link;
- commit, packet, manifest, or content hash;
- aggregate result already approved for publication; and
- non-sensitive blocker category.

Plane must not contain raw prompts, trajectories, workspace contents, private
adjudication text, database rows, bucket or object locators, credentials,
presigned URLs, internal host paths, or unapproved provider metadata. A named
redaction reviewer must approve any projection to a publicly collaborative
Plane surface.

### Study 001 admission gate

ADR 0004 selects C9 as the historical Study 001 identity; selection is not
admission. Before any evidence import, a read-only inventory must assign every
object an explicit privacy, licensing, and credential disposition:

- restricted admission;
- a separately identified redacted derivative;
- quarantine; or
- exclusion.

Source evidence is never silently altered. Every derivative retains provenance
and receives its own identity and hash. Credential-bearing objects are
quarantined and the credential is rotated. Import requires separate authority
and remains unavailable until storage, restore, role-isolation, and
reconciliation controls are verified.

## Authorization and execution scope

The owner's decision authorizes this ADR, the decision index, the CAPLAB plan
updates, and sanitized Plane links. It does not authorize database, role,
schema, migration, bucket, key, object, quota, backup, adapter, namespace,
retention, evidence import, purge, model call, publication, export, training,
verification, or acceptance effects.

CAPLAB-21 must separately select the credential-safe S3 adapter, physical
namespaces, schema, migration, secret handling, rollback, expiry, verification,
and exact authorized work items. CAPLAB-22 and CAPLAB-23 own the synthetic
round-trip, failure, backup, restore, reconciliation, and purge proofs. No
historical evidence may move during those synthetic gates.

## Consequences and preservation boundaries

- PostgreSQL and Garage remain separate authorities for operational metadata
  and evidence bytes; neither silently becomes research-decision authority.
- The independent `/nvr` copy is part of registration, not an optional later
  backup.
- Raw evidence remains on-host, accepting total-host-loss risk in exchange for
  a narrow v0 privacy boundary.
- Recovery, audits, retention review, role management, and purge create ongoing
  operational work.
- Historical experiment bytes, results, timestamps, and claim boundaries remain
  unchanged until a separately authorized admission or purge operation.
- No runtime implementation is earned merely by selecting existing services.

## Verification and fitness criteria

The decision record is internally conformant when:

- every accepted owner choice appears here without unresolved `Proposed`
  language;
- ADRs 0002, 0004, and 0005, the CAPLAB specification, and the CAPLAB plan agree
  on authority and checkpoint boundaries;
- no credential, presigned URL, existing service alias, raw evidence, or
  sensitive locator is included;
- the stopped synthetic qualification remains recorded as unexecuted rather
  than passed or failed; and
- repository link, documentation, doctrine, and general checks pass.

Runtime fitness remains pending until separately authorized checks demonstrate:

- a reviewed credential-safe S3 client or adapter;
- synthetic local backup, source-loss simulation, restore, hash verification,
  idempotent replay, collision refusal, and rollback;
- current PostgreSQL local and off-site backup health;
- a model-free PostgreSQL restore drill;
- end-to-end PostgreSQL/Garage/Git reconciliation fixtures;
- purge and backup-expiry fixtures; and
- secret handling and role isolation.

Passing those checks verifies execution against this decision. It does not
authorize historical evidence import or constitute CAPLAB acceptance.

## Acceptance owner and outcome

The repository owner is the acceptance owner. Governance is selected; runtime
fitness and CAPLAB v0 acceptance remain pending. Final v0 acceptance remains
the independent-verification checkpoint followed by the repository-owner
acceptance checkpoint.

## Reopening and supersession conditions

Reopen this decision if the existing services cannot meet the selected
isolation or recovery targets, the 1 GiB quota is disproportionate, the
local-only privacy boundary becomes unacceptable, total-host-loss recovery
becomes required, backup expiry cannot preserve the recovery objective,
artifact-specific privacy or licensing rejects Study 001, or operating both
stores proves more costly than a narrower architecture.

Changed implementation details that remain inside these boundaries belong to
CAPLAB-21. A change to systems of record, residency, retention, recovery,
authority, or disclosure requires superseding this ADR.

## Doctrine record and remaining obligations

This recording and work-decomposition question used evidence-backed doctrine
packet `pkt-9a6c897c79f79cb6`, content SHA-256
`9a6c897c79f79cb68e9429d20e6a99adf22272847194b77d4f970317f8e08605`,
corpus `corpus-2026-07-12-d2ea7b94a1ce`, doctrine
`doctrine-164e6a9e863b1ae4`, and retriever
`retriever-784b2cbe112a7b79`. Its authority ceiling was `recommend`; explicit
owner decisions and repository contracts take precedence.

The packet satisfied 32 of 66 discovered obligations. All 34 remaining
obligations are nonmaterial to this documentation-only execution but are not
discarded:

| Later gate | Unmet requirements preserved for that gate |
|---|---|
| CAPLAB-21 runtime and authorization decision | affected behavior and state; application scenario and forbidden observations; datastore consistency and isolation guarantees; datastore guarantee; forbidden observation or invariant; all mutation/creation paths and authority; actual caller needs; caller needs and decision owner; decision owner and volatility; leaked knowledge or coordinated change; material cost/failure semantics callers require; representative change scenario; expected future change from accepted plans; intervention cost and uncertainty; preservation boundary and semantic authority |
| CAPLAB-22 synthetic round-trip | atomic deduplication or uniqueness enforcement; atomic durable effect boundary; external-effect and retry behavior; identity generation and propagation path; retention period and collision semantics; stable intent identity; derivation, rebuild, reconciliation, and consumer behavior during lag; explicit application invariants |
| CAPLAB-23 recovery and failure proof | application invariants and anomaly analysis; concurrency and fault tests at the relied-upon boundary; datastore guarantee and configuration; vendor or protocol guarantee for the exact configuration; preservation matrix and consumers; checkpoint verification; `proc-establish-preservation-boundaries` |
| Already resolved for this decision or inapplicable to recording it | alternatives including no change where viable; measured read benefit plus write, storage, freshness, and consistency costs; actual current cost/risk or absence within a stated interval; `proc-decide-leave-code-alone` |

If work advances into those gates, their listed requirements become material
and must be satisfied with current configuration and runtime evidence rather
than inherited from this ADR.

## Related artifacts

- Product boundary: [`adr-0002`](adr-0002-agent-capability-lab-v0.md)
- Study selection: [`adr-0004`](adr-0004-caplab-study-001-selection.md)
- Product specification:
  [`spec-agent-capability-lab`](../product/specs/spec-agent-capability-lab.md)
- Implementation plan:
  [`plan-agent-capability-lab-v0`](../product/plans/plan-agent-capability-lab-v0.md)
- Planning projection: local Plane work item `CAPLAB-19`

## Status history

- `2026-07-15` — `decided` — repository owner selected the CAPLAB v0 evidence
  governance; implementation and evidence admission remain separately gated.
