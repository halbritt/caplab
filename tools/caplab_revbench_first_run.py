#!/usr/bin/env python3
"""Scaffold and inspect the repository-owned local Revbench fixture."""

from __future__ import annotations

import argparse
import json
import os
import shlex
import shutil
import stat
import subprocess
import sys
import tempfile
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from caplab.producer import ProducerIdentityError, producer_identity
from caplab.qualification import (
    QualificationContractError,
    derive_content_id,
    validate_binding,
    validate_measurement,
)
from caplab.qualification.export import QualificationExportError, write_export_exclusive
from caplab.qualification.ledger import (
    FilesystemQualificationLedger,
    QualificationLedgerError,
)
from caplab.revbench import RevbenchContractError, prepare
from caplab.runtime.canonical import CanonicalizationError, canonical_json, sha256_hex


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_SOURCE = (
    REPOSITORY_ROOT / "examples" / "revbench-local-fixture" / "fake_native.c"
)
BUBBLEWRAP = Path("/usr/bin/bwrap")
FIXTURE_VERSION_STDOUT = b"fake-native 1\n"
FIXTURE_VERSION_STDERR = b""
CONTENT_REF_FIELDS = {
    "kind",
    "schema",
    "media_type",
    "sha256",
    "byte_count",
    "locator",
    "registration_ref",
    "custody",
}


class FirstRunError(ValueError):
    """The requested first-run workspace operation was refused."""


@dataclass(frozen=True)
class AuthorityDeclaration:
    authorized_by: str
    source: str
    valid_for_seconds: int


@dataclass(frozen=True)
class AuthorizationWindow:
    valid_from: str
    valid_until: str


@dataclass(frozen=True)
class InstalledFixture:
    ledger: FilesystemQualificationLedger
    inputs_directory: Path
    executable: Path
    source_ref: dict[str, Any]
    executable_ref: dict[str, Any]
    bubblewrap_ref: dict[str, Any]


@dataclass(frozen=True)
class RegisteredBinding:
    binding: dict[str, Any]
    native_system_contract: dict[str, Any]
    native_system_contract_ref: dict[str, Any]


@dataclass(frozen=True)
class BasisAuthorizations:
    refs: dict[str, dict[str, Any]]
    documents: dict[str, dict[str, Any]]
    delegations: dict[str, dict[str, Any]]


def _duration(value: str) -> int:
    try:
        seconds = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("must be an integer") from error
    if not 1 <= seconds <= 86400:
        raise argparse.ArgumentTypeError("must be between 1 and 86400")
    return seconds


def _authority_value(value: str) -> str:
    if not value or value != value.strip():
        raise argparse.ArgumentTypeError("must be nonempty without outer whitespace")
    return value


def _timestamp(moment: datetime) -> str:
    return moment.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _authorization_window(seconds: int) -> AuthorizationWindow:
    valid_from = datetime.now(UTC).replace(microsecond=0)
    return AuthorizationWindow(
        _timestamp(valid_from),
        _timestamp(valid_from + timedelta(seconds=seconds)),
    )


def _require_real_directory(path: Path, role: str) -> None:
    try:
        metadata = path.lstat()
    except OSError as error:
        raise FirstRunError(f"{role}_unavailable") from error
    if not stat.S_ISDIR(metadata.st_mode) or path.is_symlink():
        raise FirstRunError(f"{role}_must_be_real_directory")


def _require_real_executable(path: Path, role: str) -> None:
    try:
        metadata = path.lstat()
    except OSError as error:
        raise FirstRunError(f"{role}_unavailable") from error
    if (
        not stat.S_ISREG(metadata.st_mode)
        or path.is_symlink()
        or metadata.st_mode & 0o111 == 0
    ):
        raise FirstRunError(f"{role}_must_be_real_executable")


def _require_real_file(path: Path, role: str) -> None:
    try:
        metadata = path.lstat()
    except OSError as error:
        raise FirstRunError(f"{role}_unavailable") from error
    if not stat.S_ISREG(metadata.st_mode) or path.is_symlink():
        raise FirstRunError(f"{role}_must_be_real_file")


def _workspace_path(raw_path: Path, *, empty: bool) -> Path:
    workspace = Path(os.path.abspath(raw_path))
    if workspace == Path("/"):
        raise FirstRunError("workspace_root_refused")
    _require_real_directory(workspace.parent, "workspace_parent")
    if workspace.exists() or workspace.is_symlink():
        _require_real_directory(workspace, "workspace")
        if empty and next(workspace.iterdir(), None) is not None:
            raise FirstRunError("workspace_must_be_empty")
    elif not empty:
        raise FirstRunError("workspace_unavailable")
    return workspace


