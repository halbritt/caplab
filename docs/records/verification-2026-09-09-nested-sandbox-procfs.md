# Preserve containment while supporting nested UID-map setup

Baseline `a90c4e0`. Primary agent under the continuing CAPLAB goal and ADR 0026.
The previous native call failed because Bubblewrap could not set up its UID map
through read-only /proc. Authorize private synthetic controls under
`/tmp/caplab-nested-procfs-*`, bounded source inspection and this record before
selecting a runtime change. Preserve installed native code, previous custody,
all historical research evidence, unrelated `docs/designs/`, services and worktrees.
No native/model/provider execution, credentials, tracker write, message or push
is authorized by this initial scope.

Compare the preceding read-only procfs with a fresh procfs mounted inside an
unshared PID namespace, permitting per-process control files while requiring
/proc/sys, /proc/sysrq-trigger, /proc/irq and /proc/bus to be read-only binds.
Keep root and /usr read-only, only /dev/null and /dev/urandom usable, the same five
64-MiB writable tmpfs mounts, no host home or task inputs, and unshared network,
mount, PID and user namespaces. Drop all capabilities for the synthetic producer
and require NoNewPrivs. Use a fixed nested Bubblewrap command that writes one
UTF-8 witness only into /work. Require read-only procfs to reproduce UID-map
failure and the new arrangement to complete the nested witness. Require both
arrangements to deny opening selected kernel controls for write without writing
to them. Verify distinct parent/child namespace identities and host PID absence
through the isolated procfs. Retain raw mountinfo and bounded command results.
Use fixed local Python/Bubblewrap processes, 10-second capture limits, 1-MiB
stream/file limits, a 30-second enclosing systemd unit with 256-MiB memory,
64 tasks and no swap. Verify exact owned cleanup. A failed control permits
bounded source diagnosis and synthetic control correction; it does not authorize
a native launch or weakening the native sandbox.

Installed Bubblewrap reports 0.9.0. Published 0.9.0 source mounts fresh procfs when
PID namespaces are unshared and conditionally covers sensitive proc directories.
The explicit read-only submounts avoid relying on conditional permission checks.
The source is advisory implementation evidence, not installed-build attestation:
https://github.com/containers/bubblewrap/blob/v0.9.0/bubblewrap.c
Kernel procfs documentation describes visibility and mount restrictions:
https://www.kernel.org/doc/html/latest/filesystems/proc.html

The first paired control reproduced read-only UID-map failure. The candidate
permitted UID mapping but failed mounting fresh nested procfs with EPERM. It
bound sensitive subdirectories from the host procfs into the isolated instance.
Kernel documentation identifies covered procfs directories as a restriction on
new user-namespace procfs mounts. Preserve this failed control and its cleanup.

Authorize a second synthetic pair under `/tmp/caplab-nested-procfs-self-*`.
For the candidate only, retain CAP_SYS_ADMIN in the outer namespace bootstrap
long enough to bind each sensitive path onto itself in that already-isolated
procfs, then remount that bind read-only and drop all capability sets before
running the producer and nested command. Do not bind host procfs subdirectories.
The bootstrap must require successful mounts and zero effective/permitted/
inheritable capabilities afterward. Preserve NoNewPrivs, namespace separation,
all five bounded tmpfs mounts, root/usr read-only, the same resource/time/capture
limits and selected control-file write-open denials. This is a setup authority
inside the owned user/mount namespace only; no host mounts or kernel writes are
permitted. No native launch is authorized.

Self-binds also failed nested procfs mounting. Published Linux `mnt_already_visible`
checks locked child mounts over nonempty directories, irrespective of whether the
bind's source was the same procfs. Neither covered topology is selected.

Authorize one third synthetic pair under `/tmp/caplab-nested-procfs-uncovered-*`.
Use Bubblewrap's normal fresh procfs without added submounts or retained setup
capabilities. Preserve the unshared PID/user/mount/network namespaces, cap-drop
ALL, NoNewPrivs and the same resource limits. This tests Linux permission and
namespace enforcement instead of claiming read-only submount enforcement.
Before the nested command, enumerate at most 10,000 regular control files below
/proc/sys, /proc/irq and /proc/bus plus /proc/sysrq-trigger, without following
symlinks or reading values. Attempt open(O_WRONLY) only, immediately close any
successful descriptor, and never write. Record every successfully opened path.
Also verify the three previously named write-open denials. A successful nested
command alone cannot establish protection: any write-open success must be
interpreted against the file's namespace ownership before adopting this topology.
No runtime change or native attempt is authorized by this amendment.

