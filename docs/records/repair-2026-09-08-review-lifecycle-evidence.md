# Expose lifecycle evidence behind missing review verdicts

Date: 2026-09-08. Report-only implementation under the continued CAPLAB
improvement request. No model execution, reviewer ranking, qualification,
evidence admission, or human acceptance is authorized by this record.

## Observations and interpretation boundary

The retained production report at source commit `57df793` contained 2,880
unknown-verdict reviews with no admitted body. Their run outcomes were 1,979
`submitted_partial`, 852 `canceled`, 40 `abandoned`, and 9 `error`.
Those outcome names did not explain the missing admissions.

Read-only source inspection found additional linked events that the canary
did not retain. For example, review 65207 closed at event 65209 with source
`scheduling_deferral` and reason `capacity_saturated`. Review 65204 instead
had submission 65281, admission refusal 65282, and closure 65283. The
submission declared its required review-ledger output absent; the admission
record said `schema_invalid`, state `absent`, detail `required output missing`.
Calling that malformed reviewer JSON would exceed the evidence.

The source inspection is retained in
`/tmp/caplab-missing-review-source-inspection.json`. It covers the older
406,971-event export through sequence 406970 at
`2026-09-08T09:53:36.328Z`, SHA-256
`ba8754dd853fc51442904fb2b7502fa253b164cff31c8205d3f4e4c37d18d3bf`.
It is not a current-ledger refresh. The diagnostic object
`896fe038f205d8a65c66c2f1a6c7c2bc0e76d1df749812301aed0abd9cb82949`
was read and hash-verified locally; it contains `exit status 1`. That
observation does not identify why the process exited.

Current Striatum source inspection also confirms that its admission path
records submission state and admission decisions separately from closure
outcome (`internal/store/admission.go`, `internal/store/admission_v2.go`).
Those sources explain the current emitter, not every historical execution.
They supply advisory integration context; CAPLAB owns its reporting contract.

## Reporting change

Version 3 canary reports now add `lifecycle_observations` to every selected
review. The reader retains linked closures, submissions, admission decisions,
submission refusals, and dispatch lapses in ledger order. Entries name their
event sequence, schema version, timestamp, and selected detail fields.
Submission and diagnostic object references are retained; the reporting path
does not read or execute diagnostic bodies.

The `unknown_verdict_lifecycle` summary declares
`caplab-review-lifecycle/1` and covers only unknown-verdict reviews. It counts
the selected closure's recorded source and, for scheduling deferrals, the
recorded deferral reason. Open reviews and absent closure-source labels stay
explicit. It pairs admission-refusal codes with submitted state and counts
both events and distinct runs. Multiple output refusals can belong to one
review, and a submission can concern other outputs; categories may overlap.

These are observations about the recording and execution path. They do not
change the review's unknown verdict or convert missing output into an
incorrect review. A scheduling deferral is not a reviewer refusal. An absent
required output is not proof that the reviewer emitted invalid JSON. Raw
details and object locators remain available for further inspection.

## Alternatives and preservation

Inferring cause from `canceled`, `submitted_partial`, or `schema_invalid`
alone would conflate scheduling, missing outputs, and admission validation.
Automatically interpreting diagnostic bodies would add an unvalidated
classification mechanism. The report instead exposes the recorded closure
and admission facts with their sources. Leaving the report unchanged would
continue hiding information already present in the ledger.

The review population, selected verdicts, downstream joins, baseline rules,
and placement freeze are unchanged. The new fields are an additive report
extension, with no new score or decision rule. Historical criterion exports
omit the new lifecycle field. No existing production report, source event,
body, or governing record was rewritten, copied into an evidence registry,
or superseded. The user-owned `docs/designs/` draft was preserved. Striatum
code and runtime were only inspected; they were not changed.

## Verification

