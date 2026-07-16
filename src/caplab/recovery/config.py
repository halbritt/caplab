"""Fail-closed P5 campaign configuration, separate from the P4 runtime."""

from __future__ import annotations

import grp
import os
import stat
import tomllib
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlparse

from caplab.runtime.config import COMMIT, ConfigurationError
from caplab.runtime.models import IDENTITY_LAYERS

from .models import (
    P5_AUTHORIZATION_EXPIRES_AT,
    P5_CAMPAIGN_ID,
    P5Authority,
    P5Identity,
)


P5_POSTGRES = {"dbname": "caplab", "host": "/var/run/postgresql"}
P5_GARAGE_ENDPOINT = "http://127.0.0.1:3900"
P5_GARAGE_REGION = "garage"
P5_GARAGE_BUCKET = "caplab-v0"
P5_CREDENTIALS_ROOT = Path("/etc/caplab-p5/credentials")
P5_LOCAL_COPY_ROOT = Path("/nvr/caplab/v0")
P5_CONFIG_PATH = Path("/etc/caplab-p5/recovery.toml")
P5_CONFIG_GROUP = "caplab-p5"
MAX_CONFIG_BYTES = 32_768


def _exact_keys(value: dict[str, object], expected: set[str], label: str) -> None:
    if set(value) != expected:
        raise ConfigurationError(
            f"{label} fields must be exactly {sorted(expected)!r}; got {sorted(value)!r}"
        )


def _required_string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ConfigurationError(f"{label} must be a non-empty string")
    return value


@dataclass(frozen=True, slots=True)
class RecoveryConfig:
    authority: P5Authority
    runtime_commit: str
    postgres_conninfo: str
    garage_endpoint_url: str
    garage_region: str
    garage_bucket: str
    credentials_root: Path
    local_copy_root: Path

    @classmethod
    def from_toml(cls, path: Path) -> "RecoveryConfig":
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            raise ConfigurationError(
                f"cannot load P5 recovery configuration: {error}"
            ) from error
        return cls._from_text(text)

    @classmethod
    def _from_text(cls, text: str) -> "RecoveryConfig":
        try:
            document = tomllib.loads(text)
        except tomllib.TOMLDecodeError as error:
            raise ConfigurationError(
                f"cannot load P5 recovery configuration: {error}"
            ) from error
        _exact_keys(
            document,
            {"campaign", "identity", "postgres", "garage", "local_copy"},
            "root",
        )
        for section in document.values():
            if not isinstance(section, dict):
                raise ConfigurationError(
                    "every P5 configuration section must be a table"
                )

        campaign = document["campaign"]
        identity = document["identity"]
        postgres = document["postgres"]
        garage = document["garage"]
        local_copy = document["local_copy"]
        _exact_keys(
            campaign,
            {
                "campaign_id",
                "authorization_expires_at",
                "authorization_sha256",
                "runtime_commit",
            },
            "campaign",
        )
        _exact_keys(
            identity,
            {
                "operation_id",
                "request_sha256",
                "content_sha256",
                "object_key",
                "manifest_sha256",
                "identity_sha256",
            },
            "identity",
        )
        _exact_keys(postgres, {"conninfo"}, "postgres")
        _exact_keys(
            garage,
            {"endpoint_url", "region", "bucket", "credentials_root"},
            "garage",
        )
        _exact_keys(local_copy, {"root"}, "local_copy")

        campaign_id = _required_string(campaign["campaign_id"], "campaign.campaign_id")
        if campaign_id != P5_CAMPAIGN_ID:
            raise ConfigurationError("campaign differs from the authorized P5 campaign")
        expiry_text = _required_string(
            campaign["authorization_expires_at"],
            "campaign.authorization_expires_at",
        )
        if expiry_text != "2026-07-23T23:59:59Z":
            raise ConfigurationError("authorization expiry differs from ADR 0009")
        runtime_commit = _required_string(
            campaign["runtime_commit"], "campaign.runtime_commit"
        )
        if not COMMIT.fullmatch(runtime_commit):
            raise ConfigurationError(
                "campaign.runtime_commit must be a full Git identity"
            )

        identity_hashes = identity["identity_sha256"]
        if not isinstance(identity_hashes, dict) or set(identity_hashes) != set(
            IDENTITY_LAYERS
        ):
            raise ConfigurationError(
                f"identity.identity_sha256 must contain exactly {IDENTITY_LAYERS!r}"
            )
        try:
            frozen_identity = P5Identity(
                operation_id=_required_string(
                    identity["operation_id"], "identity.operation_id"
                ),
                campaign_id=campaign_id,
                request_sha256=_required_string(
                    identity["request_sha256"], "identity.request_sha256"
                ),
                content_sha256=_required_string(
                    identity["content_sha256"], "identity.content_sha256"
                ),
                object_key=_required_string(
                    identity["object_key"], "identity.object_key"
                ),
                manifest_sha256=_required_string(
                    identity["manifest_sha256"], "identity.manifest_sha256"
                ),
                identity_sha256={
                    layer: _required_string(
                        identity_hashes[layer],
                        f"identity.identity_sha256.{layer}",
                    )
                    for layer in IDENTITY_LAYERS
                },
            )
            authority = P5Authority(
                identity=frozen_identity,
                authorization_sha256=_required_string(
                    campaign["authorization_sha256"],
                    "campaign.authorization_sha256",
                ),
                expires_at=P5_AUTHORIZATION_EXPIRES_AT,
            )
        except ValueError as error:
            raise ConfigurationError(str(error)) from error

        conninfo = _required_string(postgres["conninfo"], "postgres.conninfo")
        from psycopg import ProgrammingError
        from psycopg.conninfo import conninfo_to_dict

        try:
            parsed_conninfo = conninfo_to_dict(conninfo)
        except ProgrammingError as error:
            raise ConfigurationError("PostgreSQL conninfo is invalid") from error
        if parsed_conninfo != P5_POSTGRES:
            raise ConfigurationError(
                "PostgreSQL conninfo must select only the CAPLAB database and local socket"
            )

        endpoint = _required_string(garage["endpoint_url"], "garage.endpoint_url")
        parsed_endpoint = urlparse(endpoint)
        if (
            endpoint != P5_GARAGE_ENDPOINT
            or parsed_endpoint.scheme != "http"
            or parsed_endpoint.hostname != "127.0.0.1"
            or parsed_endpoint.username
            or parsed_endpoint.password
            or parsed_endpoint.query
            or parsed_endpoint.fragment
        ):
            raise ConfigurationError(
                "Garage endpoint differs from the P5 loopback endpoint"
            )
        region = _required_string(garage["region"], "garage.region")
        bucket = _required_string(garage["bucket"], "garage.bucket")
        if region != P5_GARAGE_REGION or bucket != P5_GARAGE_BUCKET:
            raise ConfigurationError(
                "Garage region or bucket differs from the P5 namespace"
            )
        credentials_root = Path(
            _required_string(garage["credentials_root"], "garage.credentials_root")
        )
        local_copy_root = Path(_required_string(local_copy["root"], "local_copy.root"))
        if (
            credentials_root != P5_CREDENTIALS_ROOT
            or local_copy_root != P5_LOCAL_COPY_ROOT
        ):
            raise ConfigurationError(
                "P5 credential or local-copy path differs from ADR 0009"
            )

        return cls(
            authority=authority,
            runtime_commit=runtime_commit,
            postgres_conninfo=conninfo,
            garage_endpoint_url=endpoint,
            garage_region=region,
            garage_bucket=bucket,
            credentials_root=credentials_root,
            local_copy_root=local_copy_root,
        )

    def require_active(self, now: datetime | None = None) -> None:
        observed = now or datetime.now(UTC)
        if observed.tzinfo is None:
            raise ConfigurationError(
                "P5 authorization comparison requires a timezone-aware clock"
            )
        try:
            self.authority.require_active(observed.astimezone(UTC))
        except (ValueError, RuntimeError) as error:
            raise ConfigurationError(str(error)) from error