The uncovered-procfs pair passed: the old mode reproduced UID-map failure and
the new mode completed the exact UTF-8 witness in a distinct nested user/PID/
mount/network namespace. Producer capabilities were zero and NoNewPrivs was 1.
The control inventory contained 1,214 regular files; 1,213 denied write-open.
Only /proc/sys/kernel/ns_last_pid opened. No value was read or written. Kernel
documentation defines that control in the calling task's current PID namespace:
https://www.kernel.org/doc/html/latest/admin-guide/sysctl/kernel.html#ns-last-pid
This uses namespace/permission enforcement, not read-only submount enforcement.

Under ADR 0026 select and authorize an opt-in `nested_userns` mode for
`mount_coverage` and `receive_mount` in `scripts/probe_cgroup_resource_limits.py`,
recorded validation in `scripts/probe_native_capture_startup.py`, a focused
`tests/test_nested_procfs.py` and a matching contract. Default topology and
existing receipt fields remain unchanged. The opt-in may add writable procfs
and namespace observations; it must reject any other unexpected writable mount,
non-proc filesystem, extra procfs submount, missing namespace separation, wrong
procfs PID view, retained effective/permitted/inheritable/ambient capabilities,
or absent NoNewPrivs. Check before child release and revalidate the recorded
invariants when inspecting custody. Procfs is a live control interface, not an
additional durable file-retention root. Preserve all original tmpfs limits,
quarantine, borrowed descriptor ownership, source identity, exact receipt hashes
and failure cleanup. Do not turn the private 8-MiB file limit into a default.

Use actual synthetic nested Bubblewrap execution and handoff as the primary
regression; add focused rejection cases for topology and namespace evidence.
Run required repository checks, preserve red/green/control logs, and commit the
complete helper/contract/test change locally. These delegated interface and
behavior decisions satisfy the TDD skill's planning gate without asking the owner
again. No native attempt, real credential administration or study adoption is
authorized in this implementation scope. Source snapshots may be retained for
changed-source provenance; historical research evidence remains unchanged.

## Implementation and regression evidence

The opt-in preserves the old mount profile while adding writable procfs only
when its filesystem/protection flags and uncovered topology match. Live handoff
inspection requires separate PID, user, mount and network namespaces, matching
procfs PID-1 visibility, zero effective/permitted/inheritable/ambient capabilities
and NoNewPrivs. It runs before descriptor-backed task capture, handoff publication
and release. Recorded custody inspection rechecks these predicates; it does not
reconstruct a live namespace after exit.

The first regression failed because the handoff had no opt-in parameter. An
initial fixture then exited 1; its nested Python string construction was corrected
without changing the required UTF-8 witness. The real integrated handoff now
completes that witness through a nested Bubblewrap process. A real peer retaining
CAP_NET_ADMIN is refused before release, emits no witness/output or final handoff,
and exits 7 on the closed channel. The supervised recorder then reports its
expected unfinished-capture error. Borrowed descriptors are closed. A direct
host-procfs control is rejected before attempting its PID-1 visibility read.

Five focused tests cover that real execution and refusal, host namespace
rejection, recorded namespace/privilege contradictions, wrong PID view, missing
observations, unexpected writable mounts, covered proc paths, wrong filesystem,
missing protection flags, read-only procfs under the opt-in and non-boolean flags.
The 20-test adjacent capture selection passed before the last privilege case was
added; the final five-test selection passed afterward. Red and intermediate
failure logs remain separate under `/tmp/caplab-nested-procfs-*`.

The three private paired controls have independently checked stream bytes and
hashes, source hashes, namespace observations and exact owned unit removal.
Their expected cgroup paths are absent. The first two preserve their nested
procfs-mount failures; the third preserves successful synthetic execution and
the bounded kernel-control open inventory. Verification:
`/tmp/caplab-nested-procfs-control-verification.json`.

