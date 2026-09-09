# Collect native outputs from a retained runtime descriptor

Date: 2026-09-08. Baseline: `9c190c9`. Primary agent under
[ADR 0026](../decisions/adr-0026-caplab-blanket-decision-authority.md).

## Authorization before execution

Implement bounded native output collection from an already-owned, quiescent
directory descriptor whose device/inode the caller independently supplies.
Preserve the existing host-directory collection path and v1 receipt behavior.
Use v2 collection/intent receipts for descriptor sources, with explicit
namespace-path and descriptor-identity provenance. Retain existing canonical
invocation, independent preparation/collection anchors, source-stability,
quota, missingness and private-custody checks. The collector borrows the caller's
descriptor and owns only its duplicate. It does not authenticate the original
handoff or prove that a native harness wrote the files.

Permitted source changes: `src/caplab/native_collection.py`,
`native_collection_verify.py`, `task_capture_verify.py`, `codex_capture_link.py`,
`claude_capture_link.py`, and `capture_accounting.py`. Extend the shared receipt
reader only to accept an explicit tuple of supported schemas. Carry verified
descriptor-source metadata into linkage and accounting results. Add
`tests/test_descriptor_native_collection.py`, update the native collection and
verification contracts, and complete this record. No other runtime changes.

Use only new synthetic task/native-layout fixtures and disposable temporary
roots. Exercise both configured harness layouts, moved or detached source
paths, descriptor ownership and identity refusal, shared quotas, receipt
version/provenance tampering, payload integrity, and downstream linking and
accounting. Run focused checks and `make check`. No actual native harness,
model, credential, network, user service or cgroup execution is authorized.
Do not treat synthetic producer bytes as native emission evidence.

Preserve historical evidence, world exposure, study decisions, source prompts,
`docs/designs/`, sibling worktrees, unrelated services/timers and Plane. No
admission, ranking, acceptance, human-time commitment, external message or push.
Retain source/authorization hashes and verification under fresh
`/tmp/caplab-descriptor-collection-*` paths; consolidate advisory provenance
before deleting only named scratch. Commit only the named files locally.
Authorization expires at commit. Stop before broader effects, missing source
identity, changed writers or unsupported custody assumptions; retain partial
output and propagate errors instead of claiming successful collection.

Additional fixture scope before execution: permit one standing integration
test to launch a fixed local Bubblewrap namespace with no network and no
writable host mount. It creates only the Codex-layout directories and one
small binary diagnostic on a private 1-MiB tmpfs, hands its directory
descriptor to the test through a private Unix socket, and exits. The test
waits at most five seconds and terminates only its own process group on
failure. This is synthetic descriptor-lifetime verification, not native
execution. It runs once in focused verification and once in the full suite;
a failed test may rerun after a relevant correction.

## Selected implementation

The host-path collector opened `preparation_root/runtime`, while the resource
recovery mechanism preserves directory descriptors after namespace exit.
Recreating a host runtime from recovered bytes would obscure that source
transition. The selected change reuses the descriptor-based inventory traversal
already inside the collector and adds an explicit source mode.

`NativeRuntimeDescriptor` supplies a borrowed FD and expected device/inode.
The collector duplicates it, checks directory kind and identity, refuses an
output parent/ancestor matching that runtime, and closes its duplicate through
a context manager. It preserves the caller's descriptor on success and failure.
The preparation and invocation still require their independently anchored host
receipts and canonical layout. Descriptor collection does not open, search or
fall back to the original host runtime path.

Only descriptor collection writes v2 intent/collection receipts. Their selected
sources are namespace paths and their `runtime_source` names the namespace root
and device/inode, without a process-local descriptor number. The verifier
requires matching supported receipt versions and the exact source metadata
shape. It checks the namespace root against the canonical invocation and rejects
invalid counts, mixed versions and a v1 intent claiming descriptor provenance.
The ordinary v1 path and inspection result shape remain unchanged for valid
existing inputs.

Codex and Claude root linkage and capture-byte accounting now accept verified
v2 collections and preserve their source metadata. Missing locations, failed
process outcomes, stream completeness and the unverified executed-invocation
claim remain distinct. No parser substitutes a successful native result for
synthetic bytes or a failed task process.

This connects retained runtime directories to the existing native collection
consumers. Task inventory integration with the resource supervisor, original
mount-handoff attestation, exact native invocation/Binding evidence and the
representative repair measurements remain incomplete. The expected device/inode
is caller-supplied provenance; neither this API nor its offline verifier can
establish that it came from an independently authenticated handoff. CAPLAB-84
remains open, and these fixtures establish no reviewer ordering or eligibility.

