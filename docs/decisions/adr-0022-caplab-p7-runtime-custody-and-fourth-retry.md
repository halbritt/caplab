---
id: adr-0022
artifact_type: architecture-decision-record
title: CAPLAB P7 runtime custody correction and exact fourth retry
status: decided
decision_owner: repository-owner
decision_authority: repository-ownership-and-direct-instruction
created: 2026-07-19
decided_at: 2026-07-19
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
  - caplab-p7-live-third-retry-attempt-2026-07-19
  - caplab-p7-runtime-custody-repair-2026-07-19
---

# CAPLAB P7 runtime custody correction and exact fourth retry

## Decision context and owner instruction

ADR 0021 stopped before access creation because the prepared venv exposed its
interpreter through a symlink that the versioned controller correctly refused.
After the stop and disabled-state observations were reported, the repository
owner instructed:

> retry again

The executor then prepared only the causal runtime-custody correction under ADR
0016 Stage A, preserved the refused runtime, and bound the exact continuation in
[`caplab-p7-live-retry-4-proposal-2026-07-19`](../records/caplab-p7-live-retry-4-proposal-2026-07-19.md).

## Decision and authorization

**Decision:** execute one further retry using the exact fourth-retry proposal.

**Owner and authority:** repository owner under repository ownership and the
direct instruction quoted above. The instruction authorizes another retry; the
existing plan and controller constrain that intent to the smallest safe
regular-file runtime correction and otherwise unchanged P7 boundary.

**Authorized executor:** the primary agent on host `proximal` may execute the
proposal once through `2026-07-25T23:59:59Z`.

The authorized effects are exactly the proposal's archive, preflight, bounded
reader enablement, two recomputations, validation, aggregate disablement,
preservation checks, and evidence sealing. The CAPLAB source remains
`bf6de2b24ac61e82107208cdc609c7e534c6eaaa`; Proximal desired state is
`1b79aa07cc4e44e8fc828449f882c6b62008edb6`; and the P6 admission remains
`d2d4f821146c3f39e6726133c383807ec9f6051834e74fbd3a5f33aae8ef148e`.

## Verification and exclusions

CAPLAB-25 may close only after both canonical outputs match, the historical
comparison is byte-identical, aggregate disablement passes, all pre/post
controls match, and the fresh evidence manifest verifies. Executor checks are
not CAPLAB-33 independent verification or CAPLAB-34 acceptance.

This decision excludes capability inference, semantic adjudication,
training-candidate eligibility, export, model/provider calls, training,
publication, Striatum placement, preference work, deletion of stopped evidence
or earlier runtimes, another retry, independent verification, and acceptance.

## Reopening conditions

Stop and reopen if any bound identity, regular-file custody check, path, timer,
expiry, access boundary, registered byte, result, replay, or preservation
control differs. Another stopped execution requires another owner decision.

## Status history

- `2026-07-19` — `decided` — after the pre-access runtime-custody stop, the
  repository owner instructed `retry again`; one exact corrected retry is
  authorized.
