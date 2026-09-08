# Retained native version verification, version 1

Status: implemented. See the
[authorization and verification record](../../records/implementation-2026-09-08-native-version-verification.md).

`caplab.native_version_verify.verify_native_version(policy_path, custody, *,
expected_version_sha256, max_receipt_bytes, max_stream_bytes)` verifies a retained
bundle from `capture_native_version`. The caller supplies the independent digest
of exact `version.json` bytes, a positive integer allowance for combined receipt
bytes and a separate positive integer allowance for combined retained stdout and
stderr bytes. Booleans are not byte limits. Custody must be quiescent, with trusted
stable parents. The native policy is the only content input outside retained custody.

The verifier follows five retained receipts: version, intent, preparation,
invocation and process. Each receipt is read as a regular file without following
its final symlink, checked against its linked digest and parsed with the existing
strict JSON reader. All five share the caller's receipt allowance. The retained
preparation/invocation pair and process receipt must also fit the allowances
recorded by the producer. Both raw stream files are checked against their exact
sizes and hashes through the shared process verifier. Their combined recorded
size must fit the caller's stream allowance before either payload is opened.
The original capture's stream and timeout limits and completion rules still apply.

The invocation is reconstructed from the canonical native policy, including the
profile, subject tuple, environment and version command. Recorded task,
preparation, runtime and installation paths must be absolute, normalized and
consistent with the producer's disjoint layout. The verifier uses these paths
as strings; it never resolves or opens them. The exact outer namespace command
is rebuilt by the existing version-command owner. Its argv, fixed outer
environment, no-network policy, read-only task access and version-only purpose
must agree with intent. Source path existence, permissions and installation
bytes at the original time cannot be established from these strings.

Version, intent and invocation must agree on their identity links. Recorded
entrypoint bytes must fit the recorded entrypoint allowance; the entrypoint hash
is retained as a recorded observation, not re-attested from an installation.
The embedded process document must equal the linked process receipt, including
JSON value types. Unsupported positive native-identity or full-Binding claims
in the final version receipt are rejected.

The result uses `caplab.native-version-inspection/v1`. It reports integrity,
recorded version-command agreement, linked digests, configured tuple/profile,
recorded entrypoint identity, stream metadata and verified byte counts. Nonzero
exit, timeout and byte-limit outcomes remain visible. An intact failed probe can
pass integrity verification; this does not turn it into a successful version
response. Output text is neither decoded, normalized nor interpreted. Streams
remain available at `process/native.stdout` and `process/native.stderr` beneath
the supplied custody root. No raw output or source-path contents enter the report.

`native_identity_verified` and `binding_complete` remain false. Hash consistency
and recorded command agreement do not authenticate an executable, provider,
account, runtime, publication history or actual namespace enforcement. The
verifier does not prove that a bundle was emitted by the producer, verify all
timestamp/preparation metadata, or establish runtime-file completeness. The
caller must retain independent anchors and the custody provenance. Relocation
and removal of original sources are supported; changing native policy or capture
format requires its own contract change.

Errors propagate as `CaptureVerificationError` or filesystem errors. Receipt and
stream reads use the existing bounded, stable-read helpers. No recorded command
is executed, no source installation is inspected, and custody is not changed.
Filesystem I/O has no wall-time bound, and this API supplies no admission,
cleanup, retry, qualification, ranking or campaign authorization.
