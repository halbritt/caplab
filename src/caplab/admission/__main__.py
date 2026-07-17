"""Bounded CLI for P6 source verification, admission, and reconciliation."""

from __future__ import annotations

import argparse
import os
import pwd
import sys
from pathlib import Path

from caplab.runtime.adapters.filesystem import FilesystemCopyStore
from caplab.runtime.adapters.s3 import S3ObjectStore
from caplab.runtime.canonical import canonical_json
from caplab.runtime.config import ConfigurationError, load_credentials
from caplab.runtime.errors import RuntimeContractError

from .adapters.postgres import PostgresAdmissionStore
from .config import CONFIG_PATH, AdmissionConfig, load_trusted_config
from .service import AdmissionService
from .source import DirectoryGitReader, SourceMismatch, build_manifest
from .study001 import source_set


ROLE_BY_COMMAND = {
    "source-verify": {"caplab_writer", "caplab_verifier"},
    "admit": {"caplab_writer"},
    "verify": {"caplab_verifier"},
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m caplab.admission")
    parser.add_argument("--config", type=Path, default=CONFIG_PATH)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("source-verify", help="verify the exact frozen P6 source set")
    subparsers.add_parser("admit", help="register and freeze the exact P6 source set")
    verify = subparsers.add_parser(
        "verify", help="reconcile the frozen P6 registration"
    )
    verify.add_argument("--manifest-sha256", required=True)
    return parser


def _role() -> str:
    return pwd.getpwuid(os.geteuid()).pw_name


def _require_role(command: str, role: str) -> None:
    if role not in ROLE_BY_COMMAND[command]:
        raise ConfigurationError(
            f"command {command!r} requires identity {sorted(ROLE_BY_COMMAND[command])!r}"
        )


def _service(config: AdmissionConfig, role: str) -> AdmissionService:
    credentials = load_credentials(config.credentials_root / role / "garage.json")
    objects = S3ObjectStore.from_settings(
        endpoint_url=config.garage_endpoint_url,
        region=config.garage_region,
        bucket=config.garage_bucket,
        access_key_id=credentials.access_key_id,
        secret_access_key=credentials.secret_access_key,
    )
    return AdmissionService(
        PostgresAdmissionStore(config.postgres_conninfo),
        objects,
        FilesystemCopyStore(config.local_copy_root),
    )


def _emit(document: dict[str, object], *, stream: object = sys.stdout) -> None:
    stream.buffer.write(canonical_json(document) + b"\n")
    stream.flush()


def run(args: argparse.Namespace) -> int:
    inherited = sorted(
        key
        for key in os.environ
        if key.startswith("PG")
        or key in {"HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "NO_PROXY"}
    )
    if inherited:
        raise ConfigurationError(
            "admission requires a clean transport environment; refused: "
            + ", ".join(inherited)
        )
    config = load_trusted_config(args.config)
    config.require_active()
    role = _role()
    _require_role(args.command, role)
    reader = DirectoryGitReader(config.git_stage)
    source = source_set(preservation_root=config.preservation_root)
    if args.command == "source-verify":
        manifest = build_manifest(source, git_reader=reader)
        _emit(
            {
                "schema_version": "caplab-study-source-verification/1",
                "study_id": manifest["study_id"],
                "manifest_sha256": manifest["manifest_sha256"],
                "summary": manifest["summary"],
                "status": "match",
            }
        )
        return 0
    service = _service(config, role)
    if args.command == "admit":
        receipt = service.admit(source, git_reader=reader)
        _emit(
            {
                "schema_version": "caplab-study-admission-receipt/1",
                "study_id": receipt.study_id,
                "manifest_sha256": receipt.manifest_sha256,
                "record_count": receipt.record_count,
                "unique_content_count": receipt.unique_content_count,
                "idempotent_replay": receipt.idempotent_replay,
            }
        )
        return 0
    if args.command == "verify":
        report = service.verify(args.manifest_sha256)
        _emit(
            {
                "schema_version": "caplab-study-admission-verification/1",
                "manifest_sha256": report.manifest_sha256,
                "metadata_status": report.metadata_status,
                "object_status": report.object_status,
                "local_copy_status": report.local_copy_status,
                "record_count": report.record_count,
                "unique_content_count": report.unique_content_count,
                "ok": report.ok,
            }
        )
        return 0 if report.ok else 3
    raise AssertionError(f"unhandled command: {args.command}")


def main(argv: list[str] | None = None) -> int:
    try:
        return run(build_parser().parse_args(argv))
    except (
        ConfigurationError,
        RuntimeContractError,
        SourceMismatch,
        ValueError,
        OSError,
    ) as error:
        _emit(
            {
                "schema_version": "caplab-study-admission-error/1",
                "error_type": type(error).__name__,
                "message": str(error),
            },
            stream=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
