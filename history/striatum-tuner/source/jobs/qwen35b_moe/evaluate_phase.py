"""Run full evaluation, a deterministic parity sample, then final export."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys

from .contract import ContractError
from .evaluate import PARITY_MAX_NEW_TOKENS
from .runtime import (
    base_gguf_from_env,
    input_dir_from_env,
    model_dir_from_env,
    output_dir_from_env,
)


def _run(command: list[str]) -> None:
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as error:
        raise ContractError(
            f"evaluation phase child failed with exit {error.returncode}: {command!r}"
        ) from error


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-dir", type=Path, default=model_dir_from_env())
    parser.add_argument("--input-dir", type=Path, default=input_dir_from_env())
    parser.add_argument(
        "--adapter",
        type=Path,
        default=output_dir_from_env() / "checkpoints/final-adapter",
    )
    parser.add_argument("--output", type=Path, default=output_dir_from_env())
    parser.add_argument(
        "--base-gguf",
        type=Path,
        default=base_gguf_from_env(),
    )
    parser.add_argument(
        "--llama-cpp",
        type=Path,
        default=Path(os.environ.get("STRIATUM_LLAMA_CPP", "/opt/llama.cpp")),
    )
    args = parser.parse_args()
    full_eval = args.output / "eval/full"
    parity_eval = args.output / "eval/parity"
    common = [
        "--model-dir",
        str(args.model_dir),
        "--input-dir",
        str(args.input_dir),
        "--adapter",
        str(args.adapter),
    ]
    _run(
        [
            sys.executable,
            "-m",
            "jobs.qwen35b_moe.evaluate",
            *common,
            "--output",
            str(full_eval),
            "--enforce-available-gates",
        ]
    )
    _run(
        [
            sys.executable,
            "-m",
            "jobs.qwen35b_moe.evaluate",
            *common,
            "--output",
            str(parity_eval),
            "--limit",
            "1",
            "--max-new-tokens",
            str(PARITY_MAX_NEW_TOKENS),
            "--deterministic",
            "--bf16-base",
            "--require-valid-output",
        ]
    )
    _run(
        [
            sys.executable,
            "-m",
            "jobs.qwen35b_moe.export",
            "--model-dir",
            str(args.model_dir),
            "--adapter",
            str(args.adapter),
            "--base-gguf",
            str(args.base_gguf),
            "--hf-reference",
            str(parity_eval / "hf-reference.json"),
            "--llama-cpp",
            str(args.llama_cpp),
            "--output",
            str(args.output / "artifacts/final/adapter-f32.gguf"),
            "--receipt",
            str(args.output / "artifacts/final/export.json"),
        ]
    )


if __name__ == "__main__":
    main()
