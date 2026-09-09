# Close the full-mount retention quarantine path

## Decision and authorization

At baseline `380d6e4`, the supervised task, process and selected native-output
components accept trusted quarantine. The full writable-mount retention path in
`scripts/probe_cgroup_resource_limits.py:retain_mount`, also used by the native
startup supervisor, still constructs `_Inventory` without a policy and seals
unchecked metadata. A caller retaining failure evidence could therefore copy a
secret from `/scratch`, `/tmp`, `/dev/shm` or unselected runtime files even when
the selected task/session captures were guarded.

Under ADR 0026 and the continuing CAPLAB improvement request, authorize an
optional `quarantine_factory` input to that existing helper, guarded file/name/
link copying, and checks of source identity metadata, output paths and receipts
before writing. Snapshot the currently flat caller identity mapping before
policy callbacks. Preserve default behavior, source-root identity checks, raw
bytes, shared remaining quotas, receipt schema and borrowed descriptor lifetime.
Reuse the existing checker and inventory; no new credential parser or matcher.

Authorize extending the synthetic helper in `tests/test_supervised_task_capture.py`
with optional policy and full-mount fixture coverage, new focused tests, a
contract and this record. Run isolated Bubblewrap fixtures with bounded tmpfs
mounts and existing process time/byte limits. They may receive only fabricated
file/event bytes and fixed local Python producers. Exercise safe Codex/Claude
format layouts and explicit secret outputs in each capture path, including
otherwise unselected writable mounts. These are fixture-format subjects, not
native harness execution or valid reviewer measurements.

No installed native CLI, actual credentials, provider calls, model spend,
resource-pressure campaign, tracker write, outbound message, historical evidence
copy/admission/rewrite/purge, or independent acceptance. Preserve unrelated
`docs/designs/`, worktrees, services and historical custody. Temporary synthetic
sources may be removed after their checks; retain failure logs and code/hash
provenance under `/tmp/caplab-mount-quarantine-*`. Run focused/full checks and
commit only this scope after verification. Stop on unexplained failures; do
not publish completed custody after a guard/source/quota/storage error or retry
into an existing root. Authorization expires at the verified commit.

## Selected approach and verification criteria

Guard the existing full-mount sink. Leaving it unchanged or guarding only named
session files misses the current supervisor's additional copies. Post-copy
checking cannot prevent durable exposure, and buffering whole trees would
defeat the bounded copier. The supervisor still chooses authorized mounts and
owns quiescence, descriptor handoff and the policy. No new general capture
framework or authenticated-adapter claim is introduced.

Verify a cross-read file secret, literal names/targets and metadata, shared
quota failure, source/descriptor preservation and gate cleanup. Then run one
selected policy through supervised snapshots, process streams, selected native
collection and complete writable-mount retention in fresh isolated fixtures.
Safe captures must retain exact bytes and pass existing independent integrity,
linkage/accounting and retained-mount checks. Negative cases must stop at the
affected sink without complete aggregate results. Keep already completed
component receipts distinct from an unavailable whole attempt. No test score,
resource-cost estimate, complete privacy proof or roadmap completion follows.

## Execution and observations

The retained-mount helper now forwards the trusted factory to the existing
inventory copier. It checks the flat identity snapshot and planned paths before
creating output, and checks the completed receipt before sealing. The unique
root entry, shared byte/entry accounting, raw payloads and borrowed descriptor
ownership remain unchanged. No diagnostic CLI automatically selects a policy.

Eight new tests exercise a secret across the 65,536-byte read boundary, literal
names and symlink targets, identity and generated-path checks, callback mutation
of the caller's identity, quota exhaustion with withheld overlap, and policy
cleanup failure. The safe integrated fixture covers both Codex and Claude
transcript formats, nonzero child exit, all five writable mounts, independent
task/native linkage and accounting, and retained-mount integrity after the
synthetic sources are removed. The child is local Python inside Bubblewrap;
neither installed native harness executes in these tests.

Fourteen failure cases place a fabricated value in process output, the task
tree, selected native files, `/scratch`, `/tmp`, `/dev/shm`, or otherwise
unselected runtime files, for each transcript format. They check both refusal
and absence of the value from earlier capture objects and metadata. Completed
component receipts remain present when the later failing stage does not own
them; no completed aggregate result is returned. Descriptor counts are stable.

The omission control deliberately disables only the native collector's policy
in an isolated fixture. It observes a completed native collection containing
the fabricated value even though the later full-mount copy refuses publication.
This establishes why testing only the final refusal would miss a policy wiring
error. The control uses no real secret and makes no native-execution claim.
Its temporary synthetic outputs were removed after inspection; its script and
result remain at `/tmp/caplab-mount-quarantine-counterfactual.py` and `.json`.

