"""Batch CLI for the authorized CAPLAB P4 runtime surface."""

from __future__ import annotations

import argparse
import json
import os
import pwd
import sys
import tempfile
from pathlib import Path
from typing import Any

from .adapters.filesystem import FilesystemCopyStore
from .adapters.postgres import PostgresMetadataStore, PostgresMigrator
from .adapters.s3 import S3ObjectStore
from .canonical import canonical_json, sha256_hex
from .config import (
    ConfigurationError,
    RuntimeConfig,
    load_credentials,
    load_trusted_runtime_config,
)
from .errors import RuntimeContractError
from .migrations import discover_migrations
from .models import RegistrationReceipt, RegistrationRequest, ReconciliationReport
from .registration import RegistrationService


CONFIG_DEFAULT = "/etc/caplab/runtime.toml"
FIXTURE_FIELDS = {
    "schema_version",
    "campaign_id",
    "artifact_kind",
    "media_type",
    "identity_layers",
}
ROLE_BY_COMMAND = {
    "migrate": {"postgres"},
    "register": {"caplab_writer"},
    "retrieve": {"caplab_reader"},
    "verify": {"caplab_verifier"},
    "reconcile": {"caplab_verifier"},
    "cleanup-plan": {"caplab_verifier"},
}


def _add_config(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--config", default=CONFIG_DEFAULT, type=Path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m caplab.runtime")
    subparsers = parser.add_subparsers(dest="command", required=True)

    migrate = subparsers.add_parser("migrate", help="apply verified forward migrations")
    _add_config(migrate)

    register = subparsers.add_parser("register", help="register one sealed synthetic attempt")
    _add_config(register)
    register.add_argument("--operation-id", required=True)
    register.add_argument("--fixture", required=True, type=Path)
    register.add_argument("--payload", required=True, type=Path)

    retrieve = subparsers.add_parser("retrieve", help="retrieve registered bytes")
    _add_config(retrieve)
    retrieve.add_argument("--operation-id", required=True)
    retrieve.add_argument("--output", required=True, type=Path)

    verify = subparsers.add_parser("verify", help="verify both registered byte copies")
    _add_config(verify)
    verify.add_argument("--operation-id", required=True)

    reconcile = subparsers.add_parser("reconcile", help="compare metadata and both byte copies")
    _add_config(reconcile)
    reconcile.add_argument("--operation-id", required=True)
    reconcile.add_argument("--fixture", required=True, type=Path)

    cleanup = subparsers.add_parser(
        "cleanup-plan", help="emit a non-executing post-effect custody plan"
    )
    _add_config(cleanup)
    cleanup.add_argument("--operation-id", required=True)
    cleanup.add_argument("--output", required=True, type=Path)
    return parser


def load_registration_request(
    fixture_path: Path,
    payload_path: Path,
    *,
    operation_id: str,
    expected_campaign: str,
    runtime_provenance: dict[str, Any] | None = None,
) -> RegistrationRequest:
    try:
        fixture_bytes = fixture_path.read_bytes()
        payload_bytes = payload_path.read_bytes()
    except OSError as error:
        raise ValueError(f"cannot load synthetic input: {error}") from error
    return registration_request_from_bytes(
        fixture_bytes,
        payload_bytes,
        operation_id=operation_id,
        expected_campaign=expected_campaign,
        runtime_provenance=runtime_provenance,
    )


