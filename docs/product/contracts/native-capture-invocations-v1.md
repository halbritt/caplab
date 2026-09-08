# Prospective native capture invocations, version 1

Status: implemented command construction, with native execution unverified.
[Decision and verification](../../records/implementation-2026-09-08-native-capture-invocations.md).

`caplab.native_capture_invocation.build_native_capture_invocation(policy_path,
tuple_id, *, context)` constructs a new prospective native command. It requires
the exact repository [native policy](native-agent-systems.json) bytes with
SHA-256 `1245d7ddda6045d0476a177cd937697be2ed5cd83438b647cdfeade39f70e5d9`.
An altered policy, unknown tuple or invalid context raises
`NativeAgentSystemContractError`; policy read failures propagate. The existing
`validate_native_agent_systems` verifies the base model/harness/effort and version
command before the fixed capture profile is applied. This does not broaden the
old validator's allowed suffixes or make the new plan an old instrument subject.

`NativeCaptureContext(task_root, runtime_root, prompt, session_id=None)` holds
paths in the intended execution namespace, exact prompt bytes and the Claude
session UUID. Paths must be absolute canonical POSIX paths below `/`, with no
NUL, dot segments, redundant separators or nesting between task and runtime.
They need not exist on the host; the builder neither creates nor resolves them.
The caller must map them to private, isolated, persistent locations before
execution. Prompt bytes must be nonempty UTF-8 without NUL. They are decoded
without normalization and appended as one argv element after `--`. Shell syntax
inside a prompt is never evaluated by this builder. Native argument-parser
compatibility still requires the exact-harness preflight.

Claude requires a canonical lowercase UUID; uniqueness and unused-session
custody remain caller obligations. Codex rejects a caller-supplied session ID:
its actual thread ID must come from native output and be linked to retained
rollout evidence.

## Profiles and output

| Profile | Fixed prospective configuration |
|---|---|
| `codex-persisted-events/1` | Native Codex/model/effort from policy; workspace-write sandbox; Git-check bypass; JSON events and no color; exposed reasoning not hidden; detailed summary requested; final-message path and task cwd explicit; no ephemeral option. |
| `claude-persisted-events/1` | Native Claude/model/effort from policy; verbose stream JSON with partial and hook events; explicit session UUID and debug file; legacy skip-permissions mode; no persistence-disable option. |

Both profiles require external containment. The environment is exactly `HOME`,
`PATH`, `LANG`, plus `CODEX_HOME` or `CLAUDE_CONFIG_DIR`. `PATH` is the prospective
`/toolbin:/usr/bin:/bin`; home and harness directories are under `runtime_root`.
No ambient environment, credential or account is read. No executable is resolved
or authenticated. The caller must prepare the `/toolbin` native executable and
its exact version/configuration/account binding. The version command uses the
same environment as the native command.

The `caplab.native-capture-invocation/v1` plan includes the validated base subject,
`caplab.native-capture-profile/v1` definition and hash, full argv/environment/cwd,
runtime root, session ID, prompt byte count/hash and declared capture locations.
`invocation_sha256` hashes canonical JSON of every other plan field. Profile
hashes cover the fixed templates; invocation hashes also cover concrete paths,
prompt and session. Every call returns its own lists/maps. These hashes identify
configuration; they confer no authorization, storage seal or complete Binding.
The plan explicitly states `execution_authorized: false` and
`binding_complete: false`.

Capture locations are configured destinations or candidate search roots:
Codex `codex/sessions`, `codex/log` and `final-message.txt`; Claude
`claude/projects` and `debug.log`, all under `runtime_root`. A search root is not
proof of emission or exhaustive diagnostic capture. Harness configuration and
version can affect actual files. The runtime home may contain credentials and
unrelated configuration; do not copy it wholesale as evidence. The future
collector must bind episode/session-specific files, preserve selected diagnostic
surfaces and make absence explicit.

OpenAI documents persistence separately from JSON output in
[non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode), and
summary/display controls in its
[configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference).
Claude's [CLI reference](https://code.claude.com/docs/en/cli-reference) describes
streaming, session and debug options; the locally inspected help also advertises
hook-event capture. Help/docs prove advertised options, not emission or support
for detailed summaries on a specific model/account. Freeze capability-check
results before adopting either profile for a study.

## Integration boundary

A future adapter must bind the exact executable and configuration, establish
external containment, reserve storage, prepare a private persistent runtime and
obtain exact execution authorization. It can then pass the concrete command,
cwd and environment to [task/process capture](task-attempt-capture-v1.md), retain
and link native session/child/diagnostic files, and use
[custody inspection](task-capture-verification-v1.md) before study interpretation.
The builder supplies no mounts, launch, timeout, capture quota, session collector,
blinding, measurement, admission or placement decision. These profiles cannot
be substituted into a frozen campaign without a new Binding and authorization.
