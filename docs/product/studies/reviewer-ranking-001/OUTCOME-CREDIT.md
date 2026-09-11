# Credit useful defect reports and identify incorrect blockers

Status: prospective development policy selected by the primary agent under
ADR 0026 and ADR 0066. Freeze this policy before its implementation challenge.
It accepts no scorer, historical assessment, case corpus or ranking. Earlier
failed assessment criteria and results remain unchanged.

## What earns a catch

A catch is an active, sufficiently specific report of an independently
established, actionable defect attributable to the reviewed change. The report
must identify the relevant behavior or mechanism and circumstance well enough
to direct corrective work. The assessor may verify that report; it may not
discover a different defect and give the reviewer credit for it. Keywords,
location overlap, a generic warning, a correct fix without a reported defect,
or the number of propositions are not catches.

Match each active finding to each independently established defect root cause
as supported, contradicted or unresolved. The match includes specificity,
applicable requirement violation and change attribution, not just observed
behavior. These are evidence judgments requiring separate validation. An
assessor's proposition status cannot be copied into this relation directly.

Both asserted and uncertain reports can earn a catch if they meet this rule.
Honest uncertainty in the author's wording is separate from whether evidence
establishes the specific defect. A withdrawn report earns no active catch;
preserve its original text and factual assessment for audit. Advisory reports
can earn catches. Count each root cause once per reviewed change regardless
of duplicate occurrences or multiple descriptions.

A supported core defect can earn credit despite an incorrect incidental
claim, provided removing that claim leaves the reported defect actionable
and change-attributable. A wrong trigger, nonexistent requirement, wrong
causal location, or false assertion of introduction is material when the
remaining report no longer identifies an eligible defect. The full report
and all errors stay visible; this rule does not endorse the incidental claim.

## What establishes an incorrect blocker

Assess the finding's actual blocking rationale, preserving its stated
scenario and author-reported acceptance effect. Its blocking basis is:

- supported when independent evidence establishes a sufficient remaining
  rationale for blocking under the task's applicable acceptance requirements;
- contradicted when evidence defeats that rationale and no independently
  supported or unresolved material rationale remains within the finding;
- unresolved when the rationale, requirement, applicability or relevant
  evidence cannot yet settle the question.

A refuted incidental premise does not make the entire finding an incorrect
blocker. A genuine unrelated defect elsewhere in the review does not excuse
a separate incorrect blocking finding. Do not infer a severity or blocking
policy merely from a reproduced behavior. Validate the relation between the
reported rationale and the acceptance requirement separately.

The report-level outcome is whether at least one active finding is an
independently refuted blocker. This incidence does not multiply when a false
blocker is repeated. Preserve individual findings for workload analysis;
incidence alone does not measure the burden of many incorrect advisories.
No ranking based solely on this policy is authorized. A comparison design
must also address completion and advisory burden so an empty failed review
or a flood of speculative advisories cannot win by avoiding explicit blockers.

An uncertain author who explicitly blocks is still blocking. A report marked
advisory contributes no false-blocker event; an undetermined acceptance effect
retains possible blocking instead of silently becoming advisory. Withdrawal
removes the active blocker, without rewriting its prior factual assessment.

## Missingness and policy arithmetic

For each known defect, the catch lower bound is one if any active finding has
a supported match. Its upper bound is one if a supported or unresolved match
exists. Otherwise both are zero. Known-defect misses have the complementary
bounds. This is a logical uncertainty interval, not a confidence interval.

For false-blocker incidence, a contradicted basis with explicit blocking gives
a lower bound of one. An unresolved basis with explicit blocking, or a
contradicted/unresolved basis with undetermined acceptance effect, permits an
upper bound of one. Supported blocking, advisory findings and withdrawals
do not create a false-blocker event. Do not convert unknown evidence into
fractional credit or false-positive labels.

All findings and every known-defect match must be accounted for. A missing
matrix entry or finding is an incomplete assessment, not a miss or a correct
clearance. An unavailable/failed review is not a completed empty report and
must be represented by the attempt/missingness system, not passed to this
completed-report projection. Native completion and capture authenticity
remain prerequisites outside this arithmetic.

Unresolved potential new defects remain explicit. These bounds cover only
the supplied known-defect set and cannot establish exhaustive recall or a
clean case. Investigate new valid findings independently, update the common
case truth basis through an authorized admission, and reassess every binding
against that same basis. Neither removal from the denominator nor credit
based solely on novelty is allowed.

## Development implementation and validation authorization

Authorize `scripts/reviewer_credit_policy.py`, its focused tests, and local
repository checks. The function projects this policy from supplied outcome
warrants and a complete original report. It does not validate their truth,
the completeness of a warrant's material premises, native completion, custody,
or admission authority. Its output must remain explicitly ineligible for
ranking even if all supplied judgments are supported. Accepting model labels
or structural checks as verified warrants is prohibited.

Tests must exercise outcome consequences: an incidental error that leaves a
valid catch; a contradicted material rationale; uncertainty that cannot become
a clearance; duplicates and withdrawals; incomplete accounting; and newly
reported unresolved defects. Constructed warrants test policy arithmetic,
not semantic assessor accuracy. No live model call, original-program execution,
historical rescoring, corpus admission or historical artifact rewrite is
authorized. This authorization ends when the implementation is verified or
the owner changes the goal.

The next validation must independently establish these warrants on natural
reports and challenge whether materiality judgments alter actual catches or
incorrect blockers. A perfect reproduction of proposition formatting is
neither required nor sufficient for this outcome. A ranking still requires
case truth, clean controls, calibrated assessment error, representative
assignments, sample-size rationale, practical effects and uncertainty rules.
