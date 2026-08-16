# Finding — `fate == final` does not establish control soundness

- Date: 2026-08-16
- Amends: [read of the matched comparison](read-2026-08-16-matched-custody-ordering.md)
- Disposition: **a measured false-alarm rate may be scoring correct
  refusals as errors.** The matched read's false-alarm conclusion is
  weakened pending an audit of the remaining control refusals.

## What was audited

Two substrates flagged `strong-reference-noisy`, where the second strong
reference (`claude-sonnet-5-high`) refused the control arm that the first
(`agy-gemini-3-7-flash-high`) cleared. Both are real striatum dispatch
subjects that passed review and reached `fate == final`. The reference was
re-run against each **unmodified** artifact and asked for its reasons.

### 1. `passes/stalls-need-no-judgment/d/design` (55.7 KB)

Refused at `#el:standing-guards`. The design states, of the four standing
guards, that there are "four programs **at exactly the registered
entrypoints** … evaluator nodes `guard-plan-totality`,
`guard-frontier-diagnosis`, `guard-oscillation`,
`guard-quiescence-blocking-scope`". Clause C7 of the same document states
that "programs exist **at exactly** `go run
./tools/standing-guards/stall-plan-totality`, `…/stall-frontier-diagnosis`,
`…/stall-oscillation`, `…/stall-quiescence-blocking-scope`".

Verified in the artifact text: `guard-*` in one section, `stall-*` in the
other, each qualified "at exactly". A reconciliation exists — a registry
node id and a program path are different namespaces — but the design never
states it, and "programs at exactly the registered entrypoints … evaluator
nodes `guard-*`" conflates the two. As a review finding this is defensible;
it is not obviously a reviewer error.

### 2. `exhaustion-needs-no-judgment/packets/p10/operator-runbook` (12.9 KB)

Refused at `#el:closed-vocabulary`. The runbook makes both terminal
categories — `quota_spend_limit` and `auth_security_failure` — members of
the `capacity_observation` enum that "write a starvation mark", and
`#el:mechanical-recovery` describes that mark as TTL-bound, judged from
`observed_at` and `validity_window`, after which "the backend re-enters the
candidate set".

But the runbook's own operator guidance separates them sharply: for
`quota_spend_limit`, "do nothing" — the window refills; for
`auth_security_failure`, "do the credential work", with exactly one lawful
escalation and resolution by credential remediation. A quota exhaustion
self-heals with time. A broken credential does not. If both write the same
self-clearing mark, the scheduler re-admits a backend whose credential is
still broken.

Also defensible, and operationally material.

## Why this matters more than two cases

The instrument's control arm rests on one assumption: an artifact that
reached `fate == final` is sound, so any refusal of it is a false alarm. The
tuner recorded that assumption's weakness and accepted it as biased in the
safe direction — "a latent defect nobody found would cost a reviewer a false
alarm it did not deserve", penalising good reviewers rather than flattering
them.

These two audits suggest the bias is not merely theoretical. If a control
carries a real defect, then:

- the reviewer that refuses it is **detecting**, and is scored as if
  erring;
- the reviewer that clears it is **missing a defect**, and is scored as if
  correct;
- `discrimination = catch − false_alarm` subtracts a correct behaviour and
  rewards an incorrect one, for that case.

The direction of the error is the opposite of what a benchmark should
tolerate: it flatters the less careful subject.

## Effect on the matched read

The read reported Gemini 0 false alarms against Sonnet 5 of 13
(p = 0.062, not established). Two of Sonnet's five control refusals have now
been audited and both look like correct catches on artifacts Gemini cleared.
That does not reverse the comparison — three refusals remain unexamined, and
the two audited findings are defensible rather than indisputable — but it
does mean the false-alarm gap **cannot be read as a reliability advantage
for Gemini** until the remaining refusals are audited. The catch-rate
result (p = 0.375) is untouched.

The read is amended accordingly. No claim is retracted, because the read's
stated conclusion was already that neither difference is established.

## Corrective

1. **Audit before scoring a false alarm on a strong reference.** A control
   refusal by a binding with demonstrated discrimination is a hypothesis
   about the substrate, not a settled error. Cheap: it is one re-run of the
   control arm with reasons recorded.
2. **Record the reasons the first time.** Validation rows now persist the
   control and mutant verdicts and each finding's anchor, severity, and
   rationale. Adjudicating these two required paying for the calls twice
   because the boolean was stored without the argument behind it.
3. **Substrate disposition.** Both substrates are flagged: their controls
   are not demonstrably sound, so cases built on them cannot score a false
   alarm against any binding until a human adjudicates the two findings.
   They are not removed — a substrate with a real latent defect is valuable
   once the defect is known, because it becomes a case with a *known*
   answer.
4. **Open question for the Principal.** If either finding is genuine, it is
   also a finding about striatum: two artifacts carrying internal
   inconsistencies passed review and reached `final`. That is a statement
   about the review pipeline, not about the case pool, and it is outside
   CAPLAB's authority to adjudicate.
