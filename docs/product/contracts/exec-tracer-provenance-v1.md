# Kernel-observed execution tracer provenance, version 1

`caplab.exec_provenance.observe_exec_tracer(peer_pid, trace_path, *,
expected_tracer_executable)` observes an independently authenticated, paused
process before its intended exec. The caller owns authentication, process
lifetime, trusted tracer installation bytes, private namespace construction,
stable host parents, authorization and the observation's sealed publication.
The function reads Linux procfs and filesystem identities. It does not launch,
release, stop, write or seal anything.

The live observation requires:

- A positive integer peer PID, excluding booleans, with a nonzero kernel
  `TracerPid`.
- Peer mount, PID, user and network namespaces distinct from the supervisor's,
  and the actual tracer in the supervisor's corresponding namespaces and cgroup.
- The actual tracer executable's device/inode equal to the caller's trusted
  executable path. This checks file identity; the caller must pin its bytes.
- An absolute trace path with a resolved parent and a regular, nonsymlink file.
  That host path must be absent beneath the peer's filesystem root.
- Exactly one of at most 128 tracer descriptors matching the trace's device
  and inode, with kernel fdinfo flags indicating writable access.

Each proc text read is limited to 65,536 bytes and must decode as ASCII. The
descriptor scan closes on refusal. Only an unrelated descriptor disappearing
during the scan is ignored. All other filesystem, decoding and kernel-interface
errors propagate; failed predicates raise `CaptureVerificationError`. The
caller supplies stable, cooperative paused processes; this is not an atomic
snapshot of a hostile process or a wall-time bound on procfs operations.

The returned `caplab.exec-tracer-observation/v1` record contains peer, tracer
and supervisor PIDs, namespace identities, both cgroup observations, tracer
executable identity, trace identity and writable descriptor details. It does
not copy command, environment, trace content or credentials. The check of one
host path does not discover every possible mount alias or inherited descriptor;
the caller's trusted containment construction must exclude those exposures.
Nor does owning the output descriptor alone prove all trace content was written
by that tracer; custody must remain unavailable to other writers.

`verify_exec_tracer(observation, trace_path, *, expected_pid)` checks a retained
observation against an independently authenticated PID and the current trace
inode. Its caller independently anchors the observation bytes, verifies the
trace hash with the [exec inspector](exec-trace-v1.md), and keeps custody stable.
The observation has a closed schema, complete namespace sets, positive distinct
process identities, nonnegative descriptor fields, valid file identities and
unified cgroup records. Boolean numeric values, missing fields and contradictory
namespace, cgroup, exposure or access claims are refused. Inputs are borrowed.

Its `caplab.exec-tracer-consistency/v1` result reports
`recorded_tracer_custody_agrees: true`; `observation_origin_verified` and
`binding_complete` remain false, `native_capture_complete` remains null and
`study_eligible` remains false. A copied JSON record cannot authenticate itself.
Replacing a trace with identical bytes on another inode fails this relationship
check; replacing bytes on the same inode is detected by the separate hash check.

The optional `--trace-exec` startup probe now records this live observation
inside its sealed mount handoff and checks it after execution alongside the
existing exact exec inspection. Prior handoff records without this field keep
their prior checks and receive no added provenance result. Public root-link
results, native policy, command profiles and study eligibility are unchanged.
See the [implementation record](../../records/implementation-2026-09-09-exec-provenance.md).
