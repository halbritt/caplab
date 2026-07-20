---
id: adr-0033
artifact_type: architecture-decision-record
title: CAPLAB-7 model-free preference instrument authorization
status: authorized
decision_owner: primary-agent
decision_authority: adr-0026
created: 2026-07-20
decided_at: 2026-07-20
expires_at: 2026-08-03T23:59:59Z
supersedes: []
superseded_by: null
affected_contexts:
  - agent-capability-lab
  - caplab-preference-001
related_specs:
  - spec-agent-capability-lab
related_plans: []
---

# CAPLAB-7 model-free preference instrument authorization

## Context

ADR 0028 preserves CAPLAB-7 as future roadmap work but does not authorize its
execution. ADR 0016 Stage A authorized a different v0 implementation campaign
and does not cover this preference study. ADR 0026 delegates bounded CAPLAB
execution-authorization decisions to the primary agent and requires an exact,
durable scope before material effects.

The frozen study contract is
[`caplab-preference-001-preregistration`](../product/studies/caplab-preference-001-preregistration.md).
It authorizes zero model calls and zero spend. CAPLAB-7 must build and verify
the instrument before any later CAPLAB-8 live authorization can be considered.

## Decision and authorization

Authorize one model-free CAPLAB-7 implementation campaign through
`2026-08-03T23:59:59Z`, starting from clean CAPLAB commit
`458ba63884f3948b79adba3b7b5b49cf03f18d64`.

Permitted repository effects are limited to:

- `src/caplab/preference/**`;
- `tests/test_preference*.py` and `tests/fixtures/preference/**`;
- CAPLAB-owned study instrument, schema, execution, and verification records;
- decision, product, and record indexes plus required package or test gates;
  and
- commits, pushes to the existing CAPLAB repository, and Plane projections for
  this campaign.

The executor may inspect local, non-secret harness and model-routing metadata
read-only to resolve exact provider model identifiers and prove that both
subjects can use one harness and tool surface. It may create fresh synthetic
task repositories and temporary model-free captures, run canned subject
drivers that never invoke a model, and delete only those task-local temporary
artifacts after verification.

The implementation must preserve all frozen task shells, subject distinctions,
execution order, reveal order, sample size, output ceiling, wall-clock limit,
replacement rules, call ceiling, spend ceiling, analysis thresholds, and stop
rules. Each shell must expose at least eight preregistered constraints across
four or more required surfaces.

## Excluded effects

This authorization permits no model, provider, or live agent-harness call; no
token consumption or inference spend; no credential read; no live or
historical evidence admission; no human adjudication or judgment attributed to
the repository owner; no subject-identity reveal; no preference or capability
inference; no dataset export; no training; and no Striatum policy change.

It does not authorize CAPLAB-8. A canned output is test data, not a model
attempt or study result. Passing checks is technical verification, not
independent verification or acceptance.

## Preservation and stop conditions

Preserve the preregistration bytes, all earlier CAPLAB decisions and records,
the historical custody tree, unrelated worktree state, and the distinction
between model, harness, infrastructure, mechanical-oracle, and human-judgment
outcomes.

Stop before instrument freeze if exact provider identifiers cannot be resolved
from non-secret authoritative metadata, if the subjects require different
harness or tool surfaces, if any task shell cannot meet its constraint and
anti-refusal contract, or if blinding cannot remove model and provider clues
without removing evidence the rubric requires. Stop on preregistration drift,
identity substitution, fixture leakage, mutable input, model-call activation,
or any required effect outside the permitted paths.

## Verification and cleanup

Model-free verification must cover:

- exact subject sealing and byte-identical instructions;
- the fixed execution and reveal order;
- deterministic rendering of all six fresh task repositories;
- at least eight frozen constraints per task across at least four surfaces;
- canned complete, partial, declined, invalid, and infrastructure outcomes;
- mechanical oracle results separated from qualitative human criteria;
- replacement and stop-rule accounting;
- blinded packet generation with a recursive identity-leak scan; and
- refusal of changed task, subject, harness, tool, order, ceiling, or manifest
  identities.

Run the complete repository gate, record artifact identities, remove generated
caches and task-local temporary files, commit, push, and leave the checkout
clean. CAPLAB-7 may close only after those technical criteria pass.

## Doctrine receipt

The authorization decision used Pincite packet `pkt-0e910757af630c19`,
packet-file SHA-256
`7eb2ba142e68842a490f4f10b80c19c2947f3575c9377e778fb34ab119e6e546`,
corpus `corpus-2026-07-12-d2ea7b94a1ce`, doctrine
`doctrine-be3dc0e2873014de`, and retriever
`retriever-52068c631d23be23` from the validated release home.

The packet's ceiling is recommendation. Execution authority comes from ADR
0026 and this decision. Its material guidance is reflected in the explicit
identity model, information-hiding boundary, evidence-before-intervention
rule, preservation matrix, stop conditions, and separation of structural
implementation from later empirical execution.

## Reopening conditions

Reopen this authorization before changing its target paths, expiry, model-free
boundary, frozen study design, preservation requirements, or verification
criteria. A later model call, spend, adjudication, or inference requires a new
authorization even if CAPLAB-7 passes.

## Status history

- `2026-07-20` — `authorized` — the ADR 0026 delegate authorized one bounded
  model-free CAPLAB-7 instrument campaign and excluded all live study effects.