def _read_canonical_document(path: Path, role: str) -> dict[str, Any]:
    _require_real_file(path, role)
    try:
        payload = path.read_bytes()
        document = json.loads(payload)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise FirstRunError(f"{role}_invalid") from error
    if not isinstance(document, dict) or payload != canonical_json(document) + b"\n":
        raise FirstRunError(f"{role}_not_canonical")
    return document


def _write_bytes_exclusive(path: Path, payload: bytes, mode: int) -> None:
    _require_real_directory(path.parent, "output_parent")
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags, mode)
    except FileExistsError as error:
        raise FirstRunError("output_exists") from error
    except OSError as error:
        raise FirstRunError("output_open_failed") from error
    try:
        with os.fdopen(descriptor, "wb", closefd=True) as stream:
            stream.write(payload)
            stream.flush()
            os.fchmod(stream.fileno(), mode)
            os.fsync(stream.fileno())
        directory_descriptor = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory_descriptor)
        finally:
            os.close(directory_descriptor)
    except OSError as error:
        raise FirstRunError("output_write_failed") from error


def _require_outputs_absent(paths: list[Path]) -> None:
    for path in paths:
        try:
            path.lstat()
        except FileNotFoundError:
            continue
        except OSError as error:
            raise FirstRunError("output_preflight_failed") from error
        raise FirstRunError("output_exists")


def _workspace_ledger(workspace: Path) -> FilesystemQualificationLedger:
    ledger_root = workspace / "ledger"
    _require_real_directory(ledger_root, "ledger")
    return FilesystemQualificationLedger(ledger_root)


def _register_document(
    ledger: FilesystemQualificationLedger,
    document: Mapping[str, Any],
    *,
    kind: str,
    schema: str,
) -> dict[str, Any]:
    return ledger.register_document(document, kind=kind, schema=schema)


def _delegation(
    ledger: FilesystemQualificationLedger,
    *,
    effect: str,
    authority: AuthorityDeclaration,
    scope: Mapping[str, Any],
    window: AuthorizationWindow,
) -> tuple[dict[str, Any], dict[str, Any]]:
    identity = {
        "schema_version": "caplab-authorization-delegation/1",
        "effect": effect,
        "authorized_by": authority.authorized_by,
        "delegate_or_mechanism": authority.source,
        "scope": dict(scope),
        "valid_from": window.valid_from,
        "valid_until": window.valid_until,
    }
    document = {
        "delegation_id": derive_content_id(identity, "delegation_id", "delegation-"),
        **identity,
    }
    ref = _register_document(
        ledger,
        document,
        kind="authorization-delegation",
        schema="caplab-authorization-delegation/1",
    )
    return document, ref


def _materialize(path: Path, document: Mapping[str, Any]) -> None:
    write_export_exclusive(path, document)


def _configuration_documents(
    ledger: FilesystemQualificationLedger,
    executable: Path,
    command_ref: Mapping[str, Any],
    bubblewrap_ref: Mapping[str, Any],
) -> dict[str, dict[str, Any]]:
    documents = {
        "inference": (
            "inference-configuration",
            {
                "schema_version": "caplab-revbench-inference/1",
                "command_ref": command_ref,
            },
        ),
        "instructions": (
            "instructions",
            {
                "schema_version": "caplab-revbench-instructions/1",
                "instruction": (
                    "Review the artifact against the requirement and return "
                    "exactly one JSON object."
                ),
            },
        ),
        "knowledge": (
            "knowledge",
            {
                "schema_version": "caplab-revbench-disabled-surface/1",
                "surface": "knowledge",
                "mode": "none",
            },
        ),
        "tools": (
            "tools",
            {
                "schema_version": "caplab-revbench-disabled-surface/1",
                "surface": "tools",
                "mode": "none",
            },
        ),
        "permissions": (
            "permissions",
            {
                "schema_version": "caplab-revbench-execution-permissions/1",
                "environment_keys": [],
                "filesystem_mode": "read-only-root-private-cwd",
                "network_mode": "not-required",
            },
        ),
        "sandbox": (
            "sandbox",
            {
                "schema_version": "caplab-revbench-execution-sandbox/1",
                "adapter_path": str(BUBBLEWRAP),
                "adapter_ref": bubblewrap_ref,
                "root_filesystem": "read-only",
                "working_directory": "private-write",
                "network_mode": "not-required",
            },
        ),
        "runtime": (
            "runtime",
            {
                "schema_version": "caplab-revbench-execution-runtime/1",
                "executable_path": str(executable),
                "executable_format": "static-elf",
                "environment_keys": [],
                "working_directory": "temporary-empty",
                "network_mode": "not-required",
                "stdin_mode": "canonical-json",
                "stdout_mode": "single-json",
            },
        ),
    }
    refs: dict[str, dict[str, Any]] = {}
    for name, (kind, document) in documents.items():
        refs[name] = _register_document(
            ledger,
            document,
            kind=kind,
            schema="caplab-binding-configuration/1",
        )
    return refs


