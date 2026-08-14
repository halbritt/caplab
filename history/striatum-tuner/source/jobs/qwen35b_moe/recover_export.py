"""Recover a validated completed run without repeating training or full eval."""

from __future__ import annotations

import argparse
from collections.abc import Iterable
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

from .contract import ContractError, sha256_file
from .evaluate import PARITY_MAX_NEW_TOKENS
from .package import (
    _validate_hf_reference,
    validate_completed_training_and_evaluation,
    validate_export_receipt,
    validate_runtime_evidence,
)
from .runtime import (
    base_gguf_from_env,
    input_dir_from_env,
    model_dir_from_env,
    output_dir_from_env,
)


_RUN_ID = re.compile(r"run-[0-9]{8}T[0-9]{6}-[0-9a-f]{12}")


def _run(command: list[str]) -> None:
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as error:
        raise ContractError(
            f"recovery child failed with exit {error.returncode}: {command!r}"
        ) from error


def _atomic_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, raw_temp = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(raw_temp)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(value, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise


def _copy_regular_tree(source: Path, destination: Path) -> None:
    if source.is_symlink() or not source.is_dir():
        raise ContractError(f"recovery source is not a regular directory: {source}")
    if destination.exists() or destination.is_symlink():
        raise ContractError(f"recovery destination already exists: {destination}")
    destination.mkdir(parents=True)
    for path in sorted(source.rglob("*")):
        if path.is_symlink():
            raise ContractError(f"recovery source contains a symlink: {path}")
        relative = path.relative_to(source)
        target = destination / relative
        if path.is_dir():
            target.mkdir()
        elif path.is_file():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target, follow_symlinks=False)
        else:
            raise ContractError(f"recovery source is not regular: {path}")


def _copy_regular_files(source_root: Path, output_root: Path, paths: Iterable[str]) -> None:
    for relative_text in paths:
        relative = Path(relative_text)
        source = source_root / relative
        target = output_root / relative
        if source.is_symlink() or not source.is_file():
            raise ContractError(f"recovery source file is absent or linked: {source}")
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() or target.is_symlink():
            raise ContractError(f"recovery destination already exists: {target}")
        shutil.copy2(source, target, follow_symlinks=False)


def _artifact_manifest(run_root: Path, source_run_id: str) -> dict[str, object]:
    files: list[dict[str, object]] = []
    for directory_name in ("artifacts", "checkpoints", "eval"):
        for path in sorted((run_root / directory_name).rglob("*")):
            if path.is_symlink():
                raise ContractError(f"recovered artifact symlink is forbidden: {path}")
            if path.is_file():
                files.append(
                    {
                        "path": path.relative_to(run_root).as_posix(),
                        "size": path.stat().st_size,
                        "sha256": sha256_file(path),
                    }
                )
    if not files:
        raise ContractError("recovery produced no artifacts")
    return {
        "protocol": "artifact-manifest/1",
        "result": "workload-succeeded-model-acceptance-pending",
        "model_acceptance_requires_local_fate_scoring": True,
        "recovered_from_run_id": source_run_id,
        "files": files,
    }


def recover(
    *,
    source_run_root: Path,
    source_run_id: str,
    output: Path,
    model_dir: Path,
    input_dir: Path,
    base_gguf: Path,
    llama_cpp: Path,
) -> dict[str, object]:
    if _RUN_ID.fullmatch(source_run_id) is None:
        raise ContractError("source run ID is invalid")
    source_run_root = source_run_root.resolve()
    output = output.resolve()
    if source_run_root.name != source_run_id:
        raise ContractError("source run root does not match the declared run ID")
    if source_run_root == output:
        raise ContractError("recovery output must be separate from the source run")

    source_evidence = validate_completed_training_and_evaluation(source_run_root)
    validate_runtime_evidence(source_run_root)

    _copy_regular_tree(
        source_run_root / "checkpoints/checkpoint-318",
        output / "checkpoints/checkpoint-318",
    )
    _copy_regular_tree(
        source_run_root / "checkpoints/final-adapter",
        output / "checkpoints/final-adapter",
    )
    _copy_regular_files(
        source_run_root,
        output,
        (
            "artifacts/train-phase/train-phase.json",
            "eval/full/results.jsonl",
            "eval/full/summary.json",
        ),
    )

    parity = output / "eval/parity"
    _run(
        [
            sys.executable,
            "-m",
            "jobs.qwen35b_moe.evaluate",
            "--model-dir",
            str(model_dir),
            "--input-dir",
            str(input_dir),
            "--adapter",
            str(output / "checkpoints/final-adapter"),
            "--output",
            str(parity),
            "--limit",
            "1",
            "--max-new-tokens",
            str(PARITY_MAX_NEW_TOKENS),
            "--deterministic",
            "--bf16-base",
            "--require-valid-output",
        ]
    )
    final_dir = output / "artifacts/final"
    _run(
        [
            sys.executable,
            "-m",
            "jobs.qwen35b_moe.export",
            "--model-dir",
            str(model_dir),
            "--adapter",
            str(output / "checkpoints/final-adapter"),
            "--base-gguf",
            str(base_gguf),
            "--hf-reference",
            str(parity / "hf-reference.json"),
            "--llama-cpp",
            str(llama_cpp),
            "--output",
            str(final_dir / "adapter-f32.gguf"),
            "--receipt",
            str(final_dir / "export.json"),
        ]
    )
    _validate_hf_reference(parity / "hf-reference.json")
    validate_export_receipt(
        final_dir / "export.json",
        final_dir / "adapter-f32.gguf",
        output / "checkpoints/final-adapter",
    )
    validate_runtime_evidence(output)
    recovery_receipt = {
        "protocol": "striatum-export-recovery/1",
        "source_run_id": source_run_id,
        "source_evidence": source_evidence,
        "post_training_inference": {
            "summary_sha256": sha256_file(parity / "summary.json"),
            "results_sha256": sha256_file(parity / "results.jsonl"),
            "hf_reference_sha256": sha256_file(parity / "hf-reference.json"),
        },
        "export_receipt_sha256": sha256_file(final_dir / "export.json"),
        "outcome": "recovered-without-retraining",
    }
    _atomic_json(output / "artifacts/recovery/recovery.json", recovery_receipt)
    manifest = _artifact_manifest(output, source_run_id)
    _atomic_json(output / "artifact-manifest.json", manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-run-id", required=True)
    parser.add_argument(
        "--runs-root", type=Path, default=Path("/workspace/runpod-jobrunner/runs")
    )
    parser.add_argument("--output", type=Path, default=output_dir_from_env())
    parser.add_argument("--model-dir", type=Path, default=model_dir_from_env())
    parser.add_argument("--input-dir", type=Path, default=input_dir_from_env())
    parser.add_argument("--base-gguf", type=Path, default=base_gguf_from_env())
    parser.add_argument("--llama-cpp", type=Path, default=Path("/opt/llama.cpp"))
    args = parser.parse_args()
    runs_root = args.runs_root.resolve()
    source_candidate = runs_root / args.source_run_id
    if source_candidate.is_symlink():
        raise ContractError("source run root must not be a symlink")
    source = source_candidate.resolve()
    try:
        source.relative_to(runs_root)
    except ValueError:
        raise ContractError("source run root escapes the runs root") from None
    manifest = recover(
        source_run_root=source,
        source_run_id=args.source_run_id,
        output=args.output,
        model_dir=args.model_dir.resolve(),
        input_dir=args.input_dir.resolve(),
        base_gguf=args.base_gguf.resolve(),
        llama_cpp=args.llama_cpp.resolve(),
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
