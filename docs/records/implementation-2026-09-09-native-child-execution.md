# Link selected native child execution to the verified entrypoint

Baseline `f2d2a3b`. Primary agent under ADR 0026 and the continuing CAPLAB goal.
The preceding turn was progress: shared custody compatibility was restored
with explicit startup selection anchors and full verification.

## Observation and scoped decision

The public native launch checker verifies the exact entrypoint and optionally
its termination. The process-creation and child exec/termination inspectors
exist separately. Private native auditors combine them by hand, but neither
existing check requires the selected child's birth to follow the selected
entrypoint exec. A pre-existing child cannot supply execution evidence for
that later launch merely because the creator PID is the same.

Select inspect_native_child_trace in native_launch_configuration.py. Accept
the existing NativeLaunchTraceEvidence plus a NativeChildTraceEvidence carrying
independently supplied child PID, executable, command and environment. Reuse
the anchored native launch/termination checker, the existing direct-parentage
checker and exact child exec/termination checker against one trace/hash/allowance.
Require the child's creation entry line after the matched entrypoint exec
completion. Preserve vfork ordering: child exec can precede the parent's
creation-call completion. Keep entrypoint and child terminal outcomes separate.

The result links recorded process evidence, not installed executable bytes,
task success, capture completeness or a full Binding. The caller still owns
authenticated parent leadership/lifetime, protected complete trace provenance,
independent child selection and expected binary configuration. No child search,
environment derivation from observed text, alternate-source fallback or
automatic admission is selected. Same-PID native executables use the existing
entrypoint interface; this new interface is only for a distinct direct child.

## Prospective authorization

Authorize the native launch module, a new child-execution test file and contract,
a link in the launch contract, and this record. Use TDD for joined exact identity,
separate zero/nonzero/signal outcomes, wrong child/parent/argv/environment,
missing/ambiguous/untranslated creation, creation before selected launch,
interleaved vfork completion, missing terminals and hash/byte/file constraints.
Run bounded synthetic local process controls under ordinary host strace and
isolated Bubblewrap, with authenticated parent/child socket peers and private
temporary files. These producers model process roles and execute no installed
native harness or provider. Use existing canonical plans as fabricated test
configuration without treating their producer as a native agent.

Retain new source, failure, control, advisory and verification artifacts under
/tmp/caplab-native-child-*. Read-only application to original close, shutdown
and WebSocket diagnostics is authorized as new inspection only. Check their
original manifests, artifact hashes and independent guard/launch/PID evidence;
preserve original dispositions. The WebSocket trace's unsupported incomplete
creation remains a refusal unless the unchanged existing parser accepts it.
Do not repair or hide that historical evidence in this scope.

Run focused/full checks, close/reap only owned local children and descriptors,
preserve unrelated designs/worktrees/services, and commit locally. No native
attempt, real credentials, provider call, model spend, tracker write, message,
push, deployment, historical rewrite/admission or independent acceptance.
Stop on unexplained failures or source drift. Authorization expires at commit.

Keeping independent reports alone leaves their temporal join to every caller.
Deriving binary expectations from matching trace text would make identity
agreement circular. The chosen composition adds the missing cross-report
invariant while retaining existing parser semantics. Prospective native-binary
configuration/selection and public startup adoption remain subsequent work;
this prerequisite does not complete native capture or CAPLAB-84.

## Implementation and observations

The first regression failed on the absent child-evidence interface. After
composition existed, the temporal regression demonstrated that separate valid
launch, creation and child checks accepted a child born before the selected
entrypoint exec. Requiring birth entry after exec completion fixed that case.
The interleaved-vfork control still passes when child exec occurs before the
parent's creation call completes. Existing parser semantics are unchanged.

Six new methods exercise separate entrypoint/child outcomes, the pre-launch
birth refusal, valid interleaving, wrong identities/commands/environments and
anchors, missing/ambiguous creation or termination, and real authenticated
processes. The real fixture uses a fabricated Python launcher at the test
entrypoint and a Python child under ordinary host strace and isolated Bubblewrap.
Both PIDs are socket-authenticated and checked as process leaders, with kernel
tracer observations. The launcher exits seven; its child independently exits
zero or terminates by SIGKILL. Both outcomes and traced parentage agree, peers
are reaped and descriptors restored. This executes no installed native harness.

