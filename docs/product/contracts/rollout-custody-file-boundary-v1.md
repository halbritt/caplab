# Rollout custody file boundary

Implemented in `caplab.artifact_rater.read_rollout_attestation` and
`preserve_rollout_attestation`. Decision and verification:
[repair record](../../records/repair-2026-09-08-rollout-custody-file-boundary.md).

Every rollout read opens the leaf with `O_NOFOLLOW | O_NONBLOCK`, checks the
opened descriptor is a regular file, and closes it on success or failure.
This applies to source snapshots, existing custody comparison and direct
attestation. A symlink cannot substitute its target, even if the leaf changes
after a separate symlink check. FIFOs are rejected without waiting for a writer;
directories and other non-regular objects cannot supply rollout bytes.

These flags protect the leaf. The caller still owns trusted, stable parent
paths and private custody; this does not resolve every ancestor by descriptor
or isolate a runtime. `O_NONBLOCK` is not a deadline for regular-file/storage
operations. See the Linux [open contract](https://man7.org/linux/man-pages/man2/open.2.html).

Preservation creates a new custody file exclusively with mode 0600. If custody
already exists, only a non-symlink regular file with exactly the source snapshot's
bytes may be reused; mismatches and partial files are never overwritten. The
source bytes are not modified, and existing custody contents and modification time
are preserved on identical reuse.

For a new file, buffered output is flushed and the original write descriptor
is synced before closing. Identical reuse also syncs its open file descriptor.
Both paths then sync the custody parent directory before returning an
attestation. A file sync alone does not establish directory-entry durability;
the additional directory barrier follows the Linux
[fsync contract](https://man7.org/linux/man-pages/man2/fsync.2.html).
Open, read, write or sync errors withhold attestation as `CalibrationError`.
Already retained bytes remain available for restricted failure inspection.
An identical retry must pass the barriers again; file presence is not a
durability receipt. Direct read-only attestation does not perform these syncs.

The returned attestation still describes the bytes retained, including their
thread ID, consistent model/effort/CLI observations and SHA-256. It does not
assert that the live source remains unchanged after its snapshot was read.
Malformed JSON or inconsistent identity remains an error after preservation.
Normal attestation fields and snapshot semantics are unchanged.

This is a local filesystem barrier, not replication, an ACID transaction,
provider authentication or evidence admission. It assumes the filesystem/device
honors successful sync operations; no power-cut or device-fault survival test
was performed. No new byte or time budget is introduced in these existing APIs.
CAPLAB-79/84 still require bounded native session/child capture, stable source
sealing and complete native adapter integration before a newly authorized
campaign. This repair processes no historical captures and selects no reviewer.
