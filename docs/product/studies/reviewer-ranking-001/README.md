# Reviewer ranking: development contract

Status: instrument development. No frozen preregistration, admitted corpus,
live reviewer measurements, or accepted ranking exists for this study.
Authority: [ADR 0066](../../../decisions/adr-0066-reviewer-ranking-outcome-selection.md).

## Purpose and outcome

Determine which exact native reviewer configurations are more useful for
first-pass code review on the owner's actual software changes: finding
actionable defects while avoiding incorrect blockers. The subject receives
the proposed change, its base, relevant repository context, acceptance
requirements, and ordinary review tools. It must discover the defect; the
prompt must not supply a known bug report, failing witness, fix, answer key,
or a list of suspect locations.

Primary outcomes are independently confirmed, change-attributable defects
caught or missed, and independently refuted blocking findings. Count distinct
root causes; copied findings and repeated versions are not extra catches.
Preserve all findings, including issues outside the initial answer key.
Missing evidence makes a finding unresolved, not false. A failed attempt is
not a correct clearance. Report latency, cost, and completion separately.
Choose the ordering rule and tradeoffs before inspecting ranked results.

Correctly detecting an arbitrary planted marker, matching answer-key wording,
producing valid JSON, writing many findings, making a repair, or agreeing with
another model does not establish this outcome. Mechanical output parsing may
be necessary; its success is never a substitute for finding the defect.

## Required gates

| Gate | Evidence required before passing |
|---|---|
| Population | Fixed census of actual changes, reasons for every selection/exclusion, repository/language/size coverage, and relationship between this frame and the intended review workload. Report changes rejected because they are hard to verify. |
| Case truth | Exact base and reviewed trees; requirement that predates reviewer output; executable behavioral witness with expected/observed results; localized causal connection between change and violation; independent reference or specification witness. A fix commit's title is not truth. |
| Clean controls | Matched real changes or alternative valid changes, with explicit acceptance properties and evidence covering them. Test success alone is insufficient for a global clean label. New valid findings on a supposed clean control invalidate that label. |
| Scoring validity | Blinded scoring against independently established outcomes. Exercise true findings, plausible wrong findings, wrong-location guesses, copied keywords, duplicate reports, unrelated genuine defects, malformed outputs, and unresolved claims. No keyword-only credit or model-consensus truth. |
| Native execution | Enforce `native-agent-systems.json`; pin harness/model/configuration and observed identity; isolate answers and other trials; equalize meaningful task access, permissions and budgets; retain authentic tool/final output and all failures. |
| Pilot validity | Demonstrate that the task still requires substantive review, lacks answer leakage, and permits accurate scoring. A ceiling result does not justify selecting only cases that favor a preferred binding. Diagnose and freeze a new instrument version before further measurement if needed. |
| Comparison | Frozen assignments, case grouping, sample-size rationale, missingness, practical effect threshold, multiple-comparison rules, and uncertainty method. Repetitions estimate variability within a case, not independent case count. |
| Generalization | Unused cases separated by incident, with repository/family separation where claims require it. Compare held-out performance and coverage to development results. Public-source memorization and prior model exposure remain explicit risks. |
| Ranking acceptance | Reproducible report, complete outcome accounting, uncertainty and sensitivity to unresolved labels and cost tradeoffs. Support ordering only where evidence does; otherwise publish ties or incomparability. Do not claim the broader goal complete using a narrow diagnostic success. |

## Autonomous verification boundary

Agents can propose candidate cases, investigate findings, and construct
reproductions. Their proposals remain inferences until an independent basis
supports the assertion. Separate contexts alone do not establish independence.
For each case record where the expected behavior came from, whether the
author saw the candidate output, and how the verifier could fail independently
of the reviewed implementation. Keep hidden witnesses outside subject mounts.

A finding that cannot be established or refuted automatically remains in the
report and uncertainty analysis. If those cases prevent a useful ranking,
continue improving independent verification. Do not silently turn this into
a benchmark of only toy algorithms, easy-to-test bugs, or witness-writing.

## Current work and completion evidence

