"""Verify the materialized runtime input tree."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import tempfile

from .contract import load_input_manifest, verify_input_tree
from .cuda_runtime import inspect_cuda_runtime
from .runtime import input_dir_from_env, output_dir_from_env


def _atomic_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, raw_temp = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(raw_temp)
    try:
        with os.fdopen(descriptor, "w") as handle:
            json.dump(value, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "input_root", type=Path, nargs="?", default=input_dir_from_env()
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path(__file__).with_name("input-manifest.json"),
    )
    args = parser.parse_args()
    cuda_receipt = inspect_cuda_runtime()
    entries = load_input_manifest(args.manifest)
    verify_input_tree(args.input_root, entries)
    _atomic_json(
        output_dir_from_env() / "artifacts/runtime/cuda-runtime.json",
        cuda_receipt,
    )
    print(
        f"verified {len(entries)} SFT files ({sum(entry.size for entry in entries)} bytes)"
    )
    print(json.dumps(cuda_receipt, sort_keys=True))


if __name__ == "__main__":
    main()
