"""Batch operator surface for durable qualification claims."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import os
import stat
import subprocess
import sys
import tomllib
from collections.abc import Callable, Mapping
from datetime import UTC, datetime
from pathlib import Path
from types import ModuleType
from typing import Any

from caplab.runtime.canonical import canonical_json

from .export import QualificationExportError, build_export, write_export_exclusive
from .ledger import FilesystemQualificationLedger, QualificationLedgerError


MEASUREMENT_SCHEMA = "caplab-measurement/1"
POLICY_SCHEMA = "caplab-qualification-policy/1"


class QualificationCliError(ValueError):
    """The operator request is incomplete or unsafe."""


class _Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise QualificationCliError(f"argument_error:{message}")


def build_parser() -> argparse.ArgumentParser:
    parser = _Parser(prog="caplab qualification")
    commands = parser.add_subparsers(dest="command", required=True)

    register = commands.add_parser("register")
    register.add_argument("--input", required=True, type=Path)
    register.add_argument("--kind", required=True)
    register.add_argument("--schema", required=True)
    register.add_argument("--media-type", default="application/json")
    register.add_argument("--custody", type=Path)
    _add_ledger(register)

    measure = commands.add_parser("measure")
    measure.add_argument("--input", required=True, type=Path)
    _add_ledger(measure)

    apply = commands.add_parser("apply")
    subject = apply.add_mutually_exclusive_group(required=True)
    subject.add_argument("--measurement", type=Path)
    subject.add_argument("--binding", type=Path)
    apply.add_argument("--policy", required=True, type=Path)
    apply.add_argument("--supersedes", nargs="*", default=[])
    _add_ledger(apply)

    history = commands.add_parser("history")
    _add_selector(history)
    _add_ledger(history)

    export = commands.add_parser("export")
    _add_selector(export)
    _add_ledger(export)
    export.add_argument("--output", required=True, type=Path)
    export.add_argument("--contracts", type=Path, default=_contracts_directory())
    return parser


def _add_ledger(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--ledger", required=True, type=Path)


def _add_selector(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--binding", required=True)
    parser.add_argument("--capability", required=True)
    parser.add_argument("--capability-version", required=True)


def _load_core() -> ModuleType:
    try:
        from . import core
    except ImportError as error:
        raise QualificationCliError("qualification_core_unavailable") from error
    return core


def _contracts_directory() -> Path:
    return Path(__file__).resolve().parents[3] / "docs" / "product" / "contracts"


def _now() -> datetime:
    return datetime.now(UTC)


def _producer_identity() -> tuple[str, str]:
    repository = Path(__file__).resolve().parents[3]
    try:
        version = importlib.metadata.version("agent-capability-lab")
    except importlib.metadata.PackageNotFoundError:
        try:
            with (repository / "pyproject.toml").open("rb") as stream:
                version = tomllib.load(stream)["project"]["version"]
        except (OSError, KeyError, TypeError, tomllib.TOMLDecodeError) as error:
            raise QualificationCliError("producer_version_unavailable") from error
    if not isinstance(version, str) or not version:
        raise QualificationCliError("producer_version_invalid")
    try:
        result = subprocess.run(
            ["git", "-C", str(repository), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        raise QualificationCliError("producer_commit_unavailable") from error
    commit = result.stdout.strip()
    if len(commit) not in {40, 64} or any(
        character not in "0123456789abcdef" for character in commit
    ):
        raise QualificationCliError("producer_commit_invalid")
    cleanliness = subprocess.run(
        ["git", "-C", str(repository), "diff-index", "--quiet", "HEAD", "--"],
        check=False,
        capture_output=True,
    )
    if cleanliness.returncode == 1:
        raise QualificationCliError("producer_worktree_has_tracked_changes")
    if cleanliness.returncode != 0:
        raise QualificationCliError("producer_worktree_state_unavailable")
    return version, commit


def _generated_at(clock: Callable[[], datetime]) -> str:
    instant = clock()
    if not isinstance(instant, datetime) or instant.tzinfo is None:
        raise QualificationCliError("clock_must_return_aware_datetime")
    return (
        instant.astimezone(UTC)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise QualificationCliError(f"duplicate_json_key:{key}")
        result[key] = value
    return result


def _read_document(path: Path, label: str) -> dict[str, Any]:
    flags = os.O_RDONLY | os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags)
    except OSError as error:
        raise QualificationCliError(f"{label}_open_failed") from error
    with os.fdopen(descriptor, "rb", closefd=True) as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise QualificationCliError(f"{label}_not_regular")
        payload = stream.read()
    try:
        document = json.loads(payload, object_pairs_hook=_unique_object)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise QualificationCliError(f"{label}_invalid_json") from error
    if not isinstance(document, dict):
        raise QualificationCliError(f"{label}_not_object")
    try:
        return json.loads(canonical_json(document))
    except ValueError as error:
        raise QualificationCliError(f"{label}_not_canonicalizable") from error


def _execute(
    options: argparse.Namespace,
    *,
    clock: Callable[[], datetime] = _now,
    core_loader: Callable[[], Any] = _load_core,
    producer_identity: Callable[[], tuple[str, str]] = _producer_identity,
) -> tuple[dict[str, Any], bool]:
    ledger = FilesystemQualificationLedger(options.ledger)
    if options.command == "register":
        document = _read_document(options.input, "registration_input")
        custody: Mapping[str, Any] | None = None
        if options.custody is not None:
            custody_document = _read_document(options.custody, "custody")
            custody = custody_document
        reference = ledger.register_document(
            document,
            kind=options.kind,
            schema=options.schema,
            media_type=options.media_type,
            custody=custody,
        )
        return reference, False

    core = core_loader()
    if options.command == "measure":
        measurement = _read_document(options.input, "measurement")
        validated = core.validate_measurement(measurement, ledger)
        ledger.register_document(
            validated,
            kind="measurement",
            schema=MEASUREMENT_SCHEMA,
        )
        retained = ledger.append_measurement(
            validated,
            validator=core.validate_measurement,
        )
        return retained, False

    if options.command == "apply":
        policy = _read_document(options.policy, "policy")
        validated_policy = core.validate_policy(policy, ledger)
        policy_ref = ledger.register_document(
            validated_policy,
            kind="qualification-policy",
            schema=POLICY_SCHEMA,
        )
        ledger.append_policy(validated_policy, validator=core.validate_policy)
        measurement: dict[str, Any] | None = None
        measurement_ref: dict[str, Any] | None = None
        binding: dict[str, Any] | None = None
        if options.measurement is not None:
            measurement_document = _read_document(options.measurement, "measurement")
            measurement = core.validate_measurement(measurement_document, ledger)
            measurement_ref = ledger.register_document(
                measurement,
                kind="measurement",
                schema=MEASUREMENT_SCHEMA,
            )
            ledger.append_measurement(
                measurement,
                validator=core.validate_measurement,
            )
        else:
            binding = _read_document(options.binding, "binding")
        version, commit = producer_identity()
        claim = core.build_claim(
            measurement,
            validated_policy,
            binding=binding,
            measurement_ref=measurement_ref,
            policy_ref=policy_ref,
            generated_at=_generated_at(clock),
            supersedes=options.supersedes,
            resolver=ledger,
            caplab_version=version,
            caplab_commit=commit,
        )
        retained_claim = ledger.append_claim(claim, validator=core.validate_claim)
        return retained_claim, False

    capability = ledger.resolve_capability(
        options.binding,
        options.capability,
        options.capability_version,
        validator=core.validate_claim,
    )
    if options.command == "history":
        history = ledger.history(
            options.binding,
            capability,
            validator=core.validate_claim,
        )
        return history, True
    if options.command == "export":
        version, commit = producer_identity()
        document = build_export(
            ledger,
            options.binding,
            capability,
            contracts_directory=options.contracts,
            producer_version=version,
            producer_commit=commit,
            claim_validator=core.validate_claim,
        )
        write_export_exclusive(options.output, document)
        return document, True
    raise QualificationCliError("unsupported_command")


def _core_error_type() -> type[Exception] | None:
    try:
        from .errors import QualificationContractError
    except ImportError:
        return None
    return QualificationContractError


def main(
    arguments: list[str] | None = None,
    *,
    clock: Callable[[], datetime] = _now,
) -> int:
    try:
        options = build_parser().parse_args(arguments)
        document, read_only = _execute(options, clock=clock)
    except (
        QualificationCliError,
        QualificationLedgerError,
        QualificationExportError,
    ) as error:
        sys.stderr.buffer.write(canonical_json({"error": str(error)}) + b"\n")
        return 2
    except Exception as error:
        contract_error = _core_error_type()
        if contract_error and isinstance(error, contract_error):
            sys.stderr.buffer.write(canonical_json({"error": str(error)}) + b"\n")
            return 2
        raise
    sys.stdout.buffer.write(canonical_json(document) + b"\n")
    return 3 if read_only and document.get("ok") is False else 0


if __name__ == "__main__":
    raise SystemExit(main())
