"""Batch CLI for the separately authorized CAPLAB P5 custody surface."""

from __future__ import annotations

import argparse
import json
import os
import pwd
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from caplab.runtime.adapters.postgres import PostgresMetadataStore, PostgresMigrator
from caplab.runtime.canonical import canonical_json, sha256_hex
from caplab.runtime.config import ConfigurationError, load_credentials
from caplab.runtime.errors import RuntimeContractError
from caplab.runtime.migrations import discover_migrations
from caplab.runtime.models import RegistrationReceipt, RegistrationRequest
from caplab.runtime.registration import RegistrationService

from .adapters.filesystem import FilesystemCustodyStore
from .adapters.postgres import PostgresCustodyStore
from .adapters.s3 import S3CustodyStore
from .config import P5_CONFIG_PATH, RecoveryConfig, load_trusted_recovery_config
from .errors import InjectedInterruption, RecoveryError
from .faults import InterruptAfterEvent
from .models import (
    P5Identity,
    PurgeRequest,
    build_orphan_inventory,
    observe_invalid_attempt,
)
from .service import PurgeService, RecoveryService


P5_OPERATOR = "caplab_p5_operator"
P5_VERIFIER = "caplab_p5_verifier"
FIXTURE_FIELDS = {
    "schema_version",
    "operation_id",
    "campaign_id",
    "artifact_kind",
    "media_type",
    "identity_layers",
}
ROLE_BY_COMMAND = {
    "migrate": {"postgres"},
    "register": {P5_OPERATOR},
    "verify": {P5_OPERATOR, P5_VERIFIER},
    "inventory": {P5_OPERATOR, P5_VERIFIER},
    "cleanup-plan": {P5_OPERATOR, P5_VERIFIER},
    "observe-invalid": {P5_OPERATOR},
    "restore-object": {P5_OPERATOR},
    "restore-copy": {P5_OPERATOR},
    "replace-object": {P5_OPERATOR},
    "replace-copy": {P5_OPERATOR},
    "remove-object": {P5_OPERATOR},
    "remove-copy": {P5_OPERATOR},
    "request-purge": {P5_OPERATOR},
    "dependency": {P5_OPERATOR},
    "purge": {P5_OPERATOR},
}


def _add_config(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--config", default=P5_CONFIG_PATH, type=Path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m caplab.recovery")
    subparsers = parser.add_subparsers(dest="command", required=True)

    identity = subparsers.add_parser("identity", help="derive the frozen P5 identity")
    identity.add_argument("--runtime-commit", required=True)
    identity.add_argument("--authorization-document", required=True, type=Path)
    identity.add_argument("--fixture", required=True, type=Path)
    identity.add_argument("--payload", required=True, type=Path)

    migrate = subparsers.add_parser("migrate", help="apply forward CAPLAB migrations")
    _add_config(migrate)

    register = subparsers.add_parser("register", help="register the frozen P5 fixture")
    _add_config(register)
    register.add_argument("--fixture", required=True, type=Path)
    register.add_argument("--payload", required=True, type=Path)
    register.add_argument(
        "--interrupt-after",
        choices=("object-verified", "local-copy-verified"),
    )

    verify = subparsers.add_parser("verify", help="verify the frozen P5 registration")
    _add_config(verify)
    verify.add_argument("--fixture", required=True, type=Path)

    inventory = subparsers.add_parser("inventory", help="inventory P5 custody state")
    _add_config(inventory)

    cleanup = subparsers.add_parser(
        "cleanup-plan", help="emit a non-applying cleanup plan"
    )
    _add_config(cleanup)
    cleanup.add_argument("--output", required=True, type=Path)

    invalid = subparsers.add_parser(
        "observe-invalid",
        help="record an invalid or ambiguous fixture without subject outcomes",
    )
    _add_config(invalid)
    invalid.add_argument("--observation-id", required=True)
    invalid.add_argument("--fixture", required=True, type=Path)
    invalid.add_argument(
        "--disposition", required=True, choices=("invalid", "ambiguous")
    )
    invalid.add_argument("--reason-code", required=True, action="append")

    for command in ("restore-object", "restore-copy", "remove-object", "remove-copy"):
        operation = subparsers.add_parser(command)
        _add_config(operation)

    for command in ("replace-object", "replace-copy"):
        operation = subparsers.add_parser(command)
        _add_config(operation)
        operation.add_argument("--input", required=True, type=Path)

    request_purge = subparsers.add_parser("request-purge")
    _add_config(request_purge)
    request_purge.add_argument("--custody-request-id", required=True)

    dependency = subparsers.add_parser("dependency")
    _add_config(dependency)
    dependency.add_argument("--kind", required=True)
    dependency.add_argument("--identity", required=True)
    dependency.add_argument("--event", required=True, choices=("retained", "released"))

    purge = subparsers.add_parser("purge")
    _add_config(purge)
    purge.add_argument("--custody-request-id", required=True)
    return parser


