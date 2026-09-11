# Define which assessment judgments affect reviewer outcomes

The development scorer now has an explicit policy for projecting catches,
known-defect misses and incorrect-blocker incidence from supplied outcome
judgments. This closes a gap between proposition assessment and the desired
review outcome. It does not establish the truth of those judgments or accept
a reviewer-ranking instrument.

The [prospective policy](../product/studies/reviewer-ranking-001/OUTCOME-CREDIT.md)
was selected under ADR 0026 and ADR 0066 before implementation. It preserves
the goal: useful reports of actionable, change-attributable defects, with
independent evidence for incorrect blockers. Prior assessor failures retain
their original criteria and dispositions; no historical review is rescored.

## Why proposition correctness is not the outcome

The recent [scheduler challenge](verification-2026-09-10-reviewer-scheduler-assessment.md)
passed representation checks but failed full proposition coverage and
evidence-phase explanation. Those observations remain valid. The new policy
asks the additional question required for ranking: could the error change
whether a reviewer caught an actionable defect or issued an incorrect blocker?

| Development observation | Required outcome reasoning |
| --- | --- |
| A report identifies the accepted incomplete scheduler decision and exaggerates source-record loss | Determine whether the independently established core still supports the reported corrective work. A false incidental consequence does not automatically erase a catch or make the entire blocker incorrect. |
| An assessor omits the reported selection counterfactual | Record incomplete decomposition. Separately determine whether that premise is necessary to establish the actionable defect and its attribution; do not equate an annotation omission with a missed reviewer catch. |
| Pre-append state is cited as proof of post-append retention | The evidence link is invalid for that claim. If a finding's blocking rationale depends on later deletion, obtain the proper later record before establishing or refuting it. True retention demonstrated elsewhere does not repair the citation. |
| The scheduler emitter omission predates the patch, but the patch newly permits the incomplete decision to append | Distinguish an inherited mechanism from a newly exposed violation. A mistaken chronology is material when the remaining report no longer identifies the eligible change-related defect; inherited wording alone is not an automatic catch or miss. |
| A supported source mechanism differs from an authored expected label | Inspect that argument against the original code and its scope. Label agreement cannot define the correct outcome. Actual production execution may remain unobserved. |
| The newsroom assessor leaves optional-RSS collection requirements unresolved | This can alter whether an actual natural finding matches a known actionable defect. Resolve the original applicable requirement; do not award credit from behavior alone or label the finding false because evidence was not understood. |
| An advisory compatibility report has a refuted version premise and an unknown deployment host | Preserve both facts. The author's advisory effect does not become a false blocker. Its possible advisory burden remains a separate issue for the comparison design. |

These are prospective materiality requirements grounded in the retained
development observations, not new score assignments. The original
[newsroom requirement basis](../product/studies/reviewer-ranking-001/REQUIREMENT-BASIS.md)
and original source/witness evidence remain authoritative for their bounded
facts. A policy cannot turn an assessor's judgment into independent truth.

## Implemented behavior

`scripts/reviewer_credit_policy.py` exposes `project_completed_review` for
one complete original document, the common known-defect IDs and a complete
matrix of supplied outcome warrants. Each warrant preserves its judgment
record reference, match evidence statuses, blocking-basis status and explicit
new-defect uncertainty. It is a separate input contract from v2 propositions;
no automatic conversion from proposition labels is implemented.

Both asserted and uncertain active findings can earn a catch when independent
evidence establishes the specific actionable defect. Advisory findings can
also earn catches. Withdrawals remain in the output but contribute no active
catch or blocker. Root-cause identity deduplicates catches, and report-level
false-blocker incidence does not multiply repeated false findings. A separate
incorrect blocker remains visible even when the same report catches a real
defect.

Unresolved evidence produces logical lower/upper bounds, not fractional
credit, confidence intervals or false-positive labels. Undetermined acceptance
effect retains possible blocking. Missing finding assessments, missing defect
matches, conflicting identities and unsupported status values raise errors;
they do not become zeros. Unresolved new findings remain explicit even when
the known answer key is empty.

The function preserves the complete document and supplied warrants. It marks
their truth as unverified and its output as ineligible for ranking, and
establishes no whole-case cleanliness. Its arithmetic assumes the caller has
an authentic completed report; the function does not verify native completion,
capture provenance, semantic materiality or evidence admission. An absent
review is rejected, but calling a fabricated empty document a completed
report remains an upstream violation, not something these calculations prove
impossible.

## Validation and limits

Seven focused tests exercise active/withdrawn effects, uncertain and advisory
catches, duplicate root causes, separate incorrect blockers, missingness,
new findings and the preservation boundary. An exhaustive oracle enumerates
every concrete resolution of 729 combinations of six evidence statuses for
two findings and two defects, including undetermined blocking. The projected
catch/miss and blocker bounds equal those concrete extrema. The oracle uses
explicit possible worlds, separately from the implementation's interval rules.

These tests use constructed warrants. They validate policy arithmetic and
input accounting, not whether an agent correctly decides what is material,
matches a natural report to a defect, or establishes a blocking rationale.
Tests do not call a model, invoke original projects or generate reviewer
performance observations. The Test Guard pass found no mocked internal calls,
prompt-wording assertions or framework-only tests. The exhaustive check
protects multi-defect arithmetic beyond the directed single-defect examples.

The corrected full `make check` passes **1,578 tests in 204.122 seconds**, with
seven skips. The first full invocation used the repository virtual environment
without its declared PyYAML dependency; eleven existing modules could not
import, and that log is preserved. Installing the existing hash-locked test
requirements added PyYAML 6.0.3 without changing the lockfile or product code.
The second invocation used the same virtual environment and passed. The
[development receipt](../product/studies/reviewer-ranking-001/credit-policy-development-receipt.json)
pins the policy, implementation, tests, environment and both full-check logs.
Private custody is
`/home/halbritt/.local/share/caplab/reviewer-ranking-001/development/credit-policy-1`.

The v1, v2 newsroom and scheduler assessor final outputs retain their original
hashes. Supplied judgment references are preserved but not authenticated or
bound to source content by this arithmetic; those checks remain part of the
required evidence-warrant verification boundary. No outcome warrant may be
reused against changed report text merely because a finding ID is unchanged.

No model invocation, corpus admission, historical rescoring or qualification
occurred. The preceding exposed development cases remain unsuitable for
held-out ranking. Comparison design must still account for completion and
incorrect advisory workload: false-blocker incidence alone would leave a
speculative-advice strategy insufficiently constrained.

The evidence-backed doctrine packet `pkt-cdafd666a23adaf1` supplied the
applicable measurement, repository-precedence and evidence-before-intervention
guidance; the release-state gate passed. Semantic warrant validation,
representative cases, clean controls and comparative uncertainty are material
unmet obligations. No architecture or datastore change was needed.

The next validation target is the evidence warrant needed for the actual
catch/blocking outcome on natural reports. Preserve proposition errors, but
distinguish outcome-changing errors from incidental ones. Keep the v2 schema
unchanged; do not require perfect auxiliary annotation as a substitute for
measuring reviewer usefulness.
