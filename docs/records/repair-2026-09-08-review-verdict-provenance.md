# Keep review verdicts attached to their source evidence

Date: 2026-09-08. Prospective report-only repair under the continued CAPLAB
improvement request. The confirmed no-spend, no-ranking disposition remains
in force. The change records observations, not review correctness or human
acceptance.

## Reproduction

At source commit `2c2ae1f`, two review-body admissions for one run could
produce a mismatched observation. If the first body contained `reject` and
the second body was unavailable, the reader kept `reject` but replaced its
artifact identity and content hash with those of the unavailable body.
The canary then called the result a body-sourced verdict. The selected
source could not supply the reported value.

Authored local bodies also reproduced whole-report failures: a JSON string
caused an attribute error, a list-valued verdict caused an unhashable-value
error, and numeric `findings` caused an iteration error. Other unreadable
bodies disappeared into the same missing-verdict presentation. Multiple
body and gate observations were overwritten, concealing source differences.
The pre-repair test log is `/tmp/caplab-verdict-red.log`.

## Prospective reporting

New canary reports use `caplab-review-canary/3` and declare
`latest-admitted-body-then-latest-review-gate/1` selection. Reading a new
body clears the previous body's selected verdict and excerpts. The latest
body supplies its own recognized verdict, or the report explicitly falls
back to the latest review gate. Without either, the decision stays unknown.
This preserves the existing body-before-gate selection convention while
removing the stale-value provenance error. It does not adjudicate whether
one admission validly supersedes another.

Every relevant body admission now retains its ledger sequence, artifact
identity, hash, read status, raw verdict field, and response-envelope error.
Missing references, invalid references, unavailable or unverified bytes,
invalid JSON, non-object JSON, and parsed objects are distinguishable.
The existing object reader combines absence, decompression failure, and
hash mismatch into one unavailable result; the report does not invent a
more specific cause. Full bodies remain at their hash-addressed source.

A recognized verdict string remains an observation even if another field
is malformed. The response-envelope error stays visible, and the report
does not call that body a conforming review. Invalid field shapes cannot
crash the report through the repaired verdict and excerpt paths. This is
not a complete validator for arbitrary malformed ledger events.

All review-gate events retain their sequences and raw outcomes. Repeated
producing-run references inside one event contribute one observation.
The report flags differing recognized body verdicts, differing gate outcomes,
and disagreement between the selected body and gate. These flags do not
decide which source is right. For example, a gate may legitimately refuse
an accepting body whose contract requirements were not met.

Reviewer summaries count latest-body statuses and source-discrepancy flags.
Markdown groups inspection issues and shows the first three run locators
per issue in ledger order. JSON retains every observation. A run with no
admitted body has status `not-admitted`, even if a gate supplies its verdict.
Baseline versions 1, 2, and 3 remain supported; baseline continuity does not
assert unchanged report calculations.

## Alternatives and preservation

Keeping the old value when the latest body is unavailable would retain the
demonstrated false source attribution. Choosing an arbitrary earlier body
would require a different selection contract. Rejecting the whole export
would hide unrelated retained reviews. The implemented repair keeps the
selection rule explicit, clears stale selected fields, and preserves all
source observations for inspection.

The shared reader supplies the historical criterion tool as well as the
canary. Its future reads receive the same stale-value and malformed-body
repairs; this is a semantic bug fix, not behavior-preserving refactoring.
The criterion export omits the new inspection-only observation arrays.
No historical criterion report, canary report, source body, or admission
record was overwritten, registered, purged, or superseded. The user-owned
`docs/designs/` draft was left untouched. No model calls or external messages
were sent.

## Verification and limits

The revised report completed on the retained export
`/tmp/caplab-production-20260908-9e8Est/ledger.jsonl`, SHA-256
`ba8754dd853fc51442904fb2b7502fa253b164cff31c8205d3f4e4c37d18d3bf`.
It contains 406,971 events through 406970 at
`2026-09-08T09:53:36.328Z`; this is not a current-ledger refresh. In its
6,348 selected reviews, all 2,880 unknown-verdict runs have no admitted
review body recorded. All 3,468 admitted bodies were readable with no shared
response-envelope error at this read. The report retains 2,888 linked review
gate events and found no multiple body verdicts, multiple gate outcomes, or
selected body/gate disagreements. Selected decisions are unchanged from the
version 2 report on the same export. These observations distinguish absent
admissions from object-store loss within this snapshot. They do not establish
why no body was admitted or prove full contract conformance.

The new report is `/tmp/caplab-verdict-production/report.json`, SHA-256
`ee96412b0353dfd1f0f89f1dfb7ae30a0d3d83d6ff808c6836c45acb40ae5fcb`.
Counts and comparison results are retained in
`/tmp/caplab-verdict-production-inspection.json`. The command completed with
exit zero (`/tmp/caplab-verdict-production.log`). The stale-provenance and
malformed-body defects are supported by local fixtures; no occurrence was
found in this production snapshot.

All 21 canary tests pass (`/tmp/caplab-verdict-focused.log`). Tests cover
the stale-hash reproduction, malformed bodies, invalid and missing body
references, conflicting body and gate values, duplicate evidence references,
unknown decisions, and the existing baseline and downstream-order checks.
Full `make check` passed 754 tests with four existing skips in 153.608 seconds
(`/tmp/caplab-verdict-make-check.log`). The skipped campaign and PostgreSQL
integration checks are outside this verification. `git diff --check` passed.

The report still lacks independently adjudicated review outcomes and exact
native Binding verification. Diagnostic coverage cannot establish reviewer
accuracy, rank configurations, adopt a gate floor, or resolve the broader
reviewer-value goal.

## Engineering guidance

Repository authority and evidence govern this repair. Retrieved guidance
supplied `testing-test-first-feedback`,
`universal-repository-contract-precedence`, and
`agent-conduct-authority-bounded-action`. Packet
`pkt-8a46d7c18e721627` has SHA-256
`8a46d7c18e721627ff193d53868633ed73b2e2710ea062caec49b1fceacea768`,
from release commit `d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`, corpus
`corpus-2026-07-12-a11702cc9217`, doctrine `doctrine-f6bbb5196a3f8bf9`,
and retriever `retriever-ec995ecdd083b2c8`. The ceiling is execution within
the stated report-only scope, without human acceptance. Source locators are
the reader, canary, shared response validator, object-store reader, tests,
and retained verification outputs named above.

Material obligations concern source identity, clearing stale selected fields,
malformed inputs, preservation limits, and executable observations. The
inspected code and regressions cover those claims. Each body observation is
identified by its admission event and body reference. A gate observation is
identified by its ledger event; repeated references to one run inside that
event do not create additional observations. Distinct gate events remain
distinct. The existing selected review population and downstream joins are
unchanged.

The remaining generic traversal and deduplication obligations are nonmaterial
beyond these exercised identities; no directory discovery or storage key
changes. The Markdown reader receives counts and three chronological example
locators per issue, with complete observation arrays in JSON. This is an
explicit first-three presentation rule, not a relevance ranking; the
packet's top-N relevance obligations do not apply. Broader presentation-budget
and asynchronous UI obligations are nonmaterial to the reporting repair.
No new declarative external references are introduced, and baseline version
support remains explicit. Paging and operational service instrumentation are
unchanged.

Actual native endpoint capability remains unverified and cannot support a
Binding or reviewer capability claim. Production correctness incidents,
operational cost over an interval, and future workload frequency are not
established. These are nonmaterial to the locally reproduced provenance
repair and remain unavailable for broader performance or reviewer-value
conclusions. The retained snapshot's absence of these failures is reported
as a bounded observation, not a universal absence claim.
