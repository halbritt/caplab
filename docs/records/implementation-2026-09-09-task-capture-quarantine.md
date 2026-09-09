# Extend prospective quarantine through task capture

## Decision and bounded authorization

Under ADR 0026 and the continuing CAPLAB improvement request, the primary agent
authorizes optional `quarantine_factory` support in `capture_task_attempt` and
`SupervisedTaskCapture`, reuse of the guarded inventory copier, and checking of
task intent, inventory, failure and final receipts before publication. Include
literal input/output paths and generated/pending custody names. The host wrapper
must forward the factory to its process capture. The supervised recorder keeps
its existing external launch/quiescence/cleanup ownership: the caller must also
select the policy on its separately owned process capture.

At baseline `7d874c4`, neither task facade forwards a policy to `_Inventory`.
Task intents retain command/environment strings; v1 failure receipts retain
exception reasons. Process capture guards raw streams but not its generated
receipt. These are concrete unguarded writes in the planned native adapter.
Authorize checking that process receipt with the existing helper before sealing.
Move the `StreamQuarantine` protocol definition into its synchronous checking
module to permit that dependency, preserving the existing public import through
`process_capture`. Do not refactor the concurrent stream loop or legacy matcher.

Permitted changes: `task_capture.py`, `supervised_task_capture.py`,
`process_capture.py`, `capture_quarantine.py`, their relevant contracts, synthetic
tests and this record. Preserve None/default capture behavior and v1/v2 receipt
formats, exact raw bytes, shared quotas, independent verification, descriptor
ownership and supervised state transitions. The factory remains trusted,
bounded, caller-owned policy. No identity or privacy attestation is added to
component receipts. Check JSON strings before escaping and exact serialized
bytes; check command/environment/path filesystem representations where those
strings also cross an execution or filesystem boundary.

Guarded exceptions must not publish a final task attempt. A quarantined failure
reason must not be copied into `failure.json`; other safe v1 task-error receipts
may still be written. Process exceptions keep their existing cleanup and stop
the host wrapper before an after scan. Supervised snapshot/publication failures
poison its existing one-use lifecycle; exit still closes only its duplicate.
Source files and already retained private safe prefixes are preserved. No retry,
purge, historical evidence effect or automatic continuation after failure.

Authorize real local Python child processes and temporary fabricated files for
tests, private artifacts under `/tmp/caplab-task-quarantine-*`, focused/full
checks and a verified local commit. Preserve unrelated files, `docs/designs/`,
worktrees, services and all credentials. No installed native harness execution,
provider call, model spend, actual credential inspection, tracker write,
outbound message, evidence admission or independent acceptance. Authorization
expires at the verified commit; stop on unexplained behavior or failing checks.

## Placement and verification

Leaving the facades unguarded would leave task files and input receipts exposed.
Checking only after publication cannot prevent durable exposure. Whole-file
buffering defeats the established quotas. Reuse the inventory and byte/document
checker while keeping filesystem state, process cleanup and supervisor lifetime
with their existing owners. The protocol move changes definition placement only;
it preserves the process module's import compatibility and avoids a cycle when
process publication calls the checker. No new service or policy implementation.

Verify pre-launch refusal for secret-bearing task/input metadata, quarantine of
after-task writes and streams, safe raw round trips through v1/v2 verification,
shared quota/failure handling, caught supervised failures/reuse rejection,
retained-descriptor ownership, metadata and cleanup failures, and preservation
of existing default tests. Synthetic processes must never receive real secrets.
Passing these checks is mechanism verification, not full-surface blinding,
authenticated execution, representative repair measurement or roadmap completion.

## Execution and focused verification

Both facades now accept the optional factory and pass it to their before/after
inventory copier. A shared task helper checks copied intent strings in JSON and
filesystem/exec representations before custody creation, including planned
directories, output names and pending receipt names. Another task helper checks
receipt names and content before calling the unchanged publisher. The v1
failure handler uses that path too. The host wrapper forwards the factory to
process capture; the supervised recorder retains external process ownership.

Process capture now uses fresh metadata gates to check its generated receipt
after complete streams and stream-gate cleanup, before publishing it. The
concurrent stream mechanism is unchanged. The protocol definition moved into
`capture_quarantine` so the process module can call its checker without a cycle;
`process_capture.StreamQuarantine` remains available. No legacy matcher or
credential-administration code changed.

Thirteen new public API tests use temporary task files and actual local Python
child processes with fabricated values. Vertical regressions first failed on
the missing host and supervised inputs, unguarded command intent, missing stream
forwarding and the process receipt's unguarded publication. Those failing logs
are retained under `/tmp/caplab-task-quarantine-` as `red.log`,
`supervised-red.log`, `intent-red.log`, `stream-red.log`, and
`process-receipt-red.log`. Each test passed after its corresponding change.

The focused suite passed 110 tests in 11.264 seconds; its log is
`/tmp/caplab-task-quarantine-focused.log`. It includes the existing host,
supervised, verifier, process, descriptor, native-quarantine and task-input tests.
The new tests establish:

- A secret crossing the file read boundary in the before tree prevents host
  launch. Supervised refusal prevents successful `capture_before`, and caught
  errors cannot resume the same recorder; its borrowed descriptor remains open.
- Command and environment secrets, including non-UTF-8 environment bytes, are
  rejected before output creation. Generated/pending names and invalid policies
  also fail before custody; failed supervised entry cannot be retried.
- Real task writes containing the secret stop the after scan for both facades
  without altering those source bytes. Stream quarantine stops the host wrapper
  before an after scan. Timeout/overflow likewise publish no guarded attempt.
- Safe binary bytes, non-ASCII filenames, literal non-UTF-8 symlinks and a safe
  incomplete secret prefix survive exact combined byte/entry budgets. Both v1
  and v2 independent verification pass with nonzero process exit 7; v2 finish
  uses the retained descriptor after the task's host directory is moved.
- Inventory/final/process metadata is checked before publication. A secret in
  a task-error reason does not enter a failure receipt, while safe quota errors
  retain their phase/truncation records and abandon incomplete buffered bytes.
- Final policy-cleanup failure prevents the supervised attempt receipt and
  poisons the one-use lifecycle even when caught. Exit preserves the borrowed
  descriptor and releases the recorder's duplicate.

These tests establish the local mechanism and its failure behavior. They do not
attest an arbitrary factory, authenticate a native harness, or prove that a
supervised caller guarded its external process. Source custody and external
exception/log handling remain caller-owned. No secret zeroization, transformed
leak detection, independent privacy acceptance or representative cost/quality
measurement follows.

The live roadmap was read at baseline `7d874c4` and still had twelve open items;
CAPLAB-84 was In Progress and CAPLAB-80/85 Ready. Read-only snapshots are
`/tmp/caplab-roadmap-20260909-7d874c4.json` and
`/tmp/caplab-roadmap-states-20260909-7d874c4.json`. No tracker state changed. The
next adapter must freeze its policy identity, apply it across all owned writers,
bind task/native/process custody and satisfy separate credential administration
and execution authorization before representative repair measurement.

## Advisory and review

The release retrieval gate verified fingerprint
`ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`,
corpus `corpus-2026-07-12-a11702cc9217`, doctrine
`doctrine-f6bbb5196a3f8bf9` and release commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`. Initial packet
`pkt-a5e89f81635c6d4b` was followed by two typed evidence passes over authority,
contracts, current source ownership and executed tests. Final packet
`pkt-6316ddcfe439c48f`, retriever `retriever-ec995ecdd083b2c8`, has content hash
`6316ddcfe439c48f81d9fa78f4762992d37f9192042f4443e56c56270a69921d`.

Seven remaining obligations are nonmaterial to the bounded local claim:
recurring change evidence (current concrete write paths establish this need),
workload evidence for optimization (no performance optimization is claimed),
CI/build matrix, formatter/static-tool configuration, Python/dependency version
matrix, formatter/linter/type-checker configuration and full repository
toolchain inspection (no dependency/toolchain change or platform qualification
is claimed). Local declared-version, neighboring-code and executed checks are
the evidence used instead of a broader conformance claim.

Seven used concepts have valid packet citations: placement by ownership,
explicit invariants, mutable ownership, structured cleanup, repository-contract
precedence, preservation by default and evidence before intervention. The
boundary is the existing caller-owned policy and capture-owned sink; the new
helpers do not introduce a different policy or transfer process ownership.
Revisit them if a selected adapter needs materially different lifetime or
representation semantics. Advisory guidance does not create product authority.

The review checked for secret-bearing exception serialization, early publication,
implicit default policy, swallowed failures, lost quota accounting, descriptor
ownership changes, source mutation, changed raw bytes and fabricated completion.
Existing unguarded behavior remains explicit. The record makes no independent
acceptance or whole-roadmap completion claim.

## Final local verification

`make check` passed: 1,289 tests in 181.464 seconds, with four skips. Its log is
`/tmp/caplab-task-quarantine-make-check.log`. Ruff's undefined-name/unused-import
check passed for all four changed runtime modules and the new tests. Changed
documentation links resolve, and `git diff --check` is clean. Runtime/test
sources remained unchanged throughout the full run.

`/tmp/caplab-task-quarantine-verify.py` checked the terminal focused/full logs,
runtime/test hashes retained by the final typed evidence and seven valid
citations. Private manifest `/tmp/caplab-task-quarantine-verification.json`,
SHA-256 `e6cc03fe8aea285de06e14556b92ee39e2989f8f76a94c53e03f8f31f220733c`,
retains hashes for 23 artifacts and final runtime/test/contract sources. Twelve
advisory scratch files were embedded byte-for-byte, rechecked and removed by
exact filename. The failing/focused/full logs, initial scope snapshot and
verification script remain separately addressable in private files. No
historical evidence was rewritten or purged.
