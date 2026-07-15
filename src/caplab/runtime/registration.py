"""The deep registration contract shared by hermetic and live adapters."""

from __future__ import annotations

from typing import Any, Protocol

from .canonical import canonical_json, sha256_hex
from .custody import build_cleanup_plan
from .errors import (
    CopyMismatch,
    LocatorMismatch,
    MetadataMismatch,
    ObjectMismatch,
    RegistrationMissing,
)
from .models import (
    RegistrationIntent,
    RegistrationReceipt,
    RegistrationRequest,
    ReconciliationReport,
    object_key,
)


class ByteStore(Protocol):
    def read(self, key: str) -> bytes | None: ...
    def write(self, key: str, data: bytes) -> None: ...


class MetadataStore(Protocol):
    def claim_operation(self, intent: RegistrationIntent) -> bool: ...
    def object_guard(self, content_sha256: str) -> Any: ...
    def append_event(self, operation_id: str, event_type: str) -> None: ...
    def finalize_registration(self, intent: RegistrationIntent) -> dict[str, Any]: ...
    def registration_for_operation(self, operation_id: str) -> dict[str, Any] | None: ...
    def operation_for_operation(self, operation_id: str) -> dict[str, Any] | None: ...


class RegistrationService:
    def __init__(self, metadata: MetadataStore, objects: ByteStore, copies: ByteStore) -> None:
        self.metadata = metadata
        self.objects = objects
        self.copies = copies

    def register(self, request: RegistrationRequest) -> RegistrationReceipt:
        intent = request.intent()
        operation_replay = self.metadata.claim_operation(intent)
        with self.metadata.object_guard(intent.content_sha256):
            completed = self.metadata.registration_for_operation(intent.operation_id)
            if completed is not None:
                self._validate_record(completed)
                self._validate_intent_record(intent, completed)
                self._verify_bytes(completed)
                return RegistrationReceipt.from_record(completed, idempotent_replay=True)

            object_replay = self._store(
                self.objects,
                intent,
                mismatch=ObjectMismatch,
                event_type="object-verified",
            )
            copy_replay = self._store(
                self.copies,
                intent,
                mismatch=CopyMismatch,
                event_type="local-copy-verified",
            )
            record = self.metadata.finalize_registration(intent)
            self._validate_record(record)
            self._validate_intent_record(intent, record)
            return RegistrationReceipt.from_record(
                record,
                idempotent_replay=operation_replay or object_replay or copy_replay,
            )

    def _store(
        self,
        store: ByteStore,
        intent: RegistrationIntent,
        *,
        mismatch: type[ObjectMismatch] | type[CopyMismatch],
        event_type: str,
    ) -> bool:
        existing = store.read(intent.object_key)
        replay = existing is not None
        if existing is not None and existing != intent.payload:
            raise mismatch(f"bytes at {intent.object_key} do not match the request")
        if existing is None:
            store.write(intent.object_key, intent.payload)
        readback = store.read(intent.object_key)
        if readback is None or sha256_hex(readback) != intent.content_sha256:
            raise mismatch(f"readback at {intent.object_key} failed SHA-256 verification")
        self.metadata.append_event(intent.operation_id, event_type)
        return replay

    def _record(self, operation_id: str) -> dict[str, Any]:
        record = self.metadata.registration_for_operation(operation_id)
        if record is None:
            raise RegistrationMissing(f"operation {operation_id!r} is not registered")
        self._validate_record(record)
        return record

    @staticmethod
    def _validate_record(record: dict[str, Any]) -> None:
        expected = object_key(record["content_sha256"])
        if record["object_key"] != expected or record["local_copy_key"] != expected:
            raise LocatorMismatch("retained locator differs from the content-derived locator")
        manifest = record.get("manifest")
        if manifest is not None:
            if sha256_hex(canonical_json(manifest)) != record["manifest_sha256"]:
                raise MetadataMismatch("manifest bytes differ from the registered identity")
            artifact = manifest.get("artifact") if isinstance(manifest, dict) else None
            if not isinstance(artifact, dict):
                raise MetadataMismatch("manifest artifact contract is absent")
            if (
                artifact.get("content_sha256") != record["content_sha256"]
                or artifact.get("object_key") != expected
                or artifact.get("byte_count") != record.get("byte_count")
                or manifest.get("identity_sha256") != record.get("identity_sha256")
            ):
                raise MetadataMismatch("manifest and registration metadata disagree")
            provenance = manifest.get("runtime_provenance")
            migration_state = record.get("migration_state")
            if provenance is not None and migration_state is not None:
                if not isinstance(provenance, dict):
                    raise MetadataMismatch("runtime provenance is not an object")
                expected_migrations = provenance.get("migrations")
                if expected_migrations != [
                    {"filename": item["filename"], "sha256": item["sha256"]}
                    for item in migration_state
                ]:
                    raise MetadataMismatch("migration ledger differs from runtime provenance")
                if any(
                    item["runtime_commit"] != provenance.get("runtime_commit")
                    for item in migration_state
                ):
                    raise MetadataMismatch("migration runtime commit differs from provenance")

    @staticmethod
    def _validate_intent_record(
        intent: RegistrationIntent, record: dict[str, Any]
    ) -> None:
        expected = intent.registration_record()
        for field in (
            "campaign_id",
            "request_sha256",
            "content_sha256",
            "object_key",
            "local_copy_key",
            "manifest_sha256",
            "identity_sha256",
        ):
            if record.get(field) != expected[field]:
                raise MetadataMismatch(f"completed registration differs at {field}")

    def _verified_payload(self, record: dict[str, Any]) -> bytes:
        content_sha256 = record["content_sha256"]
        key = record["object_key"]
        object_bytes = self.objects.read(key)
        if object_bytes is None or sha256_hex(object_bytes) != content_sha256:
            raise ObjectMismatch("object is missing or does not match its registered SHA-256")
        copy_bytes = self.copies.read(key)
        if copy_bytes is None or sha256_hex(copy_bytes) != content_sha256:
            raise CopyMismatch("local copy is missing or does not match its registered SHA-256")
        return object_bytes

    def _verify_bytes(self, record: dict[str, Any]) -> None:
        self._verified_payload(record)

    def verify(self, operation_id: str) -> RegistrationReceipt:
        record = self._record(operation_id)
        self._verify_bytes(record)
        return RegistrationReceipt.from_record(record, idempotent_replay=True)

    def retrieve(self, operation_id: str) -> bytes:
        record = self._record(operation_id)
        return self._verified_payload(record)

    def reconcile(
        self,
        operation_id: str,
        *,
        expected_runtime_provenance: dict[str, Any] | None = None,
    ) -> ReconciliationReport:
        record = self.metadata.registration_for_operation(operation_id)
        registration_complete = record is not None
        if record is None:
            record = self.metadata.operation_for_operation(operation_id)
        if record is None:
            raise RegistrationMissing(f"operation {operation_id!r} is not registered")
        content_sha256 = record["content_sha256"]
        expected_key = object_key(content_sha256)
        locator_status = (
            "match"
            if record.get("object_key") == expected_key
            and record.get("local_copy_key") == expected_key
            else "mismatch"
        )
        object_status = self._byte_status(self.objects, expected_key, content_sha256)
        copy_status = self._byte_status(self.copies, expected_key, content_sha256)
        if not registration_complete:
            metadata_status = "incomplete"
        else:
            try:
                self._validate_record(record)
                metadata_status = "match"
            except (LocatorMismatch, MetadataMismatch):
                metadata_status = "mismatch"
        retained_provenance = record.get("manifest", {}).get("runtime_provenance")
        if retained_provenance is None and expected_runtime_provenance is None:
            provenance_status = "not-applicable"
        elif expected_runtime_provenance is None:
            provenance_status = "unchecked"
        elif canonical_json(retained_provenance) == canonical_json(expected_runtime_provenance):
            provenance_status = "match"
        else:
            provenance_status = "mismatch"
        return ReconciliationReport(
            operation_id=operation_id,
            content_sha256=content_sha256,
            object_status=object_status,
            local_copy_status=copy_status,
            metadata_status=metadata_status,
            locator_status=locator_status,
            provenance_status=provenance_status,
        )

    def cleanup_plan(self, operation_id: str) -> dict[str, Any]:
        record = self.metadata.registration_for_operation(operation_id)
        registration_status = "complete"
        if record is None:
            record = self.metadata.operation_for_operation(operation_id)
            registration_status = "incomplete"
        if record is None:
            raise RegistrationMissing(f"operation {operation_id!r} has no durable request")
        return build_cleanup_plan(record, registration_status=registration_status)

    @staticmethod
    def _byte_status(store: ByteStore, key: str, content_sha256: str) -> str:
        payload = store.read(key)
        if payload is None:
            return "missing"
        return "match" if sha256_hex(payload) == content_sha256 else "mismatch"