1. Census real changes without outcome-dependent selection.
2. Validate actual defect and control candidates against original requirements.
3. Build and challenge scoring on those cases before live reviewer pilots.
   A separately authorized, unscored native output probe may inform the
   scoring interface. It cannot supply pilot or ranking measurements; see
   [the bounded output probe authorization](../../../records/authorization-2026-09-10-reviewer-output-probe.md).
4. Complete the native execution path needed by the selected configurations.
5. Freeze and execute the study, analyze held-out evidence, publish the ranking
   with its limits, and perform a requirement-by-requirement completion audit.

The census is reconnaissance, not an experimental admission manifest. None of
its rows is labeled correct, defective, representative, or independently
adjudicated merely because the census succeeded.

## Initial feasibility selection

Before opening candidate source content, select two changes per repository
and changed-code-line stratum: 0–20, 21–100, 101–500, and 501+ lines. Keep
non-text changes in a separate stratum if present. Use the lowest SHA-256
values of `reviewer-ranking-001-feasibility/v1`, repository name and commit
ID, separated by NUL. Select without replacement; retain the remainder of
every stratum in the selection record. Do not substitute an easier case when
a selected change lacks a mechanical truth basis.

This is a coverage feasibility sample, not a power calculation or the final
ranking sample. It deliberately samples repository/size strata rather than
weighting by raw commit frequency. Preserve those counts for later analysis;
do not treat the selected cases as a uniform random sample of all commits.
These inspected cases are development material and cannot become held-out
evidence. `scripts/reviewer_feasibility_sample.py` reproduces this selection
from the hash-checked census.

The [coverage projection](FEASIBILITY.md) accounts for all 32 selected changes.
Thirteen have bounded change-relevant behavioral evidence; two additional trees
have only baseline-witness evidence, and 17 changes remain without a
change-specific behavioral witness. Test-readiness runs do not promote cases
into these witness categories.
These are coverage states, not case admissions or independent defect counts.

## Verified development outcomes

The [Council provider-lifetime reproduction](../../../records/verification-2026-09-10-reviewer-timeout-outcome.md)
establishes actual timeout/cancellation violations in the original runtime and
the sampled repair's base, with ordinary-completion controls and a repair
that satisfies the tested properties. It is one related failure family with
36 repeated diagnostic observations. It supplies no whole-patch clean label,
reviewer attribution, experimental admission, or ranking. The other sampled
changes and overall coverage remain open.

The [native output feasibility probes](../../../records/verification-2026-09-10-reviewer-output-probes.md)
produced no usable final review: the first failed execution preparation, and
the second timed out with its transcript withheld by the privacy guard.
Applying that guard to the authorized task itself rejected six files. Capture
validity must be corrected and challenged before further reviewer calls.
These failures supply no reviewer score or attribution.

The [third output probe](../../../records/verification-2026-09-10-reviewer-completed-output.md)
completed with intact native capture after the guard correction. It reported
one new issue and did not report the known timeout family. A separate witness
corroborated the new report's scan-limit/error-conversion behavior; its broader
defect interpretation remains unresolved. No score is assigned. Project
dependencies must be prepared and pinned before comparative reviewer runs.

The [effort-control investigation](../../../records/verification-2026-09-10-reviewer-effort-control.md)
adds a selected real change with identical parser outcomes across 135 inputs
per revision and a compiler-confirmed unreachable fallback. This supports
named preservation properties, not an admitted whole-patch clean label.

The [dependency readiness investigation](../../../records/verification-2026-09-10-reviewer-dependency-readiness.md)
installed the four Council revisions' locked dependencies. Builds complete,
but full test readiness remains unresolved. The effort base/change have the
same 134 failing test headings in the corrected namespace; those shared
failures do not establish change-attributable defects or reviewer quality.

The [GitHub release-loss witness](../../../records/verification-2026-09-10-reviewer-github-release-outcome.md)
adds a second real failure family: the original scanner and sampled repair
base lose a successful release response at low quota, while the repair keeps
it. All 36 corrected observations have valid HTTP inputs and the predicted
contrast. Earlier invalid fixtures are preserved. The original introduction
is outside the census window, so it cannot become an in-population defective
review task merely because this development witness succeeded. Reviewer
scoring, remaining case coverage and held-out comparisons are still open.