def _load_fixture(path: Path) -> tuple[bytes, dict[str, Any]]:
    try:
        fixture_bytes = path.read_bytes()
        fixture = json.loads(fixture_bytes)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot load P5 fixture: {error}") from error
    if not isinstance(fixture, dict) or set(fixture) != FIXTURE_FIELDS:
        raise ValueError("P5 fixture has an unexpected shape")
    if fixture["schema_version"] != "caplab-p5-synthetic-attempt/1":
        raise ValueError("unsupported P5 fixture schema")
    return fixture_bytes, fixture


def current_recovery_provenance(
    runtime_commit: str, fixture_bytes: bytes
) -> dict[str, Any]:
    migrations = discover_migrations(
        Path(__file__).parents[1] / "runtime" / "migrations"
    )
    return {
        "runtime_commit": runtime_commit,
        "requirements_lock_sha256": sha256_hex(
            (Path(__file__).parents[1] / "runtime" / "requirements.lock").read_bytes()
        ),
        "fixture_sha256": sha256_hex(fixture_bytes),
        "migrations": [
            {"filename": migration.filename, "sha256": migration.sha256}
            for migration in migrations
        ],
    }


def prepare_request(
    fixture_path: Path,
    payload_path: Path,
    *,
    runtime_commit: str,
) -> RegistrationRequest:
    fixture_bytes, fixture = _load_fixture(fixture_path)
    try:
        payload = payload_path.read_bytes()
    except OSError as error:
        raise ValueError(f"cannot load P5 payload: {error}") from error
    return RegistrationRequest(
        operation_id=fixture["operation_id"],
        campaign_id=fixture["campaign_id"],
        artifact_kind=fixture["artifact_kind"],
        media_type=fixture["media_type"],
        identity_layers=fixture["identity_layers"],
        payload=payload,
        runtime_provenance=current_recovery_provenance(runtime_commit, fixture_bytes),
    )


def identity_document(
    fixture_path: Path,
    payload_path: Path,
    authorization_document: Path,
    *,
    runtime_commit: str,
) -> dict[str, Any]:
    if len(runtime_commit) != 40 or any(
        character not in "0123456789abcdef" for character in runtime_commit
    ):
        raise ValueError("runtime commit must be a full lowercase Git identity")
    request = prepare_request(
        fixture_path,
        payload_path,
        runtime_commit=runtime_commit,
    )
    try:
        authorization_bytes = authorization_document.read_bytes()
    except OSError as error:
        raise ValueError(f"cannot load P5 authorization document: {error}") from error
    identity = P5Identity.from_intent(request.intent())
    return {
        "schema_version": "caplab-p5-frozen-identity/1",
        "campaign_id": identity.campaign_id,
        "authorization_expires_at": "2026-07-23T23:59:59Z",
        "authorization_sha256": sha256_hex(authorization_bytes),
        "runtime_commit": runtime_commit,
        "operation_id": identity.operation_id,
        "request_sha256": identity.request_sha256,
        "content_sha256": identity.content_sha256,
        "object_key": identity.object_key,
        "local_copy_key": identity.object_key,
        "manifest_sha256": identity.manifest_sha256,
        "identity_sha256": dict(identity.identity_sha256),
        "runtime_provenance": dict(request.intent().manifest["runtime_provenance"]),
    }


def _role() -> str:
    return pwd.getpwuid(os.geteuid()).pw_name


