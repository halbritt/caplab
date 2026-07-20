---
id: adr-0024
artifact_type: architecture-decision-record
title: CAPLAB Study 001 no training-eligible examples
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
  - caplab-p11-eligibility-decision-proposal-2026-07-20
---

# CAPLAB Study 001 no training-eligible examples

## Decision context and owner instruction

CAPLAB-28/P10 produced candidate manifest
`0eeed6348f87d03143ad44c4b9d5440140957c33f32b70e456d80d493aad4a73`
with 20 mechanically derived candidates, zero mechanical exclusions, and one
protected split group. Every candidate is `derived-not-eligible`, human
disposition is `not-recorded`, and leakage review remains
`unavailable-pending-human-eligibility`. No completed privacy or license review
or export scope exists.

The exact P11 proposal recommended `no-example-eligible`. The repository owner
responded:

> recommendations accepted

This instruction selects the recommended P11 disposition and separately selects
the P9 refusal recorded by ADR 0023. It is not export authorization, training
authorization, independent verification, or CAPLAB v0 acceptance.

## Decision

**Decision:** `no-example-eligible`.

No candidate in the bound manifest is selected as training eligible under the
current evidence. This is a current human eligibility decision, not an
inference that the candidates are permanently ineligible.

No dataset export is authorized. CAPLAB-30/P12 is therefore unavailable and
must not materialize a bundle. The CAPLAB v0 export criterion is unmet.

## Consequences and exclusions

CAPLAB-29/P11 is complete with a named owner eligibility decision. CAPLAB-33
must verify that no export occurred and report the unmet export criterion.
CAPLAB-34 may record revision or rejection after independent verification; the
current plan does not permit acceptance when the required export criterion is
unmet.

This decision authorizes no candidate mutation, evidence export, model call,
training, deployment, publication, later export, independent verification, or
acceptance.

## Reopening conditions

Reopen only through a new owner decision after named human privacy, license,
quality, provenance, leakage, and family-safe-split reviews are recorded. Any
later export still requires its own exact destination, size, retention, expiry,
purge, and stop-condition authorization.

## Status history

- `2026-07-20` — `decided` — the repository owner accepted the recommended
  `no-example-eligible` disposition.