The [claim-interpretation experiment](../../../records/verification-2026-09-10-reviewer-claim-interpretation.md)
tested one actual review and 17 adversarial variants without exposing case
truth. Four of 18 interpretations added inferred opposing stances beyond the
frozen expected mappings; all positive claims, unknown-claim presence and
locations were retained. This exposes a reported-versus-inferred distinction
that must be resolved before scoring. Literal quote checks also do not prove
semantic support. This is an unaccepted interpretation prototype, not a
free-text reviewer scorer or a ranking measurement.

The [revised interpretation and outcome assessment](../../../records/verification-2026-09-10-reviewer-outcome-assessment.md)
matches all 24 frozen document mappings and six assessment cases. Introduced
defects, inherited behavior, tested refutations, unresolved locations,
duplicates and omitted findings remain distinct. The second attempt's partial
capture is preserved and unassessed. A new attempt retained complete readable
capture by omitting opaque encrypted reasoning with hash receipts before the
unchanged privacy guard. These exposed, authored challenges validate a bounded
development path; unseen natural reviews, new-finding investigation and broad
case coverage are still required before accepting a general scorer.

The [Go scheduler witness](../../../records/verification-2026-09-10-reviewer-scheduler-outcome.md)
adds a third real failure family across a sampled repair and its precursors.
The repair resolves the predicted-versus-evaluated schema mismatch, but its
v2 record omits an exhaustion observation that changed placement from a
supervised remote backend to local fallback. Original encoding and decoding
accept that record. The omission predates the sampled repair; the new
predictor exposes it through a serializable envelope. This is record-boundary
and counterfactual placement evidence, with full live graph behavior still
open. It prevents treating the sampled repair as a verified clean control.

The [original Driver graph witness](../../../records/verification-2026-09-10-reviewer-scheduler-graph-outcome.md)
now reproduces the missing input through decision creation, lane binding,
graph reopening and a fresh Session fold. The repaired local-fallback decision
passes those paths without its causal exhaustion observation; the supervised
control retains it. Ordinary, unrecognized-message and expiry controls also
complete. Twenty repeated observations extend the same failure family, with
zero backend dispatches. This closes the graph admission/reopening question
for the tested scenario; case admission, broader recovery behavior and reviewer
ranking remain open.

The [CAPLAB pool transport witness](../../../records/verification-2026-09-10-reviewer-pool-transport-outcome.md)
executes another fixed-sample change through the original subprocess and pool
aggregation path. The introduction/base silently send oversized argument
prompts to unread stdin and count pairs with absent responses. The repair
fixes those paths but still counts a parseable object without a verdict.
Endpoint byte receipts and original summaries corroborate 54 repeated
observations; no scripted endpoint is treated as a reviewer. The ancestors
are in the census but were not independently selected in the fixed sample.
This expands case feasibility without admitting a corpus or accepting a ranking.

The [publication-date witness](../../../records/verification-2026-09-10-reviewer-publication-outcome.md)
uses the real installed blogwatcher binary and a local feed to exercise the
selected newsroom repair. The original base loses known calendar dates,
admits stale/future RSS entries and displays a non-UTC timestamp seven hours
off. The repair preserves precision and the timestamp's meaning, applies the
window, and resolves configured tilde history paths. Original CLI output,
curator input and producer queue preservation are retained. The producer's
modified-build metadata is disclosed. These verified properties support a
bounded control candidate; the whole patch and reviewer ranking remain
unaccepted.

The [Reddit recovery witness](../../../records/verification-2026-09-10-reviewer-reddit-recovery-outcome.md)
executes the unchanged 180-second budget through real active HTTPS responses.
The selected large change completes both slow harvests after 190 seconds,
persists the response and marks it live. Ordinary completion, date filtering
and fresh-adapter pool reads pass. These observations cover named parts of
one large change. Its copied base is not an executed control, and the rest
of the change remains unverified.

The [prospective newsroom review and finding investigations](../../../records/verification-2026-09-10-reviewer-newsroom-natural-findings.md)
provide a complete natural review with original dependencies and passing suite
readiness. Of three reported findings, the optional-RSS/pool coupling is
independently reproduced as a new configuration defect. The lock finding
misapplies a publisher-exclusion requirement to a non-publishing harvester.
The HTML pacing claim remains unresolved in requirement scope and attribution;
its dispatch mechanics already exist in the base. The known recovery-deadline
family is absent from the final review. These are development assessments,
not scores from a validated semantic interpreter. The review supplies no
explicit blocking/advisory disposition, so no false-blocker rate is inferred.
The failed source preflight is preserved; a versioned guard correction lets
public `user_id` field names survive while retaining private-value protection.

