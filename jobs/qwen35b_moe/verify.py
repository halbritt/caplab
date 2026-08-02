"""Verify the materialized runtime input tree."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import tempfile

from .census import census_snapshot
from .contract import (
    ContractError,
    InputFile,
    load_input_manifest,
    sha256_file,
    verify_input_tree,
)
from .gate_acceptance import validate_gate3_acceptance
from .cuda_runtime import inspect_cuda_runtime
from .runtime import input_dir_from_env, model_dir_from_env, output_dir_from_env
from .profile import load_training_profile
from .train import _load_datasets
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


def verify_production_tokenization(
    model_dir: Path,
    input_dir: Path,
    *,
    config_path: Path,
) -> dict[str, object]:
    """Bind the complete production corpus to the real processor before model load."""

    try:
        from transformers import AutoProcessor
    except ImportError as error:
        raise ContractError(
            "transformers is required for tokenization preflight"
        ) from error
    profile = load_training_profile(config_path)
    processor = AutoProcessor.from_pretrained(model_dir, local_files_only=True)
    dataset, selection = _load_datasets(
        input_dir,
        processor,
        profile.cutoff_length,
        limit=0,
        select_longest=False,
        manifest_path=profile.input_manifest,
        expected_examples=profile.train["expected_examples"],
        strict_production=profile.strict_input_manifest,
    )
    tokenization = selection.get("tokenization")
    if selection.get("mode") != "all-authorized" or not isinstance(
        tokenization, dict
    ):
        raise ContractError("production tokenization preflight returned no census")
    return {
        "protocol": "striatum-production-tokenization-preflight/1",
        "processor_class": type(processor).__name__,
        "examples": len(dataset),
        "tokenization": tokenization,
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
    parser.add_argument("--check-production-tokenization", action="store_true")
    parser.add_argument(
        "--training-config",
        type=Path,
        default=Path(__file__).with_name("training-config.json"),
    )
    args = parser.parse_args()
    acceptance = None
    cuda_receipt = inspect_cuda_runtime()
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
    tokenization_receipt = (
        verify_production_tokenization(
            args.model_dir,
            args.input_root,
            config_path=args.training_config,
        )
        if args.check_production_tokenization
        else None
    )
    asset_receipt = verify_runtime_assets(
        args.model_dir,
        manifest_path=args.asset_manifest,
    )
    if acceptance is not None:
        acceptance_path.unlink()
    _atomic_json(
        output_dir_from_env() / "artifacts/runtime/cuda-runtime.json",
        cuda_receipt,
    )
    _atomic_json(
        output_dir_from_env() / "artifacts/runtime/volume-assets.json",
        asset_receipt,
    )
    if tokenization_receipt is not None:
        _atomic_json(
            output_dir_from_env()
            / "artifacts/runtime/production-tokenization.json",
            tokenization_receipt,
        )
    print(
        f"verified {len(entries)} SFT files ({sum(entry.size for entry in entries)} bytes)"
    )
    print(json.dumps(cuda_receipt, sort_keys=True))
    print(json.dumps(asset_receipt, sort_keys=True))
    if tokenization_receipt is not None:
        print(json.dumps(tokenization_receipt, sort_keys=True))
    if acceptance is not None:
        print(json.dumps(acceptance, sort_keys=True))


if __name__ == "__main__":
    main()
