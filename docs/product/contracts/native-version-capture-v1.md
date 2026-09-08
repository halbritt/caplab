# Isolated native version capture, version 1

Status: implemented version-only preflight. See the
[decision and verification](../../records/implementation-2026-09-08-native-version-capture.md).

The [retained version verifier](native-version-verification-v1.md) checks the
receipt chain, recorded command and raw output after source removal, preserving
process outcomes without interpreting version text or asserting full Binding.

`caplab.native_version_capture.capture_native_version(policy_path,
preparation_root, harness_source, *, expected_preparation_sha256,
expected_entrypoint_sha256, output_dir, limits)` runs the canonical native
`--version` command and retains bounded process evidence. It cannot take a prompt
or arbitrary command override. It is not a study attempt or an inference launcher.
The caller must have authority for the probe and for the selected installation
and prepared runtime. A passing version response is not an authority grant.

## Inputs and namespace

The preparation digest independently identifies exact `preparation.json` bytes.
Its linked `invocation.json` is checked and reconstructed through the canonical
native policy. This version of the adapter supports `/work` and `/episode` only;
other configured namespace paths are rejected, not rewritten. Mount maps, custody
and runtime paths must match that layout. Source paths must be absolute and
resolved, with the required file/directory kind. The prepared task and custody
must be disjoint. Unrelated preparation metadata and prompt files are not fully
reverified; no prompt is used by the version command.

For Codex, `harness_source` is an installation directory with executable
`bin/codex.js`; for Claude, it is the executable file. The entrypoint's bounded
stable read must match the caller's independent SHA-256. The native installation
must be disjoint from task and preparation. The fresh output root must have a
resolved parent and be disjoint from all three sources; existing output is refused.
Entrypoint identity is not a hash of the complete installation or its dependencies.

The fixed Linux namespace command uses `/usr/bin/bwrap --unshare-all`,
`--die-with-parent`, `--new-session` and `--clearenv`. It never shares the host
network. `/usr` is mounted read-only, with merged-usr `/bin`, `/lib` and `/lib64`
links; `/proc` and `/dev` are private mounts and `/tmp` is temporary. The selected
installation is read-only at `/opt/native` with its entrypoint linked beneath
`/toolbin`. The task is read-only at `/work`. Only the preparation's `runtime/`
is writable at `/episode`; the outer receipts and prompt file are not mounted.
Caller-supplied runtime contents remain caller-owned and must be authorized;
the probe seeds no credential or configuration files and searches no native homes.

Version execution can modify that private runtime: the observed Codex version
probe created a temporary lock and executable symlinks. Keep this runtime as
probe custody and prepare a fresh runtime for a future study episode; do not
treat version execution as a read-only operation on native state.

The outer process receives only `PATH=/usr/bin:/bin` and `LANG=C.UTF-8` through
the existing launcher policy. The inner command receives the canonical capture
profile environment. On the verified local bubblewrap, changing directory also
sets `PWD=/work`; this is derived namespace state, not inherited host state.
The command after `--` is exactly the policy's version command. The model prompt
retained in the invocation is never added to this argv.

Sources, installations and host parents must remain trusted and quiescent.
Paths are mounted after validation; entrypoint hashing is not an atomic executable
handoff. The full package tree, interpreters, libraries, bubblewrap and kernel
are not content-pinned by this API. A different installation or platform needs
its own verification; the merged-usr layout is not a portability claim.

## Custody, bounds and outcomes

`NativeVersionCaptureLimits(max_receipt_bytes, max_entrypoint_bytes,
max_stream_bytes, timeout_seconds)` is immutable. Byte limits must be positive
integers excluding booleans; timeout must be positive and finite. The two initial
receipts share `max_receipt_bytes`. The later process-receipt hash read has its
own allowance of that size. Each of the before/after entrypoint hash passes uses
`max_entrypoint_bytes`, without accumulating the binary in memory. Stream capture
uses the existing combined stdout/stderr budget and timeout, including its
prefix retention and owned-process-group termination rules. Blocked filesystem
reads, writes and syncs have no wall-time bound; runtime-file growth is not bounded
by the stream allowance. This is not a total disk quota or campaign budget.

The output root is private, with exact copied preparation/invocation receipts and
a sealed `caplab.native-version-intent/v1` before launch. Intent records anchors,
entrypoint bytes/hash and source, exact outer argv/environment/cwd, limits, network
policy and task access. The `process/` directory retains raw stdout/stderr and the
existing process-capture receipt. After execution, the entrypoint is hashed again;
a changed entrypoint prevents final version publication.

The final `caplab.native-version-capture/v1` binds intent, preparation, invocation,
configured tuple, entrypoint and exact process-receipt hashes, and embeds the
process outcome. It leaves `native_identity_verified` and `binding_complete`
false. Output stays raw: the caller must interpret the actual version string,
return code and stream completeness. Exit failure, timeout or byte-limit outcomes
remain visible and do not become a successful version assertion. No automatic
retry, acceptance, qualification or replay reservation is supplied.

Validation errors raise `ValueError` subclasses and filesystem errors propagate.
Failures after output creation leave partial custody; there is no cleanup or
recovery path. A readable partial process receipt cannot override an observed
probe or publication failure. New probe output must be kept outside every
subject-visible mount. Actual model execution, native event compatibility,
account identity, provider access and complete Binding verification remain separate.