The [finding-unit administration](../../../records/verification-2026-09-10-reviewer-finding-units.md)
corrects cross-finding location credit and introduces a
[native report contract](REVIEW-REPORT.md) with explicit acceptance effects.
One repeated native review produced an inspectable, explicitly blocking
partial-RSS-refresh claim. Its truth remains unresolved pending original-path
execution; the previously confirmed deadline and optional-RSS defects are
absent from its final report. Representation checks do not establish review
success, scorer acceptance or a comparative result. Case coverage is unchanged.

The [partial-refresh investigation](../../../records/verification-2026-09-10-reviewer-partial-refresh-outcome.md)
now confirms that review's new blocker through original CLI, HTTPS and SQLite
behavior. Partial RSS failure returns 0 with unavailable state, while healthy
collection, valid empty listings, successful RSS fallback and total failure
controls distinguish the scenario. Twelve executions repeat six conditions;
they add one failure family on the same change, not twelve cases. The prior
unresolved assessment is preserved. This closes that finding's behavioral
question without accepting a scorer or ranking.

The [launcher investigation](../../../records/verification-2026-09-10-reviewer-launcher-outcome.md)
adds a selected small CAPLAB change. Original shell execution preserves
environment export, tool selection, arguments, output-directory creation and
failure status across eight conditions. The downstream recorder executes no
supervisor or model. These bounded clean properties expand fixed-sample
coverage to eight changes; they do not admit a case or establish reviewer
performance. Three selected trees remain base-only and twenty-one changes
remain without a behavioral witness.

The [formatting investigation](../../../records/verification-2026-09-10-reviewer-formatting-outcome.md)
adds a selected small Striatum change. Both original files normalize
identically, the changed file restores formatter conformance, and the
original package builds produce identical test binaries. Both affected
tests pass twice on each tree. This is bounded preservation evidence about
the whitespace edit; historical capability assertions in those tests are
not accepted as current truth. Coverage is now nine bounded changes, three
base-only trees and twenty pending, with no case admission or reviewer score.

The [site presentation investigation](../../../records/verification-2026-09-10-reviewer-site-outcome.md)
executes the original builder and HTTP server at three adjacent revisions with
a pinned browser. The new mark renders within the tested mobile, tablet and
desktop widths, the SVG is published and served with the correct bytes and MIME
type, and the tested source-text and origin restrictions are preserved.
These are two selected changes in one related presentation sequence. Coverage
is now eleven bounded changes, three base-only trees and eighteen pending;
this is neither eleven independent incidents nor an admitted reviewer corpus.

The [first Claude native development review](../../../records/verification-2026-09-10-reviewer-claude-output.md)
completed with intact stream/session capture and a structured four-finding
report. Its optional-RSS finding matches independent original-path evidence;
two operational concerns remain unresolved, and a systemd version premise is
refuted by upstream release source. All findings are advisory, including the
explicitly uncertain compatibility concern. Native title generation used Haiku
and is retained in harness/cost accounting. This closes an administration gap
and supplies natural scoring challenges; it establishes no paired ranking.
Coverage and admission counts are unchanged.

The [blinded evidence-assessor challenge](../../../records/verification-2026-09-10-reviewer-evidence-assessor.md)
failed its frozen checks. The checker rejects valid exact-patch citations,
and the whole-finding labels overlap when a supported or refuted premise has
unresolved requirements or applicability. All eleven occurrences and reported
stances/effects survive. The preserved failure motivates a
[prospective proposition-based contract](EVIDENCE-ASSESSMENT-V2.md), which still
requires implementation and validation. No label-agreement percentage is
treated as semantic accuracy. Case coverage and admission remain unchanged.

The [proposition-based native assessment](../../../records/verification-2026-09-10-reviewer-proposition-assessor.md)
implements the v2 representation and tests it on 13 finding occurrences.
All original judgments survive, but five findings fail quotation, component
or locator checks. Content inspection also finds unsupported citation
explanations and inconsistent requirement scope. The frozen challenge fails;
eight structurally passing findings are not eight correct assessments.
Requirement interpretation and semantic validation remain open. The original
output, failed criteria and evidence are preserved; coverage is unchanged.

