# Retain downstream inspection evidence for unknown reviews

Date: 2026-09-08. Prospective report-only repair under the continued CAPLAB
improvement request and confirmed review-instrument disposition. No model
execution, ranking, evidence admission, or human-owned acceptance is involved.

## Reproduced gaps

At source commit `a8e83a3`, the production canary depended on the historical
criterion reader's timestamp-filtered downstream lists. That reader skipped
those lists entirely when a review had no verdict. The canary then applied
another timestamp comparison against review closure. Three authored fixtures
demonstrated missing or unsupported inspection links:

- A closed review without a verdict lost a later application, request
  cancellation, and newer version of its subject.
- Events following closure in the ledger were omitted when their timestamps
  equaled closure or preceded it because of clock reversal.
- An absent review content hash or request reference could join another
  event's absent identifier and manufacture a relationship.

The pre-repair regression output is `/tmp/caplab-canary-order-red.log`.
These are local reproductions, not correctness labels on production reviews.
The contiguous ledger sequence already validated by the reader supplies
event order. Wall-clock timestamps cannot override that order.

## Prospective report contract

New reports use `caplab-review-canary/2` and declare
`ledger-sequence-after-review-closure/1` ordering. The JSON retains each
review's `closed_seq` and each linked event's sequence and original timestamp.
A downstream application, conflict, or cancellation must have a strictly
greater sequence than closure. Open reviews have no post-closure events.
The existing exclusions for tree-moved conflicts and cancellations without
defect wording remain; neither establishes a correctness judgment.

The reader constructs these inspection links for every anchored review,
including those with no verdict. A known content hash or request reference
is necessary for a join. Newer subject-version observations also survive
missing verdicts. Unknown decisions remain unknown; downstream events cannot
fill in a missing review response.

The Markdown inspection list now groups related conflicts and cancellations
across cleared, refused, and unknown-verdict reviews, with separate decision
counts. Clearance and refusal summary columns retain their own populations.
One downstream event may still relate broadly to many reviews, so the report
continues to reject independent-defect and correctness interpretations.

Both report versions can supply a verified baseline. Baseline metadata names
its report version, and the rendered report distinguishes verified ledger
continuity from unchanged report calculations. Existing prefix, cutoff, and
overwrite protections remain in effect. Historical reports are not rewritten.

## Preservation and authority

The historical criterion's timestamp-based strata and summary calculations
remain separate from the canary's new sequence-based links. Its export omits
the new inspection-only field. The same authored ledger was passed to the
criterion CLI before and after the repair; both the summary JSON and case
JSONL were byte-for-byte identical. The fixture is
`/tmp/caplab-canary-order-fixture.jsonl`; outputs are in
`/tmp/caplab-canary-order-criterion-before/` and
`/tmp/caplab-canary-order-criterion-after/`. This establishes preservation for
the exercised fixture, not validity of historical criterion labels.

No criterion output on historical production evidence was regenerated. The
change does not add a review-specific gold-outcome reader, infer findings from
downstream fate, change the frozen placement policy, or file the pending
Striatum request. The user-owned `docs/designs/` draft remains untouched.

## Alternatives and limits

Leaving the canary unchanged would keep evidence invisible precisely when
review output is missing. Replacing only the final timestamp comparison would
still lose events discarded by the upstream reader. Broadly rewriting the
criterion's historical strata would exceed the necessary reporting repair.
The added inspection projection uses the existing event indexes and preserves
the historical calculation path.

Ledger order establishes when an event was recorded, not causality or the
time an underlying external action occurred. A known matching hash identifies
the content involved; a request cancellation is a broader relationship.
Neither identifies which reviewer was right. Source-event and artifact
inspection remain necessary, and independent production outcomes remain
missing from this reporting contract.

## Retained production snapshot

The new reader completed a read-only report against the previously retained
export `/tmp/caplab-production-20260908-9e8Est/ledger.jsonl`, SHA-256
`ba8754dd853fc51442904fb2b7502fa253b164cff31c8205d3f4e4c37d18d3bf`.
It contains 406,971 events through sequence 406970, timestamp
`2026-09-08T09:53:36.328Z`. This is an older snapshot, not a current-ledger
refresh. Review bodies were read from the local hash-verified object store;
availability is that of this read.

