"""Validated value objects for one synthetic registration."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping

from .canonical import canonical_json, sha256_hex


IDENTIFIER = re.compile(r"\A[a-z][a-z0-9-]{2,127}\Z")
SHA256 = re.compile(r"\A[0-9a-f]{64}\Z")
IDENTITY_LAYERS = (
    "model",
    "agent_configuration",
    "administration",
    "trial_context",
    "trial_assignment",
    "attempt",
    "analysis",
)


def _freeze(value: Any) -> Any:
    if isinstance(value, dict):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    return value


def _plain(value: Any) -> Any:
    return json.loads(canonical_json(value).decode("utf-8"))


def object_key(content_sha256: str) -> str:
    if not SHA256.fullmatch(content_sha256):
        raise ValueError("content SHA-256 must be 64 lowercase hexadecimal characters")
    return f"objects/sha256/{content_sha256[:2]}/{content_sha256}"


@dataclass(frozen=True, slots=True)
class RegistrationIntent:
    operation_id: str
    campaign_id: str
    artifact_kind: str
    media_type: str
    payload: bytes
    content_sha256: str
    object_key: str
    identity_layers: Mapping[str, Mapping[str, Any]]
    identity_sha256: Mapping[str, str]
    manifest: Mapping[str, Any]
    manifest_sha256: str
    request_sha256: str

    def registration_record(self) -> dict[str, Any]:
        return {
            "operation_id": self.operation_id,
            "campaign_id": self.campaign_id,
            "artifact_kind": self.artifact_kind,
            "media_type": self.media_type,
            "byte_count": len(self.payload),
            "content_sha256": self.content_sha256,
            "object_key": self.object_key,
            "local_copy_key": self.object_key,
            "identity_sha256": dict(self.identity_sha256),
            "identity_layers": _plain(self.identity_layers),
            "manifest": _plain(self.manifest),
            "manifest_sha256": self.manifest_sha256,
            "request_sha256": self.request_sha256,
        }


@dataclass(frozen=True, slots=True)
class RegistrationRequest:
    operation_id: str
    campaign_id: str
    artifact_kind: str
    media_type: str
    identity_layers: Mapping[str, Mapping[str, Any]]
    payload: bytes
    runtime_provenance: Mapping[str, Any] | None = None

    def __post_init__(self) -> None:
        for label, value in (
            ("operation_id", self.operation_id),
            ("campaign_id", self.campaign_id),
            ("artifact_kind", self.artifact_kind),
        ):
            if not IDENTIFIER.fullmatch(value):
                raise ValueError(f"{label} is not a bounded lowercase identifier")
        if not isinstance(self.media_type, str) or not self.media_type or len(self.media_type) > 127:
            raise ValueError("media_type must be a non-empty bounded string")
        if not isinstance(self.payload, bytes):
            raise TypeError("payload must be bytes")
        if not self.payload:
            raise ValueError("payload must not be empty")
        if set(self.identity_layers) != set(IDENTITY_LAYERS):
            raise ValueError(f"identity_layers must contain exactly {IDENTITY_LAYERS!r}")

        owned = json.loads(canonical_json(self.identity_layers).decode("utf-8"))
        for layer in IDENTITY_LAYERS:
            if not isinstance(owned[layer], dict) or not owned[layer]:
                raise ValueError(f"identity layer {layer!r} must be a non-empty object")
        object.__setattr__(self, "identity_layers", _freeze(owned))
        object.__setattr__(self, "payload", bytes(self.payload))
        if self.runtime_provenance is not None:
            provenance = _plain(self.runtime_provenance)
            if not isinstance(provenance, dict) or not provenance:
                raise ValueError("runtime_provenance must be a non-empty object")
            object.__setattr__(self, "runtime_provenance", _freeze(provenance))

    def intent(self) -> RegistrationIntent:
        content_sha256 = sha256_hex(self.payload)
        identity_sha256 = {
            layer: sha256_hex(canonical_json(self.identity_layers[layer]))
            for layer in IDENTITY_LAYERS
        }
        manifest = {
            "schema_version": "caplab-registration-manifest/1",
            "campaign_id": self.campaign_id,
            "artifact": {
                "kind": self.artifact_kind,
                "media_type": self.media_type,
                "byte_count": len(self.payload),
                "content_sha256": content_sha256,
                "object_key": object_key(content_sha256),
            },
            "identity_sha256": identity_sha256,
        }
        if self.runtime_provenance is not None:
            manifest["runtime_provenance"] = _plain(self.runtime_provenance)
        manifest_sha256 = sha256_hex(canonical_json(manifest))
        request_body = {
            "operation_id": self.operation_id,
            "campaign_id": self.campaign_id,
            "artifact_kind": self.artifact_kind,
            "media_type": self.media_type,
            "content_sha256": content_sha256,
            "manifest_sha256": manifest_sha256,
            "identity_sha256": identity_sha256,
        }
        return RegistrationIntent(
            operation_id=self.operation_id,
            campaign_id=self.campaign_id,
            artifact_kind=self.artifact_kind,
            media_type=self.media_type,
            payload=self.payload,
            content_sha256=content_sha256,
            object_key=object_key(content_sha256),
            identity_layers=self.identity_layers,
            identity_sha256=MappingProxyType(identity_sha256),
            manifest=_freeze(manifest),
            manifest_sha256=manifest_sha256,
            request_sha256=sha256_hex(canonical_json(request_body)),
        )


@dataclass(frozen=True, slots=True)
class RegistrationReceipt:
    operation_id: str
    campaign_id: str
    request_sha256: str
    content_sha256: str
    object_key: str
    manifest_sha256: str
    identity_sha256: Mapping[str, str]
    idempotent_replay: bool

    @classmethod
    def from_record(cls, record: Mapping[str, Any], *, idempotent_replay: bool) -> "RegistrationReceipt":
        return cls(
            operation_id=record["operation_id"],
            campaign_id=record["campaign_id"],
            request_sha256=record["request_sha256"],
            content_sha256=record["content_sha256"],
            object_key=record["object_key"],
            manifest_sha256=record["manifest_sha256"],
            identity_sha256=MappingProxyType(dict(record["identity_sha256"])),
            idempotent_replay=idempotent_replay,
        )


@dataclass(frozen=True, slots=True)
class ReconciliationReport:
    operation_id: str
    content_sha256: str
    object_status: str
    local_copy_status: str
    metadata_status: str
    locator_status: str
    provenance_status: str

    @property
    def ok(self) -> bool:
        core_matches = all(
            status == "match"
            for status in (
                self.object_status,
                self.local_copy_status,
                self.metadata_status,
                self.locator_status,
            )
        )
        return core_matches and self.provenance_status in {"match", "not-applicable"}
