---
id: adr-0046
artifact_type: architecture-decision-record
title: First CAPLAB Striatum lane-fit disposition
status: decided
decision_owner: primary-agent
decision_authority: adr-0026
created: 2026-07-20
decided_at: 2026-07-20
supersedes: []
superseded_by: null
affected_contexts:
  - agent-capability-lab
  - striatum-placement
related_specs:
  - spec-agent-capability-lab
related_plans: []
---

# First CAPLAB Striatum lane-fit disposition

## Context

CAPLAB-10 requires the registered subject evidence to be compared against the
two accepted profiles from ADR 0031. A comparison may recommend a scoped
candidate or Pareto set, but CAPLAB cannot mutate Striatum policy and cannot
turn missing profile evidence into a placement claim.

The comparison is recorded in
[`caplab-first-lane-fit-2026-07-20.md`](../product/striatum-pass-profiles/caplab-first-lane-fit-2026-07-20.md),
file SHA-256
`e22a141e1cc7419a24a4edbaa2e7c165bd377070f09ccedcd59266872b2bb8c1`.

## Decision

The ADR 0026 delegate accepts the report's `insufficient-evidence`
disposition. No observed subject tuple meets the accepted authorized-build or
independent fresh-review qualification floor. The qualifying set and Pareto
set are therefore empty.

CAPLAB recommends no placement or scheduler-policy change. Existing Striatum
policy and authorized human fallbacks remain in force. This decision does not
rank the tuples universally, infer that any tuple is incapable, or authorize a
new campaign.

## Evidence basis

The comparison binds the accepted profile files and all admitted tuple
evidence:

- Study 001 contains a strong task-local mechanical result, but ADR 0023
  records the owner's capability-inference refusal and the study lacks the
  required profile breadth and accepting-review set.
- CAPLAB-8 records a five-of-six blind preference for native Fable, but zero
  strict mechanical advantages and no qualifying Striatum job campaign.
- CAPLAB-13 records zero schema-valid native reviews, so its model comparison
  is not estimable and supplies no fresh-review qualification evidence.
- available latency and token observations come from the wrong populations;
  token schemas differ by native harness and no common paid-cost basis exists.

Human-owned inference remains human-owned. The negative disposition is an
accepted CAPLAB recommendation, not Striatum policy acceptance.

## Advisory doctrine

This decision reuses the directly applicable ADR 0031 Pincite packet
`pkt-9165b553e244b739`, captured SHA-256
`0ff7d9f9a857609ca0ff9180f9d80cc561e9a398da5c10aa02c69c7cbae06140`.
Its accepted-contract, task-authority, current-runtime, bounded-decision, and
reversal obligations are discharged by the immutable profile hashes, exact
evidence locators, empty candidate set, and explicit non-mutation boundary.

## Acceptance and reopening

The primary agent accepts the insufficient-evidence recommendation under ADR
0026. This completes the CAPLAB-10 comparison and disposition; it is not an
independent verification or a Striatum placement decision.

Reopen only after a content-addressed campaign satisfies one accepted
profile's exact breadth, validity, accepting-review, latency, token, and cost
requirements, or after Striatum changes the cited profile context.

## Status history

- `2026-07-20` — `decided` — the ADR 0026 delegate accepted the empty
  qualifying and Pareto sets and recommended no Striatum policy change.
