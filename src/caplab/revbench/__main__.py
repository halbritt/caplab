"""Command-line adapter for revbench preparation, execution, and scoring."""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from caplab.qualification.export import write_export_exclusive
from caplab.qualification.ledger import FilesystemQualificationLedger
from caplab.revbench import RevbenchContractError, execute, prepare, score
from caplab.revbench._core import ContentRef, JsonValue
from caplab.revbench.codex import (
    execution_apparatus_receipt,
    validate_execution_apparatus_receipt,
)
from caplab.revbench.custody import FilesystemLiveExecutionRuntime
from caplab.runtime.canonical import CanonicalizationError, canonical_json, sha256_hex


class LedgerArtifactRegistrar:
    """Adapt the durable qualification ledger to revbench's registrar seam."""

    def __init__(self, root: Path) -> None:
        self._ledger = FilesystemQualificationLedger(Path(os.path.abspath(root)))

    def register_document(
        self,
        document: JsonValue,
        *,
        kind: str,
        schema: str,
        registration_id: str,
    ) -> ContentRef:
        del registration_id
        if not isinstance(document, dict):
            raise RevbenchContractError("registered revbench documents must be objects")
        return self._ledger.register_document(document, kind=kind, schema=schema)

    def resolve(self, ref: Mapping[str, Any]) -> bytes:
        return self._ledger.resolve(ref)

    def register_bytes(
        self,
        payload: bytes,
        *,
        kind: str,
        schema: str,
        media_type: str,
        registration_id: str,
    ) -> ContentRef:
        del registration_id
        return self._ledger.register_bytes(
            payload,
            kind=kind,
            schema=schema,
            media_type=media_type,
        )


class _Parser(argparse.ArgumentParser):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault("allow_abbrev", False)
        super().__init__(*args, **kwargs)

    def error(self, _message: str) -> None:
        # argparse includes raw option values in its default diagnostic.  Live
        # runtime arguments can contain private paths, so the public error
        # boundary deliberately emits only a stable classification.
        raise RevbenchContractError("argument_error")


def _write_exclusive(path: Path, document: Mapping[str, Any]) -> None:
    write_export_exclusive(path, document)


def _read_document(path: Path) -> dict[str, Any]:
    try:
        document = json.loads(path.read_bytes())
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise RevbenchContractError(f"{path}: is not a JSON document") from error
    if not isinstance(document, dict):
        raise RevbenchContractError(f"{path}: top-level JSON value must be an object")
    return document


def _emit(document: dict[str, Any], *, stream: Any = sys.stdout) -> None:
    stream.buffer.write(canonical_json(document) + b"\n")
    stream.flush()


def _credential_sources(values: list[str] | None) -> dict[str, str]:
    result: dict[str, str] = {}
    for value in values or []:
        if value.count("=") != 1:
            raise RevbenchContractError("credential_profile_source_invalid")
        profile, source = value.split("=", 1)
        if not profile or not source or profile in result:
            raise RevbenchContractError("credential_profile_source_invalid")
        result[profile] = source
    return result


def _paths_overlap(left: Path, right: Path) -> bool:
    try:
        left = left.resolve(strict=True)
        right = right.resolve(strict=True)
    except OSError as error:
        raise RevbenchContractError("private_runtime_path_invalid") from error
    return left == right or left in right.parents or right in left.parents


def build_parser() -> argparse.ArgumentParser:
    parser = _Parser(prog="python -m caplab.revbench")
    subparsers = parser.add_subparsers(dest="command", required=True)
    prepare_parser = subparsers.add_parser(
        "prepare", help="prepare a verified revbench manifest"
    )
    prepare_parser.add_argument("--spec", type=Path, required=True)
    prepare_parser.add_argument("--ledger", type=Path, required=True)
    prepare_parser.add_argument("--output", type=Path, required=True)
    prepare_parser.add_argument("--reference-output", type=Path)
    live_runtime_parser = subparsers.add_parser(
        "prepare-live-runtime",
        help="register no-effect live apparatus and initialize its custody domain",
    )
    live_runtime_parser.add_argument("--ledger", type=Path, required=True)
    live_runtime_parser.add_argument("--live-custody-root", type=Path, required=True)
    live_runtime_parser.add_argument("--output", type=Path, required=True)
    live_runtime_parser.add_argument("--reference-output", type=Path)
    execute_parser = subparsers.add_parser(
        "execute", help="execute an authorized local fixture or pinned live Codex slice"
    )
    execute_parser.add_argument("--manifest", type=Path, required=True)
    execute_parser.add_argument(
        "--execution-authorization-ref", type=Path, required=True
    )
    execute_parser.add_argument("--ledger", type=Path, required=True)
    execute_parser.add_argument("--output", type=Path, required=True)
    execute_parser.add_argument(
        "--live-custody-root",
        type=Path,
        help="private durable root for globally one-shot live process custody",
    )
    execute_parser.add_argument(
        "--credential-root",
        type=Path,
        help="separate owner-only directory containing live credential sources",
    )
    execute_parser.add_argument(
        "--credential-profile-source",
        action="append",
        metavar="PROFILE=FILENAME",
        help="map a registered nonsecret profile ID to one direct-child secret file",
    )
    score_parser = subparsers.add_parser(
        "score", help="score registered native-harness reviews offline"
    )
    score_parser.add_argument("--manifest", type=Path, required=True)
    score_parser.add_argument("--reviews", type=Path, required=True)
    score_parser.add_argument("--ledger", type=Path, required=True)
    score_parser.add_argument("--output", type=Path, required=True)
    return parser


