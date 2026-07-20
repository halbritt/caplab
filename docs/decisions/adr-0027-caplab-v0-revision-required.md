---
id: adr-0027
artifact_type: architecture-decision-record
title: CAPLAB v0 revision required
status: decided
decision_owner: repository-owner
decision_authority: adr-0026
decision_delegate: primary-agent
decision: revision
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
  - caplab-p13-independent-verification-2026-07-20
  - caplab-p14-owner-decision-proposal-2026-07-20
---

# CAPLAB v0 revision required

## Delegated decision authority

ADR 0026 delegates blanket CAPLAB decision authority to the primary agent and
directs it to advance without returning routine decisions to the repository
owner. The delegate reviewed the exact P14 `revision` recommendation and
`rejection` alternative.

## Decision

**Decision:** `revision`.

The current CAPLAB v0 slice is not accepted. Independent P13 technical
verification failed, and the required export criterion is unmet. The completed
Study 001 registration, recomputation observation, P9 refusal, P11
`no-example-eligible` decision, P13 failure record, and all sealed execution and
verification evidence remain unchanged.

CAPLAB-34/P14 is complete with a revision disposition. This closes the current
CAPLAB v0 acceptance review; it does not relabel the stopped P13 campaign or
waive either failed criterion.

## Why revision rather than rejection

The independent verifier passed the frozen source reconstruction, P6 identity,
P8 and P10 deterministic replays, hermetic failure paths, recovery evidence,
claim ceiling, family-safe split, and bounded non-export checks. External
observations found effective access closure and no protected-state drift.

The technical failure is bounded to the P7 controller lifecycle: retained
campaign state prevented enablement, and aggregate disablement could not reach
its frozen disabled-state oracle because that state named an already-absent
Garage key. This supports revising the current slice instead of rejecting the
CAPLAB product direction. It does not establish that a repair is correct or
authorized.

## Consequences and exclusions

No CAPLAB v0 acceptance or conditional acceptance exists. The active P0-P14
queue is closed with completed, cancelled, or revision outcomes; Plane may
project CAPLAB-34 as Done after this decision is committed.

The closed P0-P14 queue is the v0 acceptance campaign, not the complete CAPLAB
roadmap. ADR 0028 preserves future work outside that slice and corrects its
Plane projection.

Revision creates no execution authority. In particular, this decision does not
permit:

- changing, reconciling, or deleting the retained P7 state;
- changing the controller or its cleanup contract;
- another P13 verification attempt;
- reopening ADR 0024 or selecting training-eligible examples;
- changing the v0 export criterion;
- materializing P12 or another export; or
- model calls, training, publication, routing, deployment, deletion, purge, or
  evidence rewriting.

Follow-on decisions and authorizations use ADR 0026 without returning ordinary
choices to the owner. A controller-state correction and a
product/export-criterion decision remain distinct work; neither may be hidden
inside a verification retry.

## Reopening conditions

Reopen the current v0 acceptance review only after new decisions and
authorizations produce all required independent verification evidence and
resolve the export criterion. This ADR remains the historical P14 disposition
even if a later CAPLAB version or acceptance campaign succeeds.

## Status history

- `2026-07-20` — `decided` — the ADR 0026 delegate selected the recommended
  `revision` disposition.
