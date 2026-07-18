"""Bounded CLI for read-only CAPLAB Study 001 recomputation."""

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

from .adapters.postgres import PostgresRecomputationStore
from .config import CONFIG_PATH, RecomputationConfig, load_trusted_config
from .service import RecomputationMismatch, RecomputationService


ROLE_BY_COMMAND = {"recompute": {"caplab_reader"}}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m caplab.recomputation")
    parser.add_argument("--config", type=Path, default=CONFIG_PATH)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser(
        "recompute", help="recompute the frozen registered Study 001 result"
    )
    return parser


def _role() -> str:
    return pwd.getpwuid(os.geteuid()).pw_name


def _require_role(command: str, role: str) -> None:
    if role not in ROLE_BY_COMMAND[command]:
        raise ConfigurationError(
            f"command {command!r} requires identity {sorted(ROLE_BY_COMMAND[command])!r}"
        )


def _service(config: RecomputationConfig, role: str) -> RecomputationService:
    credentials = load_credentials(config.credentials_root / role / "garage.json")
    objects = S3ObjectStore.from_settings(
        endpoint_url=config.garage_endpoint_url,
        region=config.garage_region,
        bucket=config.garage_bucket,
        access_key_id=credentials.access_key_id,
        secret_access_key=credentials.secret_access_key,
    )
    return RecomputationService(
        PostgresRecomputationStore(config.postgres_conninfo),
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
            "recomputation requires a clean transport environment; refused: "
            + ", ".join(inherited)
        )
    config = load_trusted_config(args.config)
    config.require_active()
    role = _role()
    _require_role(args.command, role)
    if args.command == "recompute":
        result = _service(config, role).recompute(
            config.admission_manifest_sha256,
            implementation_commit=config.source_commit,
        )
        _emit(result)
        return 0
    raise AssertionError(f"unhandled command: {args.command}")


def main(argv: list[str] | None = None) -> int:
    try:
        return run(build_parser().parse_args(argv))
    except (
        ConfigurationError,
        RecomputationMismatch,
        RuntimeContractError,
        ValueError,
        OSError,
    ) as error:
        _emit(
            {
                "schema_version": "caplab-study-recomputation-error/1",
                "error_type": type(error).__name__,
                "message": str(error),
            },
            stream=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