def load_trusted_recovery_config(path: Path) -> RecoveryConfig:
    if path != P5_CONFIG_PATH:
        raise ConfigurationError(
            f"live P5 configuration must be exactly {P5_CONFIG_PATH}"
        )
    flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC
    try:
        descriptor = os.open(path, flags)
    except OSError as error:
        raise ConfigurationError(
            f"cannot open trusted P5 configuration: {error}"
        ) from error
    try:
        metadata = os.fstat(descriptor)
        try:
            expected_group = grp.getgrnam(P5_CONFIG_GROUP).gr_gid
        except KeyError as error:
            raise ConfigurationError("P5 configuration group is absent") from error
        if (
            not stat.S_ISREG(metadata.st_mode)
            or stat.S_IMODE(metadata.st_mode) != 0o640
            or metadata.st_uid != 0
            or metadata.st_gid != expected_group
        ):
            raise ConfigurationError(
                "P5 configuration must be a root:caplab-p5 regular file with mode 0640"
            )
        with os.fdopen(descriptor, "rb", closefd=True) as stream:
            descriptor = -1
            data = stream.read(MAX_CONFIG_BYTES + 1)
    except OSError as error:
        raise ConfigurationError(
            f"cannot read trusted P5 configuration: {error}"
        ) from error
    finally:
        if descriptor >= 0:
            os.close(descriptor)
    if len(data) > MAX_CONFIG_BYTES:
        raise ConfigurationError("P5 configuration exceeds its size limit")
    try:
        text = data.decode("utf-8")
    except UnicodeError as error:
        raise ConfigurationError("P5 configuration is not UTF-8") from error
    return RecoveryConfig._from_text(text)
