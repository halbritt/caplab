---
id: adr-0030
artifact_type: architecture-decision-record
title: Preference Study 001 hypothesis selection
status: amended
decision_owner: primary-agent
decision_authority: adr-0026
created: 2026-07-20
decided_at: 2026-07-20
supersedes: []
superseded_by: adr-0039
affected_contexts:
  - agent-capability-lab
related_specs:
  - spec-agent-capability-lab
related_plans: []
---

# Preference Study 001 hypothesis selection

## Source observation

CAPLAB-6 records the repository owner's bounded statement:

> I prefer Fable for complex work.

This is a preference observation. It is not evidence that Fable is generally
better and it does not explain the preference.

## Decision

The ADR 0026 delegate selects constraint continuity as the one candidate
behavioral explanation to test. On decision-dense repository work, Fable may
retain and satisfy more distributed mandatory constraints than GPT while still
completing the requested effect. The named use is sustained repository
maintenance that otherwise consumes owner attention through repeated scope,
authority, or preservation corrections.

Under the same delegation, the primary agent accepts the six task shells in
the preregistration as the concrete complex-work examples for this hypothesis.
That is a study-design decision by the delegated mechanism, not a preference
judgment attributed to the repository owner.

The frozen hypothesis, task population, rivals, rubric, sample, order, error
rules, and call ceiling are recorded in
[`caplab-preference-001-preregistration`](../product/studies/caplab-preference-001-preregistration.md).

The selected hypothesis is disconfirmed unless both preregistered descriptive
thresholds hold. Even if they hold, the study supports only a task-conditioned
association between constraint continuity and the owner's blinded preference.
It cannot establish a causal mechanism or a global model ranking.

## Evidence used

Historical Harbor observations show that GPT-5.6 and Claude Fable 5 both
completed the existing checkout-retries task, so that task does not
discriminate them. They also show that harness failures can masquerade as
subject failures. The custody locator is commit
`c8f916123a0a88e30089066dbf872c144d732bbd`, path
`doctrine/evaluations/robustness/harbor/README.md`, Git blob
`dfcdcab612663300e0f45e8b15fbb55a78d6f69a`. Preference Study 001 therefore
uses six fresh synthetic task shells and records harness, provider, and subject
outcomes separately. No historical task or run record is admitted.

Pincite packet `pkt-0a188b1a29cd883c` was used as advisory engineering
evidence. The captured packet SHA-256 is
`f406ce707035e66f6dafe1a75d180e9ec712d2e6cc01391290bfeede12826888`.
Neither historical observation nor Pincite advice creates the decision.

## Authority boundary

This decision authorizes only the model-free preregistration. It makes no model
call, spends no inference budget, creates no preference result, and records no
judgment under the repository owner's identity. CAPLAB-7 must build and verify
the frozen instrument. CAPLAB-8 requires a separate paid-inference
authorization and the named evaluator's blinded judgments.

## Reopening conditions

ADR 0039 supersedes the former same-harness condition. Reopen the hypothesis
before a corrected CAPLAB-7 freezes the instrument if either native agent
system is unavailable, any task shell cannot expose at least eight
independently scorable constraints, or a synthetic task would need private or
historical run evidence. Native-harness unavailability blocks that subject; it
does not authorize proxy substitution.

## Status history

- `2026-07-20` — `decided` — the ADR 0026 delegate selected constraint
  continuity as the one bounded candidate explanation for preregistration.
- `2026-07-20` — `amended` — ADR 0039 replaced the incorrect common-harness
  condition with native agent-system identity; the hypothesis remains future
  work and requires a corrected instrument.
