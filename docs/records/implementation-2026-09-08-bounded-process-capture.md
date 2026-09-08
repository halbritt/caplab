# Bounded process capture for the next shakedown

Date: 2026-09-08. Baseline: `268f938`. Decision owner: primary agent under
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).

## Authorization before execution

Implement a prospective process-stream capture component for CAPLAB-84's
[CAPLAB-79 capture requirements](decision-2026-09-08-caplab-79-capture-design.md).
Permitted files: `src/caplab/process_capture.py`,
`tests/test_process_capture.py`,
`docs/product/contracts/bounded-process-capture-v1.md`, and this record.
Run only newly authored local Python child-process fixtures in temporary
private directories, with explicit minimal environments, deadlines and byte
limits. Verify output preservation, quota and timeout termination, inherited
pipes, exclusive custody, and storage/launch failures; run `make check`.

No native harness, authentication probe, model call, network experiment,
historical evidence read/copy/admission, frozen manifest change, campaign
launch, scoring, ranking, placement, or external message is authorized.
Existing native runners and their frozen instruments remain unchanged; this
component must pass future adapter integration before a new campaign uses it.
No tracker changes are authorized in this slice. Preserve `docs/designs/`,
other worktrees, services, and timers. Retain verification receipts under
`/tmp`; remove only named task doctrine scratch after retaining its receipt.
Authorization expires at commit. Stop on an unexplained process-lifecycle or
custody failure rather than claiming capture completed.

## Selected contract

Both existing native runners accumulate subprocess pipes in memory and write
raw files after exit. CAPLAB-79 requires bounded disk streams before the next
shakedown. Select a single synchronous selector loop that drains both pipes
without a thread pool, uses one shared caller-supplied byte allowance, and
retains raw binary prefixes on failure. A new private output directory prevents
accidental reuse; receipt creation is exclusive. Process group termination
owns only the launched session. External containment still owns descendants
that escape that group, disk reservation, and the other native capture surfaces.

No change leaves the next instrument without this required component. Direct
file redirection avoids memory buffering but cannot enforce a combined limit
before overshoot. Retrofitting the frozen historical runners would change
instruments outside this authorization. This is new prospective capture
behavior, not a refactor or a claim of measured native runtime performance.


## Execution and verification

Implemented `capture_process` with mandatory explicit command, environment,
working directory, fresh custody path, combined stream allowance and deadline.
It retains binary streams without decoding, hashes written bytes, reports
leader exit separately from pipe completeness, and records UTC plus monotonic
receipt bounds. Payload reads are bounded to 65,536 bytes, with at most one
extra quota-detection byte. This is a component-level payload bound, not a
measured whole-process memory or native performance improvement.

Sixteen focused tests use real local Python children. They cover alternating
binary streams larger than pipe capacity, exact-cap completion, combined-cap
prefix retention from either stream, empty output and ambient-environment
exclusion, nonzero exit, timeout with open and closed pipes, an exited leader
whose child retains pipes, existing custody, invalid limits before launch,
launch failure, short writes, storage and sync failures, and cancellation.
The inherited-pipe case also checks that its child is no longer executing;
cleanup is limited to the test's launched process group.

The first receipt-sync fault test failed because `capture.json` remained after
its sync raised. The implementation was corrected to stage and sync receipt
bytes before exclusive publication, remove the final name on directory-sync
failure when possible, and propagate errors. Raw prefixes remain; incomplete
receipt state never becomes an empty successful result. Reproduction receipt:
`/tmp/caplab-bounded-capture-receipt-red.log` (one failure among 14 tests).
Focused final receipt: `/tmp/caplab-bounded-capture-focused.log` (16 passed in
1.078 seconds). Source and tests passed AST and direct-import-use checks.
The observed local interpreter is Python 3.12.3.

## Preservation and remaining work

The public component is directly exercised by the model-free qualification
suite. It is not yet called by a native campaign adapter. The two existing
native runners, their source-bound manifests, expiry checks, historical output,
and authorizations were not changed. No live native compatibility, maximal
capture, model identity, redaction, throughput, storage sizing, or empirical
reviewer capability claim follows from these process tests.

