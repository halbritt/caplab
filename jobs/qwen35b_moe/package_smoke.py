"""Validate a ladder smoke run and publish its terminal artifact manifest."""

from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import tempfile

from .contract import ContractError, sha256_file
from .flash_qla_smoke import validate_flash_qla_smoke_receipt
from .profile import load_training_profile
from .runtime import output_dir_from_env
from .train import verify_checkpoint_manifest


def _object(path: Path, label: str) -> dict[str, object]:
    if path.is_symlink() or not path.is_file():
        raise ContractError(f"{label} is absent or a symlink: {path}")
    try:
        value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise ContractError(f"{label} is invalid: {path}") from error
    if not isinstance(value, dict):
        raise ContractError(f"{label} is not an object")
    return value


def build_smoke_manifest(run_root: Path, config: Path) -> dict[str, object]:
    run_root = run_root.resolve()
    profile = load_training_profile(config)
    root = run_root / "artifacts/preflight"
    preflight = _object(root / "preflight.json", "profile preflight receipt")
    training = _object(root / "training/training-result.json", "training receipt")
    inference = _object(root / "inference.json", "inference receipt")
    kernel = _object(root / "flash-qla-smoke.json", "FlashQLA receipt")
    validate_flash_qla_smoke_receipt(kernel)
    optimization = training.get("optimization")
    batch = training.get("batch")
    measurement = training.get("measurement")
    metrics = training.get("metrics")
    checkpoint_2 = root / "training/checkpoint-2"
    checkpoint_4 = root / "training/checkpoint-4"
    verify_checkpoint_manifest(checkpoint_2)
    verify_checkpoint_manifest(checkpoint_4)
    resumed_from = training.get("resumed_from")
    if (
        preflight.get("protocol") != "striatum-training-profile-preflight/1"
        or preflight.get("smoke") != "passed"
        or preflight.get("flash_qla") != kernel
        or not isinstance(preflight.get("model"), dict)
        or preflight["model"].get("id") != profile.model_id
        or training.get("protocol") != "striatum-training-result/2"
        or training.get("global_step") != 4
        or not isinstance(resumed_from, str)
        or Path(resumed_from).resolve() != checkpoint_2.resolve()
        or not isinstance(optimization, dict)
        or int(optimization.get("optimizer_steps", 0)) <= 0
        or int(optimization.get("backward_passes_with_adapter_gradients", 0)) <= 0
        or not optimization.get("nonzero_gradient_parameters")
        or not isinstance(batch, dict)
        or int(batch.get("image_count", 0)) <= 0
        or int(batch.get("supervised_tokens", 0)) <= 0
        or not isinstance(measurement, dict)
        or int(measurement.get("matched_module_count", 0))
        != int(profile.strategy("linear-only")["expected_target_count"])
        or int(measurement.get("trainable_parameters", 0))
        != int(profile.strategy("linear-only")["expected_trainable_parameters"])
        or not isinstance(metrics, dict)
        or not isinstance(metrics.get("train_loss"), (int, float))
        or not math.isfinite(float(metrics["train_loss"]))
        or inference.get("protocol") != "striatum-adapter-inference/1"
        or inference.get("adapter_loaded") is not True
    ):
        raise ContractError("smoke ladder terminal evidence is incomplete")

    files = []
    for path in sorted((run_root / "artifacts").rglob("*")):
        if path.is_symlink():
            raise ContractError(f"artifact symlink is forbidden: {path}")
        if path.is_file():
            files.append(
                {
                    "path": path.relative_to(run_root).as_posix(),
                    "size": path.stat().st_size,
                    "sha256": sha256_file(path),
                }
            )
    return {
        "protocol": "artifact-manifest/1",
        "result": "smoke-ladder-gate-succeeded",
        "model_acceptance_requires_local_fate_scoring": False,
        "model": {"id": profile.model_id, "revision": profile.model_revision},
        "files": files,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-root", type=Path, default=output_dir_from_env())
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    manifest = build_smoke_manifest(args.run_root, args.config)
    output = (args.output or args.run_root / "artifact-manifest.json").resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    descriptor, raw = tempfile.mkstemp(prefix=f".{output.name}.", dir=output.parent)
    temporary = Path(raw)
    try:
        with os.fdopen(descriptor, "w") as handle:
            json.dump(manifest, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, output)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
