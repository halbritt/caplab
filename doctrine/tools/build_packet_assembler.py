#!/usr/bin/env python3
"""Build the CGO-free doctrine packet assembler with a content identity."""

from __future__ import annotations

import argparse
import hashlib
import os
import subprocess
import sys
import tempfile
from pathlib import Path

DOCTRINE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = DOCTRINE_ROOT / "bin" / "assemble-packet"


def source_paths() -> list[Path]:
    paths = [
        DOCTRINE_ROOT / "go.mod",
        DOCTRINE_ROOT / "go.sum",
        Path(__file__).resolve(),
    ]
    paths.extend(sorted((DOCTRINE_ROOT / "cmd" / "assemble-packet").glob("*.go")))
    paths.extend(sorted((DOCTRINE_ROOT / "internal" / "packet").glob("*.go")))
    return sorted(paths, key=lambda path: path.relative_to(DOCTRINE_ROOT).as_posix())


def retriever_version() -> str:
    digest = hashlib.sha256()
    for path in source_paths():
        relative = path.relative_to(DOCTRINE_ROOT).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    return f"retriever-{digest.hexdigest()[:16]}"


def build_binary(output: Path, go: str) -> bool:
    output.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{output.name}.", suffix=".tmp", dir=output.parent
    )
    os.close(descriptor)
    temporary = Path(temporary_name)
    temporary.unlink()
    version = retriever_version()
    environment = os.environ.copy()
    environment.update(
        {
            "CGO_ENABLED": "0",
            "GOFLAGS": "-mod=readonly",
            "GOTOOLCHAIN": environment.get("GOTOOLCHAIN", "local"),
        }
    )
    command = [
        go,
        "build",
        "-buildvcs=false",
        "-trimpath",
        "-ldflags=-buildid= -s -w "
        f"-X main.retrieverVersion={version}",
        "-o",
        str(temporary),
        "./cmd/assemble-packet",
    ]
    try:
        completed = subprocess.run(
            command,
            cwd=DOCTRINE_ROOT,
            env=environment,
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0:
            details = completed.stderr.strip() or completed.stdout.strip()
            raise RuntimeError(
                f"Go assembler build exited with status {completed.returncode}: {details}"
            )
        if output.is_file() and output.read_bytes() == temporary.read_bytes():
            temporary.unlink()
            return False
        os.replace(temporary, output)
        return True
    finally:
        temporary.unlink(missing_ok=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--go", default=os.environ.get("GO", "go"))
    parser.add_argument(
        "--print-version",
        action="store_true",
        help="print the content-derived retriever version without building",
    )
    return parser


def main(arguments: list[str] | None = None) -> int:
    options = build_parser().parse_args(arguments)
    if options.print_version:
        print(retriever_version())
        return 0
    try:
        changed = build_binary(options.out.resolve(), options.go)
    except (OSError, RuntimeError) as error:
        print(error, file=sys.stderr)
        return 1
    disposition = "wrote" if changed else "current"
    print(
        f"doctrine assembler: {disposition} ({options.out.resolve()}; "
        f"{retriever_version()})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
