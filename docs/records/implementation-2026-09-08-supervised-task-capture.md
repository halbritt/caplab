# Capture task state across a supervised namespace lifetime

Date: 2026-09-08. Baseline: `2901f07`. Primary agent under
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).

## Authorization before execution

Add `src/caplab/supervised_task_capture.py`: a recorder that seals intent before
an externally owned supervisor launches, retains a before inventory through an
identified directory descriptor while work is blocked, and retains the after
inventory only when the caller supplies an anchored process receipt and has
stopped task writers. It does not launch or stop processes itself. Preserve
v1 task capture. Use matching v2 task intent, attempt and inventory receipts
with explicit namespace source and observed descriptor identities. Bound both
inventories under one existing task byte/entry allowance; require a separate
positive bound for the process receipt. Refuse invalid call order and preserve
partial custody on failure. Own only a duplicate of the caller's descriptor.

Allow supporting changes in `task_capture.py`, `task_capture_verify.py`,
`codex_capture_link.py`, `claude_capture_link.py`, `capture_accounting.py` and
`native_tool_pairs.py`; the last four must preserve source provenance and
existing claim ceilings. Add `tests/test_supervised_task_capture.py` and
`docs/product/contracts/supervised-task-capture-v2.md`, link the existing task
capture and verification contracts to it, and complete this record. No other
runtime changes or modifications of frozen evidence.

Use new synthetic task and native-format fixtures only. Exercise the lifecycle,
source identities, shared quotas, receipt/version corruption and downstream
consumers. Permit fixed Bubblewrap fixtures with a private 1-MiB task tmpfs,
a private 1-MiB runtime tmpfs, read-only system/test inputs and no network or
writable host mount. A fixture hands descriptors to the parent and blocks until
before capture is sealed, then changes only a small authored task file and
writes small authored native-format outputs. Cover ordinary completion and
explicit nonzero failure; no actual native harness runs. Limit each process to
five seconds and 100,000 combined stream bytes using the existing process
capture component; close received descriptors and clean only owned processes
and temporary roots. No user service or cgroup is created or changed.

Run focused tests, one retained synthetic integration example if needed for
reviewable custody, and `make check`. No model, credential, historical capture,
study admission, ranking, acceptance, external message, Plane write or push.
Preserve `docs/designs/`, sibling worktrees, unrelated runtime state and the
unanswered independent-judgment request. Keep source/authorization hashes,
failures and verification under fresh `/tmp/caplab-supervised-task-*` paths.
Consolidate advisory provenance before deleting only named scratch. Commit only
the named files locally; authorization expires at commit. Stop before wider
effects, ambiguous ownership or unsupported source-lifetime assumptions.

## Selected implementation

The v1 task wrapper captures a host directory before launching its process.
A private task namespace becomes available only after setup starts, so it needs
a before-capture barrier between setup and workload release. The new
`SupervisedTaskCapture` keeps that sequence explicit without adding another
process launcher or changing v1 execution behavior.

Entering the recorder seals intent. `capture_before` duplicates the caller's
directory descriptor, checks its expected identity and output ancestry, and
seals the before inventory. The supervisor retains that hash before release.
`finish` verifies the supplied process-receipt anchor and captured streams, then
seals the after inventory and linked attempt. Both scans use the same owned
descriptor and share the existing task byte/entry allowance. Normal context
exit without finish is an error; ordering violations cannot be caught and used
to resume the same recorder. Partial custody survives errors, and only the
duplicate is closed.

V2 intent identifies the declared namespace source separately from the host
launch/preparation directory. V2 inventories record the expected descriptor
identity and observed root stat identity. The task verifier requires matching
schema versions and both root identities; native root linkers and byte
accounting additionally compare the namespace path to the canonical invocation.
Tool-pair inspection includes the verified task source. Existing claim ceilings
remain: the recorder cannot authenticate the earlier handoff, prove a frozen
initial task was copied correctly, establish quiescence itself, or bind the
executed native invocation.

This connects before/after task custody to descriptor-based native collection.
The test supervisor exercises that connection with fixed local workloads.
Integration with the resource-limited supervisor, exact native Binding and
launch evidence, frozen task content checks, and representative repair/coding
measurements remain incomplete. CAPLAB-84 stays open. Neither these synthetic
outputs nor passing checks establish reviewer capability or independent
acceptance.

## Verification

Seven focused methods passed in 1.582 seconds. The integration method runs both
Codex-format and Claude-format fixtures at exit 0 and exit 7. Each fixture's
namespace process waits for the sealed before inventory before changing `item`
from exact bytes `old` to `changed`. Its process exits before the after snapshot
and native collection. After source removal, both native root linkers,
byte accounting and captured tool-pair inspection still verify the retained
bundles. Process exit and native-completeness limits remain explicit.

