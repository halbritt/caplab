---
id: adr-0035
artifact_type: architecture-decision-record
title: BOOKS-3 Doctrine-injection probe redesign disposition
status: decided
decision_owner: primary-agent
decision_authority: adr-0026-and-adr-0029
created: 2026-07-20
decided_at: 2026-07-20
supersedes: []
superseded_by: null
affected_contexts:
  - agent-capability-lab
  - historical-ethogram-custody
related_specs:
  - spec-agent-capability-lab
related_plans: []
---

# BOOKS-3 Doctrine-injection probe redesign disposition

## Decision

Select **redesign** for the historical BOOKS-3 Doctrine-injection probe.
Preserve the exact series as historical design evidence, but do not admit its
attempts, aggregates, or mechanical pass labels as CAPLAB model evidence.

The assessment is
[`caplab-43-books-3-admission-assessment`](../records/caplab-43-books-3-admission-assessment-2026-07-20.md).
It binds the Pincite source commit, primary preregistration and grader commit,
primary execution and diagnostic-preregistration commit, diagnostic result
commit, and every governing artifact blob.

## Why redesign

The series contains useful instrument behavior: frozen cases and falsifiers,
manifest binding, output and world-artifact canaries, explicit infrastructure
classification, and a diagnostic preregistered after the primary failure.
Rejecting the entire study family would discard those sound controls.

Admission is not viable because the raw request, response, and run bytes were
scratch-only and are absent from historical custody. CAPLAB cannot recover or
independently regrade them from hashes. Layered subject, administration, trial,
attempt, cost, and timing identities are also incomplete. The expected answer
was supplied directly, exact-string grading leaves paraphrase and indirect
effects unobserved, and the design lacks clean, manipulation, randomized,
repeated, and held-out controls.

The historical claim remains bounded to the two recorded aggregate
classifications under their declared alias, endpoint, ceilings, and grader. It
does not establish prompt-injection resistance, Doctrine safety, capability,
placement, or training eligibility.

## Authority boundary and reopening

This decision is a custody and future-design disposition. It authorizes no
historical evidence admission, copying, execution, model call, external
mutation, fresh study implementation, human disposition, capability inference,
or acceptance. `history/ethogram/` remains unchanged.

A future proposal may reopen the family only with a new CAPLAB-native
preregistration and exact implementation authorization that supplies fresh
registered inputs, complete layered identities, raw-attempt preservation,
independent regrading, clean and manipulation controls, counterbalancing,
semantic leakage checks, repetitions, held-out cases, and a bounded capability
card. It must not claim recovery of the absent historical attempts.

## Status history

- `2026-07-20` — `decided` — the ADR 0026 delegate selected redesign and
  refused historical attempt admission under ADR 0029's custody boundary.
