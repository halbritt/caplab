# Prepare and materialize an anchored task input

Date: 2026-09-08. Baseline: `d58c9bb`. Primary agent under
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).

## Authorization before execution

Add `src/caplab/task_input.py`, `tests/test_task_input.py`,
`docs/product/contracts/task-input-v1.md` and this record. Link the existing
supervised task capture contract to the new input path. Preserve all current
runtime APIs, receipt schemas, native profiles and frozen evidence.

Prepare a fresh bounded input bundle from an explicitly supplied, quiescent
host directory using the existing task inventory implementation. Return its
sealed receipt hash. Verify both receipt/payload integrity and the supported
materialization policy before creating a destination entry. Materialize only
through a caller-owned empty directory descriptor with an expected device and
inode, preserving regular-file bytes, literal symlink targets, empty
directories and supported permission modes. Reject special objects, privilege
bits and modes that prevent owner verification. Do not restore ownership,
timestamps, ACLs, extended attributes or hardlink topology. Verify the resulting
tree before returning a materialization receipt; retain partial output and
return no receipt on failure. Close only owned descriptors. Reject overlap
between input custody and destination under trusted stable ancestry.

Use new synthetic inputs and the already exposed development world's exact
`TASK.md`, `parent/transfer.py` and `repairs/transaction.py` under
`docs/product/studies/advisory-selection-001/development-worlds/atomic-transfer-v1`.
Permit copying those development files into new test inputs and retaining their
commit/path/hash provenance. This is neither historical campaign import nor
study admission. In one fixed integration fixture, a Bubblewrap process hands
the supervisor a private 1-MiB task tmpfs descriptor and waits. The supervisor
materializes the verified input, captures before state, then releases a fixed
authored repair-file copy. Retain and verify after state. No actual native CLI,
model, credential, network, user unit or cgroup is used. Limit that fixture to
five seconds and 100,000 stream bytes; clean only its owned process and roots.

Test exact byte/mode/link preservation, source removal, mutation refusals,
identity/overlap checks, quotas and partial-output ownership. Run focused tests
and `make check`. Retain new input/probe custody, source and authorization
snapshots, failures and verification under `/tmp/caplab-task-input-*`.
Consolidate advisory scratch before deleting only its named files. Preserve
`docs/designs/`, other worktrees, services, historical evidence and unanswered
human judgments. No tracker write, message, push, ranking or independent
acceptance. Commit only the named files locally; authorization expires
at commit. Stop before wider effects or unsupported filesystem semantics.

## Decision

The supervised recorder captures whatever is present in a blocked task
namespace. The successful native startup checks used an empty task; they do
not establish that a selected repair input can be reproduced there. The
existing advisory materializer is for production text trees with normalization
and historical-store semantics, so it cannot preserve the byte/link/mode
contract needed here without changing that separate instrument.

Use the existing inventory and verifier for a new anchored task-input bundle,
then create and check an empty destination through its descriptor. The caller
retains the input hash, owns the blocked interval, seals the returned
materialization receipt and connects it to before capture and launch evidence.
No-change would leave this input identity link missing; a path-based unchecked
copy would depend on a mutable host source. This component does not choose a
world, establish a complete Binding, authorize a launch or validate task truth.

## Related root-entry repair authorization

Source review found that v2 task verification takes the first sorted inventory
entry's source stat as the root identity. A valid name such as `!first` sorts
before `.`, so the recorded directory identity can be compared to a file's
inode. Authorize a regression in the new test file and the minimal repair in
`src/caplab/task_capture_verify.py`: select the validated root entry by its
exact `.` path. Preserve schema versions and all identity/type checks. This
adds that one source file to the local commit scope; it grants no new execution
or evidence effects. Reproduce the refusal before changing the verifier.

## Execution and focused verification

Added preparation, read-only verification and descriptor-based materialization
under the [task-input v1 contract](../product/contracts/task-input-v1.md).
The existing inventory verifier owns path, payload and quota validation; the
new module owns the supported reproduction policy, content identity, exclusive
creation, descriptor lifetime and final tree check. Input receipt and payload
verification completes before destination creation. Errors preserve partial
output and close only owned descriptors. No process launch or study admission
is part of this API.

The initial six-test run reproduced the root-entry defect: the blocked repair
completed, but v2 verification raised `task inventory root differs from
descriptor identity` because `!first` preceded `.`. Five other tests passed.
The minimal root-path selection repair then passed all six. Added final-tree
corruption coverage and ran seven focused tests: all passed in 0.507 seconds.
Logs are `/tmp/caplab-task-input-focused-{first,fixed,final}.log`.

