# Exact exec and PID termination, version 1

`caplab.exec_trace.inspect_exec_termination(trace_path, *,
expected_trace_sha256, expected_pid, expected_executable, expected_command,
expected_environment, max_trace_bytes)` links the existing exact-exec
observation to a subsequent terminal record for the same independently selected
host PID. It launches nothing and does not infer the outcome from a supervisor,
wrapper, shell or stream receipt.

## Evidence and interpretation

The caller supplies the same inputs and owns the same authenticated process
identity, lifetime, tracer provenance and protected quiescent custody as for
[exec trace inspection](exec-trace-v1.md). Its complete exec validation runs
first, including exact argv/environment, bounded stable file reads, independent
hash, ASCII/full-hex format, required final newline and supported selected-PID
records. Creation-call parsing and unfinished/resumed-call restrictions remain
unchanged. An interrupted, unsupported selected-PID syscall can therefore prevent
this combined report even when a terminal line is present.

The termination pass rereads the same path with the same independent hash and
byte allowance. Each of the two sequential reads is bounded by max_trace_bytes;
this is a per-read allowance, not a combined I/O budget or filesystem wall-time
limit. Any changed hash or failed read prevents a report.

Exactly one supported selected-PID terminal event is required after the matching
exec's completion line. No later record for that PID is permitted. An earlier
terminal, duplicate terminal or selected-PID activity after termination is
refused. Another PID's outcome and a signal-delivery line cannot substitute.
These checks reject those visible contradictions; they do not reconstruct all
births or independently authenticate a PID lifetime.

Supported terminal bodies are:

- `+++ exited with N +++`, where N is canonical decimal 0 through 255, without
  signs or leading zeros except for zero itself.
- `+++ killed by SIGNAME +++`, optionally with the exact ` (core dumped)` marker
  immediately before the final delimiter. SIGNAME must be in the closed
  conventional Linux signal-name set in exec_trace.py. Realtime, numeric,
  unknown and alias spellings outside that set are unsupported.

Exit 137 remains exit 137. SIGKILL termination has no exit code in this report;
it is not converted to a shell convention such as 137. The core marker means
the tracer reported it; no core file is inspected or asserted to exist. Signal
names are parsed observations, not validation of every kernel signal semantic.

Successful exec can be followed by later execs on the same PID. The report links
that PID's terminal outcome, not the duration or result of one executable image.
The nested exec report keeps the selected executable and observed exec-call
count. To report a native binary outcome, the caller must independently identify
that binary's PID and validate its invocation and parentage. Launcher termination
alone cannot substitute for child-binary termination.

## Result and failure behavior

The result schema is `caplab.exec-termination-inspection/v1`:

- `exec_trace`: the unchanged exact-exec inspection report.
- `termination`: `kind` (`exited` or `signaled`), `exit_code` (integer or null),
  `signal` (name or null), `core_dump_reported` and the original terminal `line`.
- `recorded_pid_termination_verified: true`: the selected exec and PID terminal
  observation satisfy this format and ordering contract.

`task_success_verified`, `trace_provenance_verified`, `binding_complete` and
`study_eligible` remain false; `native_capture_complete` remains null. Zero exit
is not verified task correctness, model execution, final-message linkage,
transport success, qualification or acceptance. Each needs its own evidence.
A nonzero or signal outcome is a normal inspection result, not a parsing error.

Missing, ambiguous, malformed or unsupported evidence raises the existing
CaptureVerificationError/ValueError; filesystem errors propagate. No report,
mutation, retry, source search or alternate-outcome fallback occurs on failure.
Only bounded read descriptors are owned and closed. Existing exec-only callers
and old diagnostic reports retain their prior interpretation; there is no
retroactive eligibility promotion or native rerun.
