# Observe a native child from a frozen workload cgroup

Baseline `734a8c4`. Primary agent under ADR 0026 and the continuing CAPLAB goal.
The previous turn made progress by committing independent child configuration
preparation and its verified source profile.

## Observation and scoped decision

The child trace linker still takes a caller-selected PID. The public capture
authenticates its launcher before release, and owns a separate workload cgroup,
but does not observe the child executable through the kernel. A trace cannot
establish that a pathname referred to the selected file bytes at execution.

Do not select live /proc task-children polling for complete discovery. The
[Linux manual](https://man7.org/linux/man-pages/man5/proc_tid_children.5.html)
states that exiting children can cause other live children to be omitted unless
the population is stopped or frozen. The
[kernel cgroup contract](https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html)
requires observing frozen=1 after a freeze request; even then external migration
and fatal signals remain possible. The
[procfs contract](https://www.kernel.org/doc/html/latest/filesystems/proc.html)
states that an open process-directory descriptor does not redirect to a later
process reusing its PID.

Select a read-only observer for an already frozen, owned leaf cgroup. Borrow
the launcher's /proc directory descriptor, opened while it was independently
authenticated and paused. Enumerate the cgroup's bounded process population;
verify the parent descriptor against the current kernel directory, process
leadership and cgroup membership. Find exactly one direct child whose actual
/proc executable object matches a stable host file with an independently
supplied content hash. Recheck population, freeze/leaf state, source identity
and parent/child membership before returning. No trace or argv matching chooses
the PID. Keep observation time, executable identity and eventual trace linkage
separate from continuous residence, complete capture, task success or Binding.

The caller owns cgroup lifetime, exclusive migration/freeze authority and the
absence of outside signalers. The reader neither freezes nor thaws anything.
Public capture adoption must separately select and measure the pause; this
scope does not silently change a native harness's execution conditions.

## Prospective authorization

Authorize a new native_child_process module, its contract, focused tests and
this record. Test the public observer with actual kernel processes and cgroups,
not fabricated procfs or mocked filesystem calls. New test workers may create
fresh systemd user units named caplab-child-observer-<uuid>.service with delegated
memory/pids controllers and a supervisor subgroup. Each worker creates only its
own leaf workload cgroup, with 256-MiB memory, zero swap and 32 tasks; the unit
has 512-MiB memory, zero swap, 64 tasks and a 30-second lifetime. Unit launch
and outer cleanup are bounded by 40 seconds. Freeze/thaw each owned workload
group only, with two-second observation deadlines. Never freeze the supervisor
or any existing graph/service cgroup.

Use fixed Python launchers and /usr/bin/sleep children inside isolated
Bubblewrap namespaces, with all capabilities dropped, a private Unix control
socket, 64-KiB stream/file bounds and no core dumps. Authenticate the launcher
via SO_PEERCRED before opening its borrowed /proc descriptor. Exercise one
matching child, duplicate matching children, wrong source hash/object, wrong
parent descriptor, unfrozen and non-leaf groups, missing children, borrowed
descriptor lifetime and owned cleanup. Terminate/reap only owned children;
thaw in finally before cleanup, and verify the exact unit/cgroup disappears.

Use TDD, focused/full checks and private /tmp/caplab-child-observer-* artifacts.
Retain primary-source locators and advisory provenance. Read current installed
system tools only; execute no installed native agent, model, provider or real
credentials. No historical evidence copy/admission/mutation, tracker write,
message, push, deployment, study authorization or independent acceptance.
Preserve unrelated docs/designs, worktrees and services. Stop on unexplained
failures or source drift; authorization expires at the verified local commit.

Keeping caller PID literals leaves no reusable live executable observation.
Polling an unfrozen partial list cannot establish uniqueness. Freezing a
trusted leaf population makes a bounded kernel check possible, at an explicit
instrumentation cost still requiring native-capture adoption and measurement.


Before extending the passing kernel controls, authorize ordinary host strace
outside the workload cgroup for those same fixed Python/sleep fixtures. Bound
the trace at 1 MiB while preserving 64-KiB child file/stream limits, all prior
unit/resource bounds and cleanup. At the authenticated paused-parent handoff,
observe the outside tracer through the existing provenance interface. After
thaw and owned child termination, apply the existing creation and exact
exec/termination readers to the PID chosen by the new kernel observer. Preserve
a requested termination as its own outcome. This tests the observation/trace
join without a native agent attempt or public startup behavior change.


## Implementation and observed controls

The first integration test failed on the absent observer. The first real kernel
read then exposed an empty, unrelated field in process status. The
bounded field reader preserves empty values; the selected numeric identity and
cgroup predicates still require their exact valid values. The original failure
and subsequent passing controls are retained separately.

The public reader checks the actual domain/frozen/leaf state and full bounded
cgroup.procs population. It borrows the authenticated parent's proc directory,
keeps its own process/cgroup/source descriptors scoped, hashes the source file,
and compares the selected child's executable object and stable metadata. It
rechecks the population through return. It neither changes cgroup state nor
parses trace text. A copied executable with identical bytes on another inode
is refused. Observation timestamps bracket the read, not the whole pause.

One standing integration test runs four real workload populations and ten
refusal cases: unfrozen group, wrong hash, byte allowance, process allowance,
wrong parent descriptor, identical bytes on another object, non-leaf group,
missing child, two matching direct children, and a matching grandchild whose
presence is independently checked before the expected refusal. The positive
case verifies the kernel parent/child relationship, source identity, borrowed
FD survival and descriptor restoration. The caller owns thaw/termination and
reaps only its created processes; unit and workload cgroup removal are checked.
The test skips only where the delegated systemd user-service socket is absent;
this host executes it.

The added ordinary strace control remains outside the frozen workload cgroup.
The authenticated paused launcher supplies the existing tracer observation
before release. After thaw, the child PID selected by the new kernel reader
passes the unchanged creation and exact exec/termination inspectors. The fixture
terminates the sleep child with SIGTERM, which remains the reported outcome.
No trace-derived argv/environment or child PID supplies the live observation.
No installed native agent executes in these controls.

A separate retained run uses the exact standing worker source and selects host
parent 4170487 and child 4170488 from a four-process frozen population. The
35,336-byte /usr/bin/sleep object has SHA-256
8ac215ec4c1ce4a9c23a10cd3e5898d60419bdfab1ac7444d6bdd1690701de24.
The selected object's device/inode is 64512/2767218. All ten refusal controls
pass, the trace join reports SIGTERM, all recorded processes are absent, and
unit caplab-child-observer-2f29b2fa3eb04f07bcf9878fd1ce47f0.service and its
cgroup are absent. Raw traces, outputs, intent and observations are retained
under /tmp/caplab-child-observer-run. These are fixed fixture observations, not
native pause-cost or representative repair measurements.

Nine adjacent source files, including source configuration preparation, native
startup, trace readers and capture helpers, remain byte-identical to 734a8c4.
Current Plane still has 86 items, 12 open. Test Guard checks use real infrastructure
and no internal mocks; Docs Guard links resolve and claims remain bounded to
the inspected sources and controls. Ruff F and diff checks pass.

The full make check passes 1,407 tests with four skips in 166.536 seconds.
The process completed with exit zero; no runtime/test source changed after
the run began. No broader runtime matrix or native pause overhead was measured.


## Advisory review and remaining claims

The validated release gate passes for source fingerprint
ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0,
release commit d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f, corpus
corpus-2026-07-12-a11702cc9217, doctrine doctrine-f6bbb5196a3f8bf9 and
retriever retriever-ec995ecdd083b2c8. Initial packet pkt-cea9bb86857f2da7,
first evidence packet pkt-625110468e3b6730 and final pkt-48589334418b68db
were read. Final content SHA-256 is
48589334418b68db4cb4b7f7ea50d5f925ee1cd6342dcdf72360fc7ce564659d.
Five typed records preserve authority, source, incident, tests and runtime.
A second evidence pass explicitly binds the input population to the frozen
leaf group, complete bounded enumeration and the known control populations.
It does not use a silent truncated list or borrow study-population authority.

Applied concepts are repository-contract precedence, evidence before
intervention, authority-bounded action, preservation by default, separation of
semantic and structural change, and explicit population scoping. The kernel
interface's documented limitation ruled out unfrozen task-children discovery;
real frozen controls then tested the chosen alternative. Existing readers and
startup sources remain unchanged. Freeze is an explicit prospective capture
condition, not a claim that instrumentation has no behavioral cost.

The final packet retains 24 unmet obligations. Fourteen concerning record
deduplication, async UI, symbolic declarative references and top-N ranking are
nonmaterial because those mechanisms do not change. Three monitoring obligations
are nonmaterial because no monitor, service policy or paging signal changes.
Three external-capability and four authoritative-gate obligations remain
material to complete native execution/capture and serving-parity claims, which
are withheld. The initial performance and broader runtime obligations likewise
remain unestablished for native pause-cost or representative workload claims;
no such claim is made from these small fixed controls.

The scope establishes a reusable live kernel observation for one selected image
and its bounded traced-fixture relationship. It does not establish continuous
image residence or a native agent's response to the pause. Public startup
adoption, native pause policy/measurement, full capture integration and the
representative repair/reviewer work remain open. No qualification or roadmap
completion is claimed, and the full CAPLAB goal remains active.

Private manifest `/tmp/caplab-child-observer-verification.json`, SHA-256
`0c8ae5f8b8a9fd6c61c87454ae76a57b7624d4b361ce2d7764c9ebf6c954d7f8`,
seals 25 artifacts, nine baseline/current source records and three
implementation/test/contract files. Eleven advisory scratch files were
embedded, hash-verified and removed. All six used concepts classify as valid
packet citations. The owned unit and cgroup are absent.

This local commit expires the scoped implementation authorization. No native
agent attempt, historical evidence mutation, tracker write, push, deployment
or independent acceptance occurred.
