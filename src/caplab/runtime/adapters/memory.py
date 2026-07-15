"""Hermetic adapters that exercise the same contracts as live P4 stores."""

from __future__ import annotations

import threading
from copy import deepcopy
from contextlib import contextmanager
from typing import Any, Iterator

from ..errors import CopyMismatch, ObjectMismatch, OperationConflict
from ..models import RegistrationIntent


class MemoryObjectStore:
    def __init__(self) -> None:
        self.objects: dict[str, bytes] = {}
        self.read_count = 0
        self.write_count = 0

    @property
    def effect_count(self) -> int:
        return self.read_count + self.write_count

    def read(self, key: str) -> bytes | None:
        self.read_count += 1
        value = self.objects.get(key)
        return None if value is None else bytes(value)

    def write(self, key: str, data: bytes) -> None:
        existing = self.objects.get(key)
        if existing is not None and existing != data:
            raise ObjectMismatch(f"refusing non-identical object at {key}")
        if existing is None:
            self.objects[key] = bytes(data)
            self.write_count += 1


class MemoryCopyStore:
    def __init__(self) -> None:
        self.copies: dict[str, bytes] = {}
        self.read_count = 0
        self.write_count = 0

    @property
    def effect_count(self) -> int:
        return self.read_count + self.write_count

    def read(self, key: str) -> bytes | None:
        self.read_count += 1
        value = self.copies.get(key)
        return None if value is None else bytes(value)

    def write(self, key: str, data: bytes) -> None:
        existing = self.copies.get(key)
        if existing is not None and existing != data:
            raise CopyMismatch(f"refusing non-identical local copy at {key}")
        if existing is None:
            self.copies[key] = bytes(data)
            self.write_count += 1


class MemoryMetadataStore:
    def __init__(self) -> None:
        self.operations: dict[str, dict[str, Any]] = {}
        self.registrations: dict[str, dict[str, Any]] = {}
        self.events: list[dict[str, Any]] = []
        self.audit_events: list[dict[str, Any]] = []
        self.fail_finalization_once = False
        self._locks: dict[str, threading.RLock] = {}
        self._lock = threading.RLock()

    def claim_operation(self, intent: RegistrationIntent) -> bool:
        with self._lock:
            current = self.operations.get(intent.operation_id)
            if current is not None:
                if current["request_sha256"] != intent.request_sha256:
                    raise OperationConflict(
                        f"operation {intent.operation_id!r} already has a different request"
                    )
                return True
            self.operations[intent.operation_id] = intent.registration_record()
            self.events.append({"operation_id": intent.operation_id, "event_type": "requested"})
            return False

    @contextmanager
    def object_guard(self, content_sha256: str) -> Iterator[None]:
        with self._lock:
            lock = self._locks.setdefault(content_sha256, threading.RLock())
        with lock:
            yield

    def append_event(self, operation_id: str, event_type: str) -> None:
        self.events.append({"operation_id": operation_id, "event_type": event_type})

    def finalize_registration(self, intent: RegistrationIntent) -> dict[str, Any]:
        if self.fail_finalization_once:
            self.fail_finalization_once = False
            raise RuntimeError("injected finalization failure")
        record = intent.registration_record()
        current = self.registrations.get(intent.operation_id)
        if current is not None and current != record:
            raise OperationConflict("completed registration differs from retry")
        self.registrations[intent.operation_id] = record
        self.events.append({"operation_id": intent.operation_id, "event_type": "registered"})
        self.audit_events.append(
            {
                "operation_id": intent.operation_id,
                "event_type": "registration-completed",
                "event_body": {
                    "content_sha256": intent.content_sha256,
                    "manifest_sha256": intent.manifest_sha256,
                },
            }
        )
        return dict(record)

    def registration_for_operation(self, operation_id: str) -> dict[str, Any] | None:
        record = self.registrations.get(operation_id)
        return None if record is None else deepcopy(record)

    def operation_for_operation(self, operation_id: str) -> dict[str, Any] | None:
        record = self.operations.get(operation_id)
        return None if record is None else deepcopy(record)
