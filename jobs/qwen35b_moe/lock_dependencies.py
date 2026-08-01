"""Generate or verify the platform-specific, hash-locked release inputs."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import tempfile

from .contract import ContractError


ROOT = Path(__file__).resolve().parent
LOCKS = (
    ("requirements.in", "requirements.lock", False),
    ("requirements-gpu.in", "requirements-gpu.lock", True),
    ("requirements-smoke.in", "requirements-smoke.lock", False),
)


def _compile(source: str, output: Path, no_deps: bool) -> None:
    command = [
        "uv",
        "pip",
        "compile",
        str(ROOT / source),
        "--python-version",
        "3.12",
        "--python-platform",
        "x86_64-manylinux_2_28",
        "--generate-hashes",
        "--no-annotate",
        "--custom-compile-command",
        "python3 -m jobs.qwen35b_moe.lock_dependencies",
        "--output-file",
        str(output),
    ]
    if no_deps:
        command.append("--no-deps")
    try:
        subprocess.run(command, cwd=ROOT.parents[1], check=True)
    except (OSError, subprocess.CalledProcessError) as error:
        raise ContractError(f"dependency lock generation failed: {source}") from error


def generate(check: bool) -> None:
    if not check:
        for source, target, no_deps in LOCKS:
            _compile(source, ROOT / target, no_deps)
        return
    with tempfile.TemporaryDirectory(prefix="qwen35b-lock-check-") as raw_temp:
        temporary = Path(raw_temp)
        stale: list[str] = []
        for source, target, no_deps in LOCKS:
            candidate = temporary / target
            _compile(source, candidate, no_deps)
            committed = ROOT / target
            if not committed.is_file() or candidate.read_bytes() != committed.read_bytes():
                stale.append(target)
        if stale:
            raise ContractError(
                "dependency locks are absent or stale: " + ", ".join(stale)
            )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    generate(args.check)


if __name__ == "__main__":
    main()
