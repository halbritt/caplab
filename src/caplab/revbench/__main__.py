"""Offline command-line adapter for revbench preparation and scoring."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from caplab.revbench import RevbenchContractError, prepare, score
from caplab.revbench._core import ContentRef, JsonValue
from caplab.runtime.canonical import CanonicalizationError, canonical_json, sha256_hex


class FileArtifactRegistrar:
    """A small local content-addressed store for the standalone module CLI."""

    def __init__(self, root: Path) -> None:
        self._root = root.resolve()

    def register_document(
        self,
        document: JsonValue,
        *,
        kind: str,
        schema: str,
        registration_id: str,
    ) -> ContentRef:
        data = canonical_json(document)
        digest = sha256_hex(data)
        locator = f"objects/sha256/{digest[:2]}/{digest}"
        target = self._path_for(locator)
        target.parent.mkdir(parents=True, exist_ok=True)
        target = self._path_for(locator)
        if target.exists():
            if target.read_bytes() != data:
                raise RevbenchContractError(
                    f"existing object {locator!r} has different bytes"
                )
        else:
            _write_exclusive(target, data)
        return {
            "kind": kind,
            "schema": schema,
            "media_type": "application/json",
            "sha256": digest,
            "byte_count": len(data),
            "locator": locator,
            "registration_ref": f"revbench:{registration_id}",
            "custody": None,
        }

    def resolve(self, ref: Mapping[str, Any]) -> bytes:
        locator = ref.get("locator")
        if not isinstance(locator, str):
            raise RevbenchContractError("reference locator must be a string")
        digest = ref.get("sha256")
        if not isinstance(digest, str):
            raise RevbenchContractError("reference SHA-256 must be a string")
        expected = f"objects/sha256/{digest[:2]}/{digest}"
        if locator != expected:
            raise RevbenchContractError("reference locator is not content-derived")
        target = self._path_for(locator)
        return target.read_bytes()

    def _path_for(self, locator: str) -> Path:
        relative = Path(locator)
        if relative.is_absolute() or ".." in relative.parts:
            raise RevbenchContractError("reference locator escapes the object store")
        current = self._root
        for part in relative.parts:
            current = current / part
            if current.is_symlink():
                raise RevbenchContractError("object-store paths must not use symlinks")
        target = (self._root / relative).resolve()
        try:
            target.relative_to(self._root)
        except ValueError as error:
            raise RevbenchContractError(
                "reference locator escapes the object store"
            ) from error
        return target


def _write_exclusive(path: Path, data: bytes) -> None:
    if not path.parent.is_dir():
        raise FileNotFoundError(f"output parent does not exist: {path.parent}")
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, path)
        directory_descriptor = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory_descriptor)
        finally:
            os.close(directory_descriptor)
    finally:
        temporary.unlink(missing_ok=True)


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
    parser = argparse.ArgumentParser(prog="python -m caplab.revbench")
    subparsers = parser.add_subparsers(dest="command", required=True)
    prepare_parser = subparsers.add_parser(
        "prepare", help="prepare a verified revbench manifest"
    )
    prepare_parser.add_argument("--spec", type=Path, required=True)
    prepare_parser.add_argument("--output", type=Path, required=True)
    run_parser = subparsers.add_parser(
        "run", help="score captured native-harness reviews offline"
    )
    run_parser.add_argument("--manifest", type=Path, required=True)
    run_parser.add_argument("--reviews", type=Path, required=True)
    run_parser.add_argument("--output", type=Path, required=True)
    return parser


def run(args: argparse.Namespace) -> int:
    registrar = FileArtifactRegistrar(Path.cwd())
    if args.command == "prepare":
        document = prepare(_read_document(args.spec), registrar)
    elif args.command == "run":
        document = score(
            _read_document(args.manifest),
            _read_document(args.reviews),
            registrar,
        )
    else:
        raise AssertionError(f"unhandled command: {args.command}")
    encoded = canonical_json(document) + b"\n"
    _write_exclusive(args.output, encoded)
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
