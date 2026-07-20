---
id: adr-0034
artifact_type: architecture-decision-record
title: Review dissent second-study selection
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

# Review dissent second-study selection

## Decision

Under ADR 0026, the primary agent selects evidence-calibrated independent
review dissent as CAPLAB's second, non-Doctrine capability study and accepts
the design in
[`caplab-review-dissent-001-preregistration`](../product/studies/caplab-review-dissent-001-preregistration.md).

The construct matters directly to the accepted
[`striatum-fresh-review-v1`](../product/striatum-pass-profiles/striatum-fresh-review-v1.md)
profile: an independent reviewer must refuse to clear an acceptance-critical
defect despite a favorable author cue, while still clearing clean targets and
avoiding fabricated blockers. This makes review dissent evidence-calibrated
rather than synonymous with rejection or contrarian style.

The selected design crosses clean versus defect-bearing target truth with
favorable versus cautious author cues. It includes an explicit cautious-clean
anti-refusal control, a mechanical verdict and evidence oracle, a separate
human rubric, and two development plus two held-out world families fixed before
any model call.

## Alternatives and evidence matrix

| Candidate | Pass relevance | Discrimination | Main reason not selected |
|---|---|---|---|
| Review dissent | Direct fresh-review requirement | Strong clean/defect oracle and cue inversion | Selected. |
| Scope control | Direct build requirement | Strong write-set oracle | Substantially overlaps Preference Study 001's constraint-continuity shells. |
| Recovery judgment | Useful build behavior | Strong state oracle | Overlaps checkout-retries and Preference Study 001's retained-state retry shell. |
| Architectural coherence | Useful across jobs | Weakly mechanical | Too much of the primary outcome would remain human-only for the second study. |
| Uncertainty-sensitive escalation | Direct review requirement | Moderate | Retained as a human and secondary observable within review dissent, not the primary construct. |
| No second study | Avoids implementation cost | No new evidence | Cannot satisfy the accepted cross-task or fresh-review roadmap. |

ADR 0029 separately excludes the historical BOOKS-3 Doctrine-injection probe
from satisfying CAPLAB-11. No historical task, output, result, or judgment was
used or admitted for this decision.

## Construct and claim boundary

The study measures whether a sealed fresh reviewer follows target evidence and
the frozen acceptance contract when author cues conflict. It does not measure
generic coding competence, broad review ability, personality, universal social
independence, or Striatum lane fitness. A successful study can contribute to a
later profile comparison but cannot clear a Striatum gate or select a model.

The canonical term **review dissent** is added to CAPLAB's ubiquitous language
with its clean-control requirement. This is a durable domain distinction:
dissent without correct clean acceptance is not the construct.

## Authority and next boundary

This decision accepts a model-free design. It authorizes zero calls, zero
spend, no historical or live evidence admission, no human disposition, no
external mutation, and no result or capability inference.

CAPLAB-12 requires a separate bounded implementation authorization before it
may create the instrument, synthetic worlds, hidden oracles, qualification
fixtures, or sealed held-out manifest. CAPLAB-13 requires a later exact live
authorization. The held-out set may not be inspected during calibration.

Reopen this decision before the first call if the factorial cells cannot keep
target truth and author cue independent, the verifier cannot observe evidence
inspection without revealing the oracle, a clean anti-refusal target cannot be
made unambiguous, or held-out custody cannot prevent calibration access.

## Doctrine receipt

The decision used advisory Pincite packet `pkt-c44eb86f05e49440`, packet-file
SHA-256
`57ecf923b639250481a8d548e4f922f89c52a53331bd33d854a9ec9df7fc6031`,
packet-content SHA-256
`c44eb86f05e49440a923a03f21873866bb6ce21423d6b12953b346ece353a40f`,
corpus `corpus-2026-07-12-d2ea7b94a1ce`, doctrine
`doctrine-be3dc0e2873014de`, and retriever
`retriever-52068c631d23be23` from the validated release home.

The design applies repository precedence, direct outcome measurement,
preserved controls, bounded authority, and one-uncertainty-at-a-time guidance.
The packet was recommendation only; ADR 0026 supplies the decision authority.

## Status history

- `2026-07-20` — `decided` — the ADR 0026 delegate selected and accepted the
  second-study construct and frozen design boundary.
