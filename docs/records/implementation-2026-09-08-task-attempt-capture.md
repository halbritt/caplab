# Retain task state around bounded process execution

Date: 2026-09-08. Baseline: `7c44067`. Decision owner: primary agent under
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).

## Authorization before execution

Implement prospective before/process/after capture under CAPLAB-79's task
inventory requirement. Permitted files: `src/caplab/task_capture.py`,
`src/caplab/process_capture.py`, `tests/test_task_capture.py`,
`tests/test_process_capture.py`,
`docs/product/contracts/task-attempt-capture-v1.md`,
`docs/product/contracts/bounded-process-capture-v1.md`, and this record.
Extract only the existing receipt publication mechanism needed by both capture
owners. Repair process pipe setup cleanup if a synthetic failure confirms the
unowned-pipe gap. Preserve the existing stream receipt and limit semantics.

Authorize only new synthetic task trees and local Python subprocesses in
temporary directories. Exercise filesystem changes, quotas, changing sources,
symlinks, storage failures, process failure and receipt publication. Run focused
tests and `make check`. This grants no model calls, live harness execution,
historical evidence inspection/copy/admission/rescoring/purge, new campaign,
ranking, placement, tracker write or external message. Preserve frozen source
bindings/manifests, `docs/designs/`, sibling worktrees and services. Retain
verification receipts in `/tmp`; delete only named task doctrine scratch after
retaining its receipt. Authorization expires at commit. Stop on unexplained
changes to existing capture semantics or effects outside synthetic fixtures.

## Decision and remaining boundary

CAPLAB-84's current projection is `/tmp/caplab-task-capture-84.json`. Its
capture requirement names complete task inventories before any newly authorized
episode. Current `capture_process` retains only streams, and the review content
snapshots omit modes and raw custody. Select a prospective task-attempt wrapper
that seals a task inventory before launch, uses the bounded stream owner, and
seals the final inventory plus observed changes after process cleanup.

The caller must supply a trusted, quiescent task tree at both snapshot boundaries
and custody outside subject-writable mounts. Record regular-file bytes, modes,
directories and literal link targets without following links. Use explicit
combined before/after task byte and entry limits. Reject unsupported filesystem
objects and observed source changes; leave incomplete custody without a final
attempt receipt. This is not a filesystem snapshot against an active adversary.

No change leaves final effects unrecorded. A Git diff cannot retain all
untracked/binary/mode evidence. Replacing frozen runners would silently change
their instrument, so this wrapper is prospective and requires later native
adapter integration. It does not provide session linkage, containment, an
independent identity observation, blinding, qualification or campaign authority.


## Failure-record refinement before execution

The first focused implementation passes, but its inventory quota exceptions
leave no durable truncation reason. CAPLAB-79 requires that reason alongside
retained prefixes. Select `failure.json` for `TaskCaptureError`, naming the
before/after phase, exact reason, truncation flag and sealed intent hash, then
propagate the error. A failure receipt is never a completed attempt. Storage
errors can prevent publication and continue to propagate without claiming a
receipt. This adds no launch or cleanup authority; it is within the authorized
capture files and synthetic verification scope.


## Execution and verification

Added `TaskCaptureLimits` and `capture_task_attempt`. The wrapper seals intent,
retains a before inventory, calls the existing bounded process owner, and then
retains an after inventory and hash-linked attempt receipt. The inventory uses
all task paths without filename or Git exclusions. Directory-relative opens
reject link following; regular files retain bounded raw bytes and mode/stat
observations. Symlink targets are retained as literal filesystem bytes, and
unsupported special files fail explicitly. Metadata and non-atomic snapshot
limits are stated in the [contract](../product/contracts/task-attempt-capture-v1.md).

Changes compare observable kind, mode, content and link target, leaving source
inode/time observations available separately. Rename effects remain a deletion
and addition; this component does not infer the underlying operation. Explicit
before/after byte and entry limits share one allowance. Inventory limit failures
retain a phase-specific truncation receipt and propagate; other domain failures
also record their reason. Storage/publication errors can leave only incomplete
custody and propagate without an eligible attempt.

The stream publisher was extracted to `seal_capture_json` for both owners.
Existing stream receipt JSON and `.capture.pending` naming remain unchanged.
A new setup-failure test reproduced an open stderr pipe while the process had
already been killed/reaped: `/tmp/caplab-task-capture-pipe-red.log` (one failure).
Both pipes are now registered with their cleanup owner before nonblocking setup.
Existing stream tests still exercise byte quotas, timeouts, cancellation,
short writes and receipt/directory sync failures.

The initial task test module had an unterminated triple-quoted fixture command;
that development syntax error was corrected before successful verification.
The first full suite passed 975 tests with four skips in 154.884 seconds:
`/tmp/caplab-task-capture-initial-make-check.log`. This checkpoint did not yet
include the durable inventory failure record. A subsequent test demonstrated
both missing before/after failure receipts:
`/tmp/caplab-task-capture-failure-record-red.log` (two missing-file errors).
The final focused suite passed 36 tests in 2.430 seconds:
`/tmp/caplab-task-capture-focused.log`.

Tests cover raw binary bytes, modes, empty directories, deletion/addition,
unchanged trees, non-UTF-8 filenames, literal external/dangling links, exact and
exceeded combined quotas, source mutation during copying, link replacement
before opening, FIFO rejection, disk failure, final publication failure,
nonzero process exits, timeout/stream overflow, intent-to-process observations,
and custody hashes/permissions. All inputs and processes are synthetic.

