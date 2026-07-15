"""Fail-closed loading for non-secret runtime settings and role credentials."""

from __future__ import annotations

import json
import grp
import os
import re
import stat
import tomllib
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlparse


COMMIT = re.compile(r"\A[0-9a-f]{40}\Z")
CAMPAIGN = re.compile(r"\A[a-z][a-z0-9-]{2,127}\Z")
P4_CAMPAIGN = "caplab-p4-roundtrip-2026-07-15"
P4_AUTHORIZATION_EXPIRES = "2026-07-22T23:59:59Z"
P4_POSTGRES = {"dbname": "caplab", "host": "/var/run/postgresql"}
P4_GARAGE_ENDPOINT = "http://127.0.0.1:3900"
P4_GARAGE_REGION = "garage"
P4_GARAGE_BUCKET = "caplab-v0"
P4_CREDENTIALS_ROOT = Path("/etc/caplab/credentials")
P4_LOCAL_COPY_ROOT = Path("/nvr/caplab/v0")
P4_CONFIG_PATH = Path("/etc/caplab/runtime.toml")
MAX_CONFIG_BYTES = 16_384


class ConfigurationError(RuntimeError):
    """Runtime configuration is absent, ambiguous, expired, or unsafe."""


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
class RuntimeConfig:
    campaign_id: str
    authorization_expires_at: datetime
    runtime_commit: str
    postgres_conninfo: str
    garage_endpoint_url: str
    garage_region: str
    garage_bucket: str
    credentials_root: Path
    local_copy_root: Path

    @classmethod
    def from_toml(cls, path: Path) -> "RuntimeConfig":
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            raise ConfigurationError(f"cannot load runtime configuration: {error}") from error
        return cls._from_text(text)

    @classmethod
    def _from_text(cls, text: str) -> "RuntimeConfig":
        try:
            document = tomllib.loads(text)
        except tomllib.TOMLDecodeError as error:
            raise ConfigurationError(f"cannot load runtime configuration: {error}") from error
        _exact_keys(document, {"runtime", "postgres", "garage", "local_copy"}, "root")
        for section in document.values():
            if not isinstance(section, dict):
                raise ConfigurationError("every configuration section must be a table")

        runtime = document["runtime"]
        postgres = document["postgres"]
        garage = document["garage"]
        local_copy = document["local_copy"]
        _exact_keys(
            runtime,
            {"campaign_id", "authorization_expires_at", "runtime_commit"},
            "runtime",
        )
        _exact_keys(postgres, {"conninfo"}, "postgres")
        _exact_keys(
            garage,
            {"endpoint_url", "region", "bucket", "credentials_root"},
            "garage",
        )
        _exact_keys(local_copy, {"root"}, "local_copy")

        campaign_id = _required_string(runtime["campaign_id"], "runtime.campaign_id")
        if not CAMPAIGN.fullmatch(campaign_id):
            raise ConfigurationError("runtime.campaign_id is not a bounded identifier")
        if campaign_id != P4_CAMPAIGN:
            raise ConfigurationError("runtime campaign differs from the authorized P4 campaign")
        runtime_commit = _required_string(runtime["runtime_commit"], "runtime.runtime_commit")
        if not COMMIT.fullmatch(runtime_commit):
            raise ConfigurationError("runtime.runtime_commit must be a 40-character Git identity")
        expiry_text = _required_string(
            runtime["authorization_expires_at"], "runtime.authorization_expires_at"
        )
        if expiry_text != P4_AUTHORIZATION_EXPIRES:
            raise ConfigurationError(
                "authorization expiry differs from the authorized P4 campaign"
            )
        if not expiry_text.endswith("Z"):
            raise ConfigurationError("authorization expiry must use an explicit UTC Z suffix")
        try:
            expiry = datetime.fromisoformat(expiry_text[:-1] + "+00:00")
        except ValueError as error:
            raise ConfigurationError("authorization expiry is not valid ISO 8601") from error

        conninfo = _required_string(postgres["conninfo"], "postgres.conninfo")
        from psycopg import ProgrammingError
        from psycopg.conninfo import conninfo_to_dict

        try:
            parsed_conninfo = conninfo_to_dict(conninfo)
        except ProgrammingError as error:
            raise ConfigurationError("PostgreSQL conninfo is invalid") from error
        if parsed_conninfo != P4_POSTGRES:
            raise ConfigurationError(
                "PostgreSQL conninfo must select only the authorized database and local socket"
            )

        endpoint = _required_string(garage["endpoint_url"], "garage.endpoint_url")
        parsed = urlparse(endpoint)
        if parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
            raise ConfigurationError("Garage endpoint must be loopback HTTP")
        if parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ConfigurationError("Garage endpoint must not embed credentials or parameters")
        if endpoint != P4_GARAGE_ENDPOINT:
            raise ConfigurationError("Garage endpoint differs from the authorized P4 endpoint")

        garage_region = _required_string(garage["region"], "garage.region")
        garage_bucket = _required_string(garage["bucket"], "garage.bucket")
        if garage_region != P4_GARAGE_REGION or garage_bucket != P4_GARAGE_BUCKET:
            raise ConfigurationError("Garage region or bucket differs from the P4 namespace")

        credentials_root = Path(
            _required_string(garage["credentials_root"], "garage.credentials_root")
        )
        local_copy_root = Path(_required_string(local_copy["root"], "local_copy.root"))
        if not credentials_root.is_absolute() or not local_copy_root.is_absolute():
            raise ConfigurationError("credential and local-copy roots must be absolute")
        if credentials_root != P4_CREDENTIALS_ROOT or local_copy_root != P4_LOCAL_COPY_ROOT:
            raise ConfigurationError("credential or local-copy root differs from the P4 namespace")

        return cls(
            campaign_id=campaign_id,
            authorization_expires_at=expiry.astimezone(UTC),
            runtime_commit=runtime_commit,
            postgres_conninfo=conninfo,
            garage_endpoint_url=endpoint,
            garage_region=garage_region,
            garage_bucket=garage_bucket,
            credentials_root=credentials_root,
            local_copy_root=local_copy_root,
        )

    def require_active(self, now: datetime | None = None) -> None:
        observed = now or datetime.now(UTC)
        if observed.tzinfo is None:
            raise ConfigurationError("authorization comparison requires a timezone-aware clock")
        if observed.astimezone(UTC) > self.authorization_expires_at:
            raise ConfigurationError("CAPLAB P4 authorization has expired")


