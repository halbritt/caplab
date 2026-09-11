# Separate propositions before assessing review findings

Status: prospective development contract selected by the primary agent under
ADR 0026. It follows the [failed first challenge](../../../records/verification-2026-09-10-reviewer-evidence-assessor.md).
No v2 assessor has run, and this document accepts no scorer or ranking.
The original fixture, prompt, expectations and checker remain frozen.

The intended outcome remains useful first-pass code review: detect actionable,
change-attributable defects and avoid independently refuted blocking findings.
Assessment must establish what the reviewer claimed and what independent
evidence supports before any policy assigns credit. Citation style, matching
labels, output length and agreement between models are insufficient.

## Output contract

Retain each complete original finding and its content identity. Each finding
occurrence has its original document/finding IDs, reported `claim_status`,
`acceptance_effect` and within-report `duplicate_of`. These fields do not change
when the assessor disagrees with the author. Preserve report limitations.

Represent a finding with separately identified propositions. For each, record
the original field/text span, the concrete proposition, its scenario and scope,
its role, its evidence assessment, evidence locators and an explanation.
Splitting a finding must preserve every material assertion and qualification;
the decomposition itself needs validation.

| Role | Question the evidence must answer |
| --- | --- |
| Behavior | What happens under the stated input, configuration and environment? Separate observed behavior from a predicted mechanism or consequence. |
| Requirement | What applicable source establishes that the behavior violates an expectation? A previous implementation or an assessor-authored inventory alone cannot supply the requirement. |
| Change attribution | What original base/change contrast supports introduction or worsening by this change? Added source can establish a source-level change without establishing its runtime consequence. |
| Applicability | Is the condition relevant to the declared task population, supported configuration or deployment? A possible older host is different from an observed target host. |

Each proposition has `supported`, `contradicted` or `unresolved` evidence
status, with named scope. These statuses describe evidence for that exact
proposition; they do not encode severity or permission to block. Preserve
conflicting evidence and missing information. For unresolved propositions,
name the missing evidence and the bounded observation or requirement decision
that could resolve it. Evidence absence is not contradiction.

Text with no concrete defect proposition is explicitly recorded as such and
retained without inventing propositions. Do not use a whole-finding
`mixed`, `refuted_claim` or similar field as an input to reviewer scores.
Any later rule combining propositions into actionable-defect credit must be
separately frozen, justified and validated. A refuted incidental premise does
not automatically make an entire blocker incorrect; the blocking rationale
and remaining support must be assessed in their stated scenario.

## Evidence contract

Each evidence reference names the exact artifact identity, path and locator,
the proposition it bears on, whether it supports or contradicts it, and why.
The reference must resolve within the authorized corpus and retain source
commit/hash and custody linkage. Equivalent evidence can be located in an
exact patch or its source tree. Filename-prefix membership cannot stand in
for checking what the cited bytes establish.

Original execution, source inspection, requirements and assessor inference
remain distinguishable. Runtime claims need appropriate execution evidence
and controls; source-level claims may be established by the exact source
contrast. Do not execute a new witness unless a separate authorization names
its effects. A packet inventory can establish which experiments were supplied;
it cannot establish what behavior the product requires.

## Required contrasts for the next challenge

Freeze the schema, decomposition expectations, evidence basis, acceptance
criteria and missingness rules before execution. Include the following known
development contrasts and reserve previously unexposed reports from other
changes and families to test whether the method generalizes.

| Contrast | Required assessment behavior |
| --- | --- |
| Same causal evidence cited as exact patch or current source | Preserve the same scoped proposition assessment when both citations establish it; reject an unrelated but existing locator. |
| Trace directory per successful capture versus every daily run | Support the narrower creation behavior; preserve the early-return counterexample and unresolved retention requirement. Do not claim a measured disk-impact outcome. |
| HTTP error-body removal versus diagnostic obligation | Preserve the source change separately from an unresolved requirement to retain provider bodies. |
| Pre-v250 universal cutoff versus unknown deployment host | Contradict the universal cutoff using v244; preserve uncertainty about actual target-host applicability and the original advisory stance. |
| Exactly specified v244 rejection claim | Contradict that predicate without importing a different, unspecified host scenario. |
| Confirmed RSS finding versus reversed flag | Support or contradict the behavior using the matching configured controls, retaining requirement and attribution evidence. |
| Duplicate, withdrawn and keyword-only variants | Preserve occurrence identity and author stance without multiplying defects, erasing a true proposition, or inventing a claim. |
| Plausible behavior with unrelated requirement or base-only cause | Leave the missing component unresolved; do not manufacture an introduced defect. |
| Previously unknown valid finding | Permit evidence-backed addition after independent investigation; absence from the initial answer key cannot make it false. |

For this bounded challenge, every frozen contrast must retain the material
propositions, scope, original stance and evidence relationships. Structural
checks report only structure. Independent behavioral witnesses and exact
requirement/source inspection supply the truth basis. Record all semantic
failures and inconclusive results; do not revise expectations after output.
These development examples do not become held-out reviewer comparisons.

The next execution requires a new bounded authorization. The first attempt's
consumed allowance provides no retry. Passing a future challenge would support
only the named assessment scope. Corpus admission, broader validity, reviewer
ranking policy and comparative uncertainty remain separate work.
