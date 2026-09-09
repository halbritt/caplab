# Retain every writable resource-probe mount after failure

Date: 2026-09-08. Baseline: `24f5513`. Primary agent under
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).

## Authorization before execution

Extend only `scripts/probe_cgroup_resource_limits.py` and this record. The
existing fixed probe preserves only `/scratch`; select retention of all three
writable tmpfs mounts (`/scratch`, `/tmp`, `/dev/shm`) after fixture exit,
including group OOM. Transfer one descriptor per mount, check each against the
blocked peer's named namespace path, and preserve exact mount identity. Use
one combined limit of 40 MiB and 100 entries per fixture across all three
inventories. Preserve partial custody on failure; unavailable or over-budget
retention must fail verification. Retain and check a distinct binary marker
per mount and the partial payload in the mount selected for each OOM fixture.

Authorize at most three sequential new `caplab-resource-probe-<uuid>.service`
units for the unchanged five trusted, model-free fixtures. Each unit has
128 MiB memory, zero swap, 64 tasks and 60 seconds. Each fixture has 32 MiB
memory, zero swap, group OOM, at most 16 tasks (eight for the pids fixture),
ten seconds and 200,000 combined stream bytes. Each memory fixture attempts
at most 64 one-MiB writes; each mount remains a 64-MiB tmpfs. The pids fixture
attempts at most 32 short-lived children. Only exact generated units and their
fixture cgroups may be configured, killed or removed. Outer capture remains
70 seconds and 200,000 bytes. No writable host-directory fixture mount.

Keep raw observations, failures, source hashes, offline checks and advisory
scratch under fresh `/tmp/caplab-mount-retention-*` paths. Verify all retained
payloads after service exit, independent kernel failure counters, aggregate
bounds, and exact unit/cgroup cleanup. Run bounded offline rejection checks
and `make check`. No live retry merely because polling yields. Consolidate
advisory provenance before deleting only named advisory scratch.

Preserve historical evidence, runtime owners, world files, standing tests,
`docs/designs/`, sibling worktrees, unrelated services/timers/cgroups and Plane.
No native harness, model, credential, network use, arbitrary task execution,
admission, ranking, acceptance, external message or push. Commit only these two
files locally; authorization expires at commit. Stop before wider effects or
if ownership, retention bounds, quiescence or cleanup cannot be verified.

## Change and interpretation

The [preceding probe](verification-2026-09-08-resource-mount-coverage.md)
verified resource events across three writable mounts but retained only one.
Leaving that behavior unchanged would discard the temporary and shared-memory
payloads needed to inspect those failure cases. This extension keeps the
existing fixture runner and inventory writer/verifier; it introduces no
general native adapter.

Before executing the fixture, the blocked handoff process sends three directory
descriptors in fixed mount order. The supervisor checks peer ownership and
cgroup membership, the full mount table, each descriptor's device/inode against
the peer's named namespace path, the 64-MiB capacity, and distinct root
identities. Only then does it acknowledge the handoff. The receiving function
owns descriptors until successful transfer; the fixture scope closes them in
`finally` after retention or failure.

