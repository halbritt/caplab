---
id: adr-0036
artifact_type: architecture-decision-record
title: CAPLAB-12 review-dissent instrument authorization
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
  - caplab-review-dissent-001
related_specs:
  - spec-agent-capability-lab
related_plans: []
---

# CAPLAB-12 review-dissent instrument authorization

## Context

ADR 0034 selects and accepts the `caplab-review-dissent-001` model-free study
design. CAPLAB-12 must implement and qualify that design before any calibration
authorization. ADR 0026 requires the delegated mechanism to record a bounded
execution authorization before material effects.

The clean execution baseline is commit
`2193307f5c83cdc0b619655eb36cd4fd4c2554ad`.

## Decision and authorization

Authorize one model-free CAPLAB-12 implementation campaign through
`2026-08-03T23:59:59Z`.

Permitted repository effects are limited to:

- `src/caplab/review_dissent/**`;
- `tests/test_review_dissent*.py` and fresh
  `tests/fixtures/review_dissent/**` qualification data;
- CAPLAB-owned `caplab-review-dissent-001` development, held-out, instrument,
  preservation, cost-estimate, execution, and verification records;
- decision, product, package, and record indexes plus required repository
  gates; and
- commits, pushes to the existing CAPLAB repository, and Plane projections for
  CAPLAB-12.

The executor may create 16 fresh synthetic review cells: four factorial cells
in each of the two development and two held-out worlds frozen by ADR 0034. It
may implement deterministic rendering, review-artifact capture, trace-owned
evidence observations, mechanical grading, causal-pair and leakage checks,
preservation verification, blinded human-review packets, campaign estimation,
and content-addressed manifests.

The development and held-out inputs must be separate artifacts with separate
identities. The CAPLAB-12 qualification path may load and test both. The public
calibration path must load only the development artifact and the held-out
aggregate identity; a regression test must prove that it does not read the
held-out content artifact.

## Excluded effects

This authorization permits no model, provider, or live agent-harness call; no
token use, paid inference, or local inference compute; no credential read; no
external runtime mutation; no historical or live evidence admission; no human
disposition attributed to the repository owner; no study result, construct
inference, lane-fit recommendation, or acceptance; no dataset export; no
training; and no Striatum policy change.

It does not authorize CAPLAB-13. Canned review artifacts and synthetic traces
are qualification fixtures, not subject attempts or model evidence.

## Preservation and stop conditions

Preserve the ADR 0034 task worlds, factorial dimensions, harm order, clean
anti-refusal control, development/held-out split, mechanical-versus-human
boundary, claim ceiling, and stop rules. Preserve unrelated repository state
and leave `history/ethogram/` unchanged.

Stop before instrument freeze if:

- clean and defect variants differ outside one declared semantic mutation;
- author-cue variants differ outside the handoff or leak truth through length,
  name, path, order, metadata, or treatment markers;
- the hidden oracle must enter the subject task image;
- a mechanical score would require semantic judgment over free-form model
  prose;
- the calibration loader cannot avoid held-out content reads;
- pristine reference worlds do not pass or a designed harm band is
  unreachable; or
- any required effect exceeds the permitted paths or activates inference.

## Verification and cleanup

Model-free verification must cover:

- exact instrument, development, held-out, world, cell, oracle, instruction,
  and schema identities;
- deterministic rendering and pristine reference behavior for all 16 cells;
- clean/defect single-mutation and cue-only causal-pair hygiene;
- neutral cell identifiers, equalized pair inventory and metadata, and
  recursive treatment and hidden-oracle leakage refusal;
- reference fixtures for mechanical bands `1.0`, `0.7`, `0.4`, `0.2`, and
  `0.0`, including the cautious-clean anti-refusal cell;
- provider, harness, capture, task-image, and verifier infrastructure
  classification outside the mechanical score;
- trace-owned evidence observations, target-preservation hashes, and refusal
  of fabricated or mutated capture state;
- blinded packets with an empty human disposition and no subject, treatment,
  truth, or provider clues;
- capture parity across cells and a calibration loader that does not read the
  held-out content artifact;
- an exact zero-authorized-call live estimate; and
- the complete repository gate, diff hygiene, temporary cleanup, commit,
  push, and clean synchronized checkout.

CAPLAB-12 may close after these technical criteria pass. Passing them is not an
independent verdict, live study verification, human judgment, or acceptance.

## Doctrine receipt

The authorization decision used Pincite packet `pkt-c66a0d1aa5e3e040`,
packet-file SHA-256
`eeb322a5f2b6880648abb8742ff20f94441f92b9cc82e1df7b4a8fcb432eac8d`,
packet-content SHA-256
`c66a0d1aa5e3e04076c856c108572ddd11ea13d14ece6ec2d0494767ef0b5412`,
corpus `corpus-2026-07-12-d2ea7b94a1ce`, doctrine
`doctrine-be3dc0e2873014de`, and retriever
`retriever-52068c631d23be23` from the validated release home.

The packet is advisory. This authorization applies its repository precedence,
identity, integrity, evidence, minimal-interface, preservation, and explicit
failure guidance within ADR 0034's accepted design. ADR 0026 supplies the
execution-authorization authority.

## Reopening conditions

Reopen before changing the permitted paths, expiry, model-free boundary,
development/held-out custody, task population, harm order, claim ceiling, or
verification criteria. Any live call, spend, held-out calibration access,
human disposition, or inference requires a later exact authorization.

## Status history

- `2026-07-20` — `authorized` — the ADR 0026 delegate authorized one bounded
  model-free CAPLAB-12 implementation campaign.