All 36 focused launch, child, creation and termination tests pass. Test Guard
found no mocks or internal-call assertions. The contract states the five
sequential same-hash reads, per-read allowance, borrowed mutable inputs,
vfork timing, complete-trace refusal behavior and the difference between a
selected PID's terminal outcome and executable-image identity. Public reports
retain false/null task, byte-identity, completeness and eligibility claims.

New read-only application to the three original native diagnostics verifies
all manifest/artifact hashes and the selection/intent and launch/guard anchors.
The close and shutdown traces link their selected launcher and child: both
exit zero in the former, both terminate by SIGKILL in the latter. The WebSocket
trace still refuses with missing or abbreviated clone flags because of its
existing incomplete creation record. No parser exception or historical record
was changed to obtain a link. Child PIDs come from the original raw-exec audit
observations, and expected child configuration comes from the pre-release
guard; this new read does not independently authenticate those historical PIDs.
The reports and refusal are retained in /tmp/caplab-native-child-application.json.

The source check retains 12 baseline/current identities. All prior functions
and dataclasses in the launch module have unchanged ASTs; exec, creation,
termination, tracer and capture sources remain byte-identical to f2d2a3b.
Current Plane still has 86 items, 12 open, with CAPLAB-84 In Progress. Ruff F
and diff checks pass. Prospective native-child configuration, selection and
startup adoption remain required after this reusable temporal composition.

The full make check passes 1,399 tests with four skips. No runtime or test
source changed after the run began. Documentation links resolve, and the
private inspection/source-check/closeout scripts pass Ruff F. The original
native diagnostics remain unchanged and no new native attempt occurred.

## Advisory review and conclusion limits

The retrieval-state gate passes for release commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`, corpus
`corpus-2026-07-12-a11702cc9217`, doctrine `doctrine-f6bbb5196a3f8bf9`,
retriever `retriever-ec995ecdd083b2c8`, source fingerprint
`ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`.
Initial packet `pkt-23a43fcf8fabece7` and final packet
`pkt-6e1cf9110fa627e9` were read. Final content SHA-256 is
`6e1cf9110fa627e9ef2cac1931f5b9cb9864a934c3438517f34a47238cba8d02`.
Five typed records retain authority, incident, source, test and runtime
observations with content hashes and locators.

Applied guidance is repository-contract precedence, evidence before
intervention, authority-bounded action, preservation by default and separation
of semantic from structural changes. The failed temporal control earns a
cross-report invariant; it does not earn unrelated parser repair or arbitrary
child discovery. Reusing the existing inspectors preserves their failure
semantics and avoids duplicating the trace grammar. The installed native
child's configuration must still come from independent prospective evidence.

The final packet retains 28 unmet obligations. Eighteen concerning bulk
discovery, deduplication, asynchronous UI, symbolic configuration references
and top-N ranking are nonmaterial because none of those mechanisms changes.
Three service-monitoring obligations are nonmaterial because no monitor or
paging policy changes. Three external-capability and four authoritative-gate
obligations remain material to complete native startup/serving-parity claims,
which are withheld. Current evidence supports the combined trace relationship,
the repaired temporal invariant and preserved refusal behavior, not native
byte identity, full capture, representative repair quality or acceptance.

Private manifest `/tmp/caplab-native-child-verification.json`, SHA-256
`0a0bdd2220090f95fdc18edbccdd61541b553f3ce4d95edf99936484e75c1753`,
seals 20 artifacts, 12 baseline/current source records and four current
implementation/test/contract files. Eleven advisory scratch files were
embedded, hash-verified and removed. All five used concepts classified as valid
packet citations. Original native artifact hashes remain unchanged.

This local commit completes the scoped reusable child-execution composition
and expires its authorization. No native attempt, tracker write, push or
independent acceptance occurred. Prospective native-binary configuration and
child selection, startup adoption, full capture verification and representative
repair measurement remain open under the continuing goal.
