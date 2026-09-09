# Codex child configuration preparation v1

`caplab.codex_child_configuration.prepare_codex_child_configuration` prepares
an expected child command independently of execution traces. It accepts policy,
invocation, effective launch, installation root, and keyword-only `evidence`:
`CodexChildSourceEvidence(expected_invocation_sha256, expected_launch_sha256,
expected_binary_sha256, max_installation_bytes)`.

The caller supplies independently established hashes and a stable installation
under trusted resolved filesystem ancestors. Borrowed invocation/launch objects
must remain unchanged during the call. The output owns its command/environment
copies. No process starts, no evidence is persisted or admitted, and no authority
to execute is granted.

## Supported sources and reading

The closed `codex-0.153.4-linux-x64/v1` profile requires the exact launcher and
two package metadata files identified in the module and the
[fixture provenance](../../../tests/fixtures/codex-launcher-0.153.4/provenance.json).
It does not infer support from a version string. Unknown source bytes refuse.

Four regular files are read: `bin/codex.js`, `package.json`,
`node_modules/@openai/codex-linux-x64/package.json`, and that platform package's
`vendor/x86_64-unknown-linux-musl/bin/codex`. The binary hash is selected by the
caller; agreement identifies those bytes without proving their authenticity or
behavior. Tests deliberately select a harmless fixture binary as a control.

The root must be absolute, resolved, and distinct from `/`. Each relative path
is opened through retained directory descriptors without following symlinks.
Reads use the existing stable regular-file checker; directory and file metadata
are checked again before returning. All owned descriptors close on failure.
The caller remains responsible for quiescence and preserving source identity
through eventual launch; these checks do not defeat a hostile filesystem owner.

The positive integer byte allowance is at most 1 GiB and covers the total bytes
of these four files, not the entire installation. Each of the three metadata/
launcher files also has a 1 MiB cap. Files stream through the existing reader;
their contents are not accumulated. Other installation files are not inventoried.
`node_modules/.modules.yaml` must be absent, including broken symlinks. This
closed profile rejects package-manager metadata instead of interpreting it.
Invalid configuration, bounds, hashes, or unsupported source content raise
`ValueError`; filesystem errors propagate as `OSError` subclasses. No retry or
alternate layout fallback occurs, and no partial success report is returned.

## Meaning of the preparation

The existing launch validator rebuilds both the native invocation and declared
launch profile. Canonical and scripted-local Codex launches are supported;
Claude and arbitrary rehashed launch amendments refuse. Node options/module
overrides and package-manager discovery variables are not supported.

The expected executable is the platform binary under `/opt/native`. Its argv
replaces the launch's initial `codex` with that absolute path and preserves all
remaining arguments. Its environment preserves the launch environment, removes
the four `CODEX_MANAGED_BY_*` variables supported by this launcher, sets
`CODEX_MANAGED_PACKAGE_ROOT=/opt/native`, and sets `CODEX_MANAGED_BY_NPM=1`.
The package.json `packageManager` field is not the runtime detector's result.

This transformation is conditional on the returned `namespace_assumptions`:
Linux x64 Node with default module resolution, the unchanged readonly source
mount at `/opt/native`, the stated `/toolbin/codex` link, and absent module
directories at `/node_modules`, `/opt/node_modules`, and `/toolbin/node_modules`.
Node must receive the exact prepared launch environment and entrypoint path.
The returned cwd is the declared launch cwd; this reader does not observe cwd.
Namespace, runtime/Node identity, permissions, source lifetime and actual child
identity need independent execution evidence. A successful local preparation
does not establish any of them.

The `caplab.codex-child-configuration/v1` result contains the anchored invocation
and launch hashes, selected source paths/byte counts/hashes, installation root,
expected executable/command/environment/cwd and namespace assumptions.
`child_configuration_sha256` hashes the entire record excluding that field.
The caller must seal this expectation before execution and retain its independent
anchor; recomputing it from post-execution trace text is not preparation.

`selected_source_bytes_verified` is true. `namespace_assumptions_verified`,
`executed_bytes_verified`, `execution_authorized`, `binding_complete`, and
`study_eligible` remain false. This is a prerequisite for the
[child execution linker](native-child-execution-v1.md), whose caller must still
supply an independently selected child PID. It is not yet integrated into the
public startup producer.
