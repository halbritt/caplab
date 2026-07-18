"""Fail-closed configuration for the bounded P7 recomputation campaign."""

from __future__ import annotations

import grp
import os
import re
import stat
import tomllib
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlparse

from caplab.runtime.config import ConfigurationError


CONFIG_PATH = Path("/etc/caplab/recomputation.toml")
CAMPAIGN_ID = "caplab-study-001-p7-recompute-2026-07-18"
AUTHORIZATION_EXPIRES = "2026-07-25T23:59:59Z"
ADMISSION_MANIFEST_SHA256 = (
    "d2d4f821146c3f39e6726133c383807ec9f6051834e74fbd3a5f33aae8ef148e"
)
POSTGRES_CONNINFO = "dbname=caplab host=/var/run/postgresql"
GARAGE_ENDPOINT = "http://127.0.0.1:3900"
GARAGE_REGION = "garage"
GARAGE_BUCKET = "caplab-v0"
CREDENTIALS_ROOT = Path("/etc/caplab/credentials")
LOCAL_COPY_ROOT = Path("/nvr/caplab/v0")
SHA256 = re.compile(r"\A[0-9a-f]{64}\Z")
COMMIT = re.compile(r"\A[0-9a-f]{40}\Z")
MAX_BYTES = 16_384


def _required_string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ConfigurationError(f"{label} must be a non-empty string")
    return value


@dataclass(frozen=True, slots=True)
class RecomputationConfig:
    campaign_id: str
    authorization_expires_at: datetime
    source_commit: str
    admission_manifest_sha256: str
    postgres_conninfo: str
    garage_endpoint_url: str
    garage_region: str
    garage_bucket: str
    credentials_root: Path
    local_copy_root: Path

    @classmethod
    def from_text(cls, text: str) -> "RecomputationConfig":
        try:
            document = tomllib.loads(text)
        except tomllib.TOMLDecodeError as error:
            raise ConfigurationError(
                f"cannot load recomputation configuration: {error}"
            ) from error
        expected_sections = {"authorization", "postgres", "garage", "local_copy"}
        if set(document) != expected_sections or any(
            not isinstance(section, dict) for section in document.values()
        ):
            raise ConfigurationError("recomputation configuration has unexpected sections")
        authorization = document["authorization"]
        postgres = document["postgres"]
        garage = document["garage"]
        local_copy = document["local_copy"]
        shapes = (
            (
                authorization,
                {
                    "campaign_id",
                    "expires_at",
                    "source_commit",
                    "admission_manifest_sha256",
                },
                "authorization",
            ),
            (postgres, {"conninfo"}, "postgres"),
            (
                garage,
                {"endpoint_url", "region", "bucket", "credentials_root"},
                "garage",
            ),
            (local_copy, {"root"}, "local_copy"),
        )
        for section, keys, label in shapes:
            if set(section) != keys:
                raise ConfigurationError(f"{label} configuration has unexpected fields")
        campaign_id = _required_string(authorization["campaign_id"], "campaign_id")
        if campaign_id != CAMPAIGN_ID:
            raise ConfigurationError("recomputation campaign differs from ADR 0016")
        expires_at = _required_string(authorization["expires_at"], "expires_at")
        if expires_at != AUTHORIZATION_EXPIRES:
            raise ConfigurationError("recomputation expiry differs from ADR 0016")
        try:
            expiry = datetime.fromisoformat(expires_at[:-1] + "+00:00")
        except ValueError as error:
            raise ConfigurationError("recomputation expiry is invalid") from error
        source_commit = _required_string(
            authorization["source_commit"], "source_commit"
        )
        if not COMMIT.fullmatch(source_commit):
            raise ConfigurationError("recomputation source commit is invalid")
        manifest_sha256 = _required_string(
            authorization["admission_manifest_sha256"],
            "admission_manifest_sha256",
        )
        if manifest_sha256 != ADMISSION_MANIFEST_SHA256:
            raise ConfigurationError("admission manifest differs from P6")
        conninfo = _required_string(postgres["conninfo"], "postgres.conninfo")
        if conninfo != POSTGRES_CONNINFO:
            raise ConfigurationError("PostgreSQL target differs from CAPLAB v0")
        endpoint = _required_string(garage["endpoint_url"], "garage.endpoint_url")
        parsed = urlparse(endpoint)
        if (
            endpoint != GARAGE_ENDPOINT
            or parsed.scheme != "http"
            or parsed.hostname != "127.0.0.1"
            or parsed.username
            or parsed.password
            or parsed.query
            or parsed.fragment
        ):
            raise ConfigurationError("Garage endpoint differs from CAPLAB v0")
        region = _required_string(garage["region"], "garage.region")
        bucket = _required_string(garage["bucket"], "garage.bucket")
        if region != GARAGE_REGION or bucket != GARAGE_BUCKET:
            raise ConfigurationError("Garage namespace differs from CAPLAB v0")
        credentials_root = Path(
            _required_string(garage["credentials_root"], "garage.credentials_root")
        )
        local_copy_root = Path(
            _required_string(local_copy["root"], "local_copy.root")
        )
        if credentials_root != CREDENTIALS_ROOT:
            raise ConfigurationError("credential root differs from CAPLAB v0")
        if local_copy_root != LOCAL_COPY_ROOT:
            raise ConfigurationError("local-copy root differs from CAPLAB v0")
        return cls(
            campaign_id=campaign_id,
            authorization_expires_at=expiry.astimezone(UTC),
            source_commit=source_commit,
            admission_manifest_sha256=manifest_sha256,
            postgres_conninfo=conninfo,
            garage_endpoint_url=endpoint,
            garage_region=region,
            garage_bucket=bucket,
            credentials_root=credentials_root,
            local_copy_root=local_copy_root,
        )

    def require_active(self, now: datetime | None = None) -> None:
        observed = now or datetime.now(UTC)
        if (
            observed.tzinfo is None
            or observed.astimezone(UTC) > self.authorization_expires_at
        ):
            raise ConfigurationError(
                "CAPLAB P7 authorization is expired or clock is ambiguous"
            )


def load_trusted_config(path: Path) -> RecomputationConfig:
    if path != CONFIG_PATH:
        raise ConfigurationError(
            f"live recomputation configuration must be exactly {CONFIG_PATH}"
        )
    try:
        descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
    except OSError as error:
        raise ConfigurationError(
            f"cannot open recomputation configuration: {error}"
        ) from error
    try:
        metadata = os.fstat(descriptor)
        group_id = grp.getgrnam("caplab").gr_gid
        if (
            not stat.S_ISREG(metadata.st_mode)
            or stat.S_IMODE(metadata.st_mode) != 0o640
            or metadata.st_uid != 0
            or metadata.st_gid != group_id
        ):
            raise ConfigurationError(
                "recomputation configuration must be root:caplab mode 0640"
            )
        with os.fdopen(descriptor, "rb", closefd=True) as stream:
            descriptor = -1
            data = stream.read(MAX_BYTES + 1)
    finally:
        if descriptor >= 0:
            os.close(descriptor)
    if len(data) > MAX_BYTES:
        raise ConfigurationError("recomputation configuration exceeds its size limit")
    try:
        return RecomputationConfig.from_text(data.decode("utf-8"))
    except UnicodeDecodeError as error:
        raise ConfigurationError("recomputation configuration is not UTF-8") from error
