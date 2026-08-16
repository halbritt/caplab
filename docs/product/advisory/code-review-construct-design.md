# Code-review construct — design scaffold (T3.4)

Status: design only. No generator has run, no cases exist, no binding has
been measured. This document scopes the second review-family construct so
the corpus work can proceed in a later session without re-deriving choices.

## Construct

`review.code_defect_discrimination/1` — matched-pair defect injection over
**code changes**: the subject reviews a diff (or a changed-file set) against
its repository context; one arm carries a single mechanically injected,
mechanically verified bug.

The document construct (`review.defect_discrimination/1`) measures contract
and coherence review. This construct measures what it cannot: reading
behavior across code, data flow, and tests.

## Case shape

A case is `(repo_snapshot, base_commit, change, operator, seed)`:

- **Substrate**: a real commit from an owned repository whose test suite
  passes at both parent and child (verified at harvest, recorded).
- **Control arm**: the commit's own diff, presented for review.
- **Mutant arm**: the same diff with one injected defect.

## Candidate operators (all mechanical, all checkable by test execution)

- `inverted_guard` — negate one boundary/None/error check the diff touches.
- `dropped_error_path` — replace one `raise`/error return in the diff with a
  silent pass/default (the swallowed-error class).
- `off_by_one` — perturb one range/index bound the diff introduces.
- `stale_condition` — revert one changed conditional to its pre-change form
  while keeping the rest of the diff (a half-applied change).
- `dead_write` — assign a computed result to a name the code never reads
  again (the hollow-implementation smell).

**Oracle**: the substrate repository's own test suite. A mutation is a valid
case only if tests pass on the control arm and fail on the mutant arm in a
hermetic runner. This is a stronger gate than the document corpus has — the
defect is not merely present but demonstrably behavior-changing — and it
prices each case at one test-suite run per arm at harvest time.

## Blinding and scoring

Same protocol as the document construct: arms never shown together, nothing
marks the mutant, manifest hashes re-pinned to the mutated content. Verdict
scoring identical (catch / false-alarm / discrimination). Anchoring maps to
file:line — a caught defect is `anchored` when a finding names the mutated
file and a line within the mutated hunk.

## Admission

The case-pool governance protocol applies unchanged, including the
Principal's floor rule: new cases run against reference bindings first;
strong-reference misses quarantine the case, not the binding; calibration
samples estimate the difficulty floor. The weak reference for code review
should additionally include the free local model to catch too-easy cases.

## Substrate sources (initial)

Owned repos with real test suites and honest commit history: `caplab`,
`quartermaster`, `engram`, `striatum-next` (Go), `gpu-fleet`. Partition
assignment groups by repository and artifact ancestry, consistent with the
document corpus and RFC 0019's partition discipline.

## Explicitly out of scope here

Cross-repo supply-chain cases, multi-defect arms, LLM-authored defects
(non-mechanical), and any use of these cases for training rows.