The tests cover arbitrary file and filename bytes, dangling literal link
targets, executable modes, empty directories, removal of original source,
wrong independent anchors, payload tampering, exact combined receipt limits,
unsupported modes with rehashed receipts, descriptor identity, nonempty and
overlapping destinations, task quotas, partial output after an injected
filesystem sync error, and final readback refusal after payload corruption or
an unexpected entry. Filesystem-boundary failure injection supplements real
filesystem and namespace execution; no native harness is mocked into evidence.

A separate retained run of the same fixed Bubblewrap fixture is under
`/tmp/caplab-task-input-probe/`. Its source was removed before launch. The
supervisor reproduced the anchored input in the blocked private `/work`,
sealed materialization and before-release links, captured before state, then
released the authored repair copy. Retained before bytes match the frozen
input, after bytes match the named authored repair, and only `transfer.py`
changed. Task verification succeeded after namespace exit with complete
process streams. `observations.json` SHA-256 is
`7b56eeb212de693fa7205378371e53dbd0baf8fdacea97515242508fe6d2e5c5`.
The source root is absent, the handoff socket was removed and all fixture
processes exited. No unit, cgroup, native CLI, account or model was used.

The three authorized development source files retain baseline `d58c9bb`,
absolute paths, byte counts and hashes in
`/tmp/caplab-task-input-world-sources.json`; each hash was checked again after
the retained run. These are already exposed authored development examples,
not independent repair truth or new study evidence.

## Advisory provenance and decision boundary

Pincite was advisory to repository authority. The release gate passed for
`/home/halbritt/.local/share/pincite/release` at commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`, fingerprint
`ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`,
corpus `corpus-2026-07-12-a11702cc9217`, doctrine
`doctrine-f6bbb5196a3f8bf9`, retriever `retriever-ec995ecdd083b2c8`.
The question was: how should an anchored task input be materialized into an
empty caller-owned namespace directory while preserving byte identity,
explicit quotas and partial-failure ownership?

Initial packet `pkt-b19e95fdc8722eec` was followed by one typed-evidence
gathering pass covering authority, contracts, source and tests. Final packet
`pkt-6ce1fc67727af4ba` has content SHA-256
`6ce1fc67727af4bac6d2764264e651c6015b55d77632fb1e43f49d7174b0d1c7`.
The applied concepts were repository-contract precedence, structured cleanup,
mutable ownership and explicit invariants. Citation classification closes
their consumption trace. All 12 remaining generic obligations were classified
individually as nonmaterial: ten concern Python repository conformance with no
toolchain or dependency change selected; recurring-change evidence is not
needed for a boundary grounded in the new invariant; workload evidence is not
needed because no optimization is proposed. Their exact requirements and
rationales are retained with the packets in private verification custody.

Reopen this decision if selected tasks require unsupported metadata, concurrent
source/destination writers, a different filesystem policy or a different
custody model. The next execution integration must independently connect input,
materialization, before capture, authenticated handoff and exact native launch.
This fixture does not verify that integration, native repair completion,
provider identity, representative coding reliability, study eligibility or
acceptance. No roadmap item or human-owned judgment was marked complete.

## Final verification and custody

`make check` passed 1,234 tests in 150.246 seconds with four skips; log
`/tmp/caplab-task-input-make-check.log`. The seven new focused methods include
the real private-namespace fixture; it was not skipped on this host.
Ruff's `F` checks and Python syntax parsing passed for the three affected
Python files. All eight relative links in the three affected documents
resolved, and `git diff --check` passed. Documentation was checked against the
implemented signatures, receipt fields, quota accounting and failure behavior.

Private consolidated verification is
`/tmp/caplab-task-input-verification.json`, SHA-256
`bfe09d15d85adf4b3670d47129f07757496018de97d73e3cd539e279e67cc81e`.
It hashes 27 retained artifacts and the implementation/contract files, and
embeds the exact bytes and hashes of both advisory packets, four typed
evidence records, citation observations/classification and all nonmaterial
obligation classifications. Only those eleven consolidated advisory scratch
files were removed after byte verification. The retained namespace custody
contains 21 files totaling 23,456 bytes. Failure logs, source provenance and
the pre-execution authorization snapshot remain private under `/tmp`.

Commit scope is exactly the two source files, one test file, two contracts
and this record. `docs/designs/` and sibling worktrees remain outside scope.
This is implementation verification under delegated authority, without
independent acceptance or a new capability/value measurement.
