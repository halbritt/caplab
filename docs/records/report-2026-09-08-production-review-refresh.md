# Production review follow-up with verified baseline continuity

## Authorization before execution

The primary agent, acting under ADR 0026 and the continuing CAPLAB improvement
request, authorizes one fresh read-only Striatum ledger export and one
report-only follow-up using the existing production canary procedure. This
implements the confirmed September 7 review-instrument disposition.

Source checkout: `/home/halbritt/git/striatum-next`, observed commit
`5ea87ca65c1bd25f228c0447110d991a3f0de8c8`. Source command:
`striatum -json ledger cat`, from that checkout. The export copies historical
ledger bytes into a new private local directory under `/tmp`; that exact
historical-evidence copying effect is authorized. Retain its path, hash,
event bounds, export exit status, source checkout commit and working status,
and current CAPLAB reader source hashes. Read referenced objects from the
existing local object store without copying their bodies into the report.

The baseline is `/tmp/caplab-review-report-20260907/report.json`, backed by
`/tmp/caplab-review-canary-20260907-ledger.jsonl`. Preserve both unchanged.
Use `--baseline-report` to verify the old export as a byte prefix and retain
the original sequence cutoff 403343. Do not silently substitute a new cutoff
if baseline verification fails.

Permitted outputs: the fresh export, report JSON and Markdown, command logs,
bounded event inspection and source provenance files in the new local
directory, and this repository record with resulting observations. Inspect
recorded event types and candidate review-specific judgments, preserving
their locators and distinguishing them from artifact acceptance, budget
dispositions, and downstream fate. No new labels or correctness score are
authorized. No evidence admission, historical rewriting or purging, tracker
mutation, outbound request, model execution, placement change, or edits to
Striatum are authorized.

Stop on export failure, discontinuity, ambiguous input, or report failure;
retain diagnostic evidence instead of relaxing validation. Verify successful
export and report exits, prefix metadata, report counts against its rows,
and source/output hashes. This is execution of an existing read procedure;
it selects no new engineering design or study policy. No runtime code change
or full test-suite run is planned. Preserve all outputs for inspection and
all unrelated workspace files, worktrees, services, and timers. Authorization
expires when this record and its observations are committed or this bounded
refresh fails.

## Execution and custody

The export completed with exit zero at `2026-09-09T00:37:06.632919+00:00`
(September 8 in the owner's timezone). It contains 408,813 events, sequences
0 through 408812, ending at `2026-09-09T00:36:32.951Z`. This is the fixed
snapshot observed by this report, not a claim about subsequent production.

All local outputs are retained in
`/tmp/caplab-production-followup-tyk04scp/`. The 2,653,937,134-byte export is
`ledger.jsonl`, SHA-256
`24328f54ee5d1ee87ccbf265f9bee9ca2085f877250e6af61202ad88cec2cc51`.
`export.json` records the command, source working directory, times, exit,
and byte count; `sources.json` records observed checkout commits, Striatum
working status, and CAPLAB reader/procedure hashes. A checkout commit does
not independently identify the installed Striatum executable's build.
The CAPLAB baseline commit was `b712e01`.

The report command also completed with exit zero. It verified the retained
2,534,867,842-byte baseline export as an unchanged prefix. That baseline's
SHA-256 remains
`6d06f5dff5542b1fcd45b51c39a700c74890920b67df93c8a662a6e00c2a6c93`;
its report hash is
`9f34182f130eb47baf632b5825711717390ff269b15ba0ec4a66e302283fe52c`.
The follow-up preserves cutoff 403343. Its version 6 calculations differ
from the baseline's version 1 calculations as documented in the procedure;
prefix continuity does not establish identical calculations.

The inspection surface is `report/report.md`. Its complete JSON companion,
`report/report.json`, has SHA-256
`f39441c9c42264abc8566e9e068c7480e5cb6dfd23cced8e9ae96c3e06498f19`.
Review bodies were read from the existing hash-verified object store at
`/home/halbritt/.local/share/striatum/graphs/019f22ef-0cb4-780f-9b82-b210bab24325`.
Their availability is an observation at report execution time.

## Observations in the fixed follow-up window

There are 42 anchored reviews after the cutoff, all on change sets. All 42
closed as `submitted` and have a parsed latest body supplying the selected
verdict: 41 clearances and one refusal. No selected verdict is missing or
gate-only. This small, later population does not repair missing verdicts in
the historical population or establish a general retention rate.

Twenty-one clearances link to later applications. Eight reviews link to one
request cancellation, event 404284: seven clearances and one refusal across
seven artifact identities. There are no linked non-tree-moved conflicts.
The sole refusal, run 403588 on version 403583, has a later admission 403612.
These are overlapping inspection relationships, not independent outcomes.

The complete source cancellation is retained in `cancellation-404284.json`.
It records reissuing request 388570 to 404281 after a plan rejection, a
byte-identical successor, and a compiler repair to propagate rejection
detail. Its reason describes runtime registry/dispatch defects in Product
404085 and a separate recovery defect. It does not identify which of the
eight linked review verdicts was wrong. CAPLAB did not reproduce those
Striatum defects or independently adjudicate any of those reviews in this
refresh. Their recorded existence cannot supply eight gold defects.

## New acceptance evidence remains outside the required population

The 5,469 events after the cutoff include 33 acceptance-class gate results:
18 on implementation plans, eight on proposals, and seven on designs.
None applies to a change-set materialization. Recorded authority kinds are
`principal` for 28 and `delegated_policy` for five. Those field values alone
do not establish that a human personally adjudicated the artifact.

For example, event 408786 explicitly describes delegated engineering
adjudication of Design408749, distinguishes it from personal constitutional
acceptance, and records disagreement with accepting native Review408781.
Its detail concerns a claimed direct-input relationship. This is a useful
source locator for a separate prose-review investigation, but remains a
recorded judgment on a design, outside this change-set canary population.
It is not admitted here as independently verified review truth.

There are also eight new resolution events: six `proceed` and two `reissue`.
Their embedded escalation run references are zero; they do not structurally
identify a particular review run. Resolution 405277 has a change-set blocking
scope, but its note selects request reissue after a changed work graph and
repair ancestry. It does not turn that scope into a review-verdict ruling.
New gate classes are `review`, `check`, and `acceptance`; the event-type
survey found no newly named review-specific ruling class.

`event-survey.json`, its retained `inspect.py`, and `candidate-events.json`
preserve the event counts, payload-key survey, and all 33 acceptance and
eight resolution records. This is a structural survey plus the bounded
source inspections above, not exhaustive semantic adjudication of every
ledger note. It supplies no new eligible gold outcomes and no basis to
lift the confirmed criterion-replay threshold or frozen placement. It
does not claim that no relevant statement can exist elsewhere in the ledger.

## Verification and remaining limits

Both commands exited zero. A separate streaming pass agreed with the report's
export hash and event bounds. Checks reconciled the report population with
its rows and per-backend counts, verified every selected opening exceeded
the fixed cutoff, and checked its baseline metadata. Reader source and
procedure hashes remained unchanged. `inspection.json` retains the checked
counts and event/run locators; `verification.json` inventories all retained
files and hashes. `authorization.md` preserves the pre-execution scope.

No runtime code changed, so the full suite was not rerun. The report and
source inspection are the relevant verification for this refresh. No model
ran, no historical output was replaced, and no independent acceptance,
accuracy claim, placement decision, or qualification evidence was recorded.
The source request for review-specific outcome records remains unfiled by
CAPLAB. The current observation improves freshness and traceability of the
production inspection surface; it does not complete the measurement roadmap.
