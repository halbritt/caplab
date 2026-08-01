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
from .train import validate_liger_fused_loss_proof


PACKAGES = (
    "torch",
    "transformers",
    "peft",
    "accelerate",
    "datasets",
    "bitsandbytes",
    "flash-attn",
    "flash-linear-attention",
    "causal-conv1d",
    "tilelang",
    "apache-tvm-ffi",
    "liger-kernel",
)


def _run(command: list[str]) -> None:
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as error:
        raise ContractError(
            f"preflight child failed with exit {error.returncode}: {command!r}"
        ) from error


def _run_reload_evaluation(
    *,
    model_dir: Path,
    input_dir: Path,
    checkpoint: Path,
    output: Path,
    bf16_base: bool,
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
    _run(command)
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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strategy", choices=STRATEGIES, default="linear-only")
    parser.add_argument("--model-dir", type=Path, default=model_dir_from_env())
    parser.add_argument("--input-dir", type=Path, default=input_dir_from_env())
    parser.add_argument(
        "--output", type=Path, default=output_dir_from_env() / "artifacts/preflight"
    )
    parser.add_argument("--run-smoke", action="store_true")
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

    entries = load_input_manifest(Path(__file__).with_name("input-manifest.json"))
    verify_input_tree(args.input_dir, entries)
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
            ]
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
        )

        bf16_eval_output = args.output / "bf16-parity-eval"
        receipt["bf16_longest_evaluation_example"] = _run_reload_evaluation(
            model_dir=args.model_dir,
            input_dir=args.input_dir,
            checkpoint=checkpoint,
            output=bf16_eval_output,
            bf16_base=True,
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
            ]
        )
        receipt["smoke"] = "passed"
    (args.output / "preflight.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
