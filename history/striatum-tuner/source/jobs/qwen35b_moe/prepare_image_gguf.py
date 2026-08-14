"""Create and receipt native GGUF shards suitable for OCI image layers."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import tempfile

from .base_gguf import (
    SPLIT_MAX_SIZE,
    SPLIT_RECEIPT_NAME,
    discover_split_shards,
    validate_base_gguf_artifacts,
    validate_source_receipt,
)
from .contract import MODEL, ContractError, sha256_file
from .export import LLAMA_CPP_COMMIT


def _run(command: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(command, check=True, text=True, **kwargs)
    except subprocess.CalledProcessError as error:
        raise ContractError(
            f"GGUF split command failed with exit {error.returncode}: {command!r}"
        ) from error


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-dir", type=Path, required=True)
    parser.add_argument("--llama-cpp", type=Path, required=True)
    args = parser.parse_args()
    model_dir = args.model_dir.resolve()
    llama_cpp = args.llama_cpp.resolve()
    source, source_receipt = validate_source_receipt(model_dir)
    commit = _run(
        ["git", "-C", str(llama_cpp), "rev-parse", "HEAD"], capture_output=True
    ).stdout.strip()
    if commit != LLAMA_CPP_COMMIT:
        raise ContractError(
            f"llama.cpp commit mismatch: {commit} != {LLAMA_CPP_COMMIT}"
        )
    splitter = llama_cpp / "build/bin/llama-gguf-split"
    if not splitter.is_file():
        raise ContractError(f"pinned llama-gguf-split binary is missing: {splitter}")

    existing = tuple(model_dir.glob("base-bf16-*-of-*.gguf"))
    if not existing:
        with tempfile.TemporaryDirectory(
            prefix=".base-bf16-split-", dir=model_dir
        ) as temporary:
            prefix = Path(temporary) / "base-bf16"
            _run(
                [
                    str(splitter),
                    "--split-max-size",
                    SPLIT_MAX_SIZE,
                    str(source),
                    str(prefix),
                ]
            )
            staged = discover_split_shards(Path(temporary))
            for shard in staged:
                shard.replace(model_dir / shard.name)
    shards = discover_split_shards(model_dir)
    receipt = {
        "protocol": "striatum-base-gguf-split/1",
        "model_revision": MODEL.revision,
        "llama_cpp_commit": LLAMA_CPP_COMMIT,
        "source_size": source_receipt["size"],
        "source_sha256": source_receipt["sha256"],
        "split_max_size": SPLIT_MAX_SIZE,
        "first_shard": shards[0].name,
        "shards": [
            {
                "path": shard.name,
                "size": shard.stat().st_size,
                "sha256": sha256_file(shard),
            }
            for shard in shards
        ],
    }
    receipt_path = model_dir / SPLIT_RECEIPT_NAME
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    # Source and every shard were hashed above. Re-run all structural receipt
    # checks without reading another 142 GB solely to repeat those digests.
    validate_base_gguf_artifacts(model_dir, verify_hashes=False)
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
