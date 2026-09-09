# Own process launch inputs before validation and setup

Date: 2026-09-08. Baseline: `5374fa6`. Primary agent under
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).

## Authorization before execution

Reproduce direct `capture_process` input mutation during filesystem setup with
a newly authored local Python child that only reports a synthetic argument and
environment. Add regression coverage in `tests/test_process_capture.py`; repair
`src/caplab/process_capture.py` if the reproduction establishes the defect.
Update its existing contract guide and this record. Snapshot argv and the
explicit environment before element validation or filesystem effects; use
only those owned snapshots for launch. Preserve all stream, limit, timeout,
cleanup, receipt and no-reuse behavior.

Run focused capture tests, the repository suite and an inspectable fixed local
probe with synthetic inputs only. Retain receipts, logs and source snapshots
under `/tmp/caplab-process-inputs-*`. Consolidate advisory provenance and remove
only named advisory scratch. Commit these four files locally; authorization
expires at commit. Stop if reproduction contradicts the proposed diagnosis or
if a repair requires broader effects.

No native harness/model call, historical capture read or mutation, study
admission, qualification, numerical gate, tracker write, external message,
push, service change or dependency change. Preserve the task-capture wrapper,
native adapters/verifiers, existing historical evidence, unrelated
`docs/designs/`, worktrees and timers.

## Diagnosis to test

`capture_process` currently validates the caller's command/environment, creates
the output directory and streams, then passes fresh copies of those original
objects to `Popen`. Mutation during setup can therefore change the inputs that
were validated. The reproduction changes only synthetic argument/environment
values during a real output-file open and observes the actual child output.
It does not substitute a fake process result.

The initial inspection suspected the task wrapper's intent-to-execution path,
but inspection of its function entry disproved that broader diagnosis:
`capture_task_attempt` already copies the command and environment before
sealing intent and inventory. Its owner remains unchanged. The repair concerns
direct callers of the lower-level process API, not a demonstrated historical
intent mismatch or a native provider identity defect.

The selected response, conditional on reproduction, is a local ownership fix.
Leaving caller mutation effective creates an avoidable gap between validation
and launch. Requiring locks throughout file setup adds coordination to every
caller; a private tuple and dictionary keep that responsibility in this owner.
Inputs must still remain stable while the initial snapshots are being made;
the API does not synchronize concurrent writers or arbitrary custom containers.

## Reproduction and implementation

The regression failed on baseline with child output
`["changed-argument", "changed-environment", "late-value"]` where original
values and an absent late variable were required. The failure log is
`/tmp/caplab-process-inputs-red.log`. The first divergence is the late read of
the caller containers at `Popen`, after the controlled mutation during the
real `native.stdout` open. No native/model call or historical incident is
implied by this local reproduction.

The process owner now copies argv into a tuple and the environment into a
private dictionary before validating their respective entries and before
filesystem setup. `Popen` receives those owned values. There is no ambient
environment merge. Immutable string entries need no deep copy; invalid entries
still fail before creating custody. Process cleanup, streams, deadlines and
receipt schema are unchanged. The task wrapper's earlier snapshots remain.

An inspectable two-child probe ran the retained baseline source and fixed
source with identical synthetic inputs and mutation timing. Baseline output
was `["changed", "changed", "late"]`; fixed output was
`["original", "original", null]`. Both exited 0 with complete streams.
Original inputs, changed caller values, observed output, source hashes and
capture hashes are retained in `/tmp/caplab-process-inputs-probe.json`;
raw custody is `/tmp/caplab-process-inputs-probe-egraiooo/`. The baseline source
and probe script remain under the same `/tmp/caplab-process-inputs-` prefix.

After repair, 64 focused tests passed. Adding explicit malformed-container and
entry checks produced a final focused run of 65 passing tests in 5.591 seconds
across process capture, task capture, task verification and version capture.
The final log is `/tmp/caplab-process-inputs-focused-final.log`. The two new
tests observe actual child behavior and rejection before custody; their
filesystem interception delegates real opens and does not mock process output.

This closes the demonstrated input-ownership gap for direct calls. It does
not bind a native executable or provider to a study, make initial copying
atomic against concurrent mutation, or qualify any retained historical attempt.

## Final verification and advisory closure

`make check` exited 0: 1,174 tests in 153.284 seconds, four skips. The retained
log is `/tmp/caplab-process-inputs-make-check.log`. Baseline process source SHA-256
is `bc2d05f3e919046fcaf523924ca67aaa2a1565ca8b9c9c0ce7424f8db166f615`;
fixed source is `bd89b2a8a8c0a477425d8bbd0736a07fe09633f5cb74081166a23f760ce8721f`.
Both probe receipts and stream hashes were reverified after execution. Nine
protected instruction, source, test and build files match baseline bytes.

The consolidated `/tmp/caplab-process-inputs-verification.json` retains the
source checks, failed reproduction, focused/full-suite results, actual probe,
typed evidence, advisory citation receipt and cleanup verification. Its
authorization snapshot is `/tmp/caplab-process-inputs-authorization.md`;
that preserves the typed source hash after this record's verification append.

Pincite's release retrieval gate passed at
`/home/halbritt/.local/share/pincite/release`, commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`. The final packet is
`pkt-b5ac2ebaed7f4caf`, content SHA-256
`b5ac2ebaed7f4cafe94db6186755b18358136d63a72ec422957206059cb75fc6`,
corpus `corpus-2026-07-12-a11702cc9217`, doctrine
`doctrine-f6bbb5196a3f8bf9`, retriever `retriever-ec995ecdd083b2c8`.
Four consumed concepts classified as valid citations:
`universal-repository-contract-precedence` preserves capture contracts;
`universal-evidence-before-intervention` requires the actual reproduction;
`universal-preserve-behavior-by-default` limits the repair to ownership;
`agent-conduct-authority-bounded-action` preserves the execution scope.

Reassembly also activated routes outside this repair. All 35 unmet obligations
remain individually classified with exact wording and rationale in the
manifest: ingest/deduplication, UI/presentation, configuration cross-references,
top-N ranking, external capability/monitoring, property evolution and production
incident evidence. None supports a claim made here. No such mechanism changed,
and the local reproduced defect is not called a production incident. These
obligations are nonmaterial to the demonstrated direct-process ownership repair.

Eleven exact advisory scratch files were deleted after consolidation. Probe
custody, source snapshots and test logs remain. Verification is technical
evidence, not independent acceptance or a claim that the roadmap is complete.
