---
id: adr-0016
artifact_type: architecture-decision-record
title: CAPLAB backlog-drain AFK implementation campaign
status: decided
decision_owner: repository-owner
decision_authority: repository-ownership-and-direct-instruction
created: 2026-07-18
decided_at: 2026-07-18
supersedes: []
superseded_by: null
affected_contexts:
  - agent-capability-lab
  - caplab-study-001
related_specs:
  - spec-agent-capability-lab
related_plans:
  - plan-agent-capability-lab-v0
related_receipts: []
---

# CAPLAB backlog-drain AFK implementation campaign

Status interpretation: the repository owner instructed the agent on 2026-07-18
to work the live CAPLAB backlog and clarified that the goal is to drain it.
This record authorizes the model-free implementation and repository preparation
needed for CAPLAB-25/P7, CAPLAB-26/P8, and CAPLAB-28/P10. It does not delegate
human-owned inference, training eligibility, independent verification, export
authorization, or CAPLAB acceptance.

## Decision question and scope

Which backlog work may proceed without silently promoting registered evidence
into a human assertion or granting live data access before an exact executor is
frozen?

The immediate dependency front is CAPLAB-25/P7. CAPLAB-26/P8 and CAPLAB-28/P10
are deterministic consumers of its content-addressed output and may be
implemented in the same model-free campaign. CAPLAB-27/P9, CAPLAB-29/P11, and
CAPLAB-34/P14 remain human-owned. CAPLAB-30/P12 remains unavailable until P11
selects exact eligible examples and separately authorizes one export.
CAPLAB-33/P13 remains a later independent verification campaign.

## Observations and evidence

**Observation:** CAPLAB-24/P6 received an independent PASS and froze one Study
001 registration with manifest SHA-256
`d2d4f821146c3f39e6726133c383807ec9f6051834e74fbd3a5f33aae8ef148e`,
684 restricted evidence records, 325 unique content identities, and exact
20/20/20 assignment-attempt-outcome links. **Evidence:**
[`caplab-p6-admission-verification-2026-07-17`](../records/caplab-p6-admission-verification-2026-07-17.md)
and read-only PostgreSQL inspection on 2026-07-18.

**Observation:** the selected result CSV is registered at content SHA-256
`af8d64fde0b7a93773dfc2ac36651d61ee7259095eef792fa7515810a57a2374`.
Its PostgreSQL record identifies both the Garage object key and independent
`/nvr` copy key. Writer, reader, and verifier database roles are currently
`NOLOGIN`; no Garage credential file remains for those identities.

**Observation:** the P7 contract requires the eight paired mutant outcomes to
be complete, computes `RD`, `T_obs`, and all 256 within-block sign assignments,
uses inclusive one- and two-sided comparisons without an add-one correction,
and makes the analysis undefined rather than imputing when any mutant outcome
is absent. **Evidence:** the registered preregistration bytes selected by ADR
0004 and the P7 checkpoint in the accepted plan.

**Observation:** the repository owner directly instructed the agent to work
the backlog and then stated that the goal is to drain it in the active CAPLAB
Plane context on 2026-07-18.

## Inference, rivals, and recommendation

**Inference:** the smallest faithful P7 implementation is a read-only batch
module that resolves the frozen registration through PostgreSQL locators,
verifies both immutable byte copies, re-derives a canonical no-floating-point
result from registered observations, and compares it byte-for-byte with an
independent normalization of the registered historical result rows.

Credible implementation rivals are recomputation directly from the historical
worktree, treating the registered result CSV as the sole analysis input, or
storing the derived result in mutable PostgreSQL workflow state. The first
bypasses admission, the second is circular, and the third makes mutable state
an inference authority. A no-change option preserves the verified P6 boundary
but cannot drain P7 or unlock P8 and P10.

**Recommendation selected:** implement the read-only batch boundary and keep
the normalized result, recomputation manifest, later profile proposal, and
training-candidate manifest content-addressed. Use integers, booleans, strings,
and exact numerator/denominator pairs in durable identities; do not use binary
floating-point values.

## Decision and authorization

**Decision:** execute a staged backlog-drain campaign.

Stage A is authorized now through `2026-07-25T23:59:59Z` and explicitly names:

