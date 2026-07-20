---
id: adr-0029
artifact_type: architecture-decision-record
title: BOOKS-1–6 custody and CAPLAB admission boundary
status: decided
decision_owner: primary-agent
decision_authority: adr-0026
created: 2026-07-20
decided_at: 2026-07-20
supersedes: []
superseded_by: null
affected_contexts:
  - agent-capability-lab
  - pincite
related_specs:
  - spec-agent-capability-lab
related_plans: []
---

# BOOKS-1–6 custody and CAPLAB admission boundary

## Context

The repository owner asked whether BOOKS-1 through BOOKS-6 also belong in
CAPLAB and delegated the resulting product and execution-order decisions under
ADR 0026. The six work items are complete records in the Books Plane project.
Their completion predates the standalone CAPLAB repository and cannot serve as
current CAPLAB execution, verification, or acceptance.

The exact review and execution order are recorded in
[`caplab-books-1-6-triage-2026-07-20`](../records/caplab-books-1-6-triage-2026-07-20.md).

## Decision

BOOKS-1 remains Pincite-owned infrastructure. CAPLAB consumes Pincite packets
as advisory evidence with packet provenance; it does not own the packet
assembler, retrieval index, or Pincite release state.

BOOKS-2, BOOKS-4, BOOKS-5, and BOOKS-6 contain reusable measurement-platform
behaviors. CAPLAB will implement those behaviors behind CAPLAB-native
interfaces under CAPLAB-41 and CAPLAB-42. The historical source commits are
design evidence, not an active package root. Reimplementation must preserve
the source commit and path locators and must not count historical tests or
runs as CAPLAB verification.

BOOKS-3 remains historical Doctrine-injection study evidence. CAPLAB-43 may
assess it as a future study candidate. It is not admitted by this decision and
cannot satisfy CAPLAB-11 because CAPLAB-11 requires a non-Doctrine study.

## Historical-custody boundary

This decision authorizes inspection of the exact source commits named in the
triage record and translation of their reusable contracts into new active
CAPLAB code. It does not authorize copying or registering historical model
outputs, run results, summaries, baselines, or gold judgments. It does not
authorize editing `history/ethogram/`.

The allowed active write surface for the follow-on implementation is:

- `src/caplab/evaluation/**`;
- `tests/test_evaluation*.py` and `tests/fixtures/evaluation/**`;
- CAPLAB schemas and records that those tests require; and
- the corresponding indexes, Makefile gates, and Plane projections.

Any broader historical-evidence effect requires a later exact authorization.

## Bounded follow-on authorization

Under ADR 0026, CAPLAB-41 and CAPLAB-42 are authorized through
`2026-08-03T23:59:59Z` for model-free local implementation only. They may add
deterministic synthetic fixtures, typed failure outcomes, mode matching,
snapshot comparison, and an append-only defect ledger within the active write
surface above.

They may not call models, alter external runtime state, admit historical run
evidence, mutate source history, export a dataset, train a model, or claim an
independent verdict. Verification requires the repository gate plus frozen
same-input replay, fixture-integrity, mode-mismatch refusal, and defect-ledger
tests. Temporary files and generated caches are removed after verification.
Execution stops if an implementation requires an excluded historical artifact,
cannot preserve its source locator, or would weaken an existing fail-closed
boundary.

CAPLAB-43 is authorized only for a model-free admission assessment under the
same expiry. It may record a recommendation and later decision; it may not
admit or execute the historical probe.

## Reopening conditions

Reopen this decision if Pincite no longer owns the live assembler, a required
CAPLAB behavior cannot be expressed without admitting historical evidence, or
a non-Doctrine candidate is shown to depend on the BOOKS-3 probe.

## Status history

- `2026-07-20` — `decided` — the ADR 0026 delegate classified BOOKS-1 through
  BOOKS-6, preserved their custody, and authorized the bounded CAPLAB-native
  follow-ons.