def _install_fixture(
    workspace: Path, executable_bytes: bytes, fixture_source_bytes: bytes
) -> InstalledFixture:
    workspace.mkdir(mode=0o750, exist_ok=True)
    fixture_directory = workspace / "fixture"
    inputs_directory = workspace / "inputs"
    fixture_directory.mkdir(mode=0o750)
    inputs_directory.mkdir(mode=0o750)
    source_copy = fixture_directory / "fake_native.c"
    executable = fixture_directory / "fake-native"
    _write_bytes_exclusive(source_copy, fixture_source_bytes, 0o440)
    _write_bytes_exclusive(executable, executable_bytes, 0o700)

    ledger = FilesystemQualificationLedger(workspace / "ledger")
    source_ref = ledger.register_bytes(
        fixture_source_bytes,
        kind="fixture-source",
        schema="caplab-revbench-local-fixture/1",
        media_type="text/x-c",
    )
    executable_ref = ledger.register_bytes(
        executable_bytes,
        kind="harness-executable",
        schema="caplab-native-executable/1",
    )
    bubblewrap_ref = ledger.register_bytes(
        BUBBLEWRAP.read_bytes(),
        kind="sandbox-executable",
        schema="caplab-native-executable/1",
    )
    return InstalledFixture(
        ledger,
        inputs_directory,
        executable,
        source_ref,
        executable_ref,
        bubblewrap_ref,
    )


def _register_binding(fixture: InstalledFixture) -> RegisteredBinding:
    ledger = fixture.ledger
    executable = fixture.executable
    provider = {
        "kind": "local-serving",
        "identifier": "caplab-local-fixture",
        "revision": "revbench-static-fixture-v1",
        "resolution": "immutable",
        "observed_at": None,
    }
    route_ref = _register_document(
        ledger,
        {"schema_version": "caplab-provider-route/1", **provider},
        kind="provider-route",
        schema="caplab-provider-route/1",
    )
    command_ref = _register_document(
        ledger,
        {
            "schema_version": "caplab-native-harness-command/1",
            "argv": [str(executable), "review"],
        },
        kind="native-harness-command",
        schema="caplab-native-harness-command/1",
    )
    version_command_ref = _register_document(
        ledger,
        {
            "schema_version": "caplab-native-harness-version-command/1",
            "argv": [str(executable), "--version"],
        },
        kind="native-harness-version-command",
        schema="caplab-native-harness-version-command/1",
    )
    version_probe_ref = _register_document(
        ledger,
        {
            "command_ref": version_command_ref,
            "exit_code": 0,
            "stdout_ref": ledger.register_bytes(
                FIXTURE_VERSION_STDOUT,
                kind="native-harness-version-stdout",
                schema="caplab-native-process-stream/1",
            ),
            "stderr_ref": ledger.register_bytes(
                FIXTURE_VERSION_STDERR,
                kind="native-harness-version-stderr",
                schema="caplab-native-process-stream/1",
            ),
        },
        kind="native-harness-version-probe",
        schema="caplab-native-harness-version-probe/1",
    )
    configuration_refs = _configuration_documents(
        ledger, executable, command_ref, fixture.bubblewrap_ref
    )
    binding_identity = {
        "schema_version": "caplab-binding/1",
        "model": {
            "model_id": "caplab/revbench-static-fixture",
            "revision": "revbench-static-fixture-v1",
            "weights_ref": None,
            "weights_unavailable_reason": "fixture has no model weights",
        },
        "provider_or_path": {**provider, "route_ref": route_ref},
        "harness": {
            "harness_id": "caplab-revbench-static-fixture",
            "harness_version": "fake-native 1",
            "executable_ref": fixture.executable_ref,
            "executable_unavailable_reason": None,
            "command_ref": command_ref,
            "version_probe_ref": version_probe_ref,
        },
        "reasoning_effort": "fixed",
        "configuration": {
            f"{name}_ref": configuration_refs[name]
            for name in (
                "inference",
                "instructions",
                "knowledge",
                "tools",
                "permissions",
                "sandbox",
                "runtime",
            )
        },
    }
    binding = {
        "binding_id": derive_content_id(binding_identity, "binding_id", "bnd-"),
        **binding_identity,
    }
    native_system_contract = {
        "schema": "caplab.native-agent-systems/v1",
        "policy": "caplab-revbench-local-fixture-v1",
        "decision_authority": "adr-0062",
        "source_observation": {"contract": "caplab-revbench-local-fixture/1"},
        "systems": {
            "caplab-revbench-static-fixture-fixed": {
                "model_id": "caplab/revbench-static-fixture",
                "native_harness_id": "caplab-revbench-static-fixture",
                "harness_version": "fake-native 1",
                "effort": "fixed",
                "executable": str(executable),
                "required_command_tokens": ["review"],
                "version_command": [str(executable), "--version"],
                "version_exit_code": 0,
                "version_stdout_sha256": sha256_hex(FIXTURE_VERSION_STDOUT),
                "version_stderr_sha256": sha256_hex(FIXTURE_VERSION_STDERR),
            }
        },
        "forbidden_proxy_markers": ["openrouter", "harbor", "terminus"],
        "exceptions": [],
    }
    native_system_contract_ref = _register_document(
        ledger,
        native_system_contract,
        kind="native-agent-systems-contract",
        schema="caplab.native-agent-systems/v1",
    )
    return RegisteredBinding(
        binding, native_system_contract, native_system_contract_ref
    )


