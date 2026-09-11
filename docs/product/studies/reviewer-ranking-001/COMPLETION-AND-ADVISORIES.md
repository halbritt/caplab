# Keep incomplete reviews and erroneous advisories visible

Status: prospective development policy, revision 2, selected by the primary agent under
ADR 0026 and ADR 0066, before its applicable implementation challenge. This supplements
OUTCOME-CREDIT.md without changing prior warrants, assessments or projections.
No case, scorer, comparative design or ranking is accepted by this decision.

## Assigned work is the denominator

Retain every frozen assignment, its exact binding identity, case identity and
common case-truth version. Each assignment has exactly one recorded outcome.
An absent outcome row is an accounting error, not permission to drop a slot.
Repetitions retain the same case identity; they do not create independent
incidents. All bindings must use the same truth version and known defect set
for a given case. New defect admission requires a common update, not selective
credit for one binding. The projection checks the supplied identities; it
does not authenticate bindings, assignment sealing or case admission.

Record these evidence states separately:

| State | Meaning | Completion bound | Review quality |
| --- | --- | --- | --- |
| completed | Authentic complete response available within the task contract, with terminal native execution evidence | [1, 1] | Project complete supplied warrants; otherwise retain unassessed bounds |
| incomplete | Attempt ended with partial response or an unfinished review | [0, 0] | Unassessed bounds; preserve partial artifacts and reason |
| unavailable | Confirmed absence of a usable review, including launch or delivery failure | [0, 0] | Unassessed bounds; preserve failure evidence and reason |
| unobserved | Completion or capture has not been established | [0, 1] | Unassessed bounds; retain the unresolved slot |

Successful JSON parsing does not establish completion. A complete authentic
free-text response may be normalized through a separately validated extraction
process; formatting alone must not turn it into an unavailable review.
Conversely, well-formed output from an interrupted process cannot establish
native completion. Late output and malformed-output recovery need a common,
preregistered administration rule; this projection grants no retries.

A completed review can remain unassessed. Represent that state with
`status: completed` and `report: null`, retaining the authentic response and
assessment-pending reason by evidence reference. Completion is [1, 1]; quality
remains unassessed. Do not classify an assessor backlog as a reviewer failure.
If a report assessment is supplied, it must account for the complete response
and all warrants; a partially populated assessment is an error, not a clearance.

For any unassessed review, each known defect has catch bounds [0, 1], known
misses range from zero to the known-defect count, and both incorrect-blocker
and erroneous-advisory incidence have bounds [0, 1]. These describe missing
quality evidence, not fictional findings or delivered catches. A confirmed
absence may have zero delivered utility, but these quality bounds must not be
reported as delivered utility. Completion remains visibly zero. Retained
partial findings may support a separately authorized partial-output analysis;
this projection makes no assertion that they contained no useful information.

A completed empty review on a case with a known defect has a known miss. A
failed or unobserved review is not that empty review and cannot become a
correct clearance. On a case with no known defects, zero known misses still
does not establish whole-case cleanliness. Failure causes, latency, cost and
capture remain separate records; do not hide an administration failure as a
model reasoning error or exclude it after seeing the result.

## Erroneous advisory findings

An active nonblocking finding can earn a real defect catch under OUTCOME-CREDIT
and can independently be an erroneous advisory if a separate material
rationale is refuted. For each complete original finding, retain a separate
advisory-basis warrant: supported, contradicted or unresolved, with an evidence
judgment reference. Do not copy blocking-basis judgments: a suggestion may be
reasonable while being insufficient grounds to block publication.

The advisory basis is supported when independent evidence establishes a
sufficient task-relevant rationale for the finding as actually reported.
It is contradicted only when evidence defeats its material rationale with no
supported or unresolved material rationale remaining within that finding.
An optional improvement or a reasonable request to investigate uncertainty is
not erroneous merely because it is not an established defect. An unverified
claim is unresolved. An incidental error does not refute an otherwise valid
advisory. These judgments require semantic validation independent of the
reviewer; the arithmetic does not make them true.

Report-level erroneous-advisory incidence is one when at least one active
advisory has a contradicted basis. Its upper bound permits one if an advisory
or a finding with undetermined acceptance effect has a contradicted or
unresolved advisory basis. Explicit blockers use the separate blocker outcome;
withdrawn findings create neither active event. Preserve all original findings
and the complete warrant sets. Missing advisory warrants are an incomplete
assessment, not evidence of harmless advice.

This incidence cannot be multiplied by splitting or repeating one error.
Also expose active and withdrawn finding-occurrence counts and counts of
explicit advisory, blocking and undetermined effects. Those are descriptions
of the report, not estimates of human time, effort or harm. Combining many
claims into one finding can change occurrence counts, so they must not be
used as a validated workload scale. A ranking cannot reward verbose or
speculative advice merely because none of it explicitly blocks: advisory
error and uncertainty must remain comparison dimensions alongside defect
catches, incorrect blockers and completion.

## Comparison and validation boundary

These are logical bounds, not confidence intervals or probabilities. Bounds
for different outcomes may be dependent; their Cartesian product is only a
conservative uncertainty envelope. No scalar utility, exchange rate between
missed defects and advice, ranking threshold or population weighting is
selected here. A subsequent frozen comparison design must account for all
these outcomes, incident dependence, practical effects and statistical
uncertainty. It may only assert an ordering that survives material unresolved
outcomes and stated tradeoffs; otherwise preserve incomparability.

Authorize `scripts/reviewer_assignment_outcomes.py`, focused behavior tests,
local repository checks and a verification record. Retain this turn's policy
revisions, implementation, tests and check logs in
`/home/halbritt/.local/share/caplab/reviewer-ranking-001/development/assignment-outcomes-1`,
with exact hashes and a development receipt. This names retention of this
implementation challenge, including its first-policy checkpoint; it permits
no import or rewriting of older native reports. The projection consumes
complete declared assignments and supplied observations; it verifies structural
accounting and policy arithmetic only. Preserve all originals in its output
and label evidence truth, completion authenticity and ranking eligibility as
unverified. No live model call, historical import, original-program execution,
historical rescoring, evidence admission or historical rewrite is authorized.
This authorization ends when the implementation challenge is verified or the
owner changes the goal.

Challenge a failed and an empty review on the same known-defect case, omitted
assignments, contradictory case truth across bindings, speculative advisory
flooding, valid optional advice, uncertain acceptance effects, duplication,
withdrawal and complete warrant accounting. Constructed examples establish
arithmetic behavior only. Natural advisory-basis validation and authenticated
native attempt integration remain material follow-up obligations. The retained
Doctrine packet pkt-cdafd666a23adaf1 supports evidence before scoring and bounded
authority; it does not establish those missing semantic or empirical outcomes.

## Development revision history

Revision 1 required complete assessment in the completed-state definition.
Its implementation challenge passed but source review identified an omitted
state: native completion known while assessment is pending. Revision 2
separates those facts, permits a null assessment for a completed review, and
requires a dedicated test. This is an explicit prospective policy correction,
not a changed judgment about any historical reviewer. The original policy,
implementation and tests are retained with their first-check evidence in the
verification record. Prior native reports, warrants and projections remain
unchanged.
