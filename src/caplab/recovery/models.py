"""Validated value objects for the bounded CAPLAB P5 campaign."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from types import MappingProxyType
from typing import Any, Literal, Mapping

from caplab.runtime.canonical import sha256_hex
from caplab.runtime.models import (
    IDENTIFIER,
    IDENTITY_LAYERS,
    SHA256,
    RegistrationIntent,
    object_key,
)


P5_CAMPAIGN_ID = "caplab-p5-recovery-2026-07-16"
P5_AUTHORIZATION_EXPIRES_AT = datetime(2026, 7, 23, 23, 59, 59, tzinfo=UTC)
InvalidDisposition = Literal["invalid", "ambiguous"]


def _require_identifier(label: str, value: str) -> None:
    if not IDENTIFIER.fullmatch(value):
        raise ValueError(f"{label} is not a bounded lowercase identifier")


def _require_sha256(label: str, value: str) -> None:
    if not SHA256.fullmatch(value):
        raise ValueError(f"{label} must be 64 lowercase hexadecimal characters")


def _require_utc(label: str, value: datetime) -> None:
    if value.tzinfo is None or value.utcoffset() != UTC.utcoffset(value):
        raise ValueError(f"{label} must be timezone-aware UTC")


@dataclass(frozen=True, slots=True)
class P5Identity:
    operation_id: str
    campaign_id: str
    request_sha256: str
    content_sha256: str
    object_key: str
    manifest_sha256: str
    identity_sha256: Mapping[str, str]

    def __post_init__(self) -> None:
        _require_identifier("operation_id", self.operation_id)
        if self.campaign_id != P5_CAMPAIGN_ID:
            raise ValueError("P5 identity uses an unauthorized campaign")
        for label, value in (
            ("request_sha256", self.request_sha256),
            ("content_sha256", self.content_sha256),
            ("manifest_sha256", self.manifest_sha256),
        ):
            _require_sha256(label, value)
        if self.object_key != object_key(self.content_sha256):
            raise ValueError("object_key differs from the content-derived locator")
        if set(self.identity_sha256) != set(IDENTITY_LAYERS):
            raise ValueError(
                f"identity_sha256 must contain exactly {IDENTITY_LAYERS!r}"
            )
        owned = dict(self.identity_sha256)
        for layer, value in owned.items():
            _require_sha256(f"identity_sha256[{layer!r}]", value)
        object.__setattr__(self, "identity_sha256", MappingProxyType(owned))

    @classmethod
    def from_intent(cls, intent: RegistrationIntent) -> "P5Identity":
        return cls(
            operation_id=intent.operation_id,
            campaign_id=intent.campaign_id,
            request_sha256=intent.request_sha256,
            content_sha256=intent.content_sha256,
            object_key=intent.object_key,
            manifest_sha256=intent.manifest_sha256,
            identity_sha256=intent.identity_sha256,
        )

    def require_record(self, record: Mapping[str, Any]) -> None:
        expected: dict[str, Any] = {
            "operation_id": self.operation_id,
            "campaign_id": self.campaign_id,
            "request_sha256": self.request_sha256,
            "content_sha256": self.content_sha256,
            "object_key": self.object_key,
            "local_copy_key": self.object_key,
            "manifest_sha256": self.manifest_sha256,
            "identity_sha256": dict(self.identity_sha256),
        }
        for field, value in expected.items():
            retained = record.get(field)
            if retained != value:
                raise ValueError(
                    f"registration differs from frozen P5 identity at {field}"
                )


@dataclass(frozen=True, slots=True)
class P5Authority:
    identity: P5Identity
    authorization_sha256: str
    expires_at: datetime

    def __post_init__(self) -> None:
        _require_sha256("authorization_sha256", self.authorization_sha256)
        _require_utc("expires_at", self.expires_at)
        if self.expires_at != P5_AUTHORIZATION_EXPIRES_AT:
            raise ValueError("P5 authority expiry differs from ADR 0009")

    def require_active(self, now: datetime) -> None:
        from .errors import AuthorizationExpired

        _require_utc("now", now)
        if now >= self.expires_at:
            raise AuthorizationExpired("CAPLAB P5 authorization has expired")


@dataclass(frozen=True, slots=True)
class RecoveryReport:
    operation_id: str
    content_sha256: str
    action: Literal["object-restored", "copy-restored", "already-matched"]
    source_sha256: str
    target_sha256: str


@dataclass(frozen=True, slots=True)
class InvalidAttemptObservation:
    observation_id: str
    campaign_id: str
    fixture_sha256: str
    fixture_byte_count: int
    disposition: InvalidDisposition
    reason_codes: tuple[str, ...]

    def to_record(self) -> dict[str, Any]:
        return {
            "schema_version": "caplab-invalid-attempt-observation/1",
            "observation_id": self.observation_id,
            "campaign_id": self.campaign_id,
            "fixture_sha256": self.fixture_sha256,
            "fixture_byte_count": self.fixture_byte_count,
            "disposition": self.disposition,
            "reason_codes": list(self.reason_codes),
        }


def observe_invalid_attempt(
    *,
    observation_id: str,
    campaign_id: str,
    fixture_bytes: bytes,
    disposition: str,
    reason_codes: tuple[str, ...],
) -> InvalidAttemptObservation:
    _require_identifier("observation_id", observation_id)
    if campaign_id != P5_CAMPAIGN_ID:
        raise ValueError("invalid-attempt observation uses an unauthorized campaign")
    if not isinstance(fixture_bytes, bytes) or not fixture_bytes:
        raise ValueError("fixture_bytes must be non-empty bytes")
    if disposition not in {"invalid", "ambiguous"}:
        raise ValueError("disposition must be invalid or ambiguous")
    if not reason_codes or any(not IDENTIFIER.fullmatch(code) for code in reason_codes):
        raise ValueError("reason_codes must contain bounded lowercase identifiers")
    return InvalidAttemptObservation(
        observation_id=observation_id,
        campaign_id=campaign_id,
        fixture_sha256=sha256_hex(fixture_bytes),
        fixture_byte_count=len(fixture_bytes),
        disposition=disposition,
        reason_codes=tuple(reason_codes),
    )


@dataclass(frozen=True, slots=True)
class OrphanInventory:
    incomplete_requests: tuple[str, ...]
    unreferenced_objects: tuple[str, ...]
    unreferenced_copies: tuple[str, ...]
    registered_dependencies: Mapping[str, tuple[str, ...]]


def build_orphan_inventory(
    *,
    operations: Mapping[str, Mapping[str, Any]],
    registrations: Mapping[str, Mapping[str, Any]],
    object_keys: set[str],
    copy_keys: set[str],
    dependencies: Mapping[str, tuple[str, ...]],
) -> OrphanInventory:
    incomplete = tuple(sorted(set(operations) - set(registrations)))
    referenced_objects = {
        str(record["object_key"]) for record in registrations.values()
    }
    referenced_copies = {
        str(record["local_copy_key"]) for record in registrations.values()
    }
    retained = {
        operation_id: tuple(sorted(items))
        for operation_id, items in sorted(dependencies.items())
        if operation_id in registrations and items
    }
    return OrphanInventory(
        incomplete_requests=incomplete,
        unreferenced_objects=tuple(sorted(object_keys - referenced_objects)),
        unreferenced_copies=tuple(sorted(copy_keys - referenced_copies)),
        registered_dependencies=MappingProxyType(retained),
    )


@dataclass(frozen=True, slots=True)
class PurgeRequest:
    custody_request_id: str
    operation_id: str
    campaign_id: str
    request_sha256: str
    content_sha256: str
    manifest_sha256: str
    authorization_sha256: str
    expires_at: datetime

    def __post_init__(self) -> None:
        _require_identifier("custody_request_id", self.custody_request_id)
        _require_identifier("operation_id", self.operation_id)
        for label, value in (
            ("request_sha256", self.request_sha256),
            ("content_sha256", self.content_sha256),
            ("manifest_sha256", self.manifest_sha256),
            ("authorization_sha256", self.authorization_sha256),
        ):
            _require_sha256(label, value)
        _require_utc("expires_at", self.expires_at)


@dataclass(frozen=True, slots=True)
class PurgeTombstone:
    custody_request_id: str
    operation_id: str
    campaign_id: str
    request_sha256: str
    content_sha256: str
    manifest_sha256: str
    authorization_sha256: str
    purged_at: datetime
