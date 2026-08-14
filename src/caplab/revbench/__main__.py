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
from caplab.runtime.canonical import CanonicalizationError, canonical_json


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
    def error(self, message: str) -> None:
        raise RevbenchContractError(f"argument_error:{message}")


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
    execute_parser = subparsers.add_parser(
        "execute", help="execute a sealed static local fixture under authority"
    )
    execute_parser.add_argument("--manifest", type=Path, required=True)
    execute_parser.add_argument(
        "--execution-authorization-ref", type=Path, required=True
    )
    execute_parser.add_argument("--ledger", type=Path, required=True)
    execute_parser.add_argument("--output", type=Path, required=True)
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
    if args.command == "prepare":
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
        document = execute(
            _read_document(args.manifest),
            _read_document(args.execution_authorization_ref),
            registrar,
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
    except (RevbenchContractError, CanonicalizationError, OSError, ValueError) as error:
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
