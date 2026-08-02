"""Strict PEFT-to-llama.cpp export, load, and deterministic parity smoke."""

from __future__ import annotations

import argparse
from collections.abc import Mapping
from dataclasses import dataclass
import json
from pathlib import Path
import struct
import subprocess
import sys
import threading
from typing import Any

from .contract import EXPERT_AWARE, LINEAR_ONLY, MODEL, ContractError, sha256_file
from .peft_config import LINEAR_TARGET_PATTERN, ROUTED_TARGET_PARAMETERS
from .runtime import model_dir_from_env, output_dir_from_env


LLAMA_CPP_COMMIT = "000547513f1530346ecd163db8b3e13962949961"
LLAMA_CPP_PATCH_SHA256 = (
    "3891147dde2bb277275364b21593103c4d1f957275e3ae58dc0e4dc621237d19"
)
LLAMA_CPP_PATCH_PATH = Path(
    "/opt/striatum-qwen35b/patches/llama-qwen35-lora-reorder.patch"
)
_SAFETENSORS_MAX_HEADER_BYTES = 64 * 1024 * 1024
_PARITY_STDOUT_MAX_BYTES = 1024 * 1024
_PARITY_STDERR_TAIL_BYTES = 64 * 1024
_SAFETENSORS_DTYPE_BYTES = {
    "BOOL": 1,
    "U8": 1,
    "I8": 1,
    "F8_E5M2": 1,
    "F8_E4M3": 1,
    "F8_E8M0": 1,
    "I16": 2,
    "U16": 2,
    "F16": 2,
    "BF16": 2,
    "I32": 4,
    "U32": 4,
    "F32": 4,
    "I64": 8,
    "U64": 8,
    "F64": 8,
    "C64": 8,
    "C128": 16,
}