def _fixture_cases() -> list[dict[str, Any]]:
    return [
        {
            "case_id": "case-a",
            "control": {"n": 5},
            "mutation": {
                "operator": "replace-json-value/1",
                "pointer": "/n",
                "replacement": 0,
            },
            "oracle": {
                "kind": "json-integer-minimum/1",
                "pointer": "/n",
                "minimum": 1,
            },
            "defect_anchor": "/n",
        },
        {
            "case_id": "case-b",
            "control": {"label": "b", "limits": {"minimum": 7}},
            "mutation": {
                "operator": "replace-json-value/1",
                "pointer": "/limits/minimum",
                "replacement": 2,
            },
            "oracle": {
                "kind": "json-integer-minimum/1",
                "pointer": "/limits/minimum",
                "minimum": 5,
            },
            "defect_anchor": "/limits/minimum",
        },
    ]


def _register_basis_authorizations(
    ledger: FilesystemQualificationLedger,
    shared_scope: Mapping[str, Any],
    authority: AuthorityDeclaration,
    window: AuthorizationWindow,
) -> BasisAuthorizations:
    refs: dict[str, dict[str, Any]] = {}
    documents: dict[str, dict[str, Any]] = {}
    delegations: dict[str, dict[str, Any]] = {}
    for name, role in (
        ("truth", "truth"),
        ("case_selection", "case-selection"),
        ("metric_derivation", "metric-derivation"),
    ):
        scope = {**shared_scope, "basis_role": role}
        delegation, delegation_ref = _delegation(
            ledger,
            effect="evidence-basis",
            authority=authority,
            scope=scope,
            window=window,
        )
        identity = {
            "schema_version": "caplab-evidence-basis-authorization/1",
            "authority_source_ref": delegation_ref,
            "authorized_by": authority.authorized_by,
            "delegate_or_mechanism": authority.source,
            **scope,
            "valid_from": window.valid_from,
            "valid_until": window.valid_until,
        }
        authorization = {
            "authorization_id": derive_content_id(
                identity, "authorization_id", "basis-auth-"
            ),
            **identity,
        }
        refs[name] = _register_document(
            ledger,
            authorization,
            kind="evidence-basis-authorization",
            schema="caplab-evidence-basis-authorization/1",
        )
        documents[name] = authorization
        delegations[name] = delegation
    return BasisAuthorizations(refs, documents, delegations)