Two local regressions failed before the change and pass afterward. All 23
canary tests pass (`/tmp/caplab-lifecycle-focused.log`), including retained
diagnostic references, closure-source distinctions, event ordering, missing
labels, open reviews, repeated admission decisions, and exclusion of known
verdicts from the unknown-verdict summary. The pre-change log is
`/tmp/caplab-lifecycle-red.log`. Full `make check` passed 756 tests with four
existing skips in 115.872 seconds (`/tmp/caplab-lifecycle-make-check.log`).
The skipped campaign and PostgreSQL integration checks remain outside this
verification. `git diff --check` passed.

Root cause, reviewer capability, independent production outcomes, and exact
native Binding verification remain outside these observations. Those gaps
still prevent completion of the wider reviewer-value goal.


## Retained-snapshot result

The revised report completed with exit zero on the same retained export.
Its 6,348 selected reviews and their decisions are unchanged. Among the
2,880 unknown verdicts, recorded closure sources are 1,979
`submission_admission_v2`, 800 `scheduling_deferral`, 40 `horizon`, 52
`dispatch_refusal`, six `submission_refusal_v2`, and three
`scheduling_decision`. The scheduling deferrals name 730 `capacity_saturated`,
58 `capacity_starved`, and 12 `declaration_set_stale` reasons. There are 1,979
output-admission refusal events across 1,979 unknown-verdict runs; all pair
`schema_invalid` with submitted state `absent`.

These source categories do not establish causal responsibility. In
particular, the 800 scheduling deferrals must not be interpreted as 800
reviewer mistakes, and the 1,979 absent outputs do not become 1,979 malformed
JSON responses. Diagnostic inspection and an independently grounded outcome
contract remain necessary before any reviewer-value inference.

The new report is `/tmp/caplab-lifecycle-production/report.json`, SHA-256
`6632a86fbc8943deedd822255f25955c07131c19d9d824f22184a4725c1387bd`.
Its Markdown companion displays the lifecycle breakdown. Extracted counts and
decision preservation checks are in
`/tmp/caplab-lifecycle-production-inspection.json`; command output is
`/tmp/caplab-lifecycle-production.log`.

## Engineering guidance

Repository authority and observed evidence govern this change. Retrieved
guidance supplied `testing-test-first-feedback`,
`universal-repository-contract-precedence`, and
`agent-conduct-authority-bounded-action`. Packet
`pkt-4d09285f1641fceb` has SHA-256
`4d09285f1641fceb6330f2ec17b72849795065b864d4c8415ea1dc61f7bc6d58`,
from release commit `d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`, corpus
`corpus-2026-07-12-a11702cc9217`, doctrine `doctrine-f6bbb5196a3f8bf9`,
and retriever `retriever-ec995ecdd083b2c8`. Its execution ceiling is bounded
by the report-only authority above. Source locators are the reader, canary,
tests, and retained inspection and verification outputs in this record.

Material obligations concern the selected review population, lifecycle-event
identity, unknown-verdict scope, source labels, and preservation. Events join
to anchored review openings by `run_ref` and retain their ledger sequence;
multiple events for one run are preserved. Admission summaries count both
events and distinct run references. Tests exercise repeated events, known
review exclusion, open runs, and missing labels. The real report accounts
for all 2,880 unknown-verdict runs by selected closure source without changing
any selected verdict.

The remaining generic directory-traversal and storage-deduplication
obligations are nonmaterial beyond those tested joins: neither mechanism is
introduced. The report groups recorded categories and retains their complete
event arrays in JSON; it makes no top-N relevance claim. Broader presentation
budgets, asynchronous UI, and paging obligations are nonmaterial to this
change. Source codes are reported as recorded labels, not validated against
today's catalog or adopted as a CAPLAB classification policy; no new
declarative external configuration references are introduced.

Native endpoint verification and causal diagnosis remain unverified and
material to any future reviewer-capability claim. Production correctness
incidents, operational cost over an interval, and future workload frequency
are not established here. Those obligations are nonmaterial to exposing
existing lifecycle records, and the report cannot supply broader conclusions
from their absence. Further diagnosis must inspect the named source records
and diagnostic bodies under its own bounded question.
