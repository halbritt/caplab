"""Shared runtime loading helpers for train and evaluation processes."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .contract import MODEL, ContractError


JOB_ROOT = Path(__file__).resolve().parent
DEFAULT_MODEL_DIR = Path("/workspace/models/Qwen3.6-35B-A3B-995ad96e")
DEFAULT_BASE_GGUF = DEFAULT_MODEL_DIR / "gguf/base-bf16.gguf"
DEFAULT_INPUT_DIR = Path("/run/job/inputs")
DEFAULT_OUTPUT_DIR = Path("/run/job")


def _jobrunner_mount() -> Path | None:
    value = os.environ.get("RUNPOD_JOBRUNNER_STORAGE_MOUNT")
    return Path(value) if value else None


def _jobrunner_run_root() -> Path | None:
    explicit = os.environ.get("RUNPOD_JOBRUNNER_RUN_ROOT")
    if explicit:
        return Path(explicit)
    mount = _jobrunner_mount()
    run_id = os.environ.get("RUNPOD_JOBRUNNER_RUN_ID")
    if mount is not None and run_id:
        return mount / "runpod-jobrunner/runs" / run_id
    return None


def model_dir_from_env() -> Path:
    explicit = os.environ.get("STRIATUM_MODEL_DIR")
    if explicit:
        return Path(explicit)
    return DEFAULT_MODEL_DIR


def base_gguf_from_env() -> Path:
    explicit = os.environ.get("STRIATUM_BASE_GGUF")
    if explicit:
        return Path(explicit)
    return DEFAULT_BASE_GGUF


def input_dir_from_env() -> Path:
    explicit = os.environ.get("STRIATUM_INPUT_DIR")
    if explicit:
        return Path(explicit)
    jobrunner_input = os.environ.get("RUNPOD_JOBRUNNER_INPUT_ROOT")
    if jobrunner_input:
        return Path(jobrunner_input)
    run_root = _jobrunner_run_root()
    if run_root is not None:
        return run_root / "input"
    return DEFAULT_INPUT_DIR


def output_dir_from_env() -> Path:
    explicit = os.environ.get("STRIATUM_OUTPUT_DIR")
    if explicit:
        return Path(explicit)
    run_root = _jobrunner_run_root()
    return run_root if run_root is not None else DEFAULT_OUTPUT_DIR


def training_config() -> dict[str, Any]:
    return json.loads((JOB_ROOT / "training-config.json").read_text())


def load_quantized_base(model_dir: Path) -> tuple[Any, Any]:
    """Load the pinned base in 4-bit on the single authorized GPU."""
    try:
        import torch
        from transformers import (
            AutoModelForImageTextToText,
            AutoTokenizer,
            BitsAndBytesConfig,
        )
    except ImportError as error:
        raise ContractError("torch and transformers are required") from error
    if not torch.cuda.is_available():
        raise ContractError("CUDA is required for model execution")

    quantization = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.bfloat16,
    )
    model = AutoModelForImageTextToText.from_pretrained(
        model_dir,
        local_files_only=True,
        quantization_config=quantization,
        torch_dtype=torch.bfloat16,
        device_map={"": torch.cuda.current_device()},
        attn_implementation="flash_attention_2",
    )
    tokenizer = AutoTokenizer.from_pretrained(model_dir, local_files_only=True)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    if getattr(model.config, "model_type", None) != MODEL.model_type:
        raise ContractError(
            f"loaded an unexpected model type: {model.config.model_type!r}"
        )
    return model, tokenizer


def load_bf16_base(model_dir: Path) -> tuple[Any, Any]:
    """Load a BF16 parity base, with bounded CPU offload when needed."""
    try:
        import torch
        from transformers import AutoModelForImageTextToText, AutoTokenizer
    except ImportError as error:
        raise ContractError("torch and transformers are required") from error
    if not torch.cuda.is_available():
        raise ContractError("CUDA is required for model execution")
    model = AutoModelForImageTextToText.from_pretrained(
        model_dir,
        local_files_only=True,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        max_memory={0: "74GiB", "cpu": "120GiB"},
        offload_folder=str(output_dir_from_env() / ".parity-offload"),
        attn_implementation="flash_attention_2",
    )
    tokenizer = AutoTokenizer.from_pretrained(model_dir, local_files_only=True)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    if getattr(model.config, "model_type", None) != MODEL.model_type:
        raise ContractError(
            f"loaded an unexpected model type: {model.config.model_type!r}"
        )
    return model, tokenizer
