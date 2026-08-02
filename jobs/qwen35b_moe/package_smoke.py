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
from .hopper_backend import validate_hopper_backend_evidence
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


def _positive_int(value: object) -> bool:
    return not isinstance(value, bool) and isinstance(value, int) and value > 0


def _terminal_evidence_failures(
    preflight: dict[str, object],
    training: dict[str, object],
    inference: dict[str, object],
    kernel: dict[str, object],
    hopper_backend: dict[str, object],
    *,
    model_id: str,
    expected_resume: Path,
    expected_target_count: int,
    expected_trainable_parameters: int,
) -> list[str]:
    """Name every incomplete terminal-evidence binding without weakening it."""

    failures: list[str] = []
    model = preflight.get("model")
    resumed_from = training.get("resumed_from")
    optimization = training.get("optimization")
    batch = training.get("batch")
    measurement = training.get("measurement")
    metrics = training.get("metrics")
    requirements = (
        ("preflight.protocol", preflight.get("protocol") == "striatum-training-profile-preflight/1"),
        ("preflight.smoke", preflight.get("smoke") == "passed"),
        ("preflight.flash_qla", preflight.get("flash_qla") == kernel),
        ("preflight.model.id", isinstance(model, dict) and model.get("id") == model_id),
        ("training.protocol", training.get("protocol") == "striatum-training-result/2"),
        ("training.global_step", training.get("global_step") == 4),
        ("hopper_linear_attention.status", hopper_backend.get("status") == "bound"),
        (
            "training.resumed_from",
            isinstance(resumed_from, str)
            and Path(resumed_from).resolve() == expected_resume.resolve(),
        ),
        (
            "optimization.optimizer_steps",
            isinstance(optimization, dict)
            and _positive_int(optimization.get("optimizer_steps")),
        ),
        (
            "optimization.backward_passes_with_adapter_gradients",
            isinstance(optimization, dict)
            and _positive_int(
                optimization.get("backward_passes_with_adapter_gradients")
            ),
        ),
        (
            "optimization.nonzero_gradient_parameters",
            isinstance(optimization, dict)
            and bool(optimization.get("nonzero_gradient_parameters")),
        ),
        (
            "batch.image_count",
            isinstance(batch, dict) and _positive_int(batch.get("image_count")),
        ),
        (
            "batch.supervised_tokens",
            isinstance(batch, dict)
            and _positive_int(batch.get("supervised_tokens")),
        ),
        (
            "measurement.matched_module_count",
            isinstance(measurement, dict)
            and measurement.get("matched_module_count") == expected_target_count,
        ),
        (
            "measurement.trainable_parameters",
            isinstance(measurement, dict)
            and measurement.get("trainable_parameters")
            == expected_trainable_parameters,
        ),
        (
            "metrics.train_loss",
            isinstance(metrics, dict)
            and not isinstance(metrics.get("train_loss"), bool)
            and isinstance(metrics.get("train_loss"), (int, float))
            and math.isfinite(float(metrics["train_loss"])),
        ),
        (
            "inference.protocol",
            inference.get("protocol") == "striatum-adapter-inference/1",
        ),
        ("inference.adapter_loaded", inference.get("adapter_loaded") is True),
    )
    for label, satisfied in requirements:
        if not satisfied:
            failures.append(label)
    return failures


def build_smoke_manifest(run_root: Path, config: Path) -> dict[str, object]:
    run_root = run_root.resolve()
    profile = load_training_profile(config)
    root = run_root / "artifacts/preflight"
    preflight = _object(root / "preflight.json", "profile preflight receipt")
    training = _object(root / "training/training-result.json", "training receipt")
    inference = _object(root / "inference.json", "inference receipt")
    kernel = _object(root / "flash-qla-smoke.json", "FlashQLA receipt")
    validate_flash_qla_smoke_receipt(kernel)
    hopper_backend = validate_hopper_backend_evidence(
        training.get("hopper_linear_attention")
    )
    checkpoint_2 = root / "training/checkpoint-2"
    checkpoint_4 = root / "training/checkpoint-4"
    verify_checkpoint_manifest(checkpoint_2)
    verify_checkpoint_manifest(checkpoint_4)
    strategy = profile.strategy("linear-only")
    failures = _terminal_evidence_failures(
        preflight,
        training,
        inference,
        kernel,
        hopper_backend,
        model_id=profile.model_id,
        expected_resume=checkpoint_2,
        expected_target_count=int(strategy["expected_target_count"]),
        expected_trainable_parameters=int(strategy["expected_trainable_parameters"]),
    )
    if failures:
        raise ContractError(
            "smoke ladder terminal evidence is incomplete: " + ", ".join(failures)
        )

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
