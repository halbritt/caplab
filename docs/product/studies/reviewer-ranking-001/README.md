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
Six have bounded change-relevant behavioral evidence; two additional trees
ran only as other cases' bases, and 24 changes remain behaviorally unverified.
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
