# Effective native launch configuration, version 1

`caplab.native_launch_configuration.build_native_launch_configuration(
policy_path, invocation, *, expected_invocation_sha256, context)` identifies
the effective command, environment and configured cwd separately from the
[canonical prepared invocation](native-capture-invocations-v1.md).

`NativeLaunchContext(profile, fixture_port=None)` selects one of two closed
profiles. The canonical base is rebuilt under the exact native policy and its
independent hash before the effective configuration is constructed.

| Profile | Effective configuration | Purpose |
|---|---|---|
| `canonical-native/v1` | Exact canonical argv, environment and cwd; no fixture port. Supports the canonical Codex and Claude tuples. | Native capture preparation. |
| `codex-scripted-local/v1` | The canonical Codex invocation plus the fixed local transport and diagnostic settings below. | Scripted protocol diagnostic only. |

The local profile requires an integer port from 1 through 65535, excluding
booleans. Immediately before the final `--` and prompt, it adds these exact
settings through three `-c` pairs:

- `chatgpt_base_url="http://127.0.0.1:<port>"`
- `openai_base_url="http://127.0.0.1:<port>"`
- `check_for_update_on_startup=false`

It adds `CODEX_REFRESH_TOKEN_URL_OVERRIDE` with
`http://127.0.0.1:<port>/oauth/token` and this exact `RUST_LOG` value:

```text
codex_core::stream_events_utils=trace,codex_core::tools::router=trace,codex_core::tools::code_mode=trace,codex_core::codex=debug
```

All other command tokens, prompt bytes, environment entries and cwd remain
canonical. There are no arbitrary argument, environment, model, effort,
sandbox, proxy or endpoint overrides. These settings reproduce the previously
verified local diagnostic's configuration; they do not guarantee routing,
containment or behavior for any installed harness. The caller must freeze the
exact harness, isolate networking and authorize the diagnostic separately.
The local profile supplies no model inference or eligible study configuration.

The `caplab.native-launch-configuration/v1` record includes its canonical
`invocation_sha256`, profile, port, effective command/environment/cwd, purpose
and `canonical_invocation_agrees`. That agreement covers configured values,
not execution. `launch_configuration_sha256` hashes canonical JSON of every
other field. A changed port or profile changes that identity. Each result owns
its lists and maps; the invocation is borrowed. No ambient environment or
credentials are read, and nothing is written or launched. Canonical preparation
and collection schemas remain unchanged. Every result keeps authorization,
complete Binding and study eligibility false.

`inspect_native_launch_trace(policy_path, invocation, launch, trace_path, *,
evidence)` checks the anchored configuration against one exact exec.
`NativeLaunchTraceEvidence` carries `expected_invocation_sha256`,
`expected_launch_sha256`, `expected_trace_sha256`, `expected_pid` and
`max_trace_bytes`. The caller independently obtains those anchors and the
authenticated PID, and owns tracer provenance, process lifetime, source
identity, quiescent custody and bounded loading of the in-memory documents.

The checker validates the launch hash, rebuilds the canonical base and selected
profile, and requires exact canonical-JSON equality. Rehashing a modified command,
environment, cwd, purpose, identity or eligibility field cannot bypass the
profile contract. It then uses the existing [exec inspector](exec-trace-v1.md)
to compare the full argv and environment at `/toolbin/codex` or `/toolbin/claude`
for the independently selected PID. That inspector owns bounded trace reads,
exact trace hash, format, duplicate and malformed-call checks.

The `caplab.native-launch-exec-link/v1` report includes both configuration
identities, the profile, canonical configuration agreement, the nested exec
inspection and `entrypoint_argv_environment_agree: true`. It omits prompt and
environment values. It does not observe actual cwd: `cwd_source_linked` is false.
Binding completeness and study eligibility remain false, native capture
completeness remains null, and nested tracer-provenance limits remain visible.
Program failure after a successful exec does not invalidate argv/environment
agreement and cannot be relabeled task success.

Invalid configuration or evidence raises `ValueError` or its existing capture/
runtime subclasses; filesystem errors propagate. No retry, mutation, fallback
or alternate-source search occurs. The trace allowance covers the trace bytes;
it does not bound the already supplied documents, trusted policy or wall time.

New `--trace-exec` startup selections seal the canonical launch configuration,
check selection custody and exact configuration before execution, and use this
checker afterward. Prior selections without a launch configuration keep the
existing direct exec check, without acquiring a new configuration claim. See
the [implementation record](../../records/implementation-2026-09-09-native-launch-configuration.md).