Linux documents `SCM_RIGHTS` as passing references to open file descriptions,
and `/proc/<pid>/root` as exposing the target process's filesystem view, subject
to access checks. The probe uses these mechanisms while the trusted sender is
blocked, before the workload executes. [Unix sockets](https://man7.org/linux/man-pages/man7/unix.7.html),
[process root](https://man7.org/linux/man-pages/man5/proc_pid_root.5.html).

After cgroup quiescence, the supervisor inventories all three roots under
`<mode>-retained/{0,1,2}/`. Each inventory records its remaining allowance,
namespace path and descriptor identity. The next inventory receives only the
unused byte and entry allowance. Verification recomputes that sequence and
the aggregate totals, verifies payload hashes, and requires every mount's
distinct binary marker. Each OOM fixture must also retain a nonempty partial
payload from its selected pressure mount. Observation and verification schemas
advance from v3 to v4; historical receipts are unchanged.

This establishes recovery for the fixed, trusted fixture topology. It does
not establish adversarial containment, native device compatibility, complete
intermediate writes, native invocation identity, or survival of supervisor
failure. Runtime inode/logical-size policy and complete native launch/capture
integration remain unresolved. CAPLAB-84 stays open. No capture is admitted as
a representative repair measurement, and no independent acceptance is issued.

## Verification

One of the three authorized units was used:
`caplab-resource-probe-c45d53cf703041f18a8bed5ddfba8334.service`.
The probe passed on Linux `6.8.0-138-generic` and Python `3.12.3`.
Raw custody: `/tmp/caplab-mount-retention-run/`.

| Fixture | Exit | Retained bytes across three mounts | Entries | Partial pressure payload |
| --- | ---: | ---: | ---: | ---: |
| Control | 0 | 80 | 9 | Not applicable |
| Scratch OOM | -9 | 25,825,354 | 7 | 25,825,280 |
| Caught pids limit | 0 | 74 | 6 | Not applicable |
| Temporary-directory OOM | -9 | 25,825,354 | 7 | 25,825,280 |
| Shared-memory OOM | -9 | 25,833,546 | 7 | 25,833,472 |

All 15 inventories verified after service exit. Every fixture had complete
stdout/stderr and an empty cgroup before retention. Each OOM fixture recorded
an `oom_kill` delta of four; exact counts and payload sizes are observations,
not frozen expected values. The caught-pids fixture preserved its independent
task-limit event despite exiting successfully. The control had no OOM or
pids-limit event. The unit was already collected when cleanup attempted its
exact stop (`stop` exit 5); `show` returned `not-found`, and its cgroup path
was absent.

Thirteen offline rejection checks passed: missing/reordered mount inventories,
missing/altered identities, incorrect byte/entry totals, wrong inventory hash,
reset per-mount byte/entry allowances, altered retained root inode, altered
payload, combined byte exhaustion, and combined entry exhaustion. The byte
exhaustion check retained the four-byte prefix that fit after a six-byte first
inventory exhausted a ten-byte combined allowance; it emitted no final second
inventory. These checks used new disposable files and real descriptors.

The first offline driver guessed an object filename and failed to locate the
retained prefix. Its source, log and output remain under
`/tmp/caplab-mount-retention-offline*`. The corrected driver checks the single
generated payload object and passed under
`/tmp/caplab-mount-retention-offline-final/`. No production code or live probe
was changed or repeated in response to that test-driver error.

`make check` passed 1,212 tests in 153.428 seconds with four skips; log:
`/tmp/caplab-mount-retention-make-check.log`. The fixed resource script is
verified by the explicit live probe and offline checks above; the repository
suite does not launch it automatically. `git diff --check` passed.

## Advisory provenance and closure

Pincite's release gate passed at release commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`, source fingerprint
`ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`.
Final packet: `pkt-e9d52d76e8227eaa`, content SHA-256
`e9d52d76e8227eaa369b451fe941189115a925706cfe03c41c15ba1a09c0a3e8`;
corpus `corpus-2026-07-12-a11702cc9217`, doctrine
`doctrine-f6bbb5196a3f8bf9`, retriever `retriever-ec995ecdd083b2c8`.

Four served concepts were used and classified as valid citations:
`universal-repository-contract-precedence` for the delegated scope,
`python-structured-cleanup` for descriptor ownership,
`python-text-bytes-boundary` for opaque retained payloads, and
`universal-evidence-before-intervention` for the demonstrated single-mount
retention gap. These support the implementation reasoning; CAPLAB owns the
decision and authorization.

All 15 remaining obligations are nonmaterial to this fixed local probe claim:

| Unmet requirements | Reason |
| --- | --- |
| CI and build matrix; formatter and static-tool configuration; repository version and dependency contract; Python and dependency version matrix; formatter linter and type-checker configuration; public API and tests | No public package API, dependency or cross-platform compatibility change is claimed. The observed local runtime and explicit executable checks bound verification. |
| Affected classes or attributes; demonstrated repetition and ordinary-alternative analysis; lookup and construction semantics; repeated rule; tooling and compatibility | No descriptors in the Python attribute sense, decorators, metaclasses or other dynamic mechanism is introduced. Ordinary functions and file descriptors retain their existing ownership. |
| Annotation maintenance cost; checker and trust-boundary evidence; configured checker and Python version | No type-checking guarantee or annotation change is claimed. The boundary checks are executable and exercised on the named local runtime. |
| Evidence-explicit-user-requirements | The exact scope is delegated under the inspected repository authority. It requires no new owner judgment; that delegation was supplied as repository-contract evidence. |

Consolidated provenance, retained artifact hashes, the complete obligation
classifications and citation receipt are in
`/tmp/caplab-mount-retention-verification.json`. Only the exact advisory packet,
typed-evidence and citation scratch files are deleted after consolidation.
Probe custody, offline failures and successful checks remain available.
This local commit consumes the authorization, including unused live retries.