- CAPLAB-25/P7 implementation under `src/caplab/recomputation/**`, its tests,
  documentation, and a model-free CLI;
- CAPLAB-26/P8 implementation under `src/caplab/profile/**`, its tests,
  documentation, and proposal schema; and
- CAPLAB-28/P10 implementation under `src/caplab/training_candidates/**`, its
  tests, documentation, and candidate-manifest schema.

Stage A may update the CAPLAB plan, decision and record indexes, repository
contract tests, package metadata, and hermetic integration fixtures required by
those three items. It may run `make check`, create commits, and prepare the
separate Proximal host surface for a later exact execution authorization.

Stage A creates no database row, object, local evidence copy, credential,
role login, model/provider call, human assertion, export, publication, training
action, verification verdict, or acceptance record.

Before live P7 execution, a separate durable continuation must bind the exact
clean CAPLAB implementation commit, installed-file hashes, Proximal desired
state, campaign configuration, temporary reader identities, evidence root,
expiry, cleanup, and independent checks. That continuation may authorize only
read access to the existing P6 registration and immutable copies.

## Preservation, verification, and stop conditions

Preserve the P6 registration, all historical bytes and timestamps, the live
PostgreSQL start identity, P4 control, Garage and `/nvr` objects, source-study
custody, and disabled writer/verifier identities. P7 output is an observation
or estimate, P8 output is a proposal, and P10 output is a candidate manifest.

Hermetic tests must cover complete separation, ties, undefined outcomes,
invalid cardinality, assignment/outcome disagreement, metadata substitution,
missing or altered object bytes, independent-copy disagreement, historical
result mismatch, deterministic replay, and refusal of broader assertion types.

Stop on authority, expiry, repository, commit, registration, locator, byte,
cardinality, condition, block, task, analysis, source, credential, or identity
drift. Stop before enabling any live identity until the exact continuation is
decided. Stop before CAPLAB-27, CAPLAB-29, CAPLAB-30, CAPLAB-33, or CAPLAB-34
effects unless their own dependency and authority gates are satisfied.

## Doctrine provenance

The implementation recommendation used evidenced Pincite packet
`pkt-c9d90600a8b15731`, content SHA-256
`c9d90600a8b15731d43cc3b3a2209282071eb4a6dcc12ddb9b0ad8bb21dd3bf8`,
corpus `corpus-2026-07-12-d2ea7b94a1ce`, doctrine
`doctrine-f630427242460c1e`, and retriever
`retriever-db7e43c1081abf3d`. Retrieval used a clean temporary worktree at the
repository-pinned Pincite commit
`9760d1b32cd4ced1d8b86c937203d47673f1ee85` because the installed release had
advanced. The packet's material guidance was repository-contract precedence,
evidence before intervention, explicit failure policy, content and text
boundaries, behavior preservation, structured cleanup, and authority-bounded
action.

Unmet packet obligations concerning the exact resource lifecycle, failure
taxonomy, external format, identity ownership, and idempotence remain material
until the tracer implementation and tests make those contracts executable.
Formatter/type-checker and concurrency obligations are nonmaterial here: this
repository has no configured formatter or type checker, and P7 is a sequential
read-only batch operation.

The completed tracer at clean commit
`63dc7aa4825696c6d0975c200131d53bb2b454f5` was then reassembled with the
implementation and 93-test gate as a second typed evidence pass. Final packet
`pkt-c3a7efc417d731c6`, content SHA-256
`c3a7efc417d731c6224fef79be330ab5b99922d73aaab4c07e8090735e21f093`,
uses the same corpus, doctrine, and retriever versions. It satisfied all four
required evidence classes. Its authority ceiling remains execution without
self-acceptance. The remaining material resource-lifecycle, containment,
cleanup, caller-recovery, and observability obligations belong to the bounded
Proximal executor and live continuation; they are not grounds for adding a
writer or inference surface to the tracer.

## Reopening conditions

Reopen if P6 registration or byte custody no longer reconciles, the frozen
analysis cannot be reproduced without importing historical runtime code, live
P7 requires a write effect, P8 or P10 requires a human judgment, the owner
changes the drain objective, or implementation cannot bind an exact clean
executor before expiry.