def _build_scaffold(
    workspace: Path,
    *,
    authority: AuthorityDeclaration,
    executable_bytes: bytes,
    fixture_source_bytes: bytes,
) -> None:
    fixture = _install_fixture(workspace, executable_bytes, fixture_source_bytes)
    ledger = fixture.ledger
    inputs_directory = fixture.inputs_directory
    registered_binding = _register_binding(fixture)
    binding = registered_binding.binding
    native_system_contract = registered_binding.native_system_contract
    native_system_contract_ref = registered_binding.native_system_contract_ref
    cases = _fixture_cases()
    capability_card = {
        "name": "artifact-review",
        "version": "1",
        "distribution": "json-integer-minimum/1",
        "fixture_scope": "two synthetic canonical-JSON cases",
    }
    card_ref = _register_document(
        ledger,
        capability_card,
        kind="capability-card",
        schema="caplab-revbench-local-fixture/1",
    )
    capability = {
        "name": "artifact-review",
        "version": "1",
        "role": "reviewer",
        "domain": "canonical-json",
        "distribution": "json-integer-minimum/1",
        "card_ref": card_ref,
    }
    protocol = {
        "name": "revbench first-run integer-minimum protocol",
        "experiment": {"family": "revbench", "version": "1"},
        "mutation_operator": "replace-json-value/1",
        "oracle": "json-integer-minimum/1",
        "attempts_per_case": 2,
        "retries": 0,
    }
    protocol_ref = _register_document(
        ledger,
        protocol,
        kind="protocol",
        schema="caplab-revbench-local-fixture/1",
    )
    corpus = {
        "name": "revbench first-run two-case corpus",
        "population": "repository-owned synthetic local fixture",
        "case_ids": ["case-a", "case-b"],
    }
    corpus_ref = _register_document(
        ledger,
        corpus,
        kind="corpus",
        schema="caplab-revbench-local-fixture/1",
    )
    included_case_refs = sorted(
        (
            _register_document(
                ledger,
                case,
                kind="case",
                schema="caplab-revbench-case/1",
            )
            for case in cases
        ),
        key=canonical_json,
    )
    population_ref = _register_document(
        ledger,
        {"population": "repository-owned synthetic local fixture"},
        kind="case-population",
        schema="caplab-revbench-local-fixture/1",
    )
    window = _authorization_window(authority.valid_for_seconds)
    selection_scope = {
        "population_ref": population_ref,
        "included_case_refs": included_case_refs,
        "excluded_case_refs": [],
        "selection_inputs": [],
        "exclusion_inputs": [],
        "conditioned_on": [],
    }
    selection_delegation, selection_delegation_ref = _delegation(
        ledger,
        effect="case-selection",
        authority=authority,
        scope=selection_scope,
        window=window,
    )
    selection_identity = {
        "schema_version": "caplab-case-selection-manifest/1",
        **selection_scope,
        "authorization_ref": selection_delegation_ref,
    }
    selection = {
        "selection_id": derive_content_id(
            selection_identity, "selection_id", "selection-"
        ),
        **selection_identity,
    }
    selection_ref = _register_document(
        ledger,
        selection,
        kind="case-selection",
        schema="caplab-case-selection-manifest/1",
    )
    method = {
        "name": "revbench v1 mechanical integer-minimum derivation",
        "oracle": "json-integer-minimum/1",
        "selection": "explicit two-case synthetic population",
    }
    method_ref = _register_document(
        ledger,
        method,
        kind="protocol",
        schema="caplab-revbench-local-fixture/1",
    )
    basis = _register_basis_authorizations(
        ledger,
        {
            "binding_ids": [binding["binding_id"]],
            "capability": capability,
            "experiment": {"family": "revbench", "version": "1"},
            "protocol_ref": protocol_ref,
            "corpus_ref": corpus_ref,
            "case_selection_ref": selection_ref,
            "method_ref": method_ref,
            "basis_kind": "mechanical-oracle",
        },
        authority,
        window,
    )
    version, commit, package_sha256 = producer_identity()
    spec = {
        "schema_version": "caplab-revbench-spec/1",
        "binding": binding,
        "capability": capability,
        "protocol": protocol_ref,
        "corpus": corpus_ref,
        "native_system_contract_ref": native_system_contract_ref,
        "case_selection_ref": selection_ref,
        "basis_authorization_refs": {
            "truth": basis.refs["truth"],
            "case_selection": basis.refs["case_selection"],
            "metric_derivation": basis.refs["metric_derivation"],
        },
        "cases": cases,
        "provenance": {
            "caplab_version": version,
            "caplab_commit": commit,
            "caplab_package_sha256": package_sha256,
            "source_refs": [fixture.source_ref],
        },
    }
    documents = {
        "binding.json": binding,
        "capability.json": capability,
        "capability-card.json": capability_card,
        "protocol.json": protocol,
        "corpus.json": corpus,
        "method.json": method,
        "native-system-contract.json": native_system_contract,
        "case-selection-delegation.json": selection_delegation,
        "case-selection.json": selection,
        **{
            f"basis-delegation-{name.replace('_', '-')}.json": document
            for name, document in basis.delegations.items()
        },
        **{
            f"basis-authorization-{name.replace('_', '-')}.json": document
            for name, document in basis.documents.items()
        },
    }
    for filename, document in documents.items():
        _materialize(inputs_directory / filename, document)
    _materialize(workspace / "spec.json", spec)


