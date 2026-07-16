"""P5-only recovery and guarded-purge orchestration."""

from __future__ import annotations

from datetime import datetime
from typing import Literal, Protocol

from caplab.runtime.canonical import sha256_hex

from .errors import (
    AuthorizationMismatch,
    RecoverySourceMismatch,
    RecoveryTargetMismatch,
)
from .models import P5Authority, PurgeRequest, PurgeTombstone, RecoveryReport


class CustodyByteStore(Protocol):
    def read(self, key: str) -> bytes | None: ...
    def replace(self, key: str, data: bytes) -> None: ...
    def remove(self, key: str) -> None: ...


class GuardedPurgeStore(Protocol):
    def purge(
        self, request: PurgeRequest, *, purged_at: datetime
    ) -> PurgeTombstone: ...


class RecoveryService:
    def __init__(
        self,
        authority: P5Authority,
        objects: CustodyByteStore,
        copies: CustodyByteStore,
    ) -> None:
        self.authority = authority
        self.objects = objects
        self.copies = copies

    def _restore(
        self,
        *,
        source: CustodyByteStore,
        target: CustodyByteStore,
        action: Literal["object-restored", "copy-restored"],
    ) -> RecoveryReport:
        identity = self.authority.identity
        source_bytes = source.read(identity.object_key)
        if source_bytes is None or sha256_hex(source_bytes) != identity.content_sha256:
            raise RecoverySourceMismatch(
                "recovery source does not match frozen content identity"
            )
        target_bytes = target.read(identity.object_key)
        if (
            target_bytes is not None
            and sha256_hex(target_bytes) == identity.content_sha256
        ):
            return RecoveryReport(
                operation_id=identity.operation_id,
                content_sha256=identity.content_sha256,
                action="already-matched",
                source_sha256=identity.content_sha256,
                target_sha256=identity.content_sha256,
            )
        target.replace(identity.object_key, source_bytes)
        readback = target.read(identity.object_key)
        if readback is None or sha256_hex(readback) != identity.content_sha256:
            raise RecoveryTargetMismatch("recovered target failed SHA-256 read-back")
        return RecoveryReport(
            operation_id=identity.operation_id,
            content_sha256=identity.content_sha256,
            action=action,
            source_sha256=identity.content_sha256,
            target_sha256=identity.content_sha256,
        )

    def restore_object(self) -> RecoveryReport:
        return self._restore(
            source=self.copies, target=self.objects, action="object-restored"
        )

    def restore_copy(self) -> RecoveryReport:
        return self._restore(
            source=self.objects, target=self.copies, action="copy-restored"
        )


class PurgeService:
    def __init__(self, authority: P5Authority, store: GuardedPurgeStore) -> None:
        self.authority = authority
        self.store = store

    def purge(self, request: PurgeRequest, *, now: datetime) -> PurgeTombstone:
        self.authority.require_active(now)
        identity = self.authority.identity
        if (
            request.campaign_id != identity.campaign_id
            or request.authorization_sha256 != self.authority.authorization_sha256
            or request.expires_at != self.authority.expires_at
        ):
            raise AuthorizationMismatch(
                "purge request differs from frozen P5 authority"
            )
        if request.operation_id == identity.operation_id and (
            request.request_sha256 != identity.request_sha256
            or request.content_sha256 != identity.content_sha256
            or request.manifest_sha256 != identity.manifest_sha256
        ):
            raise AuthorizationMismatch("purge request differs from frozen P5 identity")
        return self.store.purge(request, purged_at=now)
