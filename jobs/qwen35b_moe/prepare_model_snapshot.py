"""Pre-stage the exact Hugging Face revision before H100 billing starts."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import tempfile

from .contract import MODEL, ContractError


def _atomic_text(path: Path, text: str) -> None:
    descriptor, raw_temp = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temp = Path(raw_temp)
    try:
        with os.fdopen(descriptor, "w") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, path)
    except BaseException:
        temp.unlink(missing_ok=True)
        raise


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    try:
        from huggingface_hub import HfApi, snapshot_download
    except ImportError as error:
        raise ContractError(
            "huggingface_hub is required to pre-stage weights"
        ) from error

    destination = args.destination.resolve()
    destination.mkdir(parents=True, exist_ok=True)
    info = HfApi().model_info(MODEL.model_id, revision=MODEL.revision)
    if info.sha != MODEL.revision:
        raise ContractError(
            f"Hugging Face resolved {info.sha!r}, expected {MODEL.revision!r}"
        )
    snapshot_download(
        repo_id=MODEL.model_id,
        revision=MODEL.revision,
        local_dir=destination,
    )
    index_path = destination / "model.safetensors.index.json"
    if not index_path.is_file():
        raise ContractError("download completed without a safetensors index")
    index = json.loads(index_path.read_text())
    missing = sorted(
        shard
        for shard in set(index.get("weight_map", {}).values())
        if not (destination / shard).is_file()
    )
    if missing:
        raise ContractError(f"download is incomplete; missing shards: {missing}")
    _atomic_text(destination / "snapshot-revision.txt", MODEL.revision + "\n")
    print(destination)


if __name__ == "__main__":
    main()
