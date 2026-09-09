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
evidence, require_termination=False)` checks the anchored configuration against
one exact exec, optionally requiring that entrypoint PID's termination.
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

[Native child execution inspection](native-child-execution-v1.md) composes this
launch with independently selected direct-child parentage, exact exec and
termination. It additionally refuses children created before the selected launch.

`require_termination` must be an actual boolean. Its default false preserves
the v1 report and accepted exec-only behavior. When true, the same configuration
validation precedes [exec termination inspection](exec-termination-trace-v1.md).
The report schema becomes `caplab.native-launch-exec-link/v2` and adds
`entrypoint_termination`, containing that complete inspector report. The
top-level `exec_trace` remains the nested exec report for compatibility with
consumers of exact invocation evidence. The stronger inspection performs two
sequential same-hash reads, each bounded by max_trace_bytes; it adds no third
exec-only read. Missing or contradictory termination cannot fall back to v1.
Nonzero exit and signal termination remain reportable observations, not errors.

The selected PID is the authenticated entrypoint, which can exec further images
or spawn a native child. Its termination must not be relabeled as a child's
outcome or inferred from the supervisor's return code. Native-binary parentage,
task success, transport status and final-message linkage require separate
evidence. The v2 report preserves all v1 limits and false/null eligibility fields.

Invalid configuration or evidence raises `ValueError` or its existing capture/
runtime subclasses; filesystem errors propagate. No retry, mutation, fallback
or alternate-source search occurs. The trace allowance covers the trace bytes;
it does not bound the already supplied documents, trusted policy or wall time.

New `--trace-exec` startup selections seal the canonical launch configuration
and `entrypoint_termination_required: true`. The supervisor requires that exact
value and configuration before execution, then uses v2 inspection afterward.
The startup execution inspector verifies the selection-to-intent hash before
consulting the requirement. New traced startup calls supply an independent
expected selection hash, so the check also runs when a report has no trace anchor.
A required termination without a trace anchor or launch configuration fails;
malformed requirement values fail rather than selecting a weaker check.

Older selections with no requirement retain v1 inspection, and those without
a launch configuration keep direct exec inspection. Explicit false also selects
the older behavior, but the new traced producer never emits it.

The shared startup functions `inspect_custody(root, report, *,
expected_selections_sha256=None)` and `inspect_execution(root, report, native, *,
expected_selections_sha256=None)` accept that independently retained hash.
It must be 64 lowercase hexadecimal characters and must agree with the actual
selection bytes and the intent. Supplying it requires selection custody even
if the report lacks its trace anchor. New traced supervisor and post-exit calls
always supply it; the report itself cannot choose whether the caller requires it.
Missing/corrupt selections or intent, or a re-sealed selection that differs
from the independent hash, fail without retry or weaker fallback.

Without that keyword and without an exec trace anchor, shared custody inspection
returns no execution evidence and reads no startup-specific files. Other native
diagnostics use this path when their execution evidence is checked separately.
This result makes no startup-selection or execution claim. Legacy traced
callers still validate their selection-to-intent hash and retain the declared
inspection strength. This compatibility repair replaces the prior unconditional
startup-selection read for untraced shared-custody callers.

The startup script preserves its RuntimeError guards, while launch and trace
validation errors propagate unchanged. These changes do not rewrite older
selections, rerun agents or claim complete capture. See the
[selection-anchor repair](../../records/repair-2026-09-09-startup-selection-anchor.md),
[termination adoption record](../../records/implementation-2026-09-09-launch-termination-adoption.md)
and the original
[implementation record](../../records/implementation-2026-09-09-native-launch-configuration.md).
