# Execution trace inspection, version 1

The reader also accepts validated process-creation records and aligned resumed
exec results; see [process creation composition](process-creation-trace-v1.md).
Parentage remains a separate check.

[Exec termination inspection](exec-termination-trace-v1.md) additionally links
the exact exec to a subsequent terminal event for that PID. It preserves this
exec-only interface and does not substitute a wrapper exit for a native outcome.

`caplab.exec_trace.inspect_exec_trace(trace_path, *, expected_trace_sha256,
expected_pid, expected_executable, expected_command, expected_environment,
max_trace_bytes)` checks one successful Linux `execve` observation against a
caller-supplied invocation. It does not launch or trace a process. The caller
must independently identify the process, retain the trace digest and establish
that a trusted tracer wrote custody unavailable to the workload. A hash of
untrusted syscall text does not establish that an execution occurred.

The trace must use strace's numeric PID prefixes, full hexadecimal strings
(`-xx`), unabbreviated argument/environment arrays (`-v`) and a sufficiently
large string allowance (`-s`). The diagnostic uses `-f` and filters
`execve,execveat`. The inspector supports `execve` records, including paired
unfinished/resumed lines for the selected PID; `execveat` or other unsupported
selected-PID syscall records cause refusal. It accepts selected-PID signal and
exit records without treating them as execution success. Other PIDs' lines do
not supply a match. This is a bounded format contract, not a general strace
parser or a process-tree completeness checker.

The producer contract excludes `--seccomp-bpf`: a workload's seccomp denial
can prevent a selected call from reaching the trace. This reader cannot infer
such missing calls from the retained text or attest the producer's configuration.
See the [creation evidence requirements](process-creation-trace-v1.md#required-evidence)
and their fixed compatibility control. A passing exact exec check remains a
claim about the retained successful observation, not complete syscall coverage.

`expected_pid` and `max_trace_bytes` are positive integers, excluding booleans.
Expected strings are UTF-8 without NUL. The executable is an absolute path;
argv is a nonempty list with a nonempty first element. Environment names must
be nonempty and contain no `=`. Values may be empty or contain `=`. Inputs
are borrowed and never changed. The trace path must be absolute with a resolved
parent. The bounded read rejects symlink/special-file custody, changed bytes,
hash disagreement and a file larger than the raw byte allowance. The trace
must be ASCII and end with a newline; the allowance does not bound filesystem
operation time.

The selected PID must have exactly one successful `execve` of the expected
executable. That call's argv must agree byte for byte and in order. Its complete
environment must agree as a mapping; environment order is immaterial, but
duplicate names are refused. Failed calls do not count. Wrong argv or
environment, duplicate successful calls, abbreviation, malformed arrays,
unsupported selected-PID lines and unmatched resumptions are refused. A
successful exec followed by a failing program exit remains a successful exec
observation. This says nothing about successful task work.

Success returns `caplab.exec-trace-inspection/v1` with trace hash/byte count,
PID, executable, matching entry/completion line numbers, the count of parsed
selected-PID execve calls and `successful_execve_agrees: true`. It preserves
`trace_provenance_verified: false`, `binding_complete: false`,
`native_capture_complete: null` and `study_eligible: false`. The caller must
separately link the expected plan, process lifetime, executable installation,
working directory, namespace/cgroup handoff, capture and trace provenance.
In particular, an interpreted entrypoint may execute further programs or alter
its environment after this observed call. No provider/model identity or
downstream execution chain is attested here.

Validation uses `CaptureVerificationError` or `ValueError`; filesystem errors
propagate. No report is returned on failure. The function owns and closes only
its read descriptor and writes nothing. It neither admits nor rewrites evidence.

The fixed startup script's optional `--trace-exec` mode places strace outside
the workload PID/mount namespaces in the supervisor cgroup. Traces remain in
private host custody, with the authenticated handoff PID and validated native
plan used for inspection. The existing public Codex/Claude root-link results
are unchanged. Tracing is a behavior-bearing part of the observation apparatus;
it does not establish equivalence to untraced timing, capacity or behavior.
Each run still requires a fresh exact authorization. See the
[implementation and verification record](../../records/implementation-2026-09-08-native-exec-witness.md).

New traced startup handoffs also retain a
[kernel-observed tracer relationship](exec-tracer-provenance-v1.md), checked
against the trace inode after exit. This supplements the caller's provenance
evidence without changing this inspector's origin or completeness flags.
