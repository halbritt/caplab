"""Hermetic P5 custody adapters."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from typing import Any, Mapping

from ..errors import AuthorizationMismatch, DependencyRetained, UnknownPurgeIdentity
from ..models import P5_CAMPAIGN_ID, PurgeRequest, PurgeTombstone


class MemoryCustodyStore:
    def __init__(self) -> None:
        self.values: dict[str, bytes] = {}

    def read(self, key: str) -> bytes | None:
        value = self.values.get(key)
        return None if value is None else bytes(value)

    def replace(self, key: str, data: bytes) -> None:
        self.values[key] = bytes(data)

    def remove(self, key: str) -> None:
        self.values.pop(key, None)

    def keys(self) -> set[str]:
        return set(self.values)


class MemoryPurgeStore:
    def __init__(self) -> None:
        self.operations: dict[str, dict[str, Any]] = {}
        self.registrations: dict[str, dict[str, Any]] = {}
        self.dependencies: dict[str, set[str]] = {}
        self.tombstones: dict[str, PurgeTombstone] = {}

    def add_registration(self, record: Mapping[str, Any]) -> None:
        owned = deepcopy(dict(record))
        operation_id = str(owned["operation_id"])
        self.operations[operation_id] = deepcopy(owned)
        self.registrations[operation_id] = owned

    def snapshot(self) -> dict[str, Any]:
        return {
            "operations": deepcopy(self.operations),
            "registrations": deepcopy(self.registrations),
            "dependencies": deepcopy(self.dependencies),
            "tombstones": dict(self.tombstones),
        }

    def purge(self, request: PurgeRequest, *, purged_at: datetime) -> PurgeTombstone:
        record = self.registrations.get(request.operation_id)
        operation = self.operations.get(request.operation_id)
        if record is None or operation is None:
            raise UnknownPurgeIdentity("no live registration matches the purge request")
        expected = {
            "campaign_id": request.campaign_id,
            "request_sha256": request.request_sha256,
            "content_sha256": request.content_sha256,
            "manifest_sha256": request.manifest_sha256,
        }
        if request.campaign_id != P5_CAMPAIGN_ID or any(
            record.get(field) != value for field, value in expected.items()
        ):
            raise AuthorizationMismatch(
                "live registration differs from the purge request"
            )
        retained = self.dependencies.get(request.operation_id, set())
        if retained:
            raise DependencyRetained(
                f"retained dependencies prevent purge: {sorted(retained)!r}"
            )

        tombstone = PurgeTombstone(
            custody_request_id=request.custody_request_id,
            operation_id=request.operation_id,
            campaign_id=request.campaign_id,
            request_sha256=request.request_sha256,
            content_sha256=request.content_sha256,
            manifest_sha256=request.manifest_sha256,
            authorization_sha256=request.authorization_sha256,
            purged_at=purged_at,
        )
        next_operations = deepcopy(self.operations)
        next_registrations = deepcopy(self.registrations)
        next_tombstones = dict(self.tombstones)
        del next_operations[request.operation_id]
        del next_registrations[request.operation_id]
        next_tombstones[request.operation_id] = tombstone
        self.operations = next_operations
        self.registrations = next_registrations
        self.tombstones = next_tombstones
        return tombstone