def _compile_fixture(workspace: Path, fixture_source_bytes: bytes) -> tuple[bytes, str]:
    if sys.version_info < (3, 12):
        raise FirstRunError("python_3_12_required")
    _require_real_executable(BUBBLEWRAP, "bubblewrap")
    _require_real_file(FIXTURE_SOURCE, "fixture_source")
    compiler = shutil.which("cc")
    if compiler is None:
        raise FirstRunError("c_compiler_unavailable")
    compiler_path = Path(compiler)
    if not compiler_path.is_absolute():
        raise FirstRunError("c_compiler_path_invalid")
    with tempfile.TemporaryDirectory(
        prefix=".caplab-revbench-compile-", dir=workspace.parent
    ) as temporary:
        source = Path(temporary) / "fake_native.c"
        _write_bytes_exclusive(source, fixture_source_bytes, 0o400)
        output = Path(temporary) / "fake-native"
        command = [
            str(compiler_path),
            "-static",
            "-O2",
            "-s",
            "-o",
            str(output),
            str(source),
        ]
        try:
            completed = subprocess.run(
                command,
                env={"LC_ALL": "C", "PATH": os.defpath},
                check=False,
                capture_output=True,
                timeout=60,
            )
        except subprocess.TimeoutExpired as error:
            raise FirstRunError("static_fixture_compile_timed_out") from error
        if completed.returncode != 0:
            raise FirstRunError("static_fixture_compile_failed")
        try:
            payload = output.read_bytes()
        except OSError as error:
            raise FirstRunError("compiled_fixture_unavailable") from error
        if not payload.startswith(b"\x7fELF"):
            raise FirstRunError("compiled_fixture_not_elf")
    return payload, shlex.join(command)


def _command(arguments: list[str]) -> str:
    environment = (
        "PYTHONDONTWRITEBYTECODE=1 "
        f"PYTHONPATH={shlex.quote(str(REPOSITORY_ROOT / 'src'))}"
    )
    return f"{environment} {shlex.join([sys.executable, *arguments])}"


def _print_prepare_commands(workspace: Path) -> None:
    print("Next: prepare through the public Revbench interface:")
    print(
        _command(
            [
                "-m",
                "caplab.revbench",
                "prepare",
                "--spec",
                str(workspace / "spec.json"),
                "--ledger",
                str(workspace / "ledger"),
                "--output",
                str(workspace / "manifest.json"),
                "--reference-output",
                str(workspace / "manifest-ref.json"),
            ]
        )
    )
    print("Then create a separate execution authorization with this tool.")


def _print_execute_commands(workspace: Path) -> None:
    print("Next: execute through the authorization-gated local fixture interface:")
    print(
        _command(
            [
                "-m",
                "caplab.revbench",
                "execute",
                "--manifest",
                str(workspace / "manifest.json"),
                "--execution-authorization-ref",
                str(workspace / "execution-authorization-ref.json"),
                "--ledger",
                str(workspace / "ledger"),
                "--output",
                str(workspace / "reviews.json"),
            ]
        )
    )
    print("Then score offline through the public scorer:")
    print(
        _command(
            [
                "-m",
                "caplab.revbench",
                "score",
                "--manifest",
                str(workspace / "manifest.json"),
                "--reviews",
                str(workspace / "reviews.json"),
                "--ledger",
                str(workspace / "ledger"),
                "--output",
                str(workspace / "measurement.json"),
            ]
        )
    )
    print(
        shlex.join(
            [
                sys.executable,
                str(Path(__file__).resolve()),
                "inspect",
                str(workspace),
            ]
        )
    )


def _verify_prepared_manifest(
    workspace: Path,
    ledger: FilesystemQualificationLedger,
    manifest: Mapping[str, Any],
) -> dict[str, Any]:
    spec = _read_canonical_document(workspace / "spec.json", "spec")
    prepared_manifest = prepare(spec, ledger)
    if canonical_json(prepared_manifest) != canonical_json(manifest):
        raise FirstRunError("prepared_manifest_mismatch")
    manifest_ref = _read_canonical_document(
        workspace / "manifest-ref.json", "manifest_reference"
    )
    if ledger.resolve(manifest_ref) != canonical_json(manifest):
        raise FirstRunError("prepared_manifest_reference_mismatch")
    return manifest_ref


def scaffold(args: argparse.Namespace) -> int:
    workspace = _workspace_path(args.workspace, empty=True)
    fixture_source_bytes = FIXTURE_SOURCE.read_bytes()
    executable_bytes, compiler_command = _compile_fixture(
        workspace, fixture_source_bytes
    )
    _build_scaffold(
        workspace,
        authority=AuthorityDeclaration(
            args.authorized_by,
            args.delegation_source,
            args.valid_for_seconds,
        ),
        executable_bytes=executable_bytes,
        fixture_source_bytes=fixture_source_bytes,
    )
    print(f"Compiled the synthetic fixture with: {compiler_command}")
    print(f"Scaffolded provider-free workspace: {workspace}")
    print("No native review or provider call occurred.")
    _print_prepare_commands(workspace)
    return 0


