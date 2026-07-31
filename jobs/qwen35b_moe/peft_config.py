"""Direct PEFT configuration and measured meta-device injection."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from .contract import (
    EXPERT_AWARE,
    LINEAR_ONLY,
    MODEL,
    AdapterMeasurement,
    ContractError,
    expected_adapter_measurement,
    validate_adapter_measurement,
)


# A full-path regex prevents similarly named vision modules or routed expert
# parameters from entering the ordinary Linear target set.
LINEAR_TARGET_PATTERN = (
    r".*model\.language_model\.layers\.\d+\."
    r"(?:"
    r"linear_attn\.(?:in_proj_qkv|in_proj_z|in_proj_b|in_proj_a|out_proj)"
    r"|self_attn\.(?:q_proj|k_proj|v_proj|o_proj)"
    r"|mlp\.shared_expert\.(?:gate_proj|up_proj|down_proj)"
    r")$"
)
ROUTED_TARGET_PARAMETERS = (
    "mlp.experts.gate_up_proj",
    "mlp.experts.down_proj",
)


def lora_config(strategy: str) -> Any:
    try:
        from peft import LoraConfig
    except ImportError as error:
        raise ContractError("PEFT is required for paid preflight") from error

    kwargs: dict[str, Any] = {
        "base_model_name_or_path": MODEL.model_id,
        "revision": MODEL.revision,
        "r": 32,
        "lora_alpha": 64,
        "lora_dropout": 0.0 if strategy == EXPERT_AWARE else 0.05,
        "bias": "none",
        "task_type": "CAUSAL_LM",
        "target_modules": LINEAR_TARGET_PATTERN,
    }
    if strategy == EXPERT_AWARE:
        kwargs.update(
            target_parameters=list(ROUTED_TARGET_PARAMETERS),
            rank_pattern={target: 1 for target in ROUTED_TARGET_PARAMETERS},
            alpha_pattern={target: 2 for target in ROUTED_TARGET_PARAMETERS},
        )
    elif strategy != LINEAR_ONLY:
        raise ContractError(f"unknown PEFT strategy: {strategy}")
    return LoraConfig(**kwargs)


def inject_on_meta(model_dir: str, strategy: str) -> tuple[Any, AdapterMeasurement]:
    """Instantiate on meta, inject PEFT, and fail unless counts match shapes."""
    try:
        from accelerate import init_empty_weights
        from peft import get_peft_model
        from transformers import AutoConfig, AutoModelForImageTextToText
    except ImportError as error:
        raise ContractError(
            "accelerate, transformers, and PEFT are required for paid preflight"
        ) from error

    config = AutoConfig.from_pretrained(model_dir, local_files_only=True)
    with init_empty_weights():
        model = AutoModelForImageTextToText.from_config(config)
        model = get_peft_model(model, lora_config(strategy))
    measured = measure_adapter(model, strategy)
    validate_adapter_measurement(measured, expected_adapter_measurement(strategy))
    return model, measured


def _category(name: str) -> str:
    if ".linear_attn." in name:
        return "linear_attention"
    if ".self_attn." in name:
        return "attention"
    if ".mlp.shared_expert." in name:
        return "shared_expert"
    if ".mlp.experts." in name:
        return "routed_expert"
    return "unknown"


def measure_adapter(model: Any, strategy: str) -> AdapterMeasurement:
    category_parameters: dict[str, int] = defaultdict(int)
    targets: dict[str, set[str]] = defaultdict(set)
    base_trainable = 0
    trainable = 0
    for name, parameter in model.named_parameters():
        if not parameter.requires_grad:
            continue
        count = parameter.numel()
        trainable += count
        if ".lora_" not in name and "lora_embedding_" not in name:
            base_trainable += count
            continue
        category = _category(name)
        category_parameters[category] += count
        targets[category].add(name.split(".lora_", 1)[0])

    categories = ("linear_attention", "attention", "shared_expert", "routed_expert")
    measured = AdapterMeasurement(
        strategy=strategy,
        rank=32,
        expert_rank=1 if strategy == EXPERT_AWARE else None,
        trainable_parameters=trainable,
        fp32_bytes=trainable * 4,
        base_trainable_parameters=base_trainable,
        target_counts={category: len(targets[category]) for category in categories},
        category_parameters={
            category: category_parameters[category] for category in categories
        },
    )
    if category_parameters.get("unknown"):
        raise ContractError(
            f"uncategorized trainable adapter parameters: {category_parameters['unknown']}"
        )
    return measured