The real handoff checks namespace/privilege predicates, not the entire kernel
control inventory. The 1,214-file inventory is separate synthetic evidence.
The observed ns_last_pid exception is local to the calling task's PID namespace;
no kernel-control value was changed by these probes. No installed native CLI
was launched in this scope. No production capacity, successful native task,
reviewer qualification, independent acceptance or roadmap completion is claimed.

CAPLAB-84's current repository decision requires real native integration before
representative repair measurements. Leaving the read-only-only helper unchanged
would preserve the observed UID-map blocker. Globally making procfs writable
would change every existing capture caller. Duplicating the handoff/verifier in
a private native adapter would split the same containment contract across owners.
Select the explicit mode in the existing handoff owner, with its small additional
namespace record and focused checks. Kernel/environment dependence remains an
uncertainty; the mode is verified locally and native adoption remains separate.
This is a semantic compatibility extension, not a behavior-preserving refactor.

`make check` completed successfully: 1,337 tests in 212.828 seconds, four skips.
All five new tests ran without skips. Log:
`/tmp/caplab-nested-procfs-make-check.log`. Ruff F and diff checks passed.
No runtime or test change followed this full-suite run.

## Advisory closeout

The validated Doctrine release gate matched source fingerprint
`ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`
at release commit `d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`.
Initial packet: `pkt-ae515e699eb27844`. Five typed records and two evidence
passes produced final packet `pkt-b3ddc1421e340901`, content SHA-256
`b3ddc1421e3409018600a06bb6cffa489cd1d51e4d5707e724d41f0f769d0470`.
The second pass explicitly connected live kernel reads and recorded custody
predicates to their respective gates. Initial and reassembled Markdown were
read; the final revision changes only packet identity and the three satisfied
gate obligations. Versions: corpus `corpus-2026-07-12-a11702cc9217`, doctrine
`doctrine-f6bbb5196a3f8bf9`, retriever `retriever-ec995ecdd083b2c8`, schema
`evidence-packet/3`.

Twenty-six final missing obligations remain archived:

- Eighteen cover deduplication keys (3), ingestion populations (4), async UI (4),
  declarative reference validation (3) and relevance selection (4). They are
  nonmaterial: this extension neither changes nor certifies those product paths.
- Four external-capability obligations remain material to a working native/
  provider integration claim, which is withheld. The helper and real Bubblewrap
  controls are verified locally; installed-native adoption is still provisional.
- One evaluation/serving parity obligation remains material to study readiness,
  which is withheld. These synthetic controls are not the study Binding.
- Three service-monitoring obligations are nonmaterial; no monitoring or paging
  policy changed.

Applied guidance: repository-contract precedence, evidence before intervention,
separation of semantic and structural changes, default behavior preservation,
and authority-bounded action. AI-failure-mode review checked the temptation to
relax the default topology, mistake mount flags for namespace identity, treat
recorded claims as live kernel facts, or hide setup failures. Kernel-source and
actual-control evidence changed the candidate topology twice before the API was
extended. The optional mode serves the observed native integration need; no
config-object migration or unrelated handoff refactor was included. The existing
multi-argument handoff interface is preserved for its callers. Doctrine does not
supply independent acceptance, native completion or reviewer qualification.

## Retained custody

The final private manifest is `/tmp/caplab-nested-procfs-verification.json`,
SHA-256 `c877088e7dfd9c1056376ce6a11bff7ae1b34976c6d8caf61ca629fff2db9212`.
It retains 52 artifact hashes, four current source identities, two prior source
snapshots, and 13 embedded advisory scratch files removed after archival.
Before commit, every retained artifact, current source, prior snapshot and
embedded scratch hash was checked again; all 13 scratch paths remain absent.
The full-suite log still matches its recorded hash. Ruff F and diff checks pass.
No installed native CLI, provider or model was executed in this scope. No real
credentials, tracker writes, messages, push or historical research evidence
effects occurred. Installed-native adoption remains the next diagnostic step.