def authorize(args: argparse.Namespace) -> int:
    workspace = _workspace_path(args.workspace, empty=False)
    authority = AuthorityDeclaration(
        args.authorized_by,
        args.delegation_source,
        args.valid_for_seconds,
    )
    output_paths = [
        workspace / "execution-delegation.json",
        workspace / "execution-authorization.json",
        workspace / "execution-authorization-ref.json",
    ]
    _require_outputs_absent(output_paths)
    manifest = _read_canonical_document(workspace / "manifest.json", "manifest")
    if manifest.get("schema_version") != "caplab-revbench-manifest/1":
        raise FirstRunError("manifest_schema_refused")
    binding = manifest.get("binding")
    if not isinstance(binding, dict):
        raise FirstRunError("manifest_binding_invalid")
    provider = binding.get("provider_or_path")
    if not isinstance(provider, dict) or (
        provider.get("kind") != "local-serving"
        or provider.get("identifier") != "caplab-local-fixture"
        or provider.get("revision") != "revbench-static-fixture-v1"
    ):
        raise FirstRunError("local_fixture_manifest_required")
    ledger = _workspace_ledger(workspace)
    manifest_ref = _verify_prepared_manifest(workspace, ledger, manifest)
    limits = {
        "max_version_probe_processes": len(manifest["cases"]) * 2,
        "max_native_review_processes": len(manifest["cases"]) * 2,
        "timeout_seconds_per_process": 30,
        "total_wall_seconds": 120,
        "max_stdout_bytes_per_process": 65536,
        "max_stderr_bytes_per_process": 65536,
    }
    scope = {
        "experiment_id": manifest["experiment_id"],
        "manifest_ref": manifest_ref,
        "binding_id": binding["binding_id"],
        "native_system_contract_ref": manifest["native_system_contract_ref"],
        "command_ref": binding["harness"]["command_ref"],
        "version_probe_ref": binding["harness"]["version_probe_ref"],
        "effect_class": "local-fixture",
        "limits": limits,
    }
    window = _authorization_window(authority.valid_for_seconds)
    delegation, delegation_ref = _delegation(
        ledger,
        effect="revbench-execution",
        authority=authority,
        scope=scope,
        window=window,
    )
    identity = {
        "schema_version": "caplab-revbench-execution-authorization/1",
        "authority_source_ref": delegation_ref,
        "authorized_by": authority.authorized_by,
        "delegate_or_mechanism": authority.source,
        **scope,
        "valid_from": window.valid_from,
        "valid_until": window.valid_until,
    }
    authorization = {
        "authorization_id": derive_content_id(
            identity, "authorization_id", "revbench-execution-auth-"
        ),
        **identity,
    }
    authorization_ref = _register_document(
        ledger,
        authorization,
        kind="revbench-execution-authorization",
        schema="caplab-revbench-execution-authorization/1",
    )
    _materialize(workspace / "execution-delegation.json", delegation)
    _materialize(workspace / "execution-authorization.json", authorization)
    _materialize(workspace / "execution-authorization-ref.json", authorization_ref)
    print(
        "Recorded operator-supplied local execution authority for "
        f"{window.valid_from} through {window.valid_until}."
    )
    print("No native review or provider call occurred.")
    _print_execute_commands(workspace)
    return 0


def _content_refs(value: object) -> list[Mapping[str, Any]]:
    if isinstance(value, dict):
        if set(value) == CONTENT_REF_FIELDS:
            return [value]
        return [ref for nested in value.values() for ref in _content_refs(nested)]
    if isinstance(value, list):
        return [ref for nested in value for ref in _content_refs(nested)]
    return []


def _resolve_reference_graph(
    documents: Mapping[str, Mapping[str, Any]],
    ledger: FilesystemQualificationLedger,
) -> dict[bytes, bytes]:
    pending = [
        ref for document in documents.values() for ref in _content_refs(document)
    ]
    resolved_payloads: dict[bytes, bytes] = {}
    while pending:
        ref = pending.pop()
        ref_key = canonical_json(ref)
        if ref_key in resolved_payloads:
            continue
        payload = ledger.resolve(ref)
        if sha256_hex(payload) != ref["sha256"]:
            raise FirstRunError("registered_reference_digest_mismatch")
        resolved_payloads[ref_key] = payload
        if ref["media_type"] != "application/json":
            continue
        try:
            nested_document = json.loads(payload)
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise FirstRunError("registered_json_invalid") from error
        if (
            not isinstance(nested_document, dict)
            or canonical_json(nested_document) != payload
        ):
            raise FirstRunError("registered_json_not_canonical")
        pending.extend(_content_refs(nested_document))
    return resolved_payloads


