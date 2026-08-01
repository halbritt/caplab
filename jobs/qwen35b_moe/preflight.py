"""Fail-closed paid preflight, including optional one-step export smoke."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import os
from pathlib import Path
import re
import subprocess
import sys

from .census import census_snapshot
from .flash_qla_smoke import run_flash_qla_smoke
from .contract import (
    STRATEGIES,
    ContractError,
    expected_adapter_measurement,
    load_input_manifest,
    verify_input_tree,
)
from .evaluate import (
    BF16_BASE_LOAD_MODE,
    QUANTIZED_BASE_LOAD_MODE,
    verify_longest_evaluation_receipt,
)
from .peft_config import inject_on_meta, validate_base_preparation_receipt
from .runtime import (
    base_gguf_from_env,
    input_dir_from_env,
    model_dir_from_env,
    output_dir_from_env,
)
from .data import encode_sft_example
from .profile import load_training_profile
from .train import verify_checkpoint_manifest
from .train import (
    validate_liger_fused_loss_proof,
    validate_sft_tokenization_census,
)


PACKAGES = (
    "torch",
    "transformers",
    "peft",
    "accelerate",
    "datasets",
    "bitsandbytes",
    "flash-attn",
    "flash-linear-attention",
    "fla-core",
    "flash-qla",
    "causal-conv1d",
    "tilelang",
    "apache-tvm-ffi",
    "liger-kernel",
    "Pillow",
    "torchvision",
)

SMOKE_PACKAGES = (
    "torch",
    "transformers",
    "peft",
    "accelerate",
    "datasets",
    "bitsandbytes",
    "Pillow",
)


def _run(command: list[str], *, log_path: Path | None = None) -> None:
    if log_path is None:
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as error:
            raise ContractError(
                f"preflight child failed with exit {error.returncode}: {command!r}"
            ) from error
        return

    log_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with log_path.open("xb") as log:
            result = subprocess.run(
                command,
                check=False,
                stdout=log,
                stderr=subprocess.STDOUT,
            )
    except OSError as error:
        raise ContractError(
            f"preflight child log could not be created: {log_path}"
        ) from error
    if result.returncode == 0:
        return

    try:
        with log_path.open("rb") as log:
            log.seek(0, os.SEEK_END)
            log.seek(max(0, log.tell() - 65_536))
            tail = log.read().decode("utf-8", errors="replace")
    except OSError as error:
        raise ContractError(
            f"preflight child failed with exit {result.returncode}; "
            f"durable log is unreadable: {log_path}"
        ) from error
    if tail:
        print(tail, file=sys.stderr, end="" if tail.endswith("\n") else "\n")
    raise ContractError(
        f"preflight child failed with exit {result.returncode}; "
        f"durable log: {log_path}"
    )


def _run_reload_evaluation(
    *,
    model_dir: Path,
    input_dir: Path,
    checkpoint: Path,
    output: Path,
    bf16_base: bool,
    log_path: Path | None = None,
) -> dict[str, object]:
    expected_mode = BF16_BASE_LOAD_MODE if bf16_base else QUANTIZED_BASE_LOAD_MODE
    command = [
        sys.executable,
        "-m",
        "jobs.qwen35b_moe.evaluate",
        "--model-dir",
        str(model_dir),
        "--input-dir",
        str(input_dir),
        "--adapter",
        str(checkpoint),
        "--output",
        str(output),
        "--limit",
        "1",
        "--selection",
        "longest-tokenized-authorized",
        "--max-new-tokens",
        "64",
    ]
    if bf16_base:
        command.extend(["--deterministic", "--bf16-base"])
    if log_path is None:
        _run(command)
    else:
        _run(command, log_path=log_path)
    try:
        summary = json.loads((output / "summary.json").read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise ContractError(
            f"{expected_mode} longest held-out reload evaluation summary is missing "
            "or invalid"
        ) from error
    if not isinstance(summary, dict):
        raise ContractError(
            f"{expected_mode} longest held-out reload evaluation summary is invalid"
        )
    if summary.get("base_load_mode") != expected_mode:
        raise ContractError(
            f"reload evaluation did not attest the {expected_mode} base path"
        )
    return verify_longest_evaluation_receipt(summary)


def verify_longest_example_receipt(path: Path) -> dict[str, object]:
    try:
        training_result = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise ContractError("one-step training result is missing or invalid") from error
    if (
        not isinstance(training_result, dict)
        or training_result.get("protocol") != "striatum-training-result/2"
        or training_result.get("global_step") != 1
    ):
        raise ContractError("one-step training result contract is invalid")
    selection = training_result.get("example_selection")
    if not isinstance(selection, dict):
        raise ContractError("one-step training has no example-selection evidence")
    if selection.get("mode") != "longest-tokenized-authorized":
        raise ContractError("one-step training did not select the longest example")
    if selection.get("candidates") != 1_268 or selection.get("cutoff") != 40_960:
        raise ContractError("longest-example census has unexpected bounds")
    tokenization = validate_sft_tokenization_census(
        selection.get("tokenization")
    )
    expected_longest = tokenization.get("longest_example")
    if not isinstance(expected_longest, dict):
        raise ContractError("longest-example tokenization contract is invalid")
    index = selection.get("selected_global_index")
    raw = selection.get("raw_token_count")
    effective = selection.get("effective_token_count")
    if (
        isinstance(index, bool)
        or not isinstance(index, int)
        or not 0 <= index < 1_268
        or isinstance(raw, bool)
        or not isinstance(raw, int)
        or raw <= 0
        or isinstance(effective, bool)
        or not isinstance(effective, int)
        or effective <= 0
        or effective != min(raw, 40_960)
        or raw != selection.get("max_raw_token_count")
        or effective != selection.get("max_effective_token_count")
        or {
            key: selection.get(key)
            for key in (
                "selected_global_index",
                "raw_token_count",
                "effective_token_count",
                "prompt_token_count",
                "assistant_token_count",
                "supervised_token_count",
                "truncation_mode",
            )
        }
        != expected_longest
    ):
        raise ContractError("longest-example token counts are inconsistent")
    dispatch_id = selection.get("dispatch_id")
    if not isinstance(dispatch_id, str) or not dispatch_id:
        raise ContractError("longest-example dispatch_id is absent")
    census_digest = selection.get("token_length_census_sha256")
    if not isinstance(census_digest, str) or not re.fullmatch(
        r"[0-9a-f]{64}", census_digest
    ):
        raise ContractError("longest-example token census hash is invalid")
    return selection


def verify_base_preparation_receipt(path: Path) -> dict[str, object]:
    try:
        training_result = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise ContractError("one-step training result is missing or invalid") from error
    if (
        not isinstance(training_result, dict)
        or training_result.get("protocol") != "striatum-training-result/2"
        or training_result.get("global_step") != 1
    ):
        raise ContractError("one-step training result contract is invalid")
    preparation = training_result.get("base_preparation")
    if not isinstance(preparation, dict):
        raise ContractError("one-step training has no base-preparation evidence")
    return validate_base_preparation_receipt(preparation)


def verify_live_adapter_measurement(
    path: Path, strategy: str
) -> dict[str, object]:
    try:
        training_result = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise ContractError("one-step training result is missing or invalid") from error
    if (
        not isinstance(training_result, dict)
        or training_result.get("protocol") != "striatum-training-result/2"
        or training_result.get("global_step") != 1
    ):
        raise ContractError("one-step training result contract is invalid")
    measurement = training_result.get("measurement")
    expected = expected_adapter_measurement(strategy).to_dict()
    if not isinstance(measurement, dict) or measurement != expected:
        raise ContractError("live adapter measurement is invalid")
    return measurement


def verify_liger_fused_loss_receipt(path: Path) -> dict[str, object]:
    try:
        training_result = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise ContractError("one-step training result is missing or invalid") from error
    if (
        not isinstance(training_result, dict)
        or training_result.get("protocol") != "striatum-training-result/2"
        or training_result.get("global_step") != 1
    ):
        raise ContractError("one-step training result contract is invalid")
    return validate_liger_fused_loss_proof(training_result.get("liger_fused_loss"))


def _read_profile_examples(input_dir: Path, manifest_path: Path) -> list[dict[str, object]]:
    manifest = json.loads(manifest_path.read_text())
    rows: list[dict[str, object]] = []
    for item in manifest.get("files", []):
        if not isinstance(item, dict) or item.get("role", "train") != "train":
            continue
        path = input_dir / str(item.get("path"))
        try:
            for line in path.read_text().splitlines():
                if not line.strip():
                    continue
                value: object = json.loads(line)
                if not isinstance(value, dict):
                    raise ContractError(f"dataset row is not an object: {path}")
                rows.append(value)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
            raise ContractError(f"dataset is unreadable: {path}") from error
    if not rows:
        raise ContractError("profile input contains no training examples")
    return rows


def _profile_preflight(args: argparse.Namespace) -> dict[str, object]:
    try:
        import torch
        from transformers import AutoConfig, AutoProcessor
    except ImportError as error:
        raise ContractError("torch and transformers are required for preflight") from error
    profile = load_training_profile(args.config)
    flash_qla = (
        run_flash_qla_smoke(args.output / "flash-qla-smoke.json")
        if args.check_hopper_kernels
        else None
    )
    entries = load_input_manifest(
        profile.input_manifest, strict_production=profile.strict_input_manifest
    )
    verify_input_tree(args.input_dir, entries)
    revision_receipt = args.model_dir / "snapshot-revision.txt"
    if not revision_receipt.is_file() or revision_receipt.read_text().strip() != profile.model_revision:
        raise ContractError(
            "model snapshot revision receipt is missing or does not match the profile"
        )
    config = AutoConfig.from_pretrained(args.model_dir, local_files_only=True)
    if getattr(config, "model_type", None) != profile.model_type:
        raise ContractError(
            f"model configuration type mismatch: {getattr(config, 'model_type', None)!r}"
        )
    processor = AutoProcessor.from_pretrained(args.model_dir, local_files_only=True)
    rows = _read_profile_examples(args.input_dir, profile.input_manifest)
    if len(rows) > profile.maximum_examples:
        raise ContractError(
            f"smoke dataset has {len(rows)} rows; maximum is {profile.maximum_examples}"
        )
    encoded_rows = [
        encode_sft_example(
            processor,
            row,
            input_root=args.input_dir,
            cutoff=profile.cutoff_length,
            processing=profile.processing,
        )
        for row in rows
    ]
    model, measurement = inject_on_meta(str(args.model_dir), args.strategy, profile)
    del model
    measurement_value = (
        measurement.to_dict() if hasattr(measurement, "to_dict") else measurement
    )
    versions = {}
    for package in SMOKE_PACKAGES:
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError as error:
            raise ContractError(f"required package is absent: {package}") from error
    cuda = {
        "available": bool(torch.cuda.is_available()),
        "bf16_supported": bool(
            torch.cuda.is_available() and torch.cuda.is_bf16_supported()
        ),
    }
    if torch.cuda.is_available():
        cuda.update(
            {
                "device": torch.cuda.get_device_name(),
                "compute_capability": list(torch.cuda.get_device_capability()),
            }
        )
    receipt: dict[str, object] = {
        "protocol": "striatum-training-profile-preflight/1",
        "profile": str(profile.path),
        "model_dir": str(args.model_dir.resolve()),
        "input_dir": str(args.input_dir.resolve()),
        "model": {
            "id": profile.model_id,
            "revision": profile.model_revision,
            "model_type": profile.model_type,
        },
        "processor_class": type(processor).__name__,
        "versions": versions,
        "flash_qla": flash_qla,
        "cuda": cuda,
        "dataset": {
            "examples": len(rows),
            "multimodal_examples": sum(
                "pixel_values" in encoded for encoded in encoded_rows
            ),
            "maximum_tokens": max(len(encoded["input_ids"]) for encoded in encoded_rows),
            "supervised_tokens": sum(
                sum(label != -100 for label in encoded["labels"])
                for encoded in encoded_rows
            ),
        },
        "adapter": measurement_value,
        "smoke": "not-requested",
    }
    print(json.dumps(receipt, indent=2, sort_keys=True), flush=True)
    return receipt


def _run_profile_smoke(args: argparse.Namespace, receipt: dict[str, object]) -> None:
    train_output = args.output / "training"
    diagnostics = args.output / "diagnostics"
    common = [
        sys.executable,
        "-m",
        "jobs.qwen35b_moe.train",
        "--config",
        str(args.config),
        "--strategy",
        args.strategy,
        "--model-dir",
        str(args.model_dir),
        "--input-dir",
        str(args.input_dir),
        "--output",
        str(train_output),
        "--limit",
        "4",
        "--save-steps",
        "2",
        "--save-final-checkpoint",
        "--seed",
        str(args.seed),
    ]
    first = [*common, "--max-steps", "2"]
    _run(first, log_path=diagnostics / "train-to-checkpoint.log")
    checkpoint = train_output / "checkpoint-2"
    verify_checkpoint_manifest(checkpoint)
    resumed = [
        *common,
        "--max-steps",
        "4",
        "--resume-from-checkpoint",
        str(checkpoint),
    ]
    _run(resumed, log_path=diagnostics / "resume-training.log")
    final_checkpoint = train_output / "checkpoint-4"
    verify_checkpoint_manifest(final_checkpoint)
    inference_output = args.output / "inference.json"
    inference = [
        sys.executable,
        "-m",
        "jobs.qwen35b_moe.infer",
        "--config",
        str(args.config),
        "--model-dir",
        str(args.model_dir),
        "--input-dir",
        str(args.input_dir),
        "--adapter",
        str(train_output / "final-adapter"),
        "--output",
        str(inference_output),
        "--max-new-tokens",
        "32",
    ]
    _run(inference, log_path=diagnostics / "inference.log")
    first_result = json.loads((train_output / "training-result.json").read_text())
    inference_result = json.loads(inference_output.read_text())
    if first_result.get("global_step") != 4:
        raise ContractError("resumed smoke training did not reach step 4")
    if Path(str(first_result.get("resumed_from"))).resolve() != checkpoint.resolve():
        raise ContractError("smoke training did not attest checkpoint resume")
    optimization = first_result.get("optimization")
    if (
        not isinstance(optimization, dict)
        or optimization.get("optimizer_steps", 0) <= 0
        or optimization.get("backward_passes_with_adapter_gradients", 0) <= 0
        or not optimization.get("nonzero_gradient_parameters")
    ):
        raise ContractError("smoke training has incomplete optimization evidence")
    if inference_result.get("adapter_loaded") is not True:
        raise ContractError("smoke inference did not load the adapter")
    receipt.update(
        {
            "smoke": "passed",
            "commands": [first, resumed, inference],
            "checkpoint_2": str(checkpoint),
            "checkpoint_4": str(final_checkpoint),
            "training": first_result,
            "inference": inference_result,
        }
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strategy", choices=STRATEGIES, default="linear-only")
    parser.add_argument("--config", type=Path)
    parser.add_argument("--model-dir", type=Path, default=model_dir_from_env())
    parser.add_argument("--input-dir", type=Path, default=input_dir_from_env())
    parser.add_argument(
        "--output", type=Path, default=output_dir_from_env() / "artifacts/preflight"
    )
    parser.add_argument("--run-smoke", action="store_true")
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("--check-hopper-kernels", action="store_true")
    parser.add_argument("--seed", type=int, default=42)
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
    args.output.mkdir(parents=True, exist_ok=True)
    if args.config is not None:
        args.config = args.config.resolve()
        args.model_dir = args.model_dir.resolve()
        args.input_dir = args.input_dir.resolve()
        receipt = _profile_preflight(args)
        if args.run_smoke:
            _run_profile_smoke(args, receipt)
        receipt_path = args.output / "preflight.json"
        receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
        return
    diagnostics = output_dir_from_env() / "diagnostics/preflight"

    entries = load_input_manifest(Path(__file__).with_name("input-manifest.json"))
    verify_input_tree(args.input_dir, entries)
    receipt_flash_qla = run_flash_qla_smoke(
        args.output / "flash-qla-smoke.json"
    )
    census = census_snapshot(args.model_dir)
    (args.output / "target-census.json").write_text(
        json.dumps(census, indent=2, sort_keys=True) + "\n"
    )
    model, measurement = inject_on_meta(str(args.model_dir), args.strategy)
    del model
    versions = {}
    for package in PACKAGES:
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError as error:
            raise ContractError(f"required package is absent: {package}") from error

    receipt = {
        "protocol": "striatum-paid-preflight/3",
        "strategy": args.strategy,
        "measurement": measurement.to_dict(),
        "flash_qla": receipt_flash_qla,
        "versions": versions,
        "smoke": "not-requested",
    }
    if args.run_smoke:
        if not args.base_gguf.is_file():
            raise ContractError(
                f"preloaded base GGUF is missing; paid preflight will not generate it: "
                f"{args.base_gguf}"
            )
        train_output = args.output / "one-step"
        _run(
            [
                sys.executable,
                "-m",
                "jobs.qwen35b_moe.train",
                "--strategy",
                args.strategy,
                "--model-dir",
                str(args.model_dir),
                "--input-dir",
                str(args.input_dir),
                "--output",
                str(train_output),
                "--max-steps",
                "1",
                "--limit",
                "1",
                "--select-longest",
                "--save-steps",
                "1",
            ],
            log_path=diagnostics / "one-step-train.log",
        )
        training_result_path = train_output / "training-result.json"
        receipt["longest_training_example"] = verify_longest_example_receipt(
            training_result_path
        )
        receipt["liger_fused_loss"] = verify_liger_fused_loss_receipt(
            training_result_path
        )
        receipt["base_preparation"] = verify_base_preparation_receipt(
            training_result_path
        )
        receipt["live_adapter_measurement"] = verify_live_adapter_measurement(
            training_result_path, args.strategy
        )
        checkpoint = train_output / "checkpoint-1"
        if not (checkpoint / "checkpoint-complete.json").is_file():
            raise ContractError("one-step checkpoint has no completion manifest")
        quantized_eval_output = args.output / "quantized-reload-eval"
        receipt["quantized_longest_evaluation_example"] = _run_reload_evaluation(
            model_dir=args.model_dir,
            input_dir=args.input_dir,
            checkpoint=checkpoint,
            output=quantized_eval_output,
            bf16_base=False,
            log_path=diagnostics / "quantized-reload-eval.log",
        )

        bf16_eval_output = args.output / "bf16-parity-eval"
        receipt["bf16_longest_evaluation_example"] = _run_reload_evaluation(
            model_dir=args.model_dir,
            input_dir=args.input_dir,
            checkpoint=checkpoint,
            output=bf16_eval_output,
            bf16_base=True,
            log_path=diagnostics / "bf16-parity-eval.log",
        )
        _run(
            [
                sys.executable,
                "-m",
                "jobs.qwen35b_moe.export",
                "--model-dir",
                str(args.model_dir),
                "--adapter",
                str(checkpoint),
                "--base-gguf",
                str(args.base_gguf),
                "--hf-reference",
                str(bf16_eval_output / "hf-reference.json"),
                "--llama-cpp",
                str(args.llama_cpp),
                "--output",
                str(args.output / "one-step-adapter-f32.gguf"),
                "--receipt",
                str(args.output / "one-step-export.json"),
            ],
            log_path=diagnostics / "one-step-export.log",
        )
        receipt["smoke"] = "passed"
    (args.output / "preflight.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
