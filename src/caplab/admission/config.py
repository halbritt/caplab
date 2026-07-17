"""Fail-closed configuration for the bounded P6 admission campaign."""

from __future__ import annotations

import grp
import os
import stat
import tomllib
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlparse

from caplab.runtime.config import ConfigurationError

from .study001 import PRESERVATION_ROOT


CONFIG_PATH = Path("/etc/caplab/admission.toml")
AUTHORIZATION_EXPIRES = "2026-07-24T23:59:59Z"
POSTGRES_CONNINFO = "dbname=caplab host=/var/run/postgresql"
GARAGE_ENDPOINT = "http://127.0.0.1:3900"
GARAGE_REGION = "garage"
GARAGE_BUCKET = "caplab-v0"
LOCAL_COPY_ROOT = Path("/nvr/caplab/v0")
CREDENTIALS_ROOT = Path("/etc/caplab/credentials")
MAX_BYTES = 16_384


@dataclass(frozen=True, slots=True)
class AdmissionConfig:
    source_commit: str
    authorization_expires_at: datetime
    postgres_conninfo: str
    garage_endpoint_url: str
    garage_region: str
    garage_bucket: str
    credentials_root: Path
    local_copy_root: Path
    preservation_root: Path
    git_stage: Path

    @classmethod
    def from_text(cls, text: str) -> "AdmissionConfig":
        try:
            document = tomllib.loads(text)
        except tomllib.TOMLDecodeError as error:
            raise ConfigurationError(
                f"cannot load admission configuration: {error}"
            ) from error
        expected = {"authorization", "postgres", "garage", "local_copy", "source"}
        if set(document) != expected or any(
            not isinstance(value, dict) for value in document.values()
        ):
            raise ConfigurationError("admission configuration has unexpected sections")
        authorization = document["authorization"]
        postgres = document["postgres"]
        garage = document["garage"]
        local_copy = document["local_copy"]
        source = document["source"]
        shapes = (
            (authorization, {"expires_at", "source_commit"}, "authorization"),
            (postgres, {"conninfo"}, "postgres"),
            (
                garage,
                {"endpoint_url", "region", "bucket", "credentials_root"},
                "garage",
            ),
            (local_copy, {"root"}, "local_copy"),
            (source, {"preservation_root", "git_stage"}, "source"),
        )
        for section, keys, label in shapes:
            if set(section) != keys:
                raise ConfigurationError(f"{label} configuration has unexpected fields")
            if any(
                not isinstance(value, str) or not value for value in section.values()
            ):
                raise ConfigurationError(
                    f"{label} configuration requires non-empty strings"
                )
        expires = authorization["expires_at"]
        if expires != AUTHORIZATION_EXPIRES:
            raise ConfigurationError(
                "admission authorization expiry differs from ADR 0014"
            )
        try:
            expiry = datetime.fromisoformat(expires[:-1] + "+00:00")
        except ValueError as error:
            raise ConfigurationError(
                "admission authorization expiry is invalid"
            ) from error
        source_commit = authorization["source_commit"]
        if len(source_commit) != 40 or any(
            character not in "0123456789abcdef" for character in source_commit
        ):
            raise ConfigurationError("admission source commit is invalid")
        if postgres["conninfo"] != POSTGRES_CONNINFO:
            raise ConfigurationError(
                "admission PostgreSQL target differs from the local CAPLAB database"
            )
        parsed = urlparse(garage["endpoint_url"])
        if (
            garage["endpoint_url"] != GARAGE_ENDPOINT
            or parsed.scheme != "http"
            or parsed.hostname != "127.0.0.1"
            or parsed.username
            or parsed.password
            or parsed.query
            or parsed.fragment
        ):
            raise ConfigurationError(
                "admission Garage target is not the exact loopback endpoint"
            )
        if garage["region"] != GARAGE_REGION or garage["bucket"] != GARAGE_BUCKET:
            raise ConfigurationError(
                "admission Garage namespace differs from CAPLAB v0"
            )
        credentials_root = Path(garage["credentials_root"])
        copy_root = Path(local_copy["root"])
        preservation_root = Path(source["preservation_root"])
        git_stage = Path(source["git_stage"])
        if credentials_root != CREDENTIALS_ROOT or copy_root != LOCAL_COPY_ROOT:
            raise ConfigurationError("admission credential or local-copy root differs")
        if preservation_root != PRESERVATION_ROOT:
            raise ConfigurationError(
                "admission preservation root differs from ADR 0014"
            )
        if not git_stage.is_absolute() or git_stage.is_symlink():
            raise ConfigurationError(
                "admission Git stage must be an absolute non-symlink path"
            )
        return cls(
            source_commit=source_commit,
            authorization_expires_at=expiry.astimezone(UTC),
            postgres_conninfo=postgres["conninfo"],
            garage_endpoint_url=garage["endpoint_url"],
            garage_region=garage["region"],
            garage_bucket=garage["bucket"],
            credentials_root=credentials_root,
            local_copy_root=copy_root,
            preservation_root=preservation_root,
            git_stage=git_stage,
        )

    def require_active(self, now: datetime | None = None) -> None:
        observed = now or datetime.now(UTC)
        if (
            observed.tzinfo is None
            or observed.astimezone(UTC) > self.authorization_expires_at
        ):
            raise ConfigurationError(
                "CAPLAB P6 authorization is expired or clock is ambiguous"
            )


def load_trusted_config(path: Path) -> AdmissionConfig:
    if path != CONFIG_PATH:
        raise ConfigurationError(
            f"live admission configuration must be exactly {CONFIG_PATH}"
        )
    try:
        descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
    except OSError as error:
        raise ConfigurationError(
            f"cannot open admission configuration: {error}"
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
                "admission configuration must be root:caplab mode 0640"
            )
        with os.fdopen(descriptor, "rb", closefd=True) as stream:
            descriptor = -1
            data = stream.read(MAX_BYTES + 1)
    finally:
        if descriptor >= 0:
            os.close(descriptor)
    if len(data) > MAX_BYTES:
        raise ConfigurationError("admission configuration exceeds its size limit")
    try:
        return AdmissionConfig.from_text(data.decode("utf-8"))
    except UnicodeDecodeError as error:
        raise ConfigurationError("admission configuration is not UTF-8") from error
