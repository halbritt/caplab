"""Validate terminal evidence and publish a closed artifact manifest."""

from __future__ import annotations

import argparse
from collections.abc import Mapping
import json
import os
from pathlib import Path
import re
import tempfile

from .contract import (
    MODEL,
    STRATEGIES,
    Census,
    ContractError,
    expected_adapter_measurement,
    sha256_file,
    validate_production_adapter_evidence,
    validate_census,
)
from .cuda_runtime import validate_cuda_runtime_receipt
from .evaluate import (
    BF16_BASE_LOAD_MODE,
    QUANTIZED_BASE_LOAD_MODE,
    verify_evaluation_results,
    verify_longest_evaluation_receipt,
)
from .export import LLAMA_CPP_COMMIT, LLAMA_CPP_PATCH_SHA256, inspect_peft_adapter
from .peft_config import validate_base_preparation_receipt
from .preflight import (
    PACKAGES,
    verify_base_preparation_receipt,
    verify_liger_fused_loss_receipt,
    verify_live_adapter_measurement,
    verify_longest_example_receipt,
)
from .flash_qla_smoke import validate_flash_qla_smoke_receipt
from .runtime import output_dir_from_env, training_config
from .train_phase import assess_available_gates, verify_checkpoint
from .volume_assets import validate_asset_receipt


ARTIFACT_DIRS = ("artifacts", "checkpoints", "eval")
EXPECTED_CHECKPOINT_STEPS = (
    5,
    25,
    50,
    75,
    100,
    125,
    150,
    159,
    175,
    200,
    225,
    250,
    275,
    300,
    318,
)
EXPECTED_STAGE_STEPS = (
    ("timing-5", 5),
    ("screening-checkpoint-25", 25),
    ("checkpoint-25-mini-evaluation", None),
    ("epoch-one-checkpoint-159", 159),
    ("epoch-one-full-evaluation", None),
    ("second-epoch-318", 318),
)
_SHA256 = re.compile(r"[0-9a-f]{64}")


