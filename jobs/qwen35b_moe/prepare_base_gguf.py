"""Convert the staged revision to the parity GGUF before the paid run."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

from .census import census_snapshot
from .contract import ContractError, sha256_file
from .export import LLAMA_CPP_COMMIT


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(command, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as error:
        raise ContractError(
            f"base GGUF preparation failed with exit {error.returncode}: {command!r}"
        ) from error


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-dir", type=Path, required=True)
    parser.add_argument("--llama-cpp", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    census_snapshot(args.model_dir)
    commit = _run(
        ["git", "-C", str(args.llama_cpp), "rev-parse", "HEAD"]
    ).stdout.strip()
    if commit != LLAMA_CPP_COMMIT:
        raise ContractError(
            f"llama.cpp commit mismatch: {commit} != {LLAMA_CPP_COMMIT}"
        )
    converter = args.llama_cpp / "convert_hf_to_gguf.py"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    _run(
        [
            sys.executable,
            str(converter),
            "--outfile",
            str(args.output),
            "--outtype",
            "bf16",
            str(args.model_dir),
        ]
    )
    if not args.output.is_file() or args.output.stat().st_size == 0:
        raise ContractError("base conversion produced no GGUF")
    receipt = {
        "protocol": "striatum-base-gguf-readiness/1",
        "model_revision": census_snapshot(args.model_dir)["model"]["revision"],
        "llama_cpp_commit": LLAMA_CPP_COMMIT,
        "path": str(args.output),
        "size": args.output.stat().st_size,
        "sha256": sha256_file(args.output),
    }
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
