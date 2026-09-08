# Private native runtime preparation, version 1

Status: implemented host preparation. See the
[decision and verification](../../records/implementation-2026-09-08-native-runtime-preparation.md).

`caplab.native_runtime.prepare_native_runtime(policy_path, invocation, *,
expected_invocation_sha256, task_root, output_dir)` creates fresh private host
custody for a [prospective native invocation](native-capture-invocations-v1.md).
The expected digest must come from an independently retained plan record.
The function checks that digest, rebuilds the plan with the canonical invocation
builder and requires the complete plans to match. Recomputing a hash after
adding command overrides, authorization or different capture locations cannot
make an unsupported plan pass. Validation precedes filesystem creation.

The host `task_root` must be an absolute resolved existing directory below `/`.
The fresh `output_dir` must have an absolute resolved parent and neither contain
nor lie inside the task root. Existing output directories or links are refused.
The caller must keep task/custody parents trusted and stable during preparation.
These path checks are not protection from a concurrent privileged host writer.

## Retained layout

The outer `output_dir` contains:

- `invocation.json`: the complete rebuilt plan, published with its exact file hash.
- `prompt.bin`: exact UTF-8 prompt bytes, with no newline or normalization added.
- `runtime/`: the only intended writable runtime mount.
- `preparation.json`: the final preparation receipt.

Codex runtime directories are `home`, `codex`, `codex/sessions` and `codex/log`.
Claude runtime directories are `home`, `claude` and `claude/projects`. These trees
start empty; no home, configuration, credential or session file is copied.
Directories use mode 0700 and files 0600. Prompt writes sync their descriptor;
plan/receipt publication uses the existing capture publisher. Each runtime
directory is synced before publication, deepest first. Final publication syncs
the custody root and its parent. This is a local filesystem barrier, not a
hardware power-loss or replication guarantee.

The `caplab.native-runtime-preparation/v1` receipt records the independent
invocation digest, exact invocation-file digest, prompt digest/length, custody
and runtime paths, created directory list, and proposed task/runtime mount
sources and destinations. It translates the plan's capture locations into host
paths under `runtime/` without inspecting them for native output. Missing future
files are expected at preparation time. The receipt reports
`execution_authorized: false` and `binding_complete: false`.

## Failure and execution boundary

Invalid plans or host paths raise `NativeRuntimeError`. Filesystem errors
propagate as `OSError`. Failures retain partial state for inspection; they never
trigger cleanup, overwrite, a retry or a new root. A failed preparation cannot
be overridden by a component receipt or by a final file remaining after a
publication-cleanup error. The API has no adoption/recovery path for partial
roots and makes no study-assignment reservation or replay-prevention claim.

The mount mapping is a proposal, not an executed sandbox. An adapter must keep
the outer custody unmounted, verify namespace paths against its system mounts,
seed only separately authorized configuration/credentials, pin executable and
account inputs, enforce storage/timeout limits and obtain execution permission.
The runtime tree is mutable during a native attempt; initial permissions do not
prove continued host ownership or immutable evidence. The [native output collector](native-output-collection-v1.md) supplies bounded raw
retention of planned session and diagnostic paths. Session/child linkage and
completeness checks remain required before use.
Do not capture the entire runtime home, which may later contain credentials.

The integration test mounts only the prepared task and runtime alongside a
minimal read-only Python environment, runs a synthetic Python process through
[bounded task capture](task-attempt-capture-v1.md), and checks the resulting
custody with the [integrity verifier](task-capture-verification-v1.md). It checks
persistent writes and inaccessible outer inputs for those mounts. It does not
execute a native agent or establish complete containment, provider routing,
network policy, native emission, blinding or study readiness.
