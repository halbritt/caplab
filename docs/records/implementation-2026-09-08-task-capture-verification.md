# Verify retained task capture before inspection

Date: 2026-09-08. Baseline: `e3ff0b9`. Decision owner: primary agent under
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).

## Authorization before execution

Add a read-only task capture verifier and inspection CLI in
`src/caplab/task_capture_verify.py` and `scripts/verify_task_capture.py`, with
`tests/test_task_capture_verify.py`, a versioned contract, a link from the
existing task capture contract, and this record. Verify only newly created
synthetic bundles in temporary directories, including deliberate corruption,
unsafe filesystem objects and bounded local Python child processes. Run focused
checks and `make check`; commit locally. Preserve existing capture producers,
frozen bindings/manifests, historical evidence, `docs/designs/`, other worktrees
and services. No native launch, model spend, evidence admission, historical
inspection or mutation, tracker write, external message, ranking or placement.
Retain verification logs/probes; remove only named doctrine scratch after
recording its receipt. Authorization expires at commit. Stop on unexplained
producer incompatibility or any need for broader authority.

## Decision and verification boundary

The task capture contract requires later consumers to reverify component and
object hashes, but the current implementation has no such consumer. Select one
read-only API and CLI that require a caller-supplied attempt SHA-256 from an
independently retained source. Hashing the same local attempt file at inspection
time is not an independent anchor. Check its linked JSON receipts, every named
payload, counts, limits and the change summary before returning a compact
inspection report. Raw task/stream bytes remain opaque; the report omits the
command and environment. Bound combined receipt reads with an explicit caller
budget; stream payload hashing in bounded chunks under the anchored capture
limits. Refuse linked or special custody objects and unsafe object locators.

No change leaves every future consumer to reconstruct this contract. Replacing
the capture producer or adding native integration would enlarge this task
without resolving the missing read boundary. This is a new feature, not a
producer repair or a full schema/chronology validator. Source stat and timestamp
observations remain hashed metadata, not authenticated facts. A consistent
bundle can describe timeout, truncation or a failed task; none becomes eligible
or accepted through this verifier. The caller supplies trusted, stable custody
parents and quiescence. Hash checks do not establish original truth, hardware
durability, native identity, containment or successful publication history.

## Execution and focused verification

Added `verify_task_capture` and its CLI. The implementation owns directory/file
handles with context managers, parses each receipt only after matching its
expected byte hash, and hashes payloads in bounded chunks. It uses the existing
strict JSON parser and task-change comparison; it does not change either capture
producer. The new contract explicitly limits the claim to integrity and selected
summary invariants, leaving source-stat/timestamp authenticity and publication
history outside this API.

The CLI is the first consumer. The new reader and its parsed dictionaries are
owned by one synchronous call; no cache, worker, mutable default, caller-owned
JSON mutation or shared object registry is introduced. Receipt raw bytes are
bounded by the explicit caller allowance, while payload allowances come from
the independently anchored intent. The three source dependencies remain byte
identical to baseline. Existing callers and formats are preserved; no migration
or replay is selected. Reopen the design for a different capture schema or a
consumer requiring admission, chronology, stable source sealing or concurrency.

Fourteen focused tests passed in 2.019 seconds:
`/tmp/caplab-task-verify-focused.log`. They use actual local Python captures and
new synthetic files only. Checks include every linked receipt and object,
same-size payload corruption, missing payloads, linked roots/components/leaves,
a real FIFO behind the CLI's three-second child bound, ambiguous JSON, unsafe
locators, inconsistent totals and summaries, exact receipt-budget boundaries,
non-UTF-8 contents/names/targets, and timeout/truncation reports. Changing a
payload while reading produces an error and closes every observed descriptor.
A 200,000-byte payload probe observes reads no larger than 65,536 bytes. Successful
verification preserves captured bytes, modification times and modes and works
after the original task directory is removed. This is new-feature verification;
no pre-existing defect reproduction or independent study verdict is claimed.

The retained synthetic example at
`/tmp/caplab-task-verify-example-dk138joz` changes `calc.py` from subtraction to
addition, runs the local assertion, retains a separate digest file and invokes
the CLI. Its report checks 4,365 receipt bytes, 64 task bytes, four task entries
and 17 stream bytes, and reports the single content-hash change. Attempt SHA-256:
`c1abbcd970c426d6f3f07d4724d9f372ee52456bff0e02edf68c573c707079e9`.
The separate digest demonstrates the caller handoff; it is not registered or
protected external custody. Probe and result:
`/tmp/caplab-task-verify-example.py` and `/tmp/caplab-task-verify-example.json`.

Direct import-use/source checks are in
`/tmp/caplab-task-verify-source-check.json`; no unused direct imports were found.
The exercised runtime is Python 3.12.3. No new dependency, checker or CI setting
is introduced. Source inspection and executable checks support the declared
local behavior; they do not establish native-harness compatibility or hardware
persistence.

## Doctrine receipt

The release retrieval gate passed at commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`, corpus
`corpus-2026-07-12-a11702cc9217`, doctrine `doctrine-f6bbb5196a3f8bf9`,
retriever `retriever-ec995ecdd083b2c8`. Final packet:
`pkt-2728d06052c77790`, SHA-256
`2728d06052c77790727f4560959445d10a73ee4af1972a9229a54e896c3ee4b5`.
One evidence-gathering pass supplied five typed records. Five cited concepts
classified as `valid-packet-citation`:

- `implementation-minimal-coherent-api`: one reader and one inspection CLI,
  with an explicit anchor and receipt allowance.
- `python-structured-cleanup`: own descriptors through failed validation/reads.
- `python-text-bytes-boundary`: decode receipt JSON only; retain payload opacity.
- `python-runtime-static-boundary`: enforce selected JSON invariants at runtime.
- `agent-conduct-authority-bounded-action`: report integrity without admission,
  spend or historical effects.

The five unmet obligations remain nonmaterial to this bounded implementation:

| Concept | Exact unmet requirements | Reason |
|---|---|---|
| `implementation-repository-language-conformance` | CI and build matrix; formatter and static-tool configuration | No CI/toolchain change or cross-matrix conformance claim; use existing local `make check`. |
| `python-repository-shaped-idiom` | formatter linter and type-checker configuration | No formatter/checker policy change or static conformance claim. |
| `python-runtime-static-boundary` | annotation maintenance cost; configured checker and Python version | Local Python is recorded, but no configured checker is qualified and no annotation-cost or static-proof claim is made. Runtime checks and exercised failures support this boundary. |

The code review retained one inventory validator instead of splitting its
interdependent tree/count checks to meet a generic line limit. It reuses the
existing JSON and change semantics, keeps errors explicit, and introduces no
plugin, registry or fallback result. The prose pass replaced broad verification
language with the enumerated integrity checks and their exclusions.

## Completion checks

`make check` passed 999 tests with four skips in 133.293 seconds:
`/tmp/caplab-task-verify-make-check.log`. Source and test hashes did not change
after that run began. Six local documentation links resolve. The consolidated
receipt is `/tmp/caplab-task-verify-verification.json`; source/link checks and
all focused/full logs and the synthetic example remain available.

The eleven named doctrine scratch files were removed after retaining their
packet, citation and obligation receipts. No tracker field or historical
capture changed. The refreshed roadmap still has twelve open items; this
component advances capture inspection without completing native session/child
capture, containment, blinding, study execution or the overall CAPLAB goal.