The focused suite passed 53 tests in 11.687 seconds, recorded in
`/tmp/caplab-mount-quarantine-focused.log`. The retained `red.log`,
`metadata-red.log`, `integration-red.log` and `surfaces-red.log` under the same
prefix preserve earlier missing-interface and unguarded-metadata regressions.
Those logs do not establish that every integrated subcase independently failed
before implementation. The omission control supplies the distinct evidence
about an earlier durable leak despite later refusal.

The refreshed read-only roadmap matches the baseline fields: twelve items
remain open, including CAPLAB-84 In Progress. Snapshots are
`/tmp/caplab-roadmap-20260909-380d6e4.json`, its matching states file, and
`/tmp/caplab-mount-quarantine-roadmap-current.json`. No tracker write occurred.
This change closes one existing capture sink; an adopting native supervisor
still must select and record the intended policy across every owned writer,
link execution identity, and satisfy separate credential and attempt authority.
Representative repair measurements, blinding and coding reliability remain
required by CAPLAB-84 and its consumers.

## Advisory and review

The release retrieval gate verified fingerprint
`ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`,
corpus `corpus-2026-07-12-a11702cc9217`, doctrine
`doctrine-f6bbb5196a3f8bf9`, and release commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`. Initial packet
`pkt-a5bd580b01bdd1f5` was followed by two typed evidence passes. Final packet
`pkt-b914b2c1daf5f811`, retriever `retriever-ec995ecdd083b2c8`, has content hash
`b914b2c1daf5f8115ed397ca1c478352d260047e67b06ab5c51dee1db5f8b925`.
Evidence hashes name the source and original authorization snapshot inspected
before this execution report was appended.

Twenty-one unmet obligations remain explicitly nonmaterial to this local
correctness claim:

| Concept | Unmet obligations | Reason |
| --- | --- | --- |
| Performance objective | Accepted workload/operation; inspection authority and objective owner; environment/distribution/scale/concurrency/population; metric and target; objective/tradeoff owner | No performance objective or optimization is selected. |
| Memory lifecycle | Allocation/retention evidence; owner/reference/lifetime path; precise memory metric/interval; representative macro behavior | No memory improvement or representative resource-cost claim is made. |
| Metric semantics | Instrumentation access; definition/configuration; overhead/data-loss limits; runtime sanity check; unit/window/population/sampling | The byte allowance is a correctness limit, not a cost or performance measurement. |
| Causal bottleneck | Direct/cumulative contribution and concurrency analysis; profile semantics; representative workload/version/interval; corroboration | No bottleneck diagnosis or optimization follows. |
| Python repository idiom | Python/dependency matrix; formatter/linter/type-checker configuration; repository toolchain inspection | No dependency/toolchain change or platform qualification is claimed; declared Python requirements, neighboring source and local executed checks bound verification. |

The applied concepts are earned abstraction, repository-contract precedence,
evidence before intervention, preservation by default, data minimization and
authority-bounded action. Reusing the existing copier preserves one owner for
its byte, path and quota rules; the caller continues to own policy selection.
Post-copy scanning and a new whole-tree buffering framework were rejected for
the reasons recorded before execution. Advisory guidance neither selects a
credential policy nor grants execution or acceptance authority.

The review checked earlier publication, literal versus encoded metadata,
withheld-byte accounting, factory cleanup, source mutation, descriptor lifetime,
default behavior and fabricated completion. Errors propagate without a success
fallback. These checks establish the tested mechanism, not exhaustive privacy,
native authentication, reviewer capability or independent acceptance.

## Final local verification

`make check` completed successfully: 1,297 tests in 238.279 seconds with four
skips. The eight new tests ran without skips. The log is
`/tmp/caplab-mount-quarantine-make-check.log`. Source and test hashes matched
the typed evidence before and after that run. Ruff's undefined-name and
unused-import checks, `git diff --check`, and changed-document link checks
also passed. No runtime or test change followed the full run.

The private manifest `/tmp/caplab-mount-quarantine-verification.json` has SHA-256
`873737d13844be800f4700abae3deaa9e1d3b11723913ba0d6856dba6223503e`.
It retains 25 artifact entries, source hashes, suite results and the packet
identity. Twelve temporary advisory files were embedded byte-for-byte and
checked before removing those exact scratch paths. The red/focused/full logs,
original authorization snapshot, omission-control script/result, roadmap reads
and verification script remain private. No historical evidence was changed.

Commit only the five authorized source/test/contract/record files. Preserve the
unrelated `docs/designs/` directory and detached worktree. This completes the
local mechanism change and consumes this authorization; it does not complete
CAPLAB-84 or the active roadmap goal.
