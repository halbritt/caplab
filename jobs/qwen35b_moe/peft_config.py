"""Direct PEFT configuration and measured meta-device injection."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping
import hashlib
import json
import re
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
from .cuda_runtime import MIN_H200_MEMORY_MIB
from .profile import TrainingProfile, matched_lora_modules


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
BASE_PREPARATION_PROTOCOL = "striatum-moe-kbit-preparation/1"
FUSED_EXPERT_PARAMETER_COUNT = MODEL.total_layers * 2
FUSED_EXPERT_ELEMENTS = MODEL.total_layers * MODEL.num_experts * (
    (2 * MODEL.expert_intermediate_size * MODEL.hidden_size)
    + (MODEL.hidden_size * MODEL.expert_intermediate_size)
)
FUSED_EXPERT_BF16_BYTES = FUSED_EXPERT_ELEMENTS * 2


def _positive_int(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ContractError(f"{label} must be a positive integer")
    return value


def validate_base_preparation_receipt(
    candidate: Mapping[str, object],
) -> dict[str, object]:
    """Validate the frozen mixed-dtype base before PEFT adapter injection."""

    expected_fields = {
        "protocol",
        "model_type",
        "loaded_in_4bit",
        "base_trainable_parameters",
        "fused_experts",
        "quantized_parameter_count",
        "quantized_adapter_target_count",
        "converted_to_fp32",
        "remaining_half_precision_non_expert_parameters",
        "gradient_checkpointing",
        "cuda_memory",
    }
    if set(candidate) != expected_fields:
        raise ContractError("base-preparation receipt fields are not exact")
    if candidate.get("protocol") != BASE_PREPARATION_PROTOCOL:
        raise ContractError("base-preparation receipt protocol is invalid")
    if candidate.get("model_type") != MODEL.model_type:
        raise ContractError("base-preparation receipt model type is invalid")
    if candidate.get("loaded_in_4bit") is not True:
        raise ContractError("base-preparation receipt does not attest a 4-bit load")
    if candidate.get("base_trainable_parameters") != 0:
        raise ContractError("base-preparation receipt has trainable base parameters")

    fused = candidate.get("fused_experts")
    expected_fused = {
        "parameter_count": FUSED_EXPERT_PARAMETER_COUNT,
        "elements": FUSED_EXPERT_ELEMENTS,
        "bytes": FUSED_EXPERT_BF16_BYTES,
        "dtype": "torch.bfloat16",
        "spec_sha256": FUSED_EXPERT_SPEC_SHA256,
    }
    if not isinstance(fused, Mapping) or dict(fused) != expected_fused:
        raise ContractError("fused experts are not the exact frozen BF16 base tensors")

    quantized_parameter_count = _positive_int(
        candidate.get("quantized_parameter_count"), "quantized parameter count"
    )
    if quantized_parameter_count < 310:
        raise ContractError("fewer than 310 quantized parameters were observed")
    if candidate.get("quantized_adapter_target_count") != 310:
        raise ContractError("the 310 adapter target modules are not all quantized")
    converted = candidate.get("converted_to_fp32")
    if not isinstance(converted, Mapping) or set(converted) != {
        "parameter_count",
        "elements",
    }:
        raise ContractError("converted-to-FP32 census is invalid")
    _positive_int(converted.get("parameter_count"), "converted parameter count")
    _positive_int(converted.get("elements"), "converted element count")
    if candidate.get("remaining_half_precision_non_expert_parameters") != 0:
        raise ContractError("non-expert FP16 or BF16 parameters remain after preparation")
    if candidate.get("gradient_checkpointing") != {
        "enabled": True,
        "use_reentrant": False,
    }:
        raise ContractError("non-reentrant gradient checkpointing is not enabled")

    memory = candidate.get("cuda_memory")
    if not isinstance(memory, Mapping) or set(memory) != {
        "allocated_bytes",
        "reserved_bytes",
        "free_bytes",
        "total_bytes",
    }:
        raise ContractError("CUDA memory census is invalid")
    memory_values: dict[str, int] = {}
    for key in memory:
        value = memory.get(key)
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ContractError("CUDA memory census values must be positive integers")
        memory_values[key] = value
    if (
        memory_values["reserved_bytes"] < memory_values["allocated_bytes"]
        or memory_values["total_bytes"] < memory_values["reserved_bytes"]
        or memory_values["total_bytes"] < memory_values["free_bytes"]
        or memory_values["total_bytes"] < MIN_H200_MEMORY_MIB * 1024 * 1024
    ):
        raise ContractError("CUDA memory census values are inconsistent")
    return dict(candidate)


def _expected_fused_expert_shapes() -> dict[str, tuple[int, int, int]]:
    shapes: dict[str, tuple[int, int, int]] = {}
    for layer in range(MODEL.total_layers):
        prefix = f"model.language_model.layers.{layer}.mlp.experts"
        shapes[f"{prefix}.gate_up_proj"] = (
            MODEL.num_experts,
            2 * MODEL.expert_intermediate_size,
            MODEL.hidden_size,
        )
        shapes[f"{prefix}.down_proj"] = (
            MODEL.num_experts,
            MODEL.hidden_size,
            MODEL.expert_intermediate_size,
        )
    return shapes


FUSED_EXPERT_SPEC_SHA256 = hashlib.sha256(
    json.dumps(
        _expected_fused_expert_shapes(),
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
).hexdigest()


def _prepare_moe_base_for_lora_training(model: Any) -> dict[str, object]:
    """Freeze the exact quantized MoE base without upcasting fused experts."""

    try:
        import torch
    except ImportError as error:
        raise ContractError("torch is required for base-model preparation") from error

    parameters = list(model.named_parameters())
    if getattr(model.config, "model_type", None) != MODEL.model_type:
        raise ContractError("loaded model type does not match the base contract")
    if getattr(model, "is_loaded_in_4bit", False) is not True:
        raise ContractError("base model was not loaded in 4-bit mode")
    quantized_adapter_targets = [
        (name, module)
        for name, module in model.named_modules()
        if re.fullmatch(LINEAR_TARGET_PATTERN, name)
    ]
    if len(quantized_adapter_targets) != 310:
        raise ContractError(
            "loaded adapter-target module count is not exact: "
            f"{len(quantized_adapter_targets)} != 310"
        )
    parameter_ids = {id(parameter) for _, parameter in parameters}
    unquantized_targets = []
    unregistered_targets = []
    for name, module in quantized_adapter_targets:
        weight = getattr(module, "weight", None)
        if weight.__class__.__name__ != "Params4bit":
            unquantized_targets.append(name)
        elif id(weight) not in parameter_ids:
            unregistered_targets.append(name)
    if unquantized_targets:
        raise ContractError(
            "adapter target modules were not loaded in 4-bit mode: "
            f"{unquantized_targets[:3]}"
        )
    if unregistered_targets:
        raise ContractError(
            "adapter target weights are not registered model parameters: "
            f"{unregistered_targets[:3]}"
        )
    expected_fused = _expected_fused_expert_shapes()
    actual_fused = {
        name: parameter
        for name, parameter in parameters
        if ".mlp.experts." in name
    }
    if set(actual_fused) != set(expected_fused):
        missing = sorted(set(expected_fused) - set(actual_fused))
        extra = sorted(set(actual_fused) - set(expected_fused))
        raise ContractError(
            "loaded fused-expert parameter set is not exact: "
            f"missing={missing[:3]}, extra={extra[:3]}"
        )

    fused_elements = 0
    fused_bytes = 0
    for name, expected_shape in expected_fused.items():
        parameter = actual_fused[name]
        if tuple(parameter.shape) != expected_shape:
            raise ContractError(
                f"loaded fused-expert shape is invalid for {name}: "
                f"{tuple(parameter.shape)} != {expected_shape}"
            )
        if parameter.dtype != torch.bfloat16:
            raise ContractError(f"loaded fused expert is not BF16: {name}")
        fused_elements += parameter.numel()
        fused_bytes += parameter.numel() * parameter.element_size()
    if (
        fused_elements != FUSED_EXPERT_ELEMENTS
        or fused_bytes != FUSED_EXPERT_BF16_BYTES
    ):
        raise ContractError("loaded fused-expert storage does not match the model contract")

    quantized_parameter_count = sum(
        1
        for _, parameter in parameters
        if parameter.__class__.__name__ == "Params4bit"
    )
    if quantized_parameter_count < 310:
        raise ContractError("fewer than 310 quantized parameters were observed")
    conversion_candidates = [
        (name, parameter)
        for name, parameter in parameters
        if name not in expected_fused
        and parameter.__class__.__name__ != "Params4bit"
        and parameter.dtype in (torch.float16, torch.bfloat16)
    ]
    converted_parameter_count = len(conversion_candidates)
    converted_elements = sum(
        parameter.numel() for _, parameter in conversion_candidates
    )
    _positive_int(converted_parameter_count, "converted parameter count")
    _positive_int(converted_elements, "converted element count")
    if not callable(getattr(model, "gradient_checkpointing_enable", None)):
        raise ContractError("loaded model does not support gradient checkpointing")

    for _, parameter in parameters:
        parameter.requires_grad = False

    for _, parameter in conversion_candidates:
        parameter.data = parameter.data.to(torch.float32)

    remaining_half = sum(
        1
        for name, parameter in parameters
        if name not in expected_fused
        and parameter.__class__.__name__ != "Params4bit"
        and parameter.dtype in (torch.float16, torch.bfloat16)
    )
    base_trainable = sum(
        parameter.numel() for _, parameter in parameters if parameter.requires_grad
    )
    model.gradient_checkpointing_enable(
        gradient_checkpointing_kwargs={"use_reentrant": False}
    )
    if getattr(model, "is_gradient_checkpointing", False) is not True:
        raise ContractError("gradient checkpointing did not become active")
    torch.cuda.empty_cache()
    free_bytes, total_bytes = torch.cuda.mem_get_info()
    receipt: dict[str, object] = {
        "protocol": BASE_PREPARATION_PROTOCOL,
        "model_type": MODEL.model_type,
        "loaded_in_4bit": True,
        "base_trainable_parameters": base_trainable,
        "fused_experts": {
            "parameter_count": len(actual_fused),
            "elements": fused_elements,
            "bytes": fused_bytes,
            "dtype": str(torch.bfloat16),
            "spec_sha256": FUSED_EXPERT_SPEC_SHA256,
        },
        "quantized_parameter_count": quantized_parameter_count,
        "quantized_adapter_target_count": len(quantized_adapter_targets),
        "converted_to_fp32": {
            "parameter_count": converted_parameter_count,
            "elements": converted_elements,
        },
        "remaining_half_precision_non_expert_parameters": remaining_half,
        "gradient_checkpointing": {
            "enabled": True,
            "use_reentrant": False,
        },
        "cuda_memory": {
            "allocated_bytes": int(torch.cuda.memory_allocated()),
            "reserved_bytes": int(torch.cuda.memory_reserved()),
            "free_bytes": int(free_bytes),
            "total_bytes": int(total_bytes),
        },
    }
    return validate_base_preparation_receipt(receipt)


def prepare_base_for_lora_training(
    model: Any, profile: TrainingProfile | None = None
) -> dict[str, object]:
    """Prepare the strict production MoE base or the dense smoke family."""

    if profile is None or profile.model_type == MODEL.model_type:
        return _prepare_moe_base_for_lora_training(model)
    try:
        import torch
        from peft import prepare_model_for_kbit_training
    except ImportError as error:
        raise ContractError("torch and PEFT are required for base preparation") from error
    if getattr(model.config, "model_type", None) != profile.model_type:
        raise ContractError("loaded model type does not match the selected profile")
    if getattr(model, "is_loaded_in_4bit", False) is not True:
        raise ContractError("base model was not loaded in 4-bit mode")
    strategy = profile.strategy(LINEAR_ONLY)
    pattern = strategy.get("target_pattern")
    if not isinstance(pattern, str):
        raise ContractError("dense profile has no LoRA target pattern")
    targets = matched_lora_modules(model, pattern)
    expected = strategy.get("expected_target_count")
    if len(targets) != expected:
        raise ContractError(
            f"loaded adapter-target module count is not exact: {len(targets)} != {expected}"
        )
    unquantized = [
        name
        for name, module in model.named_modules()
        if name in targets
        and getattr(module, "weight", None).__class__.__name__ != "Params4bit"
    ]
    if unquantized:
        raise ContractError(f"adapter targets are not 4-bit: {unquantized[:3]}")
    prepare_model_for_kbit_training(
        model,
        use_gradient_checkpointing=True,
        gradient_checkpointing_kwargs={"use_reentrant": False},
    )
    base_trainable = sum(
        parameter.numel()
        for _, parameter in model.named_parameters()
        if parameter.requires_grad
    )
    if base_trainable:
        raise ContractError(f"base parameters remain trainable: {base_trainable}")
    free_bytes, total_bytes = torch.cuda.mem_get_info()
    return {
        "protocol": "striatum-dense-kbit-preparation/1",
        "model_type": profile.model_type,
        "loaded_in_4bit": True,
        "base_trainable_parameters": 0,
        "quantized_adapter_target_count": len(targets),
        "gradient_checkpointing": {
            "enabled": bool(getattr(model, "is_gradient_checkpointing", False)),
            "use_reentrant": False,
        },
        "cuda_memory": {
            "allocated_bytes": int(torch.cuda.memory_allocated()),
            "reserved_bytes": int(torch.cuda.memory_reserved()),
            "free_bytes": int(free_bytes),
            "total_bytes": int(total_bytes),
        },
    }


def lora_config(strategy: str, profile: TrainingProfile | None = None) -> Any:
    try:
        from peft import LoraConfig
    except ImportError as error:
        raise ContractError("PEFT is required for paid preflight") from error

    selected = profile
    strategy_config = selected.strategy(strategy) if selected is not None else {}
    target_pattern = strategy_config.get("target_pattern", LINEAR_TARGET_PATTERN)
    rank = strategy_config.get("rank", 32)
    alpha = strategy_config.get("alpha", 64)
    dropout = strategy_config.get(
        "dropout", 0.0 if strategy == EXPERT_AWARE else 0.05
    )
    kwargs: dict[str, Any] = {
        "base_model_name_or_path": selected.model_id if selected else MODEL.model_id,
        "revision": selected.model_revision if selected else MODEL.revision,
        "r": rank,
        "lora_alpha": alpha,
        "lora_dropout": dropout,
        "bias": "none",
        "task_type": "CAUSAL_LM",
        "target_modules": target_pattern,
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


def bind_adapter_source(model: Any, profile: TrainingProfile) -> None:
    """Keep saved adapters bound to the immutable model ID, not a host path."""

    configs = getattr(model, "peft_config", None)
    if not isinstance(configs, Mapping) or not configs:
        raise ContractError("PEFT model has no adapter configuration")
    for config in configs.values():
        config.base_model_name_or_path = profile.model_id
        config.revision = profile.model_revision


def inject_on_meta(
    model_dir: str,
    strategy: str,
    profile: TrainingProfile | None = None,
) -> tuple[Any, AdapterMeasurement | dict[str, object]]:
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
        if profile is not None:
            target_config = profile.strategy(strategy)
            pattern = target_config.get("target_pattern")
            if not isinstance(pattern, str):
                raise ContractError("training profile has no LoRA target pattern")
            targets = matched_lora_modules(model, pattern)
            expected = target_config.get("expected_target_count")
            if len(targets) != expected:
                raise ContractError(
                    f"LoRA target count mismatch: {len(targets)} != {expected}"
                )
            predicted = _predicted_lora_parameters(model, targets, target_config)
            configured_prediction = target_config.get(
                "expected_trainable_parameters", predicted
            )
            if predicted != configured_prediction:
                raise ContractError(
                    "meta-derived LoRA trainables do not match the profile: "
                    f"{predicted} != {configured_prediction}"
                )
        model = get_peft_model(model, lora_config(strategy, profile))
        if profile is not None:
            bind_adapter_source(model, profile)
    if profile is not None and profile.model_type != MODEL.model_type:
        evidence = adapter_evidence(model, targets, predicted, profile, strategy)
        return model, evidence
    measured = measure_adapter(model, strategy)
    validate_adapter_measurement(measured, expected_adapter_measurement(strategy))
    return model, measured


def _predicted_lora_parameters(
    model: Any, targets: tuple[str, ...], strategy: Mapping[str, Any]
) -> int:
    rank = strategy.get("rank")
    if isinstance(rank, bool) or not isinstance(rank, int) or rank <= 0:
        raise ContractError("LoRA rank must be a positive integer")
    modules = dict(model.named_modules())
    total = 0
    for name in targets:
        weight = getattr(modules[name], "weight", None)
        shape = getattr(weight, "shape", None)
        if shape is None or len(shape) != 2:
            raise ContractError(f"LoRA target is not a matrix module: {name}")
        total += rank * (int(shape[0]) + int(shape[1]))
    if total <= 0:
        raise ContractError("predicted LoRA parameter count is zero")
    return total


def adapter_evidence(
    model: Any,
    targets: tuple[str, ...],
    predicted_trainable: int,
    profile: TrainingProfile,
    strategy: str,
) -> dict[str, object]:
    total = 0
    trainable = 0
    base_trainable = 0
    for name, parameter in model.named_parameters():
        count = parameter.numel()
        total += count
        if not parameter.requires_grad:
            continue
        trainable += count
        if ".lora_" not in name and "lora_embedding_" not in name:
            base_trainable += count
    if base_trainable:
        raise ContractError(f"base parameters remain trainable: {base_trainable}")
    if trainable != predicted_trainable:
        raise ContractError(
            "measured PEFT trainables do not match the module-derived prediction: "
            f"{trainable} != {predicted_trainable}"
        )
    return {
        "protocol": "striatum-adapter-evidence/1",
        "model": {
            "id": profile.model_id,
            "revision": profile.model_revision,
            "model_type": profile.model_type,
        },
        "strategy": strategy,
        "matched_modules": list(targets),
        "matched_module_count": len(targets),
        "total_parameters": total,
        "trainable_parameters": trainable,
        "base_trainable_parameters": base_trainable,
    }


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
    adapter_storage_bytes = 0
    for name, parameter in model.named_parameters():
        if not parameter.requires_grad:
            continue
        count = parameter.numel()
        trainable += count
        if ".lora_" not in name and "lora_embedding_" not in name:
            base_trainable += count
            continue
        if str(parameter.dtype) != "torch.float32":
            raise ContractError(f"trainable adapter parameter is not FP32: {name}")
        adapter_storage_bytes += count * parameter.element_size()
        category = _category(name)
        category_parameters[category] += count
        targets[category].add(name.split(".lora_", 1)[0])

    categories = ("linear_attention", "attention", "shared_expert", "routed_expert")
    measured = AdapterMeasurement(
        strategy=strategy,
        rank=32,
        expert_rank=1 if strategy == EXPERT_AWARE else None,
        trainable_parameters=trainable,
        fp32_bytes=adapter_storage_bytes,
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