The [component contract](../product/contracts/bounded-process-capture-v1.md)
requires the future adapter to enforce stop/denominator rules, bind command and
subject identity, reserve storage for all other surfaces, preserve linked
sessions/diagnostics and task inventories, and verify hashes at the next
custody boundary. An exception cannot be overridden by finding a receipt on
disk. Process-group cleanup is not external containment of escaped descendants;
storage or kernel calls can outlast the loop's timeout. These limits are explicit
integration requirements, not implied guarantees.

The current Plane snapshot is
`/tmp/caplab-roadmap-20260908-next-current.json`. CAPLAB-84 and the broader
measurement roadmap remain incomplete. No tracker changes or external messages
were made. Reopen this component when adapter integration or a new failure
fixture demonstrates a violated capture invariant; do not renew a campaign
merely to test it.


### Existing mechanism comparison

The final source review also inspected `revbench/codex.py:_run_owned_process`,
`revbench/custody.py:FreshProcessCapture`, and
`revbench/execution.py:_run_process`. Revbench already has selector-based
bounded execution. Its live path requires a Revbench execution intent, launch
plan and credential profile, applies stream quarantine, keeps retained byte
arrays for returned observations, and uses separate stdout/stderr limits.
Its local path constructs a sealed executable/sandbox. These are not the
prospective raw-stream interface selected here. Reusing them directly would
couple this component to those study/effect contracts; extracting a common
loop would require a separate preservation campaign across both consumers.
No Revbench custody, quarantine or execution behavior was changed. Generic
selector and short-write mechanics are similar; no cross-study consolidation
or architecture improvement is claimed in this slice.

## Doctrine receipt

The release retrieval-state gate passed. Release commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`, corpus
`corpus-2026-07-12-a11702cc9217`, doctrine `doctrine-f6bbb5196a3f8bf9`,
retriever `retriever-ec995ecdd083b2c8`.

Final packet `pkt-631da42469117a39`, SHA-256
`631da42469117a39b31568dee35452c8abe446705db39eec69e7d2093436be05`.
One evidence-gathering pass supplied five typed records: authority, contracts,
source, tests and the receipt-sync failure observation.

Applied `agent-conduct-authority-bounded-action` to keep component verification
separate from campaign authorization; `universal-repository-contract-precedence`
to preserve native identity and historical custody; `python-structured-cleanup`
to keep pipe, descriptor and process ownership explicit; and
`universal-evidence-before-intervention` to correct the reproduced receipt
failure before declaring the component verified.

All nine remaining obligations are nonmaterial to the bounded component claim:

| Group | Exact unmet requirements | Classification and reason |
|---|---|---|
| `implementation-repository-language-conformance` | CI and build matrix; formatter and static-tool configuration | Nonmaterial: no CI, formatter or static-tool guarantee is made; the inspected local Makefile, interpreter and executable suite are the verification surface. |
| `performance-measurable-objective` | environment, input distribution and scale, concurrency, and success/failure population | Nonmaterial to this component contract: native workload distribution and scale remain unmeasured. The verified claim is a configured retained-payload cap and failure behavior, not measured native performance or complete episode storage. |
| `performance-representative-baseline` | exact code, dependency, build, benchmark, data, and environment versions; known resource limits and warmup/cache state; repeated raw measurements and variance | Nonmaterial: no comparative throughput, latency, total memory or campaign sizing claim is made. Representative native capture measurements remain CAPLAB-84 work. |
| `python-concurrency-model-selection` | task-size distribution; workload profile | Nonmaterial: selectors drain two pipes in one synchronous owner to prevent pipe deadlock, with real-child lifecycle tests. No thread pool, CPU parallelism, throughput or capacity claim is selected. |
| `python-repository-shaped-idiom` | formatter linter and type-checker configuration | Nonmaterial: no formatter, linter or type-checker policy is changed or claimed verified. |

## Completion checks

`make check` passed 929 tests with four skips in 131.278 seconds:
`/tmp/caplab-bounded-capture-make-check.log`. No source or test file changed
after that check began. These are technical checks, not independent acceptance
of a native instrument. Final file/link and preservation checks are retained in
`/tmp/caplab-bounded-capture-verification.json`.

Four citations classified as `valid-packet-citation`; the packet identity,
applied concepts and obligation table above retain the receipt. The eleven
named task doctrine scratch files were removed after recording that receipt;
verification logs and the current roadmap snapshot remain. Commit closes this
component implementation scope, not CAPLAB-84 or the broader goal.
