# Native entrypoint and direct child execution, version 1

`caplab.native_launch_configuration.inspect_native_child_trace(policy_path,
invocation, launch, trace_path, *, evidence, child)` joins exact entrypoint
execution, direct parentage and the selected child's exact exec and termination.
It launches nothing and does not choose a child from matching trace text.

`evidence` is the existing NativeLaunchTraceEvidence: independent invocation,
launch and trace hashes, authenticated entrypoint PID and per-read byte limit.
`child` is NativeChildTraceEvidence(expected_pid, expected_executable,
expected_command, expected_environment). The child must be distinct from the
entrypoint. Its PID and expected invocation come from the caller's separately
established identity/configuration evidence. The function does not derive
expected command or environment from observed bytes.

The caller owns parent process-leader authentication, parent/child lifetime
selection, complete ordinary namespace-decoded trace capture, tracer provenance,
protected quiescent custody and installed executable identity. Inputs are
borrowed for the synchronous call; frozen dataclasses do not make nested lists
and maps immutable. Do not mutate them concurrently. The report contains new
maps and omits full argv/environment payloads. The caller bounds the supplied
configuration objects; max_trace_bytes applies to trace reads only.

## Required composition

1. Verify the anchored native launch and its entrypoint termination using
   [launch inspection](native-launch-configuration-v1.md) with
   require_termination=true.
2. Verify a distinct direct child using [process creation](process-creation-trace-v1.md)
   against the same trace, hash, entrypoint PID and byte allowance. Existing
   namespace translation, unique-birth, lifetime and clone-flag rules apply.
3. Require the child's creation **entry** line after the matched entrypoint
   exec **completion** line. A child created before that selected launch cannot
   supply its execution evidence even when the creator PID matches.
4. Verify the selected child's exact invocation and termination using
   [exec termination](exec-termination-trace-v1.md) against the same trace/hash.

The child may exec before its parent's vfork/clone call returns; creation entry
and completion lines are intentionally distinct. Do not impose completion
ordering that rejects valid interleaving. Existing exec and lifetime checks
still reject visible contradictions, missing or duplicate terminals and
unsupported trace grammar. An incomplete unrelated creation record can prevent
the whole-trace parentage result; this composition does not bypass that refusal.

The current composition performs five sequential bounded reads: two for the
entrypoint, one for creation and two for the child. Each requires the same
independent trace hash and is bounded by max_trace_bytes. That value is not a
combined I/O budget or filesystem wall-time limit. Existing readers own and
close their descriptors; no additional file or process lifecycle is introduced.

## Result and limits

The `caplab.native-child-execution-link/v1` result includes:

- `launch`: the v2 native launch report, including entrypoint termination.
- `creation`: the direct parentage report and its original line locators.
- `child_execution`: the exact child exec/termination report.
- `recorded_child_execution_linked: true`: those observations meet the common
  trace, identity and ordering contract.

Entry and child exits remain separate. Either may exit nonzero or terminate by
signal without invalidating a well-formed evidence report. Exit 137 is not
SIGKILL. Both outcomes are about selected PID lifetimes; later execs on the same
PID do not establish that the original executable image remained resident.

`executable_bytes_verified`, `task_success_verified`, `trace_provenance_verified`,
`binding_complete` and `study_eligible` are false; `native_capture_complete` is
null. This function neither verifies native package bytes nor determines whether
the caller selected the intended native binary. It provides no output-origin,
model execution, task correctness, serving-parity, qualification or acceptance
claim. Same-PID native executables should use entrypoint inspection directly.

Invalid expectations, mismatched anchors, unsupported/missing/contradictory
evidence or pre-launch creation raise existing ValueError/capture exceptions;
filesystem errors propagate. No partial combined report, retry, child search,
alternate trace, weaker fallback, historical rewrite or automatic admission
occurs. Existing launch and individual process inspectors remain unchanged.