The report contains 6,348 anchored change-set or repo-doc reviews: 2,996
cleared, 472 refused, and 2,880 unknown. All unknown runs are closed in this
snapshot. Among them, 97 link to later applications, 59 to request
cancellations, and 2,835 to later subject versions. There are no linked
non-tree-moved conflicts among those unknown runs. The 59 cancellation-linked
reviews relate to four events: 112825, 320479, 393549, and 393550. These
overlapping relationships are not independent defects or reviewer errors.
For example, unknown review 110554 closed at 110658 and links by request
105497 to cancellation 112825; the retained reason concerns the lowering
process. Its missing verdict remains unknown.

No linked application, conflict, or cancellation in this report has a
non-increasing timestamp relative to closure. The timestamp repair is
supported by the local boundary fixtures; no observed production frequency
is claimed for that failure. The missing-verdict repair exposes the real
links above, previously skipped before downstream matching.

The new report is `/tmp/caplab-canary-order-production/report.json`, SHA-256
`b3a114f13197d34572a0d5d72c3fa08b55add87b70dd2833c070f5ebbb044139`.
Its Markdown companion is the inspection surface. The extracted counts and
example locators are in `/tmp/caplab-canary-order-production-inspection.json`.
No existing report was replaced, and this output admits no evidence into a
qualification ledger.

## Verification

All 16 canary tests pass (`/tmp/caplab-canary-order-focused.log`), including
unknown and open reviews, reversed and tied timestamps, a future timestamp
on a pre-closure event, absent join identifiers, version 1 baseline support,
and existing prefix and overwrite refusal behavior. The new tests failed
before implementation. Full `make check` passed 749 tests with four existing
skips in 152.427 seconds (`/tmp/caplab-canary-order-make-check.log`). The
skipped campaign and PostgreSQL integration checks remain outside this
verification. The production report command also completed with exit zero
(`/tmp/caplab-canary-order-production.log`). `git diff --check` passed.

## Engineering guidance

The repository contract governs this repair. Retrieved guidance supplied
`testing-test-first-feedback`, `universal-repository-contract-precedence`,
and `agent-conduct-authority-bounded-action`. The evidence packet is
`pkt-ddd718102111c22e`, SHA-256
`ddd718102111c22ea69b138a91b35bbdaa21db20d2e899b3ace1e1fe3df42fdb`,
from release commit `d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`, corpus
`corpus-2026-07-12-a11702cc9217`, doctrine `doctrine-f6bbb5196a3f8bf9`,
and retriever `retriever-ec995ecdd083b2c8`. Its ceiling is execution within
the report-only authority above, without human acceptance. Source locators
are the two reader/report scripts, tests, retained snapshot report, and
verification outputs named in this record.

Material obligations concern source ordering, complete review retention,
join identity, historical preservation, and executable observations. The
ledger reader validates contiguous sequence numbers. Inspection grouping
uses that ledger event sequence and retains every linked run; it does not
deduplicate reviews by artifact hash or treat request matches as exact
artifact identity. Missing join keys produce no relationship. The selected
population remains anchored review openings with change-set or repo-doc
subjects; missing verdicts do not remove a run. Source inspection, boundary
tests, and the retained-snapshot report cover these claims.

The packet's remaining traversal-depth and generic deduplication obligations
are nonmaterial beyond those checked relationships: no directory discovery,
new logical key, or conflict-suppression mechanism is introduced. Asynchronous
UI, top-N selection, presentation budgets, and paging obligations are
nonmaterial because those mechanisms are unchanged or absent. The report
groups events without truncating its JSON review population. No new
declarative configuration references are introduced; baseline record versions
are explicitly supported and covered by tests.

Native endpoint capability and end-to-end reviewer verification remain
unverified and are material to future capability claims, which this repair
does not make. Production correctness incidents, operational cost over an
interval, and future workload frequency are not established by the retained
snapshot. They are nonmaterial to the reproduced omission repair and cannot
be inferred from its test count or inspection-link counts. A future outcome
reader still needs an authorized contract and independently grounded outcome
evidence before it can support reviewer selection.
