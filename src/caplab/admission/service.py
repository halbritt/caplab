"""Registration and reconciliation of one frozen Study 001 evidence set."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol
from typing import Any

from caplab.runtime.canonical import canonical_json, sha256_hex
from caplab.runtime.errors import CopyMismatch, MetadataMismatch, ObjectMismatch

from .models import SourceSet
from .source import GitReader, build_manifest, read_record_bytes


class ByteStore(Protocol):
    def read(self, key: str) -> bytes | None: ...
    def write(self, key: str, data: bytes) -> None: ...


class AdmissionMetadataStore(Protocol):
    def object_guard(self, content_sha256: str) -> Any: ...
    def freeze(self, manifest: dict[str, object]) -> bool: ...
    def get(self, manifest_sha256: str) -> dict[str, object] | None: ...


@dataclass(frozen=True, slots=True)
class AdmissionReceipt:
    study_id: str
    manifest_sha256: str
    record_count: int
    unique_content_count: int
    idempotent_replay: bool


@dataclass(frozen=True, slots=True)
class AdmissionVerification:
    manifest_sha256: str
    metadata_status: str
    object_status: str
    local_copy_status: str
    record_count: int
    unique_content_count: int

    @property
    def ok(self) -> bool:
        return (
            self.metadata_status == "match"
            and self.object_status == "match"
            and self.local_copy_status == "match"
        )


def _validate_manifest(manifest: dict[str, object]) -> None:
    retained = manifest.get("manifest_sha256")
    body = {key: value for key, value in manifest.items() if key != "manifest_sha256"}
    if not isinstance(retained, str) or sha256_hex(canonical_json(body)) != retained:
        raise MetadataMismatch("admission manifest differs from its content identity")
    records = manifest.get("records")
    if not isinstance(records, list) or not records:
        raise MetadataMismatch("admission manifest has no evidence records")
    ids = [record.get("record_id") for record in records if isinstance(record, dict)]
    if len(ids) != len(records) or len(set(ids)) != len(ids):
        raise MetadataMismatch("admission evidence record identities are invalid")


class AdmissionService:
    def __init__(
        self,
        metadata: AdmissionMetadataStore,
        objects: ByteStore,
        copies: ByteStore,
    ) -> None:
        self.metadata = metadata
        self.objects = objects
        self.copies = copies

    @staticmethod
    def _write_verified(
        store: ByteStore,
        key: str,
        payload: bytes,
        digest: str,
        mismatch: type[ObjectMismatch] | type[CopyMismatch],
    ) -> bool:
        retained = store.read(key)
        replay = retained is not None
        if retained is not None and retained != payload:
            raise mismatch(f"retained bytes differ at {key}")
        if retained is None:
            store.write(key, payload)
        readback = store.read(key)
        if readback is None or sha256_hex(readback) != digest:
            raise mismatch(f"readback failed at {key}")
        return replay

    def admit(self, source: SourceSet, *, git_reader: GitReader) -> AdmissionReceipt:
        prepared = build_manifest(source, git_reader=git_reader)
        _validate_manifest(prepared)
        payloads: dict[str, bytes] = {}
        records = prepared["records"]
        assert isinstance(records, list)
        for record in records:
            assert isinstance(record, dict)
            digest = str(record["content_sha256"])
            payload = read_record_bytes(source, record, git_reader=git_reader)
            current = payloads.setdefault(digest, payload)
            if current != payload:
                raise MetadataMismatch(
                    "one content identity names different source bytes"
                )
        replay = True
        by_digest = {
            str(record["content_sha256"]): record
            for record in records
            if isinstance(record, dict)
        }
        for digest, payload in payloads.items():
            record = by_digest[digest]
            key = str(record["object_key"])
            with self.metadata.object_guard(digest):
                object_replay = self._write_verified(
                    self.objects, key, payload, digest, ObjectMismatch
                )
                copy_replay = self._write_verified(
                    self.copies, key, payload, digest, CopyMismatch
                )
            replay = replay and object_replay and copy_replay
        revalidated = build_manifest(source, git_reader=git_reader)
        if canonical_json(revalidated) != canonical_json(prepared):
            raise MetadataMismatch("source set changed before admission freeze")
        for digest, record in by_digest.items():
            key = str(record["object_key"])
            object_bytes = self.objects.read(key)
            copy_bytes = self.copies.read(key)
            if object_bytes is None or sha256_hex(object_bytes) != digest:
                raise ObjectMismatch(f"object reconciliation failed at {key}")
            if copy_bytes is None or sha256_hex(copy_bytes) != digest:
                raise CopyMismatch(f"local-copy reconciliation failed at {key}")
        metadata_replay = self.metadata.freeze(prepared)
        summary = prepared["summary"]
        assert isinstance(summary, dict)
        return AdmissionReceipt(
            study_id=str(prepared["study_id"]),
            manifest_sha256=str(prepared["manifest_sha256"]),
            record_count=int(summary["record_count"]),
            unique_content_count=int(summary["unique_content_count"]),
            idempotent_replay=metadata_replay or replay,
        )

    def verify(self, manifest_sha256: str) -> AdmissionVerification:
        manifest = self.metadata.get(manifest_sha256)
        if manifest is None:
            raise MetadataMismatch("admission manifest is not registered")
        _validate_manifest(manifest)
        records = manifest["records"]
        assert isinstance(records, list)
        by_digest = {
            str(record["content_sha256"]): record
            for record in records
            if isinstance(record, dict)
        }
        object_status = "match"
        local_status = "match"
        for digest, record in by_digest.items():
            key = str(record["object_key"])
            object_bytes = self.objects.read(key)
            copy_bytes = self.copies.read(key)
            if object_bytes is None or sha256_hex(object_bytes) != digest:
                object_status = "mismatch"
            if copy_bytes is None or sha256_hex(copy_bytes) != digest:
                local_status = "mismatch"
        return AdmissionVerification(
            manifest_sha256=manifest_sha256,
            metadata_status="match",
            object_status=object_status,
            local_copy_status=local_status,
            record_count=len(records),
            unique_content_count=len(by_digest),
        )
