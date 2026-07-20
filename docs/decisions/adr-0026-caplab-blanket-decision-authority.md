---
id: adr-0026
artifact_type: architecture-decision-record
title: CAPLAB blanket decision authority delegation
status: active
decision_owner: repository-owner
decision_authority: repository-ownership-and-explicit-delegation
decision_delegate: primary-agent
created: 2026-07-20
decided_at: 2026-07-20
supersedes: []
superseded_by: null
affected_contexts:
  - agent-capability-lab
related_specs:
  - spec-agent-capability-lab
related_plans:
  - plan-agent-capability-lab-v0
---

# CAPLAB blanket decision authority delegation

## Owner instruction

The repository owner corrected the scope of the prior delegation:

> I didn't delegate P14 authority, I delegated blanket decision authority to
> you. My attention is a constrained resource and you've overburdened it.

The owner then made the operating expectation explicit:

> do not wait on me for a decision, advance toward the goal until complete

This is blanket CAPLAB decision authority delegated to the primary agent. It is
not limited to P13 or P14.

## Decision

The primary agent is the active delegated CAPLAB decision mechanism. It may
select and record CAPLAB product, planning, prioritization, governance,
revision, rejection, acceptance, and bounded execution-authorization decisions
without returning routine choices to the repository owner.

The delegated mechanism must keep each decision and authorization durable,
scoped, and reviewable. It must continue toward the active goal until complete
instead of pausing at ordinary decision gates.

## Boundaries

Blanket decision authority does not convert evidence into verification or
verification into acceptance. The delegate cannot fabricate observations,
issue an independent verdict for its own execution, rewrite failed criteria
inside verification, or claim an effect occurred without an execution record.

Before executing a material effect, the delegate still records the exact
target, permitted effects, expiry when relevant, preservation boundary,
verification, cleanup, and stop conditions. Historical evidence remains
immutable unless an exact authorization names a historical-evidence effect.

The delegate interrupts the owner only when CAPLAB needs authority the owner
does not possess, an externally irreversible effect outside the active goal, or
an ambiguity that cannot be made safe through a narrower reversible action.
Difficulty, a failed campaign, or an ordinary product choice is not a reason to
return the decision to the owner.

## Consequences

This delegation remains active for CAPLAB until the repository owner revokes or
narrows it. Later ADRs cite this record as their decision authority. Plane
remains a projection and cannot substitute for those durable records.

The correction supersedes the primary agent's earlier narrow interpretation of
the owner's delegation. It does not retroactively broaden ADR 0025's consumed
one-attempt P13 execution authorization.

## Status history

- `2026-07-20` — `active` — the repository owner clarified blanket decision
  authority and directed the delegate to advance without waiting for routine
  decisions.
