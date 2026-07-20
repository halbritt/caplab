---
id: adr-0023
artifact_type: architecture-decision-record
title: CAPLAB Study 001 capability-inference refusal
status: decided
decision_owner: repository-owner
decision_authority: repository-ownership-and-direct-instruction
created: 2026-07-20
decided_at: 2026-07-20
supersedes: []
superseded_by: null
affected_contexts:
  - agent-capability-lab
  - caplab-study-001
related_specs:
  - spec-agent-capability-lab
related_plans:
  - plan-agent-capability-lab-v0
related_receipts:
  - caplab-p8-p10-execution-2026-07-20
  - caplab-p9-inference-decision-proposal-2026-07-20
---

# CAPLAB Study 001 capability-inference refusal

## Decision context and owner instruction

CAPLAB-26/P8 produced profile proposal
`641965dc30fd0dbfca81d56bb05282b01e8e079285ab605c12672e92f3971ef0`.
The exact P9 proposal recommended `refuse` because the completed mechanical
result still lacks cross-task confirmation, a matched equally salient
non-verification append, an independent-subject positive control, and human
interpretation of decision artifacts.

The repository owner responded:

> recommendations accepted

This instruction selects the recommended P9 disposition and separately selects
the recommended P11 disposition recorded by ADR 0024. It is not CAPLAB v0
acceptance.

## Decision

**Decision:** `refuse`.

No Study 001 capability inference is recorded. CAPLAB retains only the
mechanical observation that appending the exact V package reduced harmful
shipment relative to B for the exact frozen task, provider route, runtime,
administration, and sample.

The refusal does not invalidate or rewrite the observation. It keeps the live
rivals and missing construct evidence visible instead of promoting the
treatment effect into a capability assertion.

## Consequences and exclusions

CAPLAB-27/P9 is complete with a named owner refusal record. The capability
profile remains `pending-human-inference` as an immutable proposal; this ADR is
the separate current disposition.

Task-family capability, cross-task capability, model-wide capability,
preference, universal ranking, mechanism, safety, Striatum placement, training
eligibility, technical verification, and acceptance remain unavailable. This
decision authorizes no evidence change, export, model call, training,
independent verification, or acceptance.

## Reopening conditions

Reopen only through a new owner decision after materially stronger construct
evidence, such as the selected card's missing controls or held-out replication,
is content-addressed and reviewable. Reopening does not alter this historical
refusal.

## Status history

- `2026-07-20` — `decided` — the repository owner accepted the recommended
  `refuse` disposition.