def _require_role(command: str) -> None:
    allowed = ROLE_BY_COMMAND[command]
    role = _role()
    if role not in allowed:
        raise ConfigurationError(
            f"command {command!r} requires identity {sorted(allowed)!r}"
        )


def _stores(config: RecoveryConfig) -> tuple[S3CustodyStore, FilesystemCustodyStore]:
    credentials = load_credentials(config.credentials_root / _role() / "garage.json")
    return (
        S3CustodyStore.from_settings(
            endpoint_url=config.garage_endpoint_url,
            region=config.garage_region,
            bucket=config.garage_bucket,
            access_key_id=credentials.access_key_id,
            secret_access_key=credentials.secret_access_key,
        ),
        FilesystemCustodyStore(config.local_copy_root),
    )


def _purge_request(config: RecoveryConfig, custody_request_id: str) -> PurgeRequest:
    identity = config.authority.identity
    return PurgeRequest(
        custody_request_id=custody_request_id,
        operation_id=identity.operation_id,
        campaign_id=identity.campaign_id,
        request_sha256=identity.request_sha256,
        content_sha256=identity.content_sha256,
        manifest_sha256=identity.manifest_sha256,
        authorization_sha256=config.authority.authorization_sha256,
        expires_at=config.authority.expires_at,
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


def _emit(document: dict[str, Any], *, stream: Any = sys.stdout) -> None:
    stream.buffer.write(canonical_json(document) + b"\n")
    stream.flush()


def _load_config(args: argparse.Namespace) -> RecoveryConfig:
    config = load_trusted_recovery_config(args.config)
    config.require_active()
    _require_role(args.command)
    return config


@dataclass(frozen=True, slots=True)
class LiveContext:
    config: RecoveryConfig
    objects: S3CustodyStore
    copies: FilesystemCustodyStore
    metadata: PostgresMetadataStore
    custody: PostgresCustodyStore
    registration: RegistrationService


def _live_context(config: RecoveryConfig) -> LiveContext:
    objects, copies = _stores(config)
    metadata = PostgresMetadataStore(config.postgres_conninfo)
    return LiveContext(
        config=config,
        objects=objects,
        copies=copies,
        metadata=metadata,
        custody=PostgresCustodyStore(config.postgres_conninfo),
        registration=RegistrationService(metadata, objects, copies),
    )


def _run_identity(args: argparse.Namespace) -> int:
    _emit(
        identity_document(
            args.fixture,
            args.payload,
            args.authorization_document,
            runtime_commit=args.runtime_commit,
        )
    )
    return 0


def _require_clean_transport() -> None:
    inherited_transport_settings = sorted(
        key
        for key in os.environ
        if key.startswith("PG")
        or key in {"HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "NO_PROXY"}
    )
    if inherited_transport_settings:
        raise ConfigurationError(
            "P5 recovery requires a clean transport environment; refused inherited settings: "
            + ", ".join(inherited_transport_settings)
        )


def _run_migrate(config: RecoveryConfig) -> int:
    applied = PostgresMigrator(
        config.postgres_conninfo,
        Path(__file__).parents[1] / "runtime" / "migrations",
        config.runtime_commit,
    ).apply()
    _emit(
        {
            "schema_version": "caplab-p5-migration-receipt/1",
            "applied": [
                {"filename": migration.filename, "sha256": migration.sha256}
                for migration in applied
            ],
        }
    )
    return 0


def _run_register(args: argparse.Namespace, context: LiveContext) -> int:
    request = prepare_request(
        args.fixture,
        args.payload,
        runtime_commit=context.config.runtime_commit,
    )
    if P5Identity.from_intent(request.intent()) != context.config.authority.identity:
        raise ConfigurationError(
            "fixture and payload differ from the frozen P5 identity"
        )
    registration_metadata: Any = context.metadata
    if args.interrupt_after is not None:
        registration_metadata = InterruptAfterEvent(
            context.metadata,
            args.interrupt_after,
        )
    service = RegistrationService(
        registration_metadata,
        context.objects,
        context.copies,
    )
    _emit(_receipt(service.register(request)))
    return 0


def _run_verify(args: argparse.Namespace, context: LiveContext) -> int:
    identity = context.config.authority.identity
    record = context.metadata.registration_for_operation(identity.operation_id)
    if record is None:
        raise ValueError("frozen P5 operation is not registered")
    identity.require_record(record)
    fixture_bytes, _ = _load_fixture(args.fixture)
    report = context.registration.reconcile(
        identity.operation_id,
        expected_runtime_provenance=current_recovery_provenance(
            context.config.runtime_commit,
            fixture_bytes,
        ),
    )
    receipt = context.registration.verify(identity.operation_id)
    _emit(
        {
            **_receipt(receipt),
            "reconciliation": {
                "object_status": report.object_status,
                "local_copy_status": report.local_copy_status,
                "metadata_status": report.metadata_status,
                "locator_status": report.locator_status,
                "provenance_status": report.provenance_status,
                "ok": report.ok,
            },
        }
    )
    return 0 if report.ok else 3


def _run_inventory(context: LiveContext) -> int:
    operations, registrations, dependencies, tombstones = (
        context.custody.inventory_state()
    )
    inventory = build_orphan_inventory(
        operations=operations,
        registrations=registrations,
        object_keys=context.objects.keys(),
        copy_keys=context.copies.keys(),
        dependencies=dependencies,
    )
    _emit(
        {
            "schema_version": "caplab-p5-inventory/1",
            "operation_id": context.config.authority.identity.operation_id,
            "incomplete_requests": list(inventory.incomplete_requests),
            "unreferenced_objects": list(inventory.unreferenced_objects),
            "unreferenced_copies": list(inventory.unreferenced_copies),
            "registered_dependencies": {
                operation_id: list(entries)
                for operation_id, entries in inventory.registered_dependencies.items()
            },
            "purge_tombstones": list(tombstones),
        }
    )
    return 0


def _run_cleanup(args: argparse.Namespace, context: LiveContext) -> int:
    from caplab.runtime.__main__ import write_exclusive

    identity = context.config.authority.identity
    plan = context.registration.cleanup_plan(identity.operation_id)
    write_exclusive(args.output, canonical_json(plan) + b"\n", mode=0o440)
    _emit(
        {
            "schema_version": "caplab-p5-cleanup-plan-receipt/1",
            "operation_id": identity.operation_id,
            "plan_sha256": plan["plan_sha256"],
            "output": str(args.output),
        }
    )
    return 0


def _run_invalid(args: argparse.Namespace, context: LiveContext) -> int:
    observation = observe_invalid_attempt(
        observation_id=args.observation_id,
        campaign_id=context.config.authority.identity.campaign_id,
        fixture_bytes=args.fixture.read_bytes(),
        disposition=args.disposition,
        reason_codes=tuple(args.reason_code),
    )
    context.custody.record_invalid_observation(observation)
    _emit(observation.to_record())
    return 0


def _run_restore(command: str, context: LiveContext) -> int:
    recovery = RecoveryService(
        context.config.authority,
        context.objects,
        context.copies,
    )
    report = (
        recovery.restore_object()
        if command == "restore-object"
        else recovery.restore_copy()
    )
    _emit(
        {
            "schema_version": "caplab-p5-recovery/1",
            "operation_id": report.operation_id,
            "content_sha256": report.content_sha256,
            "action": report.action,
            "source_sha256": report.source_sha256,
            "target_sha256": report.target_sha256,
        }
    )
    return 0


def _run_replace(args: argparse.Namespace, context: LiveContext) -> int:
    identity = context.config.authority.identity
    payload = args.input.read_bytes()
    object_target = args.command == "replace-object"
    target = context.objects if object_target else context.copies
    target.replace(identity.object_key, payload)
    _emit(
        {
            "schema_version": "caplab-p5-byte-effect/1",
            "operation_id": identity.operation_id,
            "target": "object" if object_target else "copy",
            "action": "replaced",
            "observed_sha256": sha256_hex(payload),
        }
    )
    return 0


def _run_remove(command: str, context: LiveContext) -> int:
    identity = context.config.authority.identity
    object_target = command == "remove-object"
    target = context.objects if object_target else context.copies
    target.remove(identity.object_key)
    if target.read(identity.object_key) is not None:
        raise RuntimeError("P5 byte removal failed read-back")
    _emit(
        {
            "schema_version": "caplab-p5-byte-effect/1",
            "operation_id": identity.operation_id,
            "target": "object" if object_target else "copy",
            "action": "removed",
        }
    )
    return 0


def _run_request_purge(args: argparse.Namespace, context: LiveContext) -> int:
    request = _purge_request(context.config, args.custody_request_id)
    context.custody.request_purge(request)
    _emit(
        {
            "schema_version": "caplab-p5-custody-request/1",
            "custody_request_id": request.custody_request_id,
            "operation_id": request.operation_id,
            "authorization_sha256": request.authorization_sha256,
        }
    )
    return 0


def _run_dependency(args: argparse.Namespace, context: LiveContext) -> int:
    identity = context.config.authority.identity
    context.custody.record_dependency(
        operation_id=identity.operation_id,
        dependency_kind=args.kind,
        dependency_identity=args.identity,
        event_type=args.event,
    )
    _emit(
        {
            "schema_version": "caplab-p5-dependency-event/1",
            "operation_id": identity.operation_id,
            "dependency_kind": args.kind,
            "dependency_identity": args.identity,
            "event_type": args.event,
        }
    )
    return 0


def _run_purge(args: argparse.Namespace, context: LiveContext) -> int:
    identity = context.config.authority.identity
    if (
        context.objects.read(identity.object_key) is not None
        or context.copies.read(identity.object_key) is not None
    ):
        raise ValueError("P5 bytes must be absent before the database purge")
    tombstone = PurgeService(context.config.authority, context.custody).purge(
        _purge_request(context.config, args.custody_request_id),
        now=datetime.now(UTC),
    )
    _emit(
        {
            "schema_version": "caplab-p5-purge-tombstone/1",
            "custody_request_id": tombstone.custody_request_id,
            "operation_id": tombstone.operation_id,
            "campaign_id": tombstone.campaign_id,
            "request_sha256": tombstone.request_sha256,
            "content_sha256": tombstone.content_sha256,
            "manifest_sha256": tombstone.manifest_sha256,
            "authorization_sha256": tombstone.authorization_sha256,
            "purged_at": tombstone.purged_at.astimezone(UTC)
            .isoformat()
            .replace("+00:00", "Z"),
        }
    )
    return 0


def run(args: argparse.Namespace) -> int:
    if args.command == "identity":
        return _run_identity(args)
    _require_clean_transport()
    config = _load_config(args)
    if args.command == "migrate":
        return _run_migrate(config)
    context = _live_context(config)
    if args.command == "register":
        return _run_register(args, context)
    if args.command == "verify":
        return _run_verify(args, context)
    if args.command == "inventory":
        return _run_inventory(context)
    if args.command == "cleanup-plan":
        return _run_cleanup(args, context)
    if args.command == "observe-invalid":
        return _run_invalid(args, context)
    if args.command in {"restore-object", "restore-copy"}:
        return _run_restore(args.command, context)
    if args.command in {"replace-object", "replace-copy"}:
        return _run_replace(args, context)
    if args.command in {"remove-object", "remove-copy"}:
        return _run_remove(args.command, context)
    if args.command == "request-purge":
        return _run_request_purge(args, context)
    if args.command == "dependency":
        return _run_dependency(args, context)
    if args.command == "purge":
        return _run_purge(args, context)
    raise AssertionError(f"unhandled command: {args.command}")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return run(args)
    except InjectedInterruption as error:
        _emit(
            {
                "schema_version": "caplab-p5-interruption/1",
                "error_type": type(error).__name__,
                "message": str(error),
            },
            stream=sys.stderr,
        )
        return 4
    except (
        ConfigurationError,
        RecoveryError,
        RuntimeContractError,
        ValueError,
        OSError,
    ) as error:
        _emit(
            {
                "schema_version": "caplab-p5-error/1",
                "error_type": type(error).__name__,
                "message": str(error),
            },
            stream=sys.stderr,
        )
        return 2
    except Exception as error:
        _emit(
            {
                "schema_version": "caplab-p5-error/1",
                "error_type": type(error).__name__,
                "message": "unexpected P5 failure; no effect was declared successful",
            },
            stream=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