def _object_without_duplicates(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ContractError(f"JSON object contains duplicate key {key!r}")
        result[key] = value
    return result


def _same_json_value(actual: object, expected: object) -> bool:
    if type(actual) is not type(expected):
        return False
    if isinstance(expected, dict):
        return set(actual) == set(expected) and all(
            _same_json_value(actual[key], value) for key, value in expected.items()
        )
    if isinstance(expected, list):
        return len(actual) == len(expected) and all(
            _same_json_value(item, expected_item)
            for item, expected_item in zip(actual, expected, strict=True)
        )
    return actual == expected


def _run(command: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(command, check=True, text=True, **kwargs)
    except subprocess.CalledProcessError as error:
        raise ContractError(
            f"export command failed with exit {error.returncode}: {command!r}"
        ) from error


@dataclass(frozen=True)
class BoundedParityResult:
    stdout: str
    stderr_tail: str
    stderr_bytes: int


def _run_bounded_parity(
    command: list[str],
    *,
    stdout_limit: int = _PARITY_STDOUT_MAX_BYTES,
    stderr_tail_limit: int = _PARITY_STDERR_TAIL_BYTES,
) -> BoundedParityResult:
    """Run llama.cpp without retaining its unbounded diagnostic stream.

    llama.cpp can emit a very large stderr stream while evaluating a long
    context. The parity text is stdout, so retain that under a strict ceiling
    while continuously draining stderr into a fixed-size tail buffer.
    """

    for value, label in (
        (stdout_limit, "stdout limit"),
        (stderr_tail_limit, "stderr tail limit"),
    ):
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ContractError(f"llama.cpp parity {label} must be positive")
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except OSError as error:
        raise ContractError("could not start llama.cpp parity command") from error
    if process.stdout is None or process.stderr is None:
        process.kill()
        process.wait()
        raise ContractError("llama.cpp parity pipes were not created")

    stdout = bytearray()
    stderr_tail = bytearray()
    stderr_bytes = 0
    stdout_exceeded = False

    def drain_stdout() -> None:
        nonlocal stdout_exceeded
        while chunk := process.stdout.read(64 * 1024):
            remaining = stdout_limit - len(stdout)
            if remaining > 0:
                stdout.extend(chunk[:remaining])
            if len(chunk) > remaining and not stdout_exceeded:
                stdout_exceeded = True
                process.terminate()

    def drain_stderr() -> None:
        nonlocal stderr_bytes
        while chunk := process.stderr.read(64 * 1024):
            stderr_bytes += len(chunk)
            if len(chunk) >= stderr_tail_limit:
                stderr_tail[:] = chunk[-stderr_tail_limit:]
            else:
                stderr_tail.extend(chunk)
                excess = len(stderr_tail) - stderr_tail_limit
                if excess > 0:
                    del stderr_tail[:excess]

    stdout_thread = threading.Thread(target=drain_stdout, name="llama-stdout")
    stderr_thread = threading.Thread(target=drain_stderr, name="llama-stderr")
    stdout_thread.start()
    stderr_thread.start()
    return_code = process.wait()
    stdout_thread.join()
    stderr_thread.join()

    decoded_stderr = stderr_tail.decode("utf-8", errors="replace")
    if stdout_exceeded:
        raise ContractError(
            f"llama.cpp parity stdout exceeded {stdout_limit} bytes; "
            f"stderr tail: {decoded_stderr}"
        )
    try:
        decoded_stdout = stdout.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ContractError("llama.cpp parity stdout is not UTF-8") from error
    if return_code != 0:
        raise ContractError(
            f"llama.cpp parity command failed with exit {return_code}; "
            f"stderr tail: {decoded_stderr}"
        )
    return BoundedParityResult(
        stdout=decoded_stdout,
        stderr_tail=decoded_stderr,
        stderr_bytes=stderr_bytes,
    )


def _check_llama_commit(llama_cpp: Path) -> None:
    result = _run(
        ["git", "-C", str(llama_cpp), "rev-parse", "HEAD"], capture_output=True
    )
    commit = result.stdout.strip()
    if commit != LLAMA_CPP_COMMIT:
        raise ContractError(
            f"llama.cpp commit mismatch: {commit} != {LLAMA_CPP_COMMIT}"
        )
    if (
        LLAMA_CPP_PATCH_PATH.is_symlink()
        or not LLAMA_CPP_PATCH_PATH.is_file()
        or sha256_file(LLAMA_CPP_PATCH_PATH) != LLAMA_CPP_PATCH_SHA256
    ):
        raise ContractError("llama.cpp Qwen LoRA patch is missing or does not match")
    _run(
        [
            "git",
            "-C",
            str(llama_cpp),
            "apply",
            "--reverse",
            "--check",
            str(LLAMA_CPP_PATCH_PATH),
        ],
        capture_output=True,
    )
    changed = _run(
        ["git", "-C", str(llama_cpp), "diff", "--name-only"], capture_output=True
    ).stdout.splitlines()
    if changed != ["conversion/qwen.py", "convert_lora_to_gguf.py"]:
        raise ContractError(f"llama.cpp patched source inventory is invalid: {changed!r}")


def _read_adapter_config(path: Path) -> Mapping[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise ContractError(f"PEFT adapter config is absent or a symlink: {path}")
    try:
        value: object = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_object_without_duplicates,
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ContractError("PEFT adapter config is not valid JSON") from error
    if not isinstance(value, Mapping) or not value:
        raise ContractError("PEFT adapter config must be a nonempty object")
    return value


def _adapter_strategy(config: Mapping[str, Any]) -> str:
    target_parameters = config.get("target_parameters")
    if target_parameters is None:
        strategy = LINEAR_ONLY
    elif target_parameters == list(ROUTED_TARGET_PARAMETERS):
        strategy = EXPERT_AWARE
    else:
        raise ContractError("PEFT adapter has unexpected target_parameters")

    expected = {
        "base_model_name_or_path": MODEL.model_id,
        "revision": MODEL.revision,
        "peft_type": "LORA",
        "task_type": "CAUSAL_LM",
        "inference_mode": True,
        "r": 32,
        "lora_alpha": 64,
        "bias": "none",
        "target_modules": LINEAR_TARGET_PATTERN,
        "lora_dropout": 0.0 if strategy == EXPERT_AWARE else 0.05,
        "rank_pattern": (
            {target: 1 for target in ROUTED_TARGET_PARAMETERS}
            if strategy == EXPERT_AWARE
            else {}
        ),
        "alpha_pattern": (
            {target: 2 for target in ROUTED_TARGET_PARAMETERS}
            if strategy == EXPERT_AWARE
            else {}
        ),
    }
    mismatched = [
        key
        for key, value in expected.items()
        if not _same_json_value(config.get(key), value)
    ]
    if mismatched:
        raise ContractError(
            "PEFT adapter config does not match the pinned model and strategy: "
            + ", ".join(sorted(mismatched))
        )
    return strategy


def _validate_safetensors(path: Path) -> None:
    if path.is_symlink() or not path.is_file():
        raise ContractError(f"PEFT adapter weights are absent or a symlink: {path}")
    file_size = path.stat().st_size
    if file_size < 11:
        raise ContractError("PEFT adapter weights are not a safetensors file")
    try:
        with path.open("rb") as handle:
            raw_header_size = handle.read(8)
            if len(raw_header_size) != 8:
                raise ContractError("PEFT adapter safetensors header is truncated")
            header_size = struct.unpack("<Q", raw_header_size)[0]
            if not 2 < header_size <= _SAFETENSORS_MAX_HEADER_BYTES:
                raise ContractError("PEFT adapter safetensors header size is unsafe")
            if 8 + header_size > file_size:
                raise ContractError("PEFT adapter safetensors header exceeds the file")
            raw_header = handle.read(header_size)
        header: object = json.loads(
            raw_header, object_pairs_hook=_object_without_duplicates
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ContractError("PEFT adapter safetensors header is invalid") from error
    if not isinstance(header, Mapping):
        raise ContractError("PEFT adapter safetensors header must be an object")
    metadata = header.get("__metadata__")
    if metadata is not None and (
        not isinstance(metadata, Mapping)
        or any(
            not isinstance(key, str) or not isinstance(value, str)
            for key, value in metadata.items()
        )
    ):
        raise ContractError("PEFT adapter safetensors metadata is invalid")

    data_size = file_size - 8 - header_size
    ranges: list[tuple[int, int]] = []
    tensors = 0
    for name, raw_tensor in header.items():
        if name == "__metadata__":
            continue
        tensors += 1
        if not isinstance(name, str) or not name or not isinstance(raw_tensor, Mapping):
            raise ContractError("PEFT adapter safetensors tensor record is invalid")
        if set(raw_tensor) != {"dtype", "shape", "data_offsets"}:
            raise ContractError("PEFT adapter safetensors tensor fields are invalid")
        dtype = raw_tensor.get("dtype")
        shape = raw_tensor.get("shape")
        offsets = raw_tensor.get("data_offsets")
        if dtype not in _SAFETENSORS_DTYPE_BYTES:
            raise ContractError("PEFT adapter safetensors dtype is unsupported")
        if not isinstance(shape, list) or any(
            isinstance(dimension, bool)
            or not isinstance(dimension, int)
            or dimension < 0
            for dimension in shape
        ):
            raise ContractError("PEFT adapter safetensors shape is invalid")
        if (
            not isinstance(offsets, list)
            or len(offsets) != 2
            or any(
                isinstance(offset, bool) or not isinstance(offset, int)
                for offset in offsets
            )
        ):
            raise ContractError("PEFT adapter safetensors offsets are invalid")
        start, end = offsets
        if not 0 <= start <= end <= data_size:
            raise ContractError("PEFT adapter safetensors offsets exceed the file")
        elements = 1
        for dimension in shape:
            elements *= dimension
        if end - start != elements * _SAFETENSORS_DTYPE_BYTES[str(dtype)]:
            raise ContractError("PEFT adapter safetensors tensor size is inconsistent")
        ranges.append((start, end))
    if tensors == 0:
        raise ContractError("PEFT adapter safetensors file contains no tensors")
    expected_start = 0
    for start, end in sorted(ranges):
        if start != expected_start:
            raise ContractError("PEFT adapter safetensors data ranges are not contiguous")
        expected_start = end
    if expected_start != data_size:
        raise ContractError("PEFT adapter safetensors data is not fully described")


def inspect_peft_adapter(adapter: Path) -> dict[str, object]:
    """Validate one PEFT adapter and return its exact source binding."""

    if adapter.is_symlink() or not adapter.is_dir():
        raise ContractError(f"PEFT adapter is absent or a symlink: {adapter}")
    root = adapter.resolve()
    config_path = root / "adapter_config.json"
    weights_path = root / "adapter_model.safetensors"
    strategy = _adapter_strategy(_read_adapter_config(config_path))
    _validate_safetensors(weights_path)
    return {
        "path": str(root),
        "strategy": strategy,
        "files": [
            {
                "path": path.name,
                "size": path.stat().st_size,
                "sha256": sha256_file(path),
            }
            for path in (config_path, weights_path)
        ],
    }


def direct_export(args: argparse.Namespace) -> dict[str, object]:
    converter = args.llama_cpp / "convert_lora_to_gguf.py"
    llama_cli = args.llama_cpp / "build/bin/llama-cli"
    if (
        not converter.is_file()
        or not llama_cli.is_file()
        or not args.base_gguf.is_file()
    ):
        raise ContractError(
            "llama.cpp converter, llama-cli, or exact base GGUF is missing"
        )
    source_adapter = inspect_peft_adapter(args.adapter)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    _run(
        [
            sys.executable,
            str(converter),
            "--base",
            str(args.model_dir),
            "--outfile",
            str(args.output),
            "--outtype",
            "f32",
            str(args.adapter),
        ]
    )
    if not args.output.is_file() or args.output.stat().st_size == 0:
        raise ContractError("llama.cpp conversion returned without a non-empty adapter")

    reference = json.loads(args.hf_reference.read_text())
    result = _run_bounded_parity(
        [
            str(llama_cli),
            "-m",
            str(args.base_gguf),
            "--lora",
            str(args.output),
            "--ctx-size",
            "40960",
            "--gpu-layers",
            "all",
            "--fit",
            "on",
            "--prompt",
            reference["rendered_prompt"],
            "--no-display-prompt",
            "--no-conversation",
            "--single-turn",
            "--simple-io",
            "--log-disable",
            "--seed",
            str(reference["seed"]),
            "--temp",
            "0",
            "-n",
            str(len(reference["generated_tokens"])),
        ]
    )
    print(
        json.dumps(
            {
                "llama_parity_stderr_bytes": result.stderr_bytes,
                "llama_parity_stderr_tail_bytes": len(
                    result.stderr_tail.encode("utf-8")
                ),
            },
            sort_keys=True,
        )
    )
    llama_content = result.stdout.strip()
    hf_content = reference["content"].strip()
    if llama_content != hf_content:
        raise ContractError(
            "llama.cpp deterministic output does not match the HF adapter output"
        )
    if inspect_peft_adapter(args.adapter) != source_adapter:
        raise ContractError("PEFT source adapter changed during llama.cpp export")
    return {
        "mode": "direct-peft-adapter",
        "source_adapter": source_adapter,
        "adapter_gguf": str(args.output),
        "adapter_sha256": sha256_file(args.output),
        "base_gguf": str(args.base_gguf),
        "base_gguf_sha256": sha256_file(args.base_gguf),
        "llama_cpp_commit": LLAMA_CPP_COMMIT,
        "llama_cpp_patch_sha256": LLAMA_CPP_PATCH_SHA256,
        "parity": "exact-text-match",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-dir", type=Path, default=model_dir_from_env())
    parser.add_argument("--adapter", type=Path, required=True)
    parser.add_argument("--base-gguf", type=Path, required=True)
    parser.add_argument("--hf-reference", type=Path, required=True)
    parser.add_argument("--llama-cpp", type=Path, default=Path("/opt/llama.cpp"))
    parser.add_argument(
        "--output",
        type=Path,
        default=output_dir_from_env() / "artifacts/adapter-f32.gguf",
    )
    parser.add_argument(
        "--receipt", type=Path, default=output_dir_from_env() / "artifacts/export.json"
    )
    args = parser.parse_args()
    args.model_dir = args.model_dir.resolve()
    args.adapter = args.adapter.resolve()
    args.base_gguf = args.base_gguf.resolve()
    args.hf_reference = args.hf_reference.resolve()
    args.llama_cpp = args.llama_cpp.resolve()
    args.output = args.output.resolve()
    args.receipt = args.receipt.resolve()
    _check_llama_commit(args.llama_cpp)
    receipt = {"protocol": "striatum-llama-export/2", **direct_export(args)}
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
