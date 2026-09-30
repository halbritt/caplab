"""``caplab catalog``: read-only discovery of shared-catalog routes for this consumer."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from caplab.catalog.discovery import discover, load_native_policy
from caplab.catalog.projection import CatalogSelectionError, load_projection
from caplab.qualification.export import write_export_exclusive
from caplab.runtime.canonical import canonical_json


class _Parser(argparse.ArgumentParser):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault("allow_abbrev", False)
        super().__init__(*args, **kwargs)

    def error(self, _message: str) -> None:
        # argparse echoes raw option values; only a stable classification leaves here.
        raise CatalogSelectionError("argument_error")


def quartermaster_argv(value: str) -> list[str]:
    """Parse the explicit ``--quartermaster-argv`` JSON list of command tokens."""

    try:
        argv = json.loads(value)
    except ValueError as error:
        raise CatalogSelectionError("catalog_quartermaster_argv_invalid") from error
    if not isinstance(argv, list) or not argv or not all(isinstance(t, str) and t for t in argv):
        raise CatalogSelectionError("catalog_quartermaster_argv_invalid")
    return argv


def add_catalog_arguments(parser: argparse.ArgumentParser, *, prefix: str = "") -> None:
    parser.add_argument(f"--{prefix}release", type=Path, required=not prefix)
    parser.add_argument(f"--{prefix}overlay", type=Path, required=not prefix)
    parser.add_argument("--quartermaster-argv", required=not prefix,
                        help='JSON list, for example ["/home/me/.local/bin/quartermaster"]')


def build_parser() -> argparse.ArgumentParser:
    parser = _Parser(prog="caplab catalog", description="Shared-catalog discovery (proposal only).")
    commands = parser.add_subparsers(dest="command", required=True)
    find = commands.add_parser("discover", help="list catalog routes projected for Caplab")
    add_catalog_arguments(find)
    find.add_argument("--native-policy", type=Path,
                      help="the digest-pinned native-agent-systems contract, to report admission")
    find.add_argument("--sweep-config", type=Path,
                      help="advisory sweep configuration, to warn about dropped supervised runtimes")
    find.add_argument("--output", type=Path)
    return parser


def run(arguments: argparse.Namespace) -> int:
    projection = load_projection(
        arguments.release, arguments.overlay, quartermaster_argv(arguments.quartermaster_argv)
    )
    policy = load_native_policy(arguments.native_policy) if arguments.native_policy else None
    sweep = None
    if arguments.sweep_config:
        try:
            sweep = json.loads(arguments.sweep_config.read_bytes())
        except (OSError, ValueError) as error:
            raise CatalogSelectionError("catalog_sweep_config_invalid") from error
    document = discover(projection, policy=policy, sweep_config=sweep)
    if arguments.output is not None:
        write_export_exclusive(arguments.output, document)
    sys.stdout.buffer.write(canonical_json(document) + b"\n")
    sys.stdout.flush()
    return 0


def main(argv: list[str] | None = None) -> int:
    try:
        return run(build_parser().parse_args(argv))
    except (CatalogSelectionError, OSError) as error:
        code = "filesystem_error" if isinstance(error, OSError) else str(error)
        sys.stderr.buffer.write(
            canonical_json({"schema_version": "caplab-catalog-error/1", "code": code}) + b"\n"
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