def run(args: argparse.Namespace) -> int:
    registrar = LedgerArtifactRegistrar(args.ledger)
    if args.command == "prepare-live-runtime":
        if _paths_overlap(args.ledger, args.live_custody_root):
            raise RevbenchContractError("live_private_roots_must_be_disjoint")
        runtime = FilesystemLiveExecutionRuntime(args.live_custody_root)
        apparatus = validate_execution_apparatus_receipt(execution_apparatus_receipt())
        apparatus_ref = registrar.register_document(
            apparatus,
            kind="execution-apparatus-receipt",
            schema="caplab-revbench-execution-apparatus/1",
            registration_id=apparatus["apparatus_id"],
        )
        identity = {
            "schema_version": "caplab-revbench-live-authority-inputs/1",
            "apparatus_ref": apparatus_ref,
            "custody_domain_id": runtime.custody_domain_id,
        }
        document = {
            **identity,
            "authority_inputs_id": "live-authority-inputs-"
            + sha256_hex(canonical_json(identity)),
        }
        authority_inputs_ref = registrar.register_document(
            document,
            kind="live-authority-inputs",
            schema="caplab-revbench-live-authority-inputs/1",
            registration_id=document["authority_inputs_id"],
        )
        if args.reference_output is not None:
            _write_exclusive(args.reference_output, authority_inputs_ref)
    elif args.command == "prepare":
        document = prepare(_read_document(args.spec), registrar)
        manifest_ref = registrar.register_document(
            document,
            kind="revbench-manifest",
            schema="caplab-revbench-manifest/1",
            registration_id=document["experiment_id"],
        )
        if args.reference_output is not None:
            _write_exclusive(args.reference_output, manifest_ref)
    elif args.command == "execute":
        manifest = _read_document(args.manifest)
        binding = manifest.get("binding")
        provider = (
            binding.get("provider_or_path") if isinstance(binding, dict) else None
        )
        live = isinstance(provider, dict) and provider.get("kind") != "local-serving"
        runtime = None
        live_options = (
            args.live_custody_root,
            args.credential_root,
            args.credential_profile_source,
        )
        if live:
            if any(value is None for value in live_options):
                raise RevbenchContractError("live_execution_private_runtime_required")
            assert args.live_custody_root is not None
            assert args.credential_root is not None
            sources = _credential_sources(args.credential_profile_source)
            if not sources:
                raise RevbenchContractError("live_execution_private_runtime_required")
            if _paths_overlap(args.ledger, args.live_custody_root) or _paths_overlap(
                args.ledger, args.credential_root
            ):
                raise RevbenchContractError("live_private_roots_must_be_disjoint")
            runtime = FilesystemLiveExecutionRuntime(
                args.live_custody_root,
                credential_root=args.credential_root,
                credential_sources=sources,
            )
        elif any(value is not None for value in live_options):
            raise RevbenchContractError("local_fixture_rejects_live_runtime_options")
        document = execute(
            manifest,
            _read_document(args.execution_authorization_ref),
            registrar,
            live_runtime=runtime,
        )
    elif args.command == "score":
        document = score(
            _read_document(args.manifest),
            _read_document(args.reviews),
            registrar,
        )
    else:
        raise AssertionError(f"unhandled command: {args.command}")
    _write_exclusive(args.output, document)
    _emit(document)
    return 0


def main(argv: list[str] | None = None) -> int:
    try:
        return run(build_parser().parse_args(argv))
    except OSError as error:
        _emit(
            {
                "schema_version": "caplab-revbench-error/1",
                "error_type": type(error).__name__,
                "message": "filesystem_error",
            },
            stream=sys.stderr,
        )
        return 2
    except (RevbenchContractError, CanonicalizationError, ValueError) as error:
        _emit(
            {
                "schema_version": "caplab-revbench-error/1",
                "error_type": type(error).__name__,
                "message": str(error),
            },
            stream=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
