# Native collection verification, version 1

Status: implemented read-only inspection. See the
[decision and verification](../../records/implementation-2026-09-08-native-collection-verification.md).

`caplab.native_collection_verify.verify_native_collection(policy_path, custody,
*, expected_collection_sha256, max_receipt_bytes)` inspects a retained
[native output collection](native-output-collection-v1.md). The expected digest
must be independently retained SHA-256 of the exact `collection.json` bytes.
Computing it from the same untrusted directory immediately before inspection
checks internal consistency only; it does not establish the intended collection.
The policy path supplies the repository's canonical native policy to the existing
invocation builder, which checks its pinned content hash.

The caller supplies quiescent custody and trusted stable host parents. The
custody path must be absolute with a resolved parent. The root, receipts,
objects directory and referenced payload files open with no-follow descriptors;
receipts and payloads must be regular files. No original runtime or task path is
opened. Those source paths are checked lexically as retained metadata, allowing
the original runtime to be removed and the collection directory to be moved.
The policy file remains a separate trusted input, outside custody read limits.

## Checks and resource bounds

The caller's positive integer `max_receipt_bytes` bounds the combined raw bytes
of four JSON receipts: collection, intent, preparation and invocation. Booleans
are rejected. Each linked file must match its exact expected hash and v1 schema.
The existing strict JSON reader rejects invalid UTF-8, duplicate keys and
non-finite constants. The source preparation/invocation byte count must also fit
the collector's anchored source-receipt allowance.

Canonical invocation reconstruction checks configured subject/profile identity.
The intent and preparation invocation hashes must agree. Both selected-path maps
must match the canonical plan translated under the recorded source runtime.
Locations must be unique, sorted, complete for that plan, and carry the expected
source and directory/file kind. A location's status is `retained` or `missing`;
the missing-location summary must agree exactly.

Inventory entries may belong only to retained selected locations. Every retained
location needs a root of its expected kind. The task inventory verifier checks
normalized sorted unique paths, parent directories, valid modes, regular-file
object locators and unique object references, exact sizes/hashes, and canonical
literal symlink targets. It checks the native entries beneath one transient
in-memory directory root; that root is never written or counted as a retained
entry. The shared artifact-byte and entry limits come from the anchored intent,
and the reported totals must match. All-missing collections with zero entries
and bytes can pass integrity checks while retaining explicit missingness.

Payloads remain opaque bytes. Reads use chunks no larger than 65,536 bytes and
check descriptor/path identity around reading. Size limits detect oversized or
growing files; source identity changes fail. Hashing does not accumulate payload
contents in memory. Parsed receipt memory is bounded by the caller's combined
receipt allowance. These checks are not an atomic multi-file snapshot and do not
bound wall time on a blocked filesystem. Unreferenced files are not enumerated
or opened; this verifier does not assert that the directory contains only the
referenced bundle.

## Result and failure meaning

The `caplab.native-collection-inspection/v1` report contains the independent
collection hash, `integrity_verified: true`, configured tuple/profile/invocation
identities, verified receipt-byte count, retained artifact/entry totals and
missing locations. It omits prompts, commands, raw output and source paths.
The source collection must retain `native_identity_verified: false` and
`native_capture_complete: null`; a contradictory positive claim is rejected.
The report preserves those values. Configured identity is not observed identity.

The reader writes nothing, launches no native process and performs no evidence
admission. It raises `CaptureVerificationError` or propagates filesystem errors.
It checks byte integrity and selected consistency fields, not every metadata
field: timestamps and source stat records remain hash-covered observations
without independent chronology or provenance verification. Unrelated preparation
metadata is not fully reverified. A valid bundle does not prove publication
completed, recover an interrupted capture, establish session/attempt or child
linkage, prove exhaustive native emission or containment, or grant eligibility.
Known capture failures cannot be overridden by this reader.

The CLI runs from an environment with CAPLAB importable:

```bash
PYTHONPATH=src python3 scripts/verify_native_collection.py /absolute/collection \
  --policy docs/product/contracts/native-agent-systems.json \
  --expected-collection-sha256 "$INDEPENDENT_COLLECTION_SHA256" \
  --max-receipt-bytes 1048576
```

Replace the collection path, digest and byte allowance with the intended
retained inputs; the command never discovers an anchor automatically. Exit zero
prints the JSON inspection, including missingness. Invalid input or integrity
failure exits two through argparse, with no JSON success on stdout. This exit
status is not a native-completeness or eligibility verdict.


The [Codex root linker](codex-root-capture-linkage-v1.md) consumes this verified
custody alongside an independently anchored task capture. It compares retained
stdout and rollout identity while keeping execution binding, child linkage and
native completeness unverified.