A retained end-to-end example changes `calc.py`, runs a real local Python
assertion, and captures its zero exit and `assertion passed` stdout. The two
inventories retain 64 file bytes across four entries. These are example counts,
not representative capture cost or a study budget. Script and summary:
`/tmp/caplab-task-capture-example.py` and
`/tmp/caplab-task-capture-example.json`; raw example custody:
`/tmp/caplab-task-capture-example-z35hc3ts/custody/attempt.json`, SHA-256
`ceac7e58666e8c8495908471b262f7b0b625c7cfa95c459f8f13b08ee36017fa`.

AST/direct-import checks and source hashes are retained in
`/tmp/caplab-task-capture-source-check.json`; no unused direct imports were found.
The source relies on the local Python 3.12.3/Linux filesystem APIs exercised by
the tests. No dependency, selected native harness, frozen source binding or study parameter changed.

## Remaining requirements

The caller still owns quiescence at both boundaries, stable trusted parents,
external containment and accounting for metadata/source copies/campaign storage.
These checks cannot make an actively changing tree atomic or establish every
intermediate write. Existing frozen native runners remain unchanged. CAPLAB-84
still needs adapters that link sessions, child sessions and diagnostics, enforce
native binding identity and campaign stops, and measure representative costs.
No reviewer, reference label, blinded surface or study outcome was accepted.


The failure-record checkpoint passed 976 tests with four skips in 120.664
seconds: `/tmp/caplab-task-capture-failure-record-make-check.log`. A subsequent
source-stability test showed that a newly added directory entry was labeled
`task-entry-limit` by the bounded recheck even with budget available. The check
now reports `source-entries-changed`, leaving `truncated: false` in that failure
receipt. Reproduction: `/tmp/caplab-task-capture-growth-red.log` (one failure).
This changes the stated failure cause, not whether the attempt is withheld.
The example was rerun on the final source after this refinement; the earlier
synthetic example custody remains retained separately.


## Doctrine receipt

The release retrieval-state gate passed at commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`. Corpus:
`corpus-2026-07-12-a11702cc9217`; doctrine: `doctrine-f6bbb5196a3f8bf9`;
retriever: `retriever-ec995ecdd083b2c8`.

Final packet `pkt-96d35aba7469917a`, content SHA-256
`96d35aba7469917a6ac8f650411b46d069ec69c5f8965dde66b6655d4bdb1227`,
uses five typed evidence records refreshed over two gathering passes. Applied
`universal-repository-contract-precedence` to implement CAPLAB-79 without
changing frozen runners; `python-structured-cleanup` to own descriptors and
both child pipes across failure; `python-text-bytes-boundary` to preserve raw
file and link bytes; and `agent-conduct-authority-bounded-action` to separate
synthetic component verification from live execution and reviewer acceptance.
Four citations classified as `valid-packet-citation`.

The 19 remaining obligations do not support a performance conclusion; none
is claimed. Their bounded applicability is retained here:

| Concept | Exact unmet requirements | Classification and reason |
|---|---|---|
| `implementation-repository-language-conformance` | CI and build matrix; formatter and static-tool configuration | Nonmaterial: no CI or static-tool conformance claim and no tooling change; local Python/Makefile checks are named above. |
| `performance-measurable-objective` | accepted workload and operation boundary; authority to inspect the target and identify the objective owner; environment, input distribution and scale, concurrency, and success/failure population; latency percentile, throughput, CPU, memory, I/O, network, cost, or other metric with a target; owner for the objective and any quality tradeoff | Nonmaterial to this correctness feature: no performance optimization, native workload cost target or study budget is selected. CAPLAB-84 retains representative measurement and CAPLAB-71 parameter selection. |
| `performance-metric-semantics` | access to instrumentation definition or benchmark harness; instrumentation definition and configuration; instrumentation overhead and data-loss limits; sanity check against actual runtime behavior; unit, aggregation window, population, and sampling behavior | Nonmaterial as a performance/profiling obligation: no observer-overhead or native cost claim is made. Task byte/entry units, combined allowances and loss behavior are explicitly specified and exercised above; example counts are not extrapolated. |
| `performance-representative-baseline` | correctness validation for the measured workload; exact code, dependency, build, benchmark, data, and environment versions; known resource limits and warmup/cache state; repeated raw measurements and variance | Nonmaterial: synthetic correctness checks do not claim representative speed, resource improvement or native capture cost. Those measurements remain unperformed. |
| `python-concurrency-model-selection` | task-size distribution; workload profile | Nonmaterial: no new worker or concurrency mechanism is selected; the wrapper uses sequential inventory phases around the existing owned process. No workload-scaling claim. |
| `python-repository-shaped-idiom` | formatter linter and type-checker configuration | Nonmaterial: no formatter, linter or type-checker policy change or conformance claim. |


## Completion checks

The final `make check` passed 977 tests with four skips in 136.562 seconds:
`/tmp/caplab-task-capture-make-check.log`. No source or test file changed after
this final run began. Final source/link and retained-example custody checks:
`/tmp/caplab-task-capture-final-source-links.json`. The consolidated receipt is
`/tmp/caplab-task-capture-verification.json`.

The eleven named doctrine scratch files were removed after retaining packet,
citation and obligation receipts. Test logs and both synthetic example trees
remain. The docs guard checked source/API names, units, error paths, links and
limits; no code sample or performance extrapolation is implied by the prose.
No tracker field, frozen manifest or external message changed. Commit closes
this prospective component implementation, not CAPLAB-84 or the broader goal.
