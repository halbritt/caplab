"""File-to-canonical-document boundary for capability-profile proposals."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from caplab.runtime.canonical import canonical_json

from . import ProfileMismatch, build_profile


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m caplab.profile")
    parser.add_argument("--recomputation", required=True, type=Path)
    parser.add_argument("--card", required=True, type=Path)
    parser.add_argument("--selection", required=True, type=Path)
    return parser


def _load_document(path: Path) -> dict[str, object]:
    parsed = json.loads(path.read_bytes())
    if not isinstance(parsed, dict):
        raise ProfileMismatch(f"{path} is not a JSON object")
    return parsed


def _emit(document: dict[str, object], *, stream: object = sys.stdout) -> None:
    stream.buffer.write(canonical_json(document) + b"\n")
    stream.flush()


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = build_profile(
            _load_document(args.recomputation),
            args.card.read_bytes(),
            args.selection.read_bytes(),
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ProfileMismatch) as error:
        _emit(
            {
                "schema_version": "caplab-capability-profile-proposal-error/1",
                "error_type": type(error).__name__,
                "message": str(error),
            },
            stream=sys.stderr,
        )
        return 2
    _emit(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