def load_trusted_runtime_config(path: Path) -> RuntimeConfig:
    """Load the one root-custodied live configuration from one no-follow descriptor."""

    if path != P4_CONFIG_PATH:
        raise ConfigurationError(
            f"live runtime configuration must be exactly {P4_CONFIG_PATH}"
        )
    flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC
    try:
        descriptor = os.open(path, flags)
    except OSError as error:
        raise ConfigurationError(f"cannot open trusted runtime configuration: {error}") from error
    try:
        metadata = os.fstat(descriptor)
        try:
            expected_group = grp.getgrnam("caplab").gr_gid
        except KeyError as error:
            raise ConfigurationError("CAPLAB runtime group is absent") from error
        if (
            not stat.S_ISREG(metadata.st_mode)
            or stat.S_IMODE(metadata.st_mode) != 0o640
            or metadata.st_uid != 0
            or metadata.st_gid != expected_group
        ):
            raise ConfigurationError(
                "runtime configuration must be a root:caplab regular file with mode 0640"
            )
        with os.fdopen(descriptor, "rb", closefd=True) as stream:
            descriptor = -1
            data = stream.read(MAX_CONFIG_BYTES + 1)
    except OSError as error:
        raise ConfigurationError(f"cannot read trusted runtime configuration: {error}") from error
    finally:
        if descriptor >= 0:
            os.close(descriptor)
    if len(data) > MAX_CONFIG_BYTES:
        raise ConfigurationError("runtime configuration exceeds its size limit")
    try:
        text = data.decode("utf-8")
    except UnicodeError as error:
        raise ConfigurationError("runtime configuration is not UTF-8") from error
    return RuntimeConfig._from_text(text)


@dataclass(frozen=True, slots=True)
class GarageCredentials:
    access_key_id: str
    secret_access_key: str


def load_credentials(path: Path) -> GarageCredentials:
    try:
        metadata = path.lstat()
    except OSError as error:
        raise ConfigurationError(f"cannot inspect Garage credential file: {error}") from error
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode):
        raise ConfigurationError("Garage credential path must be a regular non-symlink file")
    if stat.S_IMODE(metadata.st_mode) != 0o400:
        raise ConfigurationError("Garage credential file mode must be exactly 0400")
    if metadata.st_uid != os.geteuid():
        raise ConfigurationError("Garage credential file must be owned by the runtime identity")
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ConfigurationError(f"cannot load Garage credential file: {error}") from error
    if not isinstance(document, dict):
        raise ConfigurationError("Garage credential document must be an object")
    _exact_keys(document, {"access_key_id", "secret_access_key"}, "Garage credentials")
    return GarageCredentials(
        access_key_id=_required_string(document["access_key_id"], "access_key_id"),
        secret_access_key=_required_string(document["secret_access_key"], "secret_access_key"),
    )