The [requirement-provenance investigation](../../../records/verification-2026-09-10-reviewer-requirement-provenance.md)
locates the publisher-specific requirement before the harvester's introduction
and verifies that its exact source was already available to both assessors.
The [development requirement basis](REQUIREMENT-BASIS.md) separates publisher
exclusion, optional-RSS collection, provider pacing and failed-refresh exit
behavior. Global HTML pacing remains unresolved. These prospective scope
interpretations preserve the prior failed results and create no ranking credit.

The [scheduler assessment challenge](../../../records/verification-2026-09-10-reviewer-scheduler-assessment.md)
tests the unchanged v2 contract on six authored reports about a different
real change. All 29 propositions pass representation checks, but content
inspection finds missing claim coverage and pre-append state cited as
post-append evidence. It also finds a credible source argument not anticipated
by the frozen expectations; label agreement cannot define correctness.
The native attempt is complete and preserved, but the semantic challenge
does not pass. Natural-report validation, case admission and the broader
ranking remain open; no additional schema expansion is selected.

The [outcome-credit policy](OUTCOME-CREDIT.md) defines when supported core
findings earn catches, when a blocking rationale is independently refuted,
and how unresolved evidence affects known-defect and blocker bounds.
Its [implementation verification](../../../records/verification-2026-09-10-reviewer-credit-policy.md)
separates outcome-changing assessment errors from incidental annotation
errors. The calculations preserve duplicates, withdrawals and new-finding
uncertainty; they do not verify the supplied judgments or establish ranking
eligibility. Natural-report warrant validation, authenticated completion and
advisory-basis validation, case admission and comparative study design remain
required.

The [natural outcome-warrant challenge](../../../records/verification-2026-09-10-reviewer-natural-warrants.md)
applies the credit policy to five natural findings and two authored controls.
Content inspection supports two distinct natural catches, the shared miss of
an unreported deadline defect, and refutation of both authored blockers. Three
unresolved advisories remain visible. Individual citation and auxiliary-field
limitations are preserved without turning them into incorrect outcome scores.
The complete reports and inspected warrants are bound to their source hashes
in a development projection. This is one exposed change, not an accepted scorer
or comparative measurement; broader validation and admission remain open.

The [brief-preview witness](../../../records/verification-2026-09-10-reviewer-brief-preview-outcome.md)
reproduces preview/live duplicate-selection divergence in a selected change's
base and verifies agreement after the change. Original history remains
byte-identical across previews, distinct content stays eligible, and empty
selections remain distinct from failures. Forty original component executions
use real local HTTP and SQLite, with controlled provider responses. This adds
one bounded change and named clean-control properties; the full main-digest
caller and whole-change cleanliness remain unverified. No case is admitted.

The [editorial-route witness](../../../records/verification-2026-09-10-reviewer-editorial-route-outcome.md)
checks dedicated credentials and reviewer exclusivity after writer fallback,
actual-writer family rules, separate review inputs and durable publication
control. Fifty-six source executions use original application paths with real
local HTTP and SQLite. All observed route and publication effects match the
frozen conditions. Three source URLs repeat one excerpt, and the executor
lacks its own unexpected-endpoint stop; both preparation departures are
recorded. These named control properties add one bounded change, with no
editorial-quality claim or case admission. Coverage is thirteen bounded, two
base-only and seventeen pending changes.

The [completion and advisory policy](COMPLETION-AND-ADVISORIES.md) and its
[implementation check](../../../records/verification-2026-09-10-reviewer-assignment-outcomes.md)
retain every declared assignment, reject conflicting case truth across
bindings, and distinguish completed, partial, unavailable and unobserved
reviews. A completed review awaiting assessment keeps known completion and
unknown quality. Separate advisory-basis warrants prevent refuted or unresolved
nonblocking findings from disappearing behind a zero false-blocker count.
Finding occurrences remain descriptive, with no claim to measure human effort.
This is prospective accounting and arithmetic; native authenticity, natural
advisory judgments and comparative performance remain unverified.
