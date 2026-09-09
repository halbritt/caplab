# Reuse kernel-observed tracer custody in native capture

Baseline `e514287`. The primary agent acts under ADR 0026 and the continuing
CAPLAB goal. The preceding private diagnostic authenticated a native exec guard
and checked the actual tracer and its output descriptor. The repository startup
probe checks only namespace separation and absence of the host trace path; its
reusable trace inspector explicitly leaves provenance to the caller.

## Decision and prospective authorization

Authorize a reusable `caplab.exec_provenance` module, integration in
`scripts/probe_native_capture_startup.py`, focused tests, contracts and this
record. Private verification artifacts use `/tmp/caplab-exec-provenance-*`.
Observe a caller-authenticated paused PID through kernel procfs: its actual
TracerPid, tracer executable identity, supervisor cgroup and namespaces, peer
namespace separation, and the unique tracer descriptor for the regular private
trace. Validate the descriptor is open for writing. No matching syscall text
may choose the expected PID. Preserve the caller's responsibility for process
lifetime, trusted tracer bytes, private mount topology and source custody.

Provide separate retained-observation consistency checks against the expected
PID and current trace inode. The existing exact exec parser still checks the
independently anchored trace bytes. A consistent JSON observation is not proof
of its own origin; public root linkage and Binding/completeness flags remain
unchanged. New startup observations carry the stronger record. Older receipts
remain readable without acquiring that additional claim.

Use TDD with real bounded local Python processes under host strace and isolated
Bubblewrap. Verify the successful authenticated handoff and exact UTF-8 command
output, and rejection of absent/wrong tracer, wrong trace file, exposed trace,
and contradictory retained identity. Bound test processes, streams and waits;
release/reap only owned children and close all owned descriptors. Verify source
and retained artifact hashes and run the focused and repository check suites.
No installed native agent, credential, external endpoint or model spend is
authorized by this record. No historical research evidence effect, tracker
write, message, deployment, push or independent acceptance. Preserve unrelated
`docs/designs/`, worktrees and services. Authorization expires at local commit.

This is a semantic strengthening of optional trace verification. Keeping only
the private implementation would leave the reusable producer without the
verified checks. Trusting a new caller-supplied boolean would not establish
tracer identity. Full root-to-launch integration also needs an explicit record
of actual launch configuration: the local scripted fixture adds declared
transport/debug settings to the canonical prepared plan. The present change
does not silently treat those configurations as identical or finish CAPLAB-84.

## Implementation and focused verification

The new live observer reads kernel TracerPid, executable device/inode, cgroup,
namespace links and the exact open output descriptor. Reads and descriptor
enumeration are bounded; unrelated disappearing descriptors are the only
ignored filesystem exception. The API launches or releases no process. The
caller still owns authenticated process lifetime, tracer byte pinning and
private mount construction. In particular, absence of one host path does not
prove absence of every mount alias or inherited descriptor.

The retained verifier validates a closed typed record and compares its peer
and trace inode with independent caller expectations. It explicitly leaves
observation origin and Binding completeness unverified. Native startup now
places the observation in its sealed pre-release mount handoff and checks it
alongside the exact trace parser after exit. Older records without the new field
retain their prior checks and gain no new claim. No root-link flag changed.

The first test failed because the module did not exist, then passed after
implementation. A later record-validation test exposed accepted false tracer
PIDs, boolean descriptor flags and empty cgroup records, plus uncontrolled
missing-record errors. Strict record validation then passed those regressions.
The startup integration test first failed on the absent tracer observation and
passed after wiring the observer into the actual startup handoff function.
Red and green logs remain under `/tmp/caplab-exec-provenance-`.

Eight new tests use actual isolated local processes and kernel-authenticated
Unix peers. Successful cases release the peer, require the exact UTF-8 output
and exit zero, then inspect the completed trace and retained observation before
temporary custody is removed. Negative cases close without release, require
exit seven and empty stdout, and restore the supervisor descriptor set. They
cover missing/wrong tracers, a different output inode, exposed trace paths,
shared namespaces, malformed/contradictory records and trace replacement or
symlinks. The focused run passed all 14 tests, including the existing six exact
exec parser tests; Ruff F passed. These controls execute no installed native
agent and make no performance or model-capability claim.

## Repository verification and advisory closeout

`make check` passed: 1,351 tests in 161.089 seconds, four skips. All eight new
provenance tests ran. The full-suite log is
`/tmp/caplab-exec-provenance-make-check.log`. No runtime or test source changed
after that run. Source review confirms the only existing runtime change is
the optional traced startup path; ordinary startup, canonical invocation and
public root-link contracts remain unchanged. The exact exec parser is reused.

The Doctrine gate passed at release
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`, source fingerprint
`ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`.
Initial packet `pkt-5509138082c77eae` and five typed evidence records produced
`pkt-9c7821e212e8ade1`, SHA-256
`9c7821e212e8ade166eaebf9a8646e36f2640b52d53e44ffd51be3dae90b8ef2`.
Both Markdown packets were read. Versions remain corpus
`corpus-2026-07-12-a11702cc9217`, doctrine `doctrine-f6bbb5196a3f8bf9`,
retriever `retriever-ec995ecdd083b2c8`, schema `evidence-packet/3`.

The final 25 unmet obligations remain visible. Eighteen on deduplication (3),
ingest populations (4), asynchronous UI (4), declarative references (3) and
ranking (4) are nonmaterial to the changed tracer boundary; those paths are
unchanged and not certified here. Three external capability obligations and
one evaluation/serving-parity obligation remain material to broader native
integration and study readiness, which this change does not establish. Three
monitoring obligations are nonmaterial because no service or paging policy
changed. No performance, throughput or concurrency improvement is claimed.

Applied guidance is repository-contract precedence, evidence before
intervention, separation of semantic and structural work, preservation of
default behavior and authority-bounded action. Code review preserved explicit
failure propagation and the split between live kernel evidence, trusted
retained-record consistency and exact trace-byte verification. Native adapter
adoption, actual-launch configuration linkage and representative reviewer
measurements require further work; CAPLAB-84 remains incomplete.

## Final custody

Private manifest `/tmp/caplab-exec-provenance-verification.json`, SHA-256
`8f89e65817be52c4dee31b9154c90004f37e61eed9b39b941a5670f2155f81c7`,
retains nine source identities, 16 artifact hashes and 11 embedded advisory
scratch files removed after hash verification. Five citation observations were
classified as valid packet citations. The first sealer stopped before writing
the manifest because its test-name selector expected class-only unittest IDs;
the full log includes method names. The eight successful rows were inspected
and the selector corrected. Both sealer versions and that failure are retained;
runtime and test sources were unchanged.

No installed native agent, model spend, tracker write, message, push or
historical research evidence effect occurred. The local commit closes this
implementation authorization and preserves the continuing CAPLAB goal.