def inspect_workspace(args: argparse.Namespace) -> int:
    workspace = _workspace_path(args.workspace, empty=False)
    ledger = _workspace_ledger(workspace)
    documents = {
        path.relative_to(workspace).as_posix(): _read_canonical_document(
            path, "workspace_document"
        )
        for path in sorted(workspace.rglob("*.json"))
    }
    binding = documents.get("inputs/binding.json")
    if binding is None:
        raise FirstRunError("binding_unavailable")
    spec = documents.get("spec.json")
    if spec is None:
        raise FirstRunError("spec_unavailable")
    spec_binding = spec.get("binding")
    if not isinstance(spec_binding, dict) or canonical_json(
        spec_binding
    ) != canonical_json(binding):
        raise FirstRunError("workspace_binding_mismatch")
    validate_binding(binding, ledger)
    prepared_manifest = prepare(spec, ledger)
    manifest = documents.get("manifest.json")
    manifest_ref = documents.get("manifest-ref.json")
    if (manifest is None) != (manifest_ref is None):
        raise FirstRunError("prepared_manifest_pair_incomplete")
    if manifest is not None:
        if canonical_json(prepared_manifest) != canonical_json(manifest):
            raise FirstRunError("prepared_manifest_mismatch")
        if ledger.resolve(manifest_ref) != canonical_json(manifest):
            raise FirstRunError("prepared_manifest_reference_mismatch")
    reviews = documents.get("reviews.json")
    measurement = documents.get("measurement.json")
    if reviews is not None and manifest is None:
        raise FirstRunError("reviews_without_manifest")
    if measurement is not None and reviews is None:
        raise FirstRunError("measurement_without_reviews")
    if measurement is not None:
        validate_measurement(measurement, ledger)
    resolved_payloads = _resolve_reference_graph(documents, ledger)
    print(f"workspace: {workspace}")
    print(f"binding_id: {binding['binding_id']}")
    print(f"registered_refs_resolved: {len(resolved_payloads)}")
    if measurement is None:
        print("measurement: unavailable")
    else:
        print(f"measurement: {measurement['measurement_id']}")
        print(f"measurement_disposition: {measurement['disposition']}")
        print(
            "attempts: "
            f"planned={measurement['sample_flow']['planned']} "
            f"attempted={measurement['sample_flow']['attempted']} "
            f"usable={measurement['sample_flow']['usable']}"
        )
        for name, metric in sorted(measurement["metrics"].items()):
            value = metric["value"]
            print(f"{name}: {value['numerator']}/{value['denominator']}")
    print("configured_subject: local-fixture")
    print("qualification_evaluation: not performed by this tool")
    print("acceptance_evaluation: not performed by this tool")
    print("provider_execution: unavailable for this local-fixture subject")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create and inspect a provider-free CAPLAB Revbench first run."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    scaffold_parser = subparsers.add_parser(
        "scaffold", help="create one new or empty local-fixture workspace"
    )
    scaffold_parser.add_argument("workspace", type=Path)
    scaffold_parser.add_argument(
        "--authorized-by", required=True, type=_authority_value
    )
    scaffold_parser.add_argument(
        "--delegation-source", required=True, type=_authority_value
    )
    scaffold_parser.add_argument("--valid-for-seconds", required=True, type=_duration)
    scaffold_parser.set_defaults(operation=scaffold)

    authorize_parser = subparsers.add_parser(
        "authorize", help="record exact operator-supplied local execution authority"
    )
    authorize_parser.add_argument("workspace", type=Path)
    authorize_parser.add_argument(
        "--authorized-by", required=True, type=_authority_value
    )
    authorize_parser.add_argument(
        "--delegation-source", required=True, type=_authority_value
    )
    authorize_parser.add_argument("--valid-for-seconds", required=True, type=_duration)
    authorize_parser.set_defaults(operation=authorize)

    inspect_parser = subparsers.add_parser(
        "inspect", help="resolve retained references without changing the workspace"
    )
    inspect_parser.add_argument("workspace", type=Path)
    inspect_parser.set_defaults(operation=inspect_workspace)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.operation(args)
    except (
        CanonicalizationError,
        FirstRunError,
        OSError,
        ProducerIdentityError,
        QualificationContractError,
        QualificationExportError,
        QualificationLedgerError,
        RevbenchContractError,
    ) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
