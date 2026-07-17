"""Hermetic append-only admission metadata store."""

from __future__ import annotations

from copy import deepcopy
from contextlib import contextmanager
import threading
from collections.abc import Iterator

from caplab.runtime.canonical import canonical_json
from caplab.runtime.errors import OperationConflict


class MemoryAdmissionStore:
    def __init__(self) -> None:
        self.manifests: dict[str, dict[str, object]] = {}
        self._mutex = threading.RLock()
        self._locks: dict[str, threading.RLock] = {}

    @contextmanager
    def object_guard(self, content_sha256: str) -> Iterator[None]:
        with self._mutex:
            lock = self._locks.setdefault(content_sha256, threading.RLock())
        with lock:
            yield

    def freeze(self, manifest: dict[str, object]) -> bool:
        digest = str(manifest["manifest_sha256"])
        current = self.manifests.get(digest)
        if current is not None:
            if canonical_json(current) != canonical_json(manifest):
                raise OperationConflict("admission manifest identity collision")
            return True
        study_id = manifest.get("study_id")
        if any(item.get("study_id") == study_id for item in self.manifests.values()):
            raise OperationConflict(
                "study already has a different frozen admission manifest"
            )
        self.manifests[digest] = deepcopy(manifest)
        return False

    def get(self, manifest_sha256: str) -> dict[str, object] | None:
        current = self.manifests.get(manifest_sha256)
        return None if current is None else deepcopy(current)