def _mapping(value: object, label: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ContractError(f"{label} must be an object")
    return value


def _read_json_object(path: Path, label: str) -> Mapping[str, object]:
    if path.is_symlink() or not path.is_file():
        raise ContractError(f"{label} is absent or a symlink: {path}")
    try:
        value: object = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ContractError(f"{label} is invalid JSON: {path}") from error
    return _mapping(value, label)


def _regular_nonempty_file(path: Path, label: str) -> None:
    if path.is_symlink() or not path.is_file() or path.stat().st_size <= 0:
        raise ContractError(f"{label} is absent, empty, or a symlink: {path}")


def _validate_hf_reference(path: Path) -> None:
    reference = _read_json_object(path, "HF parity reference")
    if (
        set(reference)
        != {"protocol", "rendered_prompt", "content", "generated_tokens", "seed"}
        or reference.get("protocol") != "hf-llama-parity-reference/1"
        or not isinstance(reference.get("rendered_prompt"), str)
        or not isinstance(reference.get("content"), str)
        or not isinstance(reference.get("generated_tokens"), list)
        or not reference.get("generated_tokens")
        or any(
            isinstance(token, bool) or not isinstance(token, int) or token < 0
            for token in reference["generated_tokens"]
        )
        or isinstance(reference.get("seed"), bool)
        or not isinstance(reference.get("seed"), int)
    ):
        raise ContractError("HF parity reference contract is invalid")


def validate_export_receipt(path: Path, gguf: Path, source_adapter: Path) -> None:
    receipt = _read_json_object(path, "llama.cpp export receipt")
    expected_fields = {
        "protocol",
        "mode",
        "source_adapter",
        "adapter_gguf",
        "adapter_sha256",
        "base_gguf",
        "base_gguf_sha256",
        "llama_cpp_commit",
        "llama_cpp_patch_sha256",
        "parity",
    }
    if (
        set(receipt) != expected_fields
        or receipt.get("protocol") != "striatum-llama-export/2"
        or receipt.get("mode") != "direct-peft-adapter"
        or receipt.get("llama_cpp_commit") != LLAMA_CPP_COMMIT
        or receipt.get("llama_cpp_patch_sha256") != LLAMA_CPP_PATCH_SHA256
        or receipt.get("parity") != "exact-text-match"
    ):
        raise ContractError("llama.cpp export receipt contract is invalid")
    if receipt.get("source_adapter") != inspect_peft_adapter(source_adapter):
        raise ContractError(
            "llama.cpp export receipt does not bind the current PEFT source adapter"
        )
    _regular_nonempty_file(gguf, "exported adapter GGUF")
    declared_path = receipt.get("adapter_gguf")
    if not isinstance(declared_path, str) or Path(declared_path).resolve() != gguf.resolve():
        raise ContractError("llama.cpp export receipt names another adapter GGUF")
    if receipt.get("adapter_sha256") != sha256_file(gguf):
        raise ContractError("exported adapter GGUF hash does not match its receipt")
    for field in ("adapter_sha256", "base_gguf_sha256"):
        digest = receipt.get(field)
        if not isinstance(digest, str) or _SHA256.fullmatch(digest) is None:
            raise ContractError(f"llama.cpp export {field} is invalid")
    if not isinstance(receipt.get("base_gguf"), str) or not receipt["base_gguf"]:
        raise ContractError("llama.cpp export base GGUF path is invalid")


def _validate_census_receipt(receipt: Mapping[str, object]) -> None:
    if receipt.get("protocol") != "qwen35b-target-census/1":
        raise ContractError("target census protocol is invalid")
    model = _mapping(receipt.get("model"), "target census model")
    if model != {"id": MODEL.model_id, "revision": MODEL.revision}:
        raise ContractError("target census names another model revision")
    raw = _mapping(receipt.get("census"), "target census counts")
    try:
        census = Census(
            linear_attention=raw["linear_attention"],
            attention=raw["attention"],
            shared_expert=raw["shared_expert"],
            routers=raw["router"],
            shared_expert_gates=raw["shared_expert_gate"],
            routed_expert_parameters=raw["routed_expert"],
        )
    except KeyError as error:
        raise ContractError("target census counts are incomplete") from error
    validate_census(census)


def _validate_census(path: Path) -> None:
    _validate_census_receipt(_read_json_object(path, "target census"))


def _validate_preflight(run_root: Path) -> None:
    root = run_root / "artifacts/preflight"
    receipt = _read_json_object(root / "preflight.json", "paid preflight receipt")
    strategy = receipt.get("strategy")
    versions = _mapping(receipt.get("versions"), "paid preflight versions")
    if (
        receipt.get("protocol") != "striatum-paid-preflight/3"
        or receipt.get("smoke") != "passed"
        or strategy not in STRATEGIES
        or receipt.get("measurement")
        != expected_adapter_measurement(str(strategy)).to_dict()
        or set(versions) != set(PACKAGES)
        or any(not isinstance(value, str) or not value for value in versions.values())
    ):
        raise ContractError("paid preflight receipt contract is invalid")
    if receipt.get("flash_qla") != validate_flash_qla_smoke_receipt(
        _read_json_object(root / "flash-qla-smoke.json", "FlashQLA smoke receipt")
    ):
        raise ContractError("paid preflight FlashQLA evidence disagrees")

    _validate_census(root / "target-census.json")
    training_result = root / "one-step/training-result.json"
    if receipt.get("longest_training_example") != verify_longest_example_receipt(
        training_result
    ):
        raise ContractError("paid preflight longest-training evidence disagrees")
    if receipt.get("liger_fused_loss") != verify_liger_fused_loss_receipt(
        training_result
    ):
        raise ContractError("paid preflight Liger evidence disagrees")
    if receipt.get("base_preparation") != verify_base_preparation_receipt(
        training_result
    ):
        raise ContractError("paid preflight base-preparation evidence disagrees")
    if receipt.get("live_adapter_measurement") != verify_live_adapter_measurement(
        training_result, str(strategy)
    ):
        raise ContractError("paid preflight live adapter measurement disagrees")
    verify_checkpoint(root / "one-step/checkpoint-1", 1)

    quantized_reload_summary = _read_json_object(
        root / "quantized-reload-eval/summary.json",
        "quantized reload evaluation summary",
    )
    if quantized_reload_summary.get("base_load_mode") != QUANTIZED_BASE_LOAD_MODE:
        raise ContractError(
            "paid preflight quantized reload evaluation has the wrong base-load mode"
        )
    if receipt.get(
        "quantized_longest_evaluation_example"
    ) != verify_longest_evaluation_receipt(quantized_reload_summary):
        raise ContractError(
            "paid preflight quantized longest-evaluation evidence disagrees"
        )

    bf16_parity_summary = _read_json_object(
        root / "bf16-parity-eval/summary.json", "BF16 parity evaluation summary"
    )
    if bf16_parity_summary.get("base_load_mode") != BF16_BASE_LOAD_MODE:
        raise ContractError(
            "paid preflight BF16 parity evaluation has the wrong base-load mode"
        )
    if receipt.get(
        "bf16_longest_evaluation_example"
    ) != verify_longest_evaluation_receipt(bf16_parity_summary):
        raise ContractError(
            "paid preflight BF16 longest-evaluation evidence disagrees"
        )
    _validate_hf_reference(root / "bf16-parity-eval/hf-reference.json")
    validate_export_receipt(
        root / "one-step-export.json",
        root / "one-step-adapter-f32.gguf",
        root / "one-step/checkpoint-1",
    )


def _validate_passed_projection(receipt: Mapping[str, object], field: str) -> None:
    projection = _mapping(receipt.get(field), f"training receipt {field}")
    if projection.get("passed") is not True:
        raise ContractError(f"training receipt {field} did not pass")


def _validate_training_receipt(run_root: Path) -> None:
    receipt = _read_json_object(
        run_root / "artifacts/train-phase/train-phase.json", "paid training receipt"
    )
    if (
        receipt.get("protocol") != "striatum-paid-training-phase/2"
        or receipt.get("outcome")
        != "training-completed-full-evaluation-pending"
        or receipt.get("full_evaluation") != "separate-evaluate-job-phase"
        or receipt.get("strategy") not in STRATEGIES
    ):
        raise ContractError("paid training receipt terminal outcome is invalid")
    policy = _mapping(receipt.get("policy"), "paid training policy")
    expected_policy = {
        "timing_steps": 5,
        "screening_checkpoint_step": 25,
        "epoch_one_checkpoint_step": 159,
        "total_steps": 318,
        "checkpoint_interval": 25,
        "mini_eval_examples": 16,
        "epoch_one_eval_examples": 98,
    }
    if any(policy.get(key) != value for key, value in expected_policy.items()):
        raise ContractError("paid training receipt step policy is invalid")
    for field in (
        "timing_projection",
        "timing_train_phase_projection",
        "pre_epoch_one_projection",
        "pre_epoch_one_train_phase_projection",
        "pre_second_epoch_projection",
        "pre_second_epoch_train_phase_projection",
    ):
        _validate_passed_projection(receipt, field)

    stages = receipt.get("stages")
    if not isinstance(stages, list) or len(stages) != len(EXPECTED_STAGE_STEPS):
        raise ContractError("paid training stage sequence is incomplete")
    for raw_stage, (expected_name, expected_step) in zip(
        stages, EXPECTED_STAGE_STEPS, strict=True
    ):
        stage = _mapping(raw_stage, f"paid training stage {expected_name}")
        if stage.get("stage") != expected_name or (
            expected_step is not None and stage.get("global_step") != expected_step
        ):
            raise ContractError("paid training stage sequence is invalid")
        if expected_step is not None:
            preparation = _mapping(
                stage.get("base_preparation"),
                f"paid training stage {expected_name} base preparation",
            )
            validate_base_preparation_receipt(preparation)
            validate_production_adapter_evidence(
                stage.get("adapter_measurement"), str(receipt.get("strategy"))
            )

    config = training_config()
    quality = _mapping(config.get("quality_gate"), "quality gate configuration")
    baseline = _mapping(quality.get("strictly_beat"), "quality gate baseline")
    mini_policy = _mapping(
        quality.get("checkpoint_25_mini"), "checkpoint-25 mini policy"
    )
    epoch_policy = _mapping(quality.get("epoch_one_full"), "epoch-one policy")
    mini = _read_json_object(
        run_root / "eval/checkpoint-25-mini/summary.json",
        "checkpoint-25 mini summary",
    )
    mini_gate = assess_available_gates(
        mini, baseline, expected_examples=16, expected_selection=mini_policy
    )
    epoch = _read_json_object(
        run_root / "eval/epoch-one-full/summary.json", "epoch-one full summary"
    )
    epoch_gate = assess_available_gates(
        epoch, baseline, expected_examples=98, expected_selection=epoch_policy
    )
    if (
        receipt.get("checkpoint_25_gate") != mini_gate
        or receipt.get("epoch_one_gate") != epoch_gate
        or not all(item["passed"] is True for item in mini_gate.values())
        or not all(item["passed"] is True for item in epoch_gate.values())
    ):
        raise ContractError("paid training quality-gate evidence is invalid")

    raw_checkpoints = receipt.get("checkpoints")
    if not isinstance(raw_checkpoints, list):
        raise ContractError("paid training checkpoint evidence is absent")
    checkpoints = run_root / "checkpoints"
    verified = [
        verify_checkpoint(checkpoints / f"checkpoint-{step}", step).to_dict()
        for step in EXPECTED_CHECKPOINT_STEPS
    ]
    if raw_checkpoints != verified:
        raise ContractError("paid training checkpoint evidence is not exact")


def validate_completed_training_and_evaluation(
    run_root: Path,
) -> dict[str, object]:
    """Validate the expensive work independently of parity and export."""

    _validate_training_receipt(run_root)
    adapter = run_root / "checkpoints/final-adapter"
    config = _read_json_object(adapter / "adapter_config.json", "adapter config")
    if not config:
        raise ContractError("adapter config must not be empty")
    _regular_nonempty_file(
        adapter / "adapter_model.safetensors", "final adapter safetensors"
    )

    training = training_config()
    quality = _mapping(training.get("quality_gate"), "quality gate configuration")
    baseline = _mapping(quality.get("strictly_beat"), "quality gate baseline")
    epoch_policy = _mapping(quality.get("epoch_one_full"), "full evaluation policy")
    full = _read_json_object(run_root / "eval/full/summary.json", "full evaluation")
    full_gate = assess_available_gates(
        full, baseline, expected_examples=98, expected_selection=epoch_policy
    )
    if not all(item["passed"] is True for item in full_gate.values()):
        raise ContractError("full evaluation quality gates did not pass")
    checkpoint = verify_checkpoint(run_root / "checkpoints/checkpoint-318", 318)
    checkpoint_adapter = inspect_peft_adapter(run_root / "checkpoints/checkpoint-318")
    final_adapter = inspect_peft_adapter(adapter)
    if checkpoint_adapter["files"] != final_adapter["files"]:
        raise ContractError("final adapter does not match checkpoint-318")
    full_results = run_root / "eval/full/results.jsonl"
    _regular_nonempty_file(full_results, "full evaluation results")
    verify_evaluation_results(full, full_results)
    return {
        "source_run_root": str(run_root.resolve()),
        "training_receipt_sha256": sha256_file(
            run_root / "artifacts/train-phase/train-phase.json"
        ),
        "checkpoint_318": checkpoint.to_dict(),
        "final_adapter": final_adapter,
        "full_evaluation_summary_sha256": sha256_file(
            run_root / "eval/full/summary.json"
        ),
        "full_evaluation_results_sha256": sha256_file(full_results),
        "full_quality_gates": full_gate,
    }


def _validate_full(run_root: Path) -> None:
    validate_completed_training_and_evaluation(run_root)
    adapter = run_root / "checkpoints/final-adapter"
    _validate_hf_reference(run_root / "eval/parity/hf-reference.json")
    validate_export_receipt(
        run_root / "artifacts/final/export.json",
        run_root / "artifacts/final/adapter-f32.gguf",
        adapter,
    )


def validate_runtime_evidence(run_root: Path) -> None:
    """Validate the exact CUDA and persistent-volume evidence for one run."""

    validate_cuda_runtime_receipt(
        _read_json_object(
            run_root / "artifacts/runtime/cuda-runtime.json",
            "CUDA runtime receipt",
        )
    )
    runtime_assets = _read_json_object(
        run_root / "artifacts/runtime/volume-assets.json",
        "volume asset receipt",
    )
    if runtime_assets.get("protocol") != "striatum-runtime-assets/1":
        raise ContractError("volume asset receipt protocol is invalid")
    validate_asset_receipt(
        _mapping(runtime_assets.get("assets"), "volume asset receipt assets")
    )
    census = _mapping(runtime_assets.get("census"), "volume asset receipt census")
    _validate_census_receipt(census)


def build_manifest(run_root: Path, *, preflight_only: bool) -> dict[str, object]:
    run_root = run_root.resolve()
    if preflight_only:
        _validate_preflight(run_root)
    else:
        _validate_full(run_root)
    validate_runtime_evidence(run_root)

    files = []
    for directory_name in ARTIFACT_DIRS:
        directory = run_root / directory_name
        for path in sorted(directory.rglob("*")):
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
        "result": (
            "preflight-succeeded"
            if preflight_only
            else "workload-succeeded-model-acceptance-pending"
        ),
        "model_acceptance_requires_local_fate_scoring": not preflight_only,
        "files": files,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-root", type=Path, default=output_dir_from_env())
    parser.add_argument("--output", type=Path)
    parser.add_argument("--preflight-only", action="store_true")
    args = parser.parse_args()
    run_root = args.run_root.resolve()
    output = (args.output or run_root / "artifact-manifest.json").resolve()
    manifest = build_manifest(run_root, preflight_only=args.preflight_only)
    output.parent.mkdir(parents=True, exist_ok=True)
    descriptor, raw_temp = tempfile.mkstemp(
        prefix=f".{output.name}.", dir=output.parent
    )
    temp = Path(raw_temp)
    try:
        with os.fdopen(descriptor, "w") as handle:
            json.dump(manifest, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, output)
    except BaseException:
        temp.unlink(missing_ok=True)
        raise
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