Other checks cover unfinished/out-of-order recording, recovery attempts after a
caught ordering error, descriptor mismatch, shared before/after byte and entry
limits, wrong process anchors, a too-small process-receipt allowance, rehashed
inventory identity/version/source changes, and duplicate-descriptor cleanup.
No actual native harness, network endpoint, user service or cgroup was used.

Final source review found that Python dictionary equality could accept an after
identity with inode `True` when the before inode was integer `1`. The verifier
now validates the after identity's integer types independently. A rehashed
synthetic regression fixture fixes both root inode observations at integer `1`
and sets only the after descriptor inode to Boolean `True`; verification must
refuse it. This test protects the type requirement without treating offline
source-stat consistency as physical handoff authentication.

The first full suite passed 1,226 tests in 163.607 seconds with four skips.
It preceded the final Boolean-identity guard, so a final suite was required.
The earlier result remains at `/tmp/caplab-supervised-task-make-check-first.log`;
focused final result is `/tmp/caplab-supervised-task-focused-verified.log`.

One new failed-work example remains at `/tmp/caplab-supervised-task-probe/`.
Its `report.json` SHA-256 is
`f058aba817a0bc0f505fa27ec2d1fd1b67227e940bd39f98d2f94df21349dab7`.
It retains exit 7, exact before/after bytes, task source `/work`, native runtime
source `/episode`, and 532 logical payload bytes across retained occurrences.
Its root descriptor identities are observations from this synthetic run;
they do not attest a model or native harness. The source directories were
removed and received descriptors closed. `final-recheck.json` confirms the
retained task report remains identical under the final identity guard.

The final `make check` passed 1,227 tests in 167.444 seconds with four skips;
log `/tmp/caplab-supervised-task-make-check-final.log`. Changed Python parsed,
imports were checked for unused names, document links resolved, and
`git diff --check` passed. No runtime or test source changed after this final
verification.

## Advisory provenance and closure

Pincite's release gate passed at commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`, source fingerprint
`ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`.
Final packet `pkt-c38028ad0921ede8` has SHA-256
`c38028ad0921ede8075976bf06aa5fb70835a24dba9687765f15524c8d99af90`;
corpus `corpus-2026-07-12-a11702cc9217`, doctrine
`doctrine-f6bbb5196a3f8bf9`, retriever `retriever-ec995ecdd083b2c8`.

Four served concepts informed the change and were classified as valid citations:
`universal-repository-contract-precedence` for delegated scope,
`python-structured-cleanup` for descriptor and context ownership,
`universal-evidence-before-intervention` for the blocked-namespace lifecycle
gap, and `universal-preserve-behavior-by-default` for retaining the valid v1
path and consumer claim ceilings. CAPLAB owns the authorization and decision.

All 28 remaining obligations are nonmaterial to this implementation claim:

| Unmet requirements | Reason |
| --- | --- |
| CI and build matrix; formatter and static-tool configuration; repository version and dependency contract; Python and dependency version matrix; formatter linter and type-checker configuration | No dependency, tooling or cross-platform support change. The existing local toolchain and full suite bound verification. |
| Accepted workload and operation boundary; authority to inspect the target and identify the objective owner; environment, input distribution and scale, concurrency, and success/failure population; latency percentile, throughput, CPU, memory, I/O, network, cost, or other metric with a target; owner for the objective and any quality tradeoff | No performance target, optimization or representative native-workload conclusion is selected. The fixtures verify capture behavior only. |
| Access to instrumentation definition or benchmark harness; instrumentation definition and configuration; instrumentation overhead and data-loss limits; sanity check against actual runtime behavior; unit, aggregation window, population, and sampling behavior | No new performance metric or capture-overhead estimate. The retained byte total keeps the existing logical-occurrence meaning; representative cost measurement remains open. |
| Correctness validation for the measured workload; exact code, dependency, build, benchmark, data, and environment versions; known resource limits and warmup/cache state; repeated raw measurements and variance | No performance comparison or representative baseline claim. Reported test durations describe verification executions only. |
| Baseline; task-size distribution; workload profile | The recorder is sequential. One bounded fixture thread drains process streams during the blocked handoff; no throughput or parallel-capacity gain is claimed. |
| Affected classes or attributes; demonstrated repetition and ordinary-alternative analysis; lookup and construction semantics; repeated rule; tooling and compatibility | No dynamic attribute, descriptor protocol or metaclass mechanism. Ordinary methods and context ownership express the required lifecycle. |
| Evidence-explicit-user-requirements | Exact bounded scope derives from ADR 0026, supplied as repository-contract evidence; no new owner judgment is needed for these edits. |

`/tmp/caplab-supervised-task-verification.json` consolidates source/result
hashes, complete advisory packet/evidence contents, obligation classifications
and the citation receipt. Only eleven named advisory scratch files are deleted
after consolidation. Authorization snapshots, logs and the retained failed-work
example remain available. This local commit consumes the authorization.
