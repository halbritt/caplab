# Process creation trace inspection, version 1

`caplab.process_trace.inspect_process_creation(trace_path, *, evidence)` verifies
one direct parent-to-child creation in a bounded host strace file.
`ProcessCreationEvidence` contains independently supplied
`expected_trace_sha256`, `parent_pid`, `child_pid` and `max_trace_bytes`.
PID and byte values are positive integers, excluding booleans; parent and child
must differ. The caller authenticates the parent process identity (including
that it is the process leader, not an arbitrary thread), selects the child
identity, retains the protected trace anchor and owns stable, quiescent custody.
The API does not authenticate these caller inputs or launch processes.

## Required evidence

The trace is produced outside the workload PID namespace with strace
`-f -v -xx -s 65536 --decode-pids=pidns` and syscall selection
`execve,execveat,clone,clone3,fork,vfork`. The installed tracer and its output
custody require separate verification. Calls must not be filtered by outcome,
and the caller must bound file growth and retain complete process lifetimes.

Do not use `--seccomp-bpf` for this producer contract. A workload filter can
suppress the tracer's notification for a selected denied call; a successful
exec or parentage match cannot establish that those records were retained.
The [fixed compatibility control](../../records/decision-2026-09-09-trace-filter-compatibility.md)
demonstrated both omitted denied calls and passing selected-call checks with
strace 6.8 on the recorded Linux host. The caller must verify the actual tracer
configuration separately: this text reader cannot detect a syscall omitted
before writing. Ordinary tracing remains the selected producer configuration;
that selection alone does not establish complete capture or trusted origin.

The reader verifies the file's independent hash and byte allowance using the
existing stable regular-file reader. It requires a resolved absolute parent,
ASCII text and final newline. Every line must have a positive host PID prefix.
It recognizes completed fork, vfork, clone and clone3 records, including failed
calls and interleaved unfinished/resumed calls. Resumptions must match the
same PID and syscall; overlapping, orphaned or incomplete calls fail. Signals
may interrupt an unfinished creation. A child may execute or exit before its
parent's vfork call resumes; entry and completion line numbers remain distinct.

The exact internal result `? ERESTARTNOINTR (To be restarted)` is recognized
for these creation calls. Flags and call/resumption structure still validate,
but this result supplies no child PID and creates no parentage record. A later
successful call must independently supply the selected birth; its original line
numbers are retained without linking it to the earlier restart request. Other
question-mark results remain unsupported. This does not certify that a requested
restart eventually occurred or that the process completed successfully.

Successful returns identify the child. For the selected edge, an explicit
`local_pid /* host_pid in strace's PID NS */` translation is mandatory. A bare
number cannot establish which PID namespace it belongs to. Exactly one creation
in the whole trace may identify the selected child, and its creator must equal
that independently supplied. Duplicate births are refused even if PID reuse
could explain them. Selected child records before creation and selected
parent/child records after a terminal event also fail. These checks reject
visible lifetime contradictions; the caller still owns complete trace capture
and the authenticated parent's lifetime.

Fork/vfork arguments must be empty. Clone/clone3 require unabbreviated
flags from the closed set in `process_trace.py`. The legacy `CLONE_DETACHED`
flag also accepts the observed `0x400000` encoding, with optional leading zeros
after `0x`, and the exact optional strace annotation ` /* CLONE_??? */`.
No other numeric bit, combined numeric mask or numeric annotation is accepted.
Successful creation with that flag requires legacy clone without `CLONE_PIDFD`;
clone3 and the PIDFD combination are refused on a successful return. Failed
calls with those known flags remain parseable but supply no child evidence.
This follows the Linux clone contract and is not a general validator of every
flag combination. Unknown bits and unrecognized flags fail.
`CLONE_PARENT` and `CLONE_THREAD` are recognized for
other calls but refused for the selected edge: they do not establish ordinary
parentage to the calling process. `CLONE_PARENT_SETTID` is a different flag
and remains supported. Other clone argument fields are not semantically
verified. Exec payloads and signal details are not interpreted by this reader;
they cannot substitute for a creation record.

## Composition and claim limits

The existing exec inspector recognizes the same validated creation record
shapes for its selected PID and excludes only their original line numbers
from exec interpretation. It still requires exact successful exec argv and
environment, refuses unsupported exec records, and rejects overlap between an
unfinished exec and process creation. Valid horizontal padding before an exec
result is accepted, including strace's aligned resumed-call output. An exec
match alone supplies no parentage; callers must separately run both checks
against the same protected trace and linked identities.

The `caplab.process-creation-inspection/v1` result reports trace hash/size,
parent and child host PIDs, returned namespace PID, syscall and original
entry/completion lines, and `recorded_parentage_agrees: true`. It omits argv,
environment and response bytes. `trace_provenance_verified` and
`binding_complete` remain false, `native_capture_complete` remains null and
`study_eligible` remains false. This is neither full ancestry reconstruction
nor executable-byte verification, stream-origin proof, native success or
capability measurement.

Parsing/storage is proportional to the bounded trace. Stable file reads do
not impose a wall-time bound on filesystem I/O. Missing, ambiguous or
unsupported evidence fails without writes, retries, source searches or fallback.
No existing research trace is rewritten to add missing creation evidence.
