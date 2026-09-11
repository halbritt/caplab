# Natural reviewer catches the scheduler defect and reports two new concerns

One native Codex CLI 0.153.4 / gpt-5.6-terra / max review completed on the
admitted scheduler development case with the known answer withheld. It
reported the accepted incomplete-decision defect and two additional concerns.
The first report matches the independently established defect. The other
two require independent investigation and remain unresolved in the outcome
accounting. This is one development observation, with no comparative ranking.

| Natural finding | Reported effect | Current evidence disposition |
| --- | --- | --- |
| Capacity-driven fallback is admitted without its causal input | Block | Supported catch of the admitted known defect; complete-input requirement and original graph evidence support the block. |
| New scheduling preview omits the required host clock | Block | Source and the reviewer's retained test corroborate the narrow error. Independent validation of the full finding and blocking basis remains open. |
| Live-store diagnostic can create objects and runtime directories | Advise | Source supports the potential write path when objects/directories are absent. An isolated end-to-end storage observation and requirement-scope check remain open. |

The complete report has three asserted findings, thirteen resolved source
locations and four explicit limitations. Its development projection preserves
one known catch and zero misses within the single admitted root, two unresolved
potential new defects, and logical bounds `[0, 1]` for both incorrect-blocker
and erroneous-advisory incidence. These are not probabilities or confidence
intervals. No whole-patch clean label follows from the known catch.

## What supports the known catch

The reviewer identifies the actual changed boundary: the predictor now agrees
with the preexisting v2 evaluator, permitting acceptance of a decision that
omits the active exhaustion input which changed placement. It distinguishes
the inherited omission from the newly enabled admission and states the
complete-input requirement. The [case admission](decision-2026-09-10-reviewer-development-case-admission.md)
already binds the original C11 requirement and the original append, binding,
reopen and input-removal evidence. That independent basis predates this review.

The reviewer's own reproduction logs current stamp/evaluation `2/2`, base
`5/2`, and a change from `local` to `starved` when the observation is removed.
Its passing test alone is insufficient: it logs the values without asserting
all of them, does not append through the Driver, and removes the observation
from a full input rather than reconstructing solely from serialized fields.
The registered original graph evidence supplies the material admission proof.
The finding earns no additional credit for an invented erasure or production
misdispatch consequence.

## New claims remain separate

The new preview builds an input and immediately calls `Evaluate`; its source
does not install the clock sample that the existing recovery path supplies
for v3/v5. The reviewer wrote a test using an original supervised-run fixture
and observed the required missing-clock error. Follow-up must independently
check the normal preview contract, clock-supplied control and reported CLI
behavior. A reviewer-authored reproduction is evidence to inspect, not its
own truth oracle.

The advisory names `buildSession`, `PutObject` and `EnsureLayout`, with the
specific condition that target objects or directories are absent. It notes
that writes may be idempotent when already present and does not claim an
observed production mutation. Follow-up must check the end-to-end effect on
an isolated original store and the scope of the read-only promise. The actual
live-store diagnostic was skipped in this review; no production store was used.

These findings remain outside the admitted root catalog. Any future admission
must update the common case truth for all compared reviewers. Unknown claims
cannot become false findings or disappear from the denominator.

## Task and native verification

The [authorization](authorization-2026-09-10-reviewer-scheduler-natural-review.md)
names one 900-second invocation and a neutral first-pass review prompt. The
task contains 2,544 original source files, the exact patch, the existing report
schema and an omission list. Every source file matches its original Git blob;
executable modes are preserved. The omitted `CLAUDE.md` symlink and compiled
`target-hash` binary are explicit. Known defect descriptions, witnesses,
assessments and case-truth records were outside every subject mount.

The original Go 1.23.4 toolchain and three cached module versions were
available read-only, with dependency downloads disabled. An offline namespace
preflight passed. The reviewer could copy source to scratch space and run
local checks. User configuration/rules, apps and plugins were disabled as
recorded; these configuration limits remain part of the observed subject.

The invocation completed in 569.016 seconds with exit zero. Native stream,
saved session and final message agree on identity and final bytes. Capture
retains 86 files and receipts for 58 omitted opaque encrypted reasoning
fields. Sixty recorded commands and three scratch-file changes were inspected.
Five reproduction source/output artifacts are retained; earlier revisions
remain in the transcript. The scheduler, driver and CLI package test command
returned zero on the modified scratch tree. This does not establish full
repository conformance or prove the three findings correct.

Source bytes/modes, task membership, toolchain and dependencies remain
unchanged. The native process and its process group are terminal and the
volatile workspace is removed. A generated wrapper-attribute substitution was
corrected and preserved before preflight or model launch; it caused no model
retry. No CAPLAB runtime code changed or full CAPLAB test suite was rerun.

Private custody:
`/home/halbritt/.local/share/caplab/reviewer-ranking-001/development/scheduler-natural-review-1`.
Fixture SHA-256:
`aae43b5aca34560ddb7ee745dbc3e17b2816c85af0243bc0c84054e71e6b78ac`.
Final review SHA-256:
`4fa7a73703f5cd88ea9bce10b6746cb3a06bc575d8afd98a8bdfcde9b0187fe5`.
The [receipt](../product/studies/reviewer-ranking-001/scheduler-natural-review-development-receipt.json)
pins preparation, capture, completion verification, the complete report,
primary inspection and bounded outcome accounting. Native token counters
are retained separately from any provider invoice.

The earlier native scorer remains unaccepted. This source-grounded primary
inspection does not supply independent campaign acceptance or unseen-case
accuracy. Next, investigate the two new claims, collect a natural review of
the effort preservation case, and continue corpus/control coverage before
freezing comparative assignments and uncertainty rules. Case admission and
coverage counts are unchanged; eligible comparative measurements remain zero.
