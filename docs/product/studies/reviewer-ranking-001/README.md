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
