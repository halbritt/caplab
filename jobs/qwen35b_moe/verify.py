"""Verify the materialized runtime input tree."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import tempfile

from .census import census_snapshot
from .contract import InputFile, load_input_manifest, sha256_file, verify_input_tree
from .gate_acceptance import validate_gate3_acceptance
from .cuda_runtime import inspect_cuda_runtime
from .runtime import input_dir_from_env, model_dir_from_env, output_dir_from_env
from .volume_assets import ASSET_MANIFEST_SHA256, verify_asset_manifest


def verify_runtime_assets(
    model_dir: Path,
    *,
    manifest_path: Path,
    expected_manifest_sha256: str = ASSET_MANIFEST_SHA256,
) -> dict[str, object]:
    return {
        "protocol": "striatum-runtime-assets/1",
        "assets": verify_asset_manifest(
            model_dir,
            manifest_path=manifest_path,
            expected_manifest_sha256=expected_manifest_sha256,
        ),
        "census": census_snapshot(model_dir),
    }


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
    parser.add_argument("--model-dir", type=Path, default=model_dir_from_env())
    parser.add_argument(
        "--asset-manifest",
        type=Path,
        default=Path(__file__).with_name("network-volume-assets.sha256"),
    )
    parser.add_argument("--require-gate3-acceptance", action="store_true")
    args = parser.parse_args()
    acceptance = None
    cuda_receipt = inspect_cuda_runtime()
    asset_receipt = verify_runtime_assets(
        args.model_dir,
        manifest_path=args.asset_manifest,
    )
    entries = load_input_manifest(args.manifest)
    if args.require_gate3_acceptance:
        acceptance_path = args.input_root / "control/gate3-acceptance.json"
        request_path_value = os.environ.get("RUNPOD_JOBRUNNER_REQUEST_PATH")
        if not request_path_value:
            raise ValueError("RUNPOD_JOBRUNNER_REQUEST_PATH is required")
        request = json.loads(Path(request_path_value).read_text())
        acceptance = validate_gate3_acceptance(
            acceptance_path, expected_image_digest=str(request.get("image_digest"))
        )
        entries = (
            *entries,
            InputFile(
                path="control/gate3-acceptance.json",
                role="asset",
                size=acceptance_path.stat().st_size,
                sha256=sha256_file(acceptance_path),
            ),
        )
    verify_input_tree(args.input_root, entries)
    _atomic_json(
        output_dir_from_env() / "artifacts/runtime/cuda-runtime.json",
        cuda_receipt,
    )
    _atomic_json(
        output_dir_from_env() / "artifacts/runtime/volume-assets.json",
        asset_receipt,
    )
    print(
        f"verified {len(entries)} SFT files ({sum(entry.size for entry in entries)} bytes)"
    )
    print(json.dumps(cuda_receipt, sort_keys=True))
    print(json.dumps(asset_receipt, sort_keys=True))
    if acceptance is not None:
        print(json.dumps(acceptance, sort_keys=True))


if __name__ == "__main__":
    main()