## Executed verification

The eight focused test methods passed in 0.906 seconds. They cover:

- A moved runtime with a decoy at its old host path, opaque binary bytes and a
  literal symlink, followed by verification after source removal.
- Wrong device/inode, non-directory, closed or invalid descriptors and output
  inside the actual runtime; refusal before custody and preservation of the
  borrowed descriptor without a duplicate leak.
- Shared byte and entry exhaustion, retained allowed prefixes, absent final
  receipts on failure, and successful exact-limit collection.
- Nine rehashed provenance/version mutations and altered payload rejection.
- Both native-format fixture layouts through collection, root linkage and byte
  accounting after source removal, preserving process exit 7 and the absence of
  native execution/completeness claims.
- A fixed private 1-MiB tmpfs whose namespace process exited before collection;
  the collector recovered its binary diagnostic through the retained descriptor.

These tests use real local file descriptors and subprocesses. The native-format
bytes are authored fixtures; no Codex or Claude executable runs. The namespace
fixture exits and its transferred descriptor closes in the test's cleanup.

The first focused run failed only because the closed-FD test expected an OS
error. Opening preparation receipts can reuse the closed descriptor number, so
the collector may instead refuse its different identity. The assertion now
accepts either refusal while requiring no output. This corrected the test's
assumption; it did not weaken the collector. The failed log is retained as
`/tmp/caplab-descriptor-collection-focused-first.log`.

The existing host-path collection tests also passed: 11 tests in 1.156 seconds,
log `/tmp/caplab-descriptor-collection-existing.log`. Focused result:
`/tmp/caplab-descriptor-collection-focused.log`.

`make check` passed 1,220 tests in 163.966 seconds with four skips, including
the new namespace fixture. Log:
`/tmp/caplab-descriptor-collection-make-check.log`. Changed Python parsed,
documentation links resolved, and `git diff --check` passed. Verification does
not supply independent acceptance or complete the repair measurement task.

## Advisory provenance and closure

Pincite's release gate passed at commit
`d3e0c0d4ccd1920b2e045c156f1cf0db4fc5f04f`, source fingerprint
`ce9bd74fa3a711c9354726a64f6c9da2427c4475a85e60c062ba8d0dce449fe0`.
Final packet: `pkt-0f5232d701cd65c9`, SHA-256
`0f5232d701cd65c93db439971407135c8974b4b67f09dc564822e7d1418ae433`;
corpus `corpus-2026-07-12-a11702cc9217`, doctrine
`doctrine-f6bbb5196a3f8bf9`, retriever `retriever-ec995ecdd083b2c8`.

Four served concepts informed the change and were classified as valid citations:
`universal-repository-contract-precedence` for the delegated scope and v1
preservation, `python-structured-cleanup` for duplicate-descriptor ownership,
`python-text-bytes-boundary` for opaque payload custody, and
`universal-evidence-before-intervention` for the observed source-lifetime gap.
The CAPLAB authorization above owns the decision.

All 15 remaining obligations are nonmaterial to this bounded local claim:

| Unmet requirements | Reason |
| --- | --- |
| CI and build matrix; formatter and static-tool configuration; repository version and dependency contract; Python and dependency version matrix; formatter linter and type-checker configuration | No dependency, tooling or cross-platform support change is claimed. The existing local toolchain and full suite bound verification. |
| CI-only build path for release artifacts; build pipeline inventory; dependency and plugin verification against upstream signatures; write-protection and provenance records on the artifact store | No production executable is built, published or accepted. Native build provenance remains a separate Binding requirement. |
| Affected classes or attributes; demonstrated repetition and ordinary-alternative analysis; lookup and construction semantics; repeated rule; tooling and compatibility | The source input uses an ordinary frozen dataclass and context manager; no Python dynamic descriptor, decorator framework or metaclass mechanism is selected. |
| Evidence-explicit-user-requirements | The exact bounded scope derives from the inspected ADR 0026 delegation, supplied as repository-contract evidence; no new owner judgment is required for these edits. |

`/tmp/caplab-descriptor-collection-verification.json` consolidates source and
result hashes, all advisory packet/evidence contents, obligation classifications
and the citation receipt. Only the eleven named advisory scratch files are
deleted after consolidation. Authorization snapshots and verification logs
remain available. This local commit consumes the authorization.