def registration_request_from_bytes(
    fixture_bytes: bytes,
    payload_bytes: bytes,
    *,
    operation_id: str,
    expected_campaign: str,
    runtime_provenance: dict[str, Any] | None = None,
) -> RegistrationRequest:
    try:
        fixture = json.loads(fixture_bytes)
    except (UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot load synthetic fixture: {error}") from error
    if not isinstance(fixture, dict) or set(fixture) != FIXTURE_FIELDS:
        raise ValueError("synthetic fixture has an unexpected shape")
    if fixture["schema_version"] != "caplab-synthetic-attempt/1":
        raise ValueError("unsupported synthetic fixture schema")
    if fixture["campaign_id"] != expected_campaign:
        raise ValueError("synthetic fixture campaign differs from runtime configuration")
    return RegistrationRequest(
        operation_id=operation_id,
        campaign_id=fixture["campaign_id"],
        artifact_kind=fixture["artifact_kind"],
        media_type=fixture["media_type"],
        identity_layers=fixture["identity_layers"],
        payload=payload_bytes,
        runtime_provenance=runtime_provenance,
    )


def current_runtime_provenance(
    config: RuntimeConfig, fixture_bytes: bytes
) -> dict[str, Any]:
    discovered = discover_migrations(Path(__file__).with_name("migrations"))
    return {
        "runtime_commit": config.runtime_commit,
        "requirements_lock_sha256": sha256_hex(
            Path(__file__).with_name("requirements.lock").read_bytes()
        ),
        "fixture_sha256": sha256_hex(fixture_bytes),
        "migrations": [
            {"filename": migration.filename, "sha256": migration.sha256}
            for migration in discovered
        ],
    }


def prepare_registration_request(
    fixture_path: Path,
    payload_path: Path,
    *,
    operation_id: str,
    config: RuntimeConfig,
) -> RegistrationRequest:
    try:
        fixture_bytes = fixture_path.read_bytes()
        payload_bytes = payload_path.read_bytes()
    except OSError as error:
        raise ValueError(f"cannot load synthetic input: {error}") from error
    return registration_request_from_bytes(
        fixture_bytes,
        payload_bytes,
        operation_id=operation_id,
        expected_campaign=config.campaign_id,
        runtime_provenance=current_runtime_provenance(config, fixture_bytes),
    )


def write_exclusive(path: Path, data: bytes, *, mode: int) -> None:
    if not path.parent.is_dir():
        raise FileNotFoundError(f"output parent does not exist: {path.parent}")
    descriptor, temporary_name = tempfile.mkstemp(prefix=".caplab-output-", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb", closefd=True) as stream:
            stream.write(data)
            stream.flush()
            os.fchmod(stream.fileno(), mode)
            os.fsync(stream.fileno())
        os.link(temporary, path)
        directory_fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        temporary.unlink(missing_ok=True)


def _role() -> str:
    return pwd.getpwuid(os.geteuid()).pw_name


def _require_role(command: str, role: str) -> None:
    allowed = ROLE_BY_COMMAND[command]
    if role not in allowed:
        raise ConfigurationError(
            f"command {command!r} requires runtime identity {sorted(allowed)!r}"
        )


def _service(config: RuntimeConfig, role: str) -> RegistrationService:
    credential_path = config.credentials_root / role / "garage.json"
    credentials = load_credentials(credential_path)
    objects = S3ObjectStore.from_settings(
        endpoint_url=config.garage_endpoint_url,
        region=config.garage_region,
        bucket=config.garage_bucket,
        access_key_id=credentials.access_key_id,
        secret_access_key=credentials.secret_access_key,
    )
    return RegistrationService(
        PostgresMetadataStore(config.postgres_conninfo),
        objects,
        FilesystemCopyStore(config.local_copy_root),
    )


def _receipt(receipt: RegistrationReceipt) -> dict[str, Any]:
    return {
        "schema_version": "caplab-registration-receipt/1",
        "operation_id": receipt.operation_id,
        "campaign_id": receipt.campaign_id,
        "request_sha256": receipt.request_sha256,
        "content_sha256": receipt.content_sha256,
        "object_key": receipt.object_key,
        "manifest_sha256": receipt.manifest_sha256,
        "identity_sha256": dict(receipt.identity_sha256),
        "idempotent_replay": receipt.idempotent_replay,
    }


def _report(report: ReconciliationReport) -> dict[str, Any]:
    return {
        "schema_version": "caplab-reconciliation/1",
        "operation_id": report.operation_id,
        "content_sha256": report.content_sha256,
        "object_status": report.object_status,
        "local_copy_status": report.local_copy_status,
        "metadata_status": report.metadata_status,
        "locator_status": report.locator_status,
        "provenance_status": report.provenance_status,
        "ok": report.ok,
    }


def _emit(document: dict[str, Any], *, stream: Any = sys.stdout) -> None:
    stream.buffer.write(canonical_json(document) + b"\n")
    stream.flush()


def run(args: argparse.Namespace) -> int:
    inherited_transport_settings = sorted(
        key
        for key in os.environ
        if key.startswith("PG")
        or key in {"HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "NO_PROXY"}
    )
    if inherited_transport_settings:
        raise ConfigurationError(
            "runtime requires a clean transport environment; refused inherited settings: "
            + ", ".join(inherited_transport_settings)
        )
    config = load_trusted_runtime_config(args.config)
    config.require_active()
    role = _role()
    _require_role(args.command, role)

    if args.command == "migrate":
        migrator = PostgresMigrator(
            config.postgres_conninfo,
            Path(__file__).with_name("migrations"),
            config.runtime_commit,
        )
        applied = migrator.apply()
        _emit(
            {
                "schema_version": "caplab-migration-receipt/1",
                "runtime_commit": config.runtime_commit,
                "applied": [
                    {"filename": migration.filename, "sha256": migration.sha256}
                    for migration in applied
                ],
            }
        )
        return 0

    service = _service(config, role)
    if args.command == "register":
        request = prepare_registration_request(
            args.fixture,
            args.payload,
            operation_id=args.operation_id,
            config=config,
        )
        _emit(_receipt(service.register(request)))
        return 0
    if args.command == "retrieve":
        payload = service.retrieve(args.operation_id)
        write_exclusive(args.output, payload, mode=0o440)
        receipt = service.verify(args.operation_id)
        _emit(
            {
                "schema_version": "caplab-retrieval-receipt/1",
                "operation_id": args.operation_id,
                "content_sha256": receipt.content_sha256,
                "output": str(args.output),
            }
        )
        return 0
    if args.command == "verify":
        _emit(_receipt(service.verify(args.operation_id)))
        return 0
    if args.command == "reconcile":
        try:
            fixture_bytes = args.fixture.read_bytes()
        except OSError as error:
            raise ValueError(f"cannot load synthetic fixture: {error}") from error
        report = service.reconcile(
            args.operation_id,
            expected_runtime_provenance=current_runtime_provenance(config, fixture_bytes),
        )
        _emit(_report(report))
        return 0 if report.ok else 3
    if args.command == "cleanup-plan":
        plan = service.cleanup_plan(args.operation_id)
        write_exclusive(args.output, canonical_json(plan) + b"\n", mode=0o440)
        _emit(
            {
                "schema_version": "caplab-cleanup-plan-receipt/1",
                "operation_id": args.operation_id,
                "plan_sha256": plan["plan_sha256"],
                "output": str(args.output),
            }
        )
        return 0
    raise AssertionError(f"unhandled command: {args.command}")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return run(args)
    except (ConfigurationError, RuntimeContractError, ValueError, OSError) as error:
        _emit(
            {
                "schema_version": "caplab-runtime-error/1",
                "error_type": type(error).__name__,
                "message": str(error),
            },
            stream=sys.stderr,
        )
        return 2
    except Exception as error:
        _emit(
            {
                "schema_version": "caplab-runtime-error/1",
                "error_type": type(error).__name__,
                "message": "unexpected runtime failure; no effect was declared successful",
            },
            stream=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
