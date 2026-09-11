# Preserve assignment completion and advisory uncertainty

The development projection now distinguishes an empty completed review, an
incomplete or unavailable review, and a completed review whose assessment is
pending. It retains every declared assignment and exposes advisory error and
uncertainty alongside the existing defect-catch and incorrect-blocker bounds.
This closes an accounting gap; it does not validate a scorer or rank reviewers.

The [prospective policy](../product/studies/reviewer-ranking-001/COMPLETION-AND-ADVISORIES.md)
is selected under ADR 0026 and ADR 0066. Its implementation is
`scripts/reviewer_assignment_outcomes.py`. Existing OUTCOME-CREDIT policy,
implementation, natural warrants and historical projections remain unchanged.

## What the implementation establishes

Each supplied assignment keeps its binding, case, common truth version and
known defect identities. Missing, extra or duplicate observation rows are
rejected. A case cannot silently use a different truth version or defect set
for another binding. Repetitions remain rows of the same case; the function
calculates neither independent sample counts nor aggregate rates.

A complete assessment reuses the existing catch and blocker arithmetic and
adds a separately warranted erroneous-advisory incidence. Advisory judgments
are not inferred from blocking judgments. Duplicating an error does not
multiply incidence, and withdrawal removes its active event while preserving
its original text. Active finding counts describe occurrences; they do not
measure human effort or supply a ranking utility.

The following are constructed implementation challenges with one known defect,
not observed performance of any native reviewer:

| Input | Completion | Known misses | Incorrect blocker | Erroneous advisory |
| --- | --- | --- | --- | --- |
| Completed empty review | [1, 1] | [1, 1] | [0, 0] | [0, 0] |
| Confirmed unavailable review | [0, 0] | [0, 1] | [0, 1] | [0, 1] |
| Completed response, assessment pending | [1, 1] | [0, 1] | [0, 1] | [0, 1] |
| One supported advisory catch | [1, 1] | [0, 0] | [0, 0] | [0, 0] |
| Same catch plus 32 unresolved advisory occurrences | [1, 1] | [0, 0] | [0, 0] | [0, 1] |

Intervals are logical uncertainty bounds. Missing-review bounds are not
fictional findings or delivered utility. They prevent missing quality evidence
from becoming a clearance. No ordering follows from this table without a
validated truth basis, complete comparative design and stated tradeoffs.

## Challenge and policy correction

The first policy combined native completion with assessment completion. Its
seven focused tests passed. A subsequent source review identified the missing
state: a completed native response awaiting assessment. The original policy,
implementation and tests are preserved in the development receipt. Original
policy SHA-256:
`8b0395533ddfa7faeb1a94571f1b895727ad749f7a144f1accefd684951f08ba`.

Policy revision 2 explicitly separates native completion and assessment. A new
test first failed because the original implementation rejected that state.
The correction permits a null assessment for a completed review, preserving
its response locator and pending reason. Quality stays unassessed. Supplying
a partial or inconsistent warrant set still fails accounting; it cannot be
silently accepted as complete. No historical reviewer outcome was rescored.

Eight focused tests exercise the public projection, including whole-assignment
accounting, differing truth versions, empty versus failed reviews, pending
assessment, advisory uncertainty, duplicates, withdrawals and missing advisory
judgments. An enumerated oracle checks 162 two-finding configurations against
all 512 permitted concrete resolutions of evidence and acceptance effects.
It derives extrema from those concrete worlds rather than copying the
implementation's three-valued incidence expression. The existing seven
outcome-credit tests also pass. These are tests of arithmetic and accounting,
not evidence that supplied semantic warrants are correct.

The final revision passed `PATH="$PWD/.venv/bin:$PATH" make check`: 1586
tests in 205.602 seconds, with seven skips. The earlier full-suite result
(1585 tests) remains preserved; the final rerun includes the added
completed-but-unassessed case. No older scoring implementation was changed.

## Custody and limits

The [development receipt](../product/studies/reviewer-ranking-001/assignment-outcomes-development-receipt.json)
retains this turn's policy revisions, code, tests,
failed and passing checks and verification record under
`/home/halbritt/.local/share/caplab/reviewer-ranking-001/development/assignment-outcomes-1`.
Its hashes bind the exact implementation to the recorded checks. All test
reports and references are explicitly constructed. No live reviewer call,
case admission, historical rescoring or original-program witness was run for
this change. The retained Doctrine packet `pkt-cdafd666a23adaf1` supplies general
evidence-before-scoring and authority guidance, not acceptance of this method.

The projection does not dereference or authenticate native evidence, establish
assignment sealing, verify semantic advisory judgments, or declare ranking
eligibility. It deliberately leaves all those authority and truth flags false.
A completed free-text response needs valid extraction, not mandatory JSON
formatting; capture and extraction integration remain outside this arithmetic.
Partial-output utility, real workload burden, incident weighting, practical
effects, statistical uncertainty and comparison tradeoffs remain open.

Fixed-sample coverage remains thirteen bounded changes, two base-only trees
and seventeen pending changes. Admission remains zero. The next necessary
validation is to establish advisory-basis judgments independently on natural
reports and connect this accounting to authentic native assignment and
completion evidence. Passing these implementation checks alone cannot satisfy
the reviewer-ranking goal.
