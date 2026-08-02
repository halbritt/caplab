from __future__ import annotations

import argparse
import base64
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT))

from jobs.qwen35b_moe.contract import (  # noqa: E402
    EXPERT_AWARE,
    LINEAR_ONLY,
    MODEL,
    AdapterMeasurement,
    Census,
    ContractError,
    InputFile,
    expected_adapter_measurement,
    load_input_manifest,
    sha256_file,
    validate_adapter_measurement,
    validate_census,
    verify_input_tree,
)
from jobs.qwen35b_moe.base_gguf import (  # noqa: E402
    validate_base_gguf_artifacts,
)
from jobs.qwen35b_moe.build_image import (  # noqa: E402
    _asset_manifest_receipt,
    _validate_jobrunner_release,
    _write_receipt,
)
from jobs.qwen35b_moe.cuda_runtime import (  # noqa: E402
    validate_cuda_observations,
    validate_cuda_runtime_receipt,
)
from jobs.qwen35b_moe.export import (  # noqa: E402
    LLAMA_CPP_COMMIT,
    LLAMA_CPP_PATCH_SHA256,
    direct_export,
    inspect_peft_adapter,
)
from jobs.qwen35b_moe.evaluate import (  # noqa: E402
    _read_examples,
    PARITY_MAX_NEW_TOKENS,
    derive_checkpoint_25_dispatch_ids,
    require_valid_inference,
    verify_evaluation_results,
    verify_longest_evaluation_receipt,
)
from jobs.qwen35b_moe.materialize import _render_job, materialize  # noqa: E402
from jobs.qwen35b_moe.gate_acceptance import (  # noqa: E402
    _resolve_controller_recovery,
    validate_gate3_acceptance,
)
from jobs.qwen35b_moe.flash_qla_smoke import (  # noqa: E402
    _observe_flash_qla_calls,
    validate_flash_qla_smoke_receipt,
)
from jobs.qwen35b_moe.fla_dispatch_compat import (  # noqa: E402
    BACKEND_ADAPTATION,
    BACKEND_ADMISSION,
    BACKEND_REJECTIONS,
    BACKEND_RETURN,
    POSTIMAGE_DECORATORS,
    PREIMAGE_DECORATORS,
    patch_backend_source,
    patch_source,
)
from jobs.qwen35b_moe.hopper_backend import (  # noqa: E402
    bind_required_hopper_backend,
    validate_hopper_backend_evidence,
)
from jobs.qwen35b_moe.peft_config import (  # noqa: E402
    FUSED_EXPERT_SPEC_SHA256,
    LINEAR_TARGET_PATTERN,
    ROUTED_TARGET_PARAMETERS,
    lora_config,
    measure_adapter,
    prepare_base_for_lora_training,
    validate_base_preparation_receipt,
)
from jobs.qwen35b_moe.package import (  # noqa: E402
    EXPECTED_CHECKPOINT_STEPS,
    build_manifest,
    validate_export_receipt,
)
from jobs.qwen35b_moe.package_smoke import _terminal_evidence_failures  # noqa: E402
from jobs.qwen35b_moe.preflight import (  # noqa: E402
    PACKAGES,
    verify_liger_fused_loss_receipt,
    verify_longest_example_receipt,
)
from jobs.qwen35b_moe.runtime import (  # noqa: E402
    base_gguf_from_env,
    model_dir_from_env,
    output_dir_from_env,
)
from jobs.qwen35b_moe import preflight as preflight_module  # noqa: E402
from jobs.qwen35b_moe import recover_export as recover_export_module  # noqa: E402
from jobs.qwen35b_moe import score_fate as score_fate_module  # noqa: E402
from jobs.qwen35b_moe import train as train_module  # noqa: E402
from jobs.qwen35b_moe.train import (  # noqa: E402
    ACK_NAMESPACE,
    ACK_PROTOCOL,
    _checkpoint_manifest,
    _production_adapter_evidence,
    require_checkpoint_acknowledgement,
    require_no_full_logits,
    select_longest_tokenized_index,
    should_force_final_checkpoint,
    synchronize_resumed_optimizer_learning_rate,
    synchronize_trainer_save_interval,
    validate_liger_fused_loss_proof,
    verify_checkpoint_manifest,
)
from jobs.qwen35b_moe import train_phase  # noqa: E402
from jobs.qwen35b_moe.train_phase import (  # noqa: E402
    PaidLimits,
    _training_result,
    assess_available_gates,
    optimizer_steps_per_epoch,
    project_paid_run,
    require_available_gate_improvement,
)
from jobs.qwen35b_moe.update_image_digest import update  # noqa: E402
from jobs.qwen35b_moe.volume_assets import (  # noqa: E402
    _manifest_entries,
    validate_asset_receipt,
    verify_asset_manifest,
)
from jobs.qwen35b_moe import verify as verify_module  # noqa: E402
from jobs.qwen35b_moe.profile import (  # noqa: E402
    load_training_profile,
    matched_lora_modules,
    resolve_multimodal_paths,
)
from jobs.qwen35b_moe.data import encode_sft_example  # noqa: E402


JOB = ROOT / "jobs" / "qwen35b_moe"


def test_smoke_profile_selects_dense_model_without_changing_production_default() -> None:
    production = load_training_profile(JOB / "training-config.json")
    smoke = load_training_profile(JOB / "smoke" / "training-config.json")

    assert production.model_id == "Qwen/Qwen3.6-35B-A3B"
    assert production.model_type == "qwen3_5_moe"
    assert production.liger_fused_loss is True
    assert production.runtime["hopper_linear_attention_backend"] == "flash_qla"
    assert smoke.model_id == "Qwen/Qwen3.5-0.8B"
    assert smoke.model_revision == "2fc06364715b967f1860aea9cf38778875588b17"
    assert smoke.model_type == "qwen3_5"
    assert smoke.cutoff_length == 512
    assert smoke.maximum_examples == 8
    assert smoke.liger_fused_loss is False
    assert smoke.runtime["hopper_linear_attention_backend"] == "flash_qla"


def test_training_profile_rejects_unknown_hopper_backend_before_model_loading(
    tmp_path: Path,
) -> None:
    profile = json.loads((JOB / "smoke" / "training-config.json").read_text())
    profile["runtime"]["hopper_linear_attention_backend"] = "implicit-fallback"
    path = tmp_path / "training-config.json"
    path.write_text(json.dumps(profile))

    with pytest.raises(ContractError, match="hopper_linear_attention_backend"):
        load_training_profile(path)


def test_multimodal_paths_are_resolved_inside_the_input_root(tmp_path: Path) -> None:
    image = tmp_path / "assets" / "review-flow.pbm"
    image.parent.mkdir()
    image.write_text("P1\n1 1\n0\n")
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image", "path": "assets/review-flow.pbm"},
                {"type": "text", "text": "Review this flow."},
            ],
        },
        {"role": "assistant", "content": "Looks bounded."},
    ]

    resolved = resolve_multimodal_paths(messages, tmp_path)

    assert resolved[0]["content"][0]["path"] == str(image.resolve())
    assert messages[0]["content"][0]["path"] == "assets/review-flow.pbm"


def test_multimodal_paths_reject_escape_and_lora_targets_fail_closed(
    tmp_path: Path,
) -> None:
    outside = tmp_path.parent / "outside.pbm"
    outside.write_text("P1\n1 1\n0\n")
    messages = [
        {
            "role": "user",
            "content": [{"type": "image", "path": "../outside.pbm"}],
        },
        {"role": "assistant", "content": "No."},
    ]
    with pytest.raises(ContractError, match="outside the input root"):
        resolve_multimodal_paths(messages, tmp_path)

    model = SimpleNamespace(named_modules=lambda: iter([("model.embed_tokens", object())]))
    with pytest.raises(ContractError, match="matched zero modules"):
        matched_lora_modules(model, r".*\\.q_proj$")


def test_sft_encoding_uses_processor_for_image_and_masks_only_the_prompt(
    tmp_path: Path,
) -> None:
    image = tmp_path / "flow.pbm"
    image.write_text("P1\n1 1\n0\n")
    calls: list[list[dict[str, object]]] = []

    class FakeProcessor:
        def apply_chat_template(self, messages, **kwargs):  # noqa: ANN001
            calls.append(messages)
            prompt = len(messages) == 1
            return {
                "input_ids": [[10, 11] if prompt else [10, 11, 20, 21]],
                "attention_mask": [[1, 1] if prompt else [1, 1, 1, 1]],
                "mm_token_type_ids": [[1, 1] if prompt else [1, 1, 0, 0]],
                "pixel_values": [[0.0, 1.0]],
                "image_grid_thw": [[1, 1, 1]],
            }

    encoded = encode_sft_example(
        FakeProcessor(),
        {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "path": "flow.pbm"},
                        {"type": "text", "text": "Review it."},
                    ],
                },
                {"role": "assistant", "content": "Accept."},
            ]
        },
        input_root=tmp_path,
        cutoff=16,
        processing={},
    )

    assert encoded["labels"] == [-100, -100, 20, 21]
    assert encoded["mm_token_type_ids"] == [1, 1, 0, 0]
    assert encoded["pixel_values"] == [[0.0, 1.0]]
    assert calls[0][0]["content"][0]["path"] == str(image.resolve())
    assert len(calls) == 2


def _canonical_json(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode()


def _liger_proof(calls: int = 8) -> dict[str, object]:
    return {
        "protocol": "striatum-liger-fused-loss-proof/1",
        "model_type": "qwen3_5_moe",
        "implementation_module": "liger_kernel.transformers.model.qwen3_5_moe",
        "implementation_name": "lce_forward_conditional_generation",
        "bound_forward_identity_verified": True,
        "fused_linear_cross_entropy": True,
        "training_logits": "not-materialized",
        "no_full_logits_observed": True,
        "observed_forward_calls": calls,
    }


def _flash_qla_receipt() -> dict[str, object]:
    return {
        "protocol": "striatum-flash-qla-smoke/1",
        "dispatcher": "FlashQLABackend",
        "dispatch_calls": 1,
        "production_fused_inputs_adapted": True,
        "device": {"name": "NVIDIA H200", "compute_capability": [9, 0]},
        "shape": {
            "batch": 1,
            "tokens": 64,
            "qk_heads": 16,
            "v_heads": 32,
            "dim": 128,
        },
        "dtype": "bfloat16",
        "forward_finite": True,
        "loss_finite": True,
        "loss": 1.0,
        "gradients": {
            name: "finite-nonzero"
            for name in (
                "q",
                "k",
                "v",
                "g",
                "beta",
                "A_log",
                "dt_bias",
                "initial_state",
            )
        },
        "versions": {
            "flash-linear-attention": "0.5.2",
            "fla-core": "0.5.2",
            "flash-qla": "0.1.2",
            "tilelang": "0.1.9",
            "apache-tvm-ffi": "0.1.9",
        },
    }


def test_flash_qla_receipt_requires_observed_dispatch_without_assuming_call_count() -> None:
    receipt = _flash_qla_receipt()
    receipt["dispatch_calls"] = 2

    assert validate_flash_qla_smoke_receipt(receipt) == receipt

    receipt["dispatch_calls"] = 0
    with pytest.raises(ContractError, match="implementation was not invoked"):
        validate_flash_qla_smoke_receipt(receipt)

    receipt = _flash_qla_receipt()
    receipt["production_fused_inputs_adapted"] = False
    with pytest.raises(ContractError, match="fused-input evidence is missing"):
        validate_flash_qla_smoke_receipt(receipt)


def test_flash_qla_observer_wraps_the_actual_implementation_and_restores_it() -> None:
    original = lambda value: value + 1  # noqa: E731
    module = SimpleNamespace(chunk_gated_delta_rule=original)

    with _observe_flash_qla_calls(module) as observed:
        assert module.chunk_gated_delta_rule(3) == 4
        assert observed["count"] == 1

    assert module.chunk_gated_delta_rule is original


def test_required_hopper_backend_binds_every_qwen_linear_layer_and_records_calls() -> None:
    class LinearLayer:
        def __init__(self) -> None:
            self.chunk_gated_delta_rule = lambda *args, **kwargs: "fallback"
            self.causal_conv1d_fn = lambda x, **kwargs: f"conv-{x}"

    layers = [LinearLayer(), LinearLayer()]
    model = SimpleNamespace(
        named_modules=lambda: iter(
            [
                ("", object()),
                *((f"layer.{index}.linear_attn", layer) for index, layer in enumerate(layers)),
            ]
        )
    )
    calls: list[tuple[tuple[object, ...], dict[str, object]]] = []

    class Backend:
        @classmethod
        def is_available(cls) -> bool:
            return True

        @classmethod
        def is_enabled(cls) -> bool:
            return True

        def verify(self, name, *args, **kwargs):  # noqa: ANN001
            assert name == "chunk_gated_delta_rule"
            return True, None

        def chunk_gated_delta_rule(self, *args, **kwargs):  # noqa: ANN001
            calls.append((args, kwargs))
            return "flash-qla"

    evidence = bind_required_hopper_backend(
        model,
        {"hopper_linear_attention_backend": "flash_qla"},
        compute_capability=(9, 0),
        backend_factory=Backend,
        causal_conv_input_normalizer=lambda value: ("bf16", value == "fp32"),
    )

    assert evidence["bound_module_count"] == 2
    assert evidence["causal_conv_module_count"] == 2
    assert layers[0].causal_conv1d_fn(x="fp32") == "conv-bf16"
    assert evidence["causal_conv_input_casts"] == 1
    assert layers[0].chunk_gated_delta_rule("q", g="g") == "flash-qla"
    assert evidence["observed_calls"] == 1
    assert calls == [(('q',), {"g": "g"})]
    assert validate_hopper_backend_evidence(evidence) == evidence


def test_required_hopper_backend_is_not_applied_on_ampere_and_fails_closed() -> None:
    model = SimpleNamespace(named_modules=lambda: iter([]))
    evidence = bind_required_hopper_backend(
        model,
        {"hopper_linear_attention_backend": "flash_qla"},
        compute_capability=(8, 6),
    )
    assert evidence == {
        "protocol": "striatum-hopper-linear-attention/1",
        "configured_backend": "flash_qla",
        "status": "not-applicable",
        "compute_capability": [8, 6],
        "bound_modules": [],
        "bound_module_count": 0,
        "observed_calls": 0,
        "causal_conv_modules": [],
        "causal_conv_module_count": 0,
        "causal_conv_input_casts": 0,
    }

    class RejectingBackend:
        @classmethod
        def is_available(cls) -> bool:
            return True

        @classmethod
        def is_enabled(cls) -> bool:
            return True

        def verify(self, name, *args, **kwargs):  # noqa: ANN001
            return False, "K must be 128"

        def chunk_gated_delta_rule(self, *args, **kwargs):  # noqa: ANN001
            raise AssertionError("rejected backend must not execute")

    layer = SimpleNamespace(
        chunk_gated_delta_rule=lambda: "fallback",
        causal_conv1d_fn=lambda x: x,
    )
    model = SimpleNamespace(
        named_modules=lambda: iter([("model.layers.0.linear_attn", layer)])
    )
    evidence = bind_required_hopper_backend(
        model,
        {"hopper_linear_attention_backend": "flash_qla"},
        compute_capability=(9, 0),
        backend_factory=RejectingBackend,
        causal_conv_input_normalizer=lambda value: (value, False),
    )
    with pytest.raises(ContractError, match="FlashQLA rejected.*K must be 128"):
        layer.chunk_gated_delta_rule("q")
    with pytest.raises(ContractError, match="no observed FlashQLA layer calls"):
        validate_hopper_backend_evidence(evidence)


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def _cuda_runtime_receipt() -> dict[str, object]:
    return {
        "protocol": "striatum-cuda-runtime/1",
        "cuda_backend_library": "/opt/llama.cpp/build/bin/libggml-cuda.so",
        "driver_library": "/usr/local/nvidia/lib64/libcuda.so.1",
        "llama_cli": "/opt/llama.cpp/build/bin/llama-cli",
        "device": {
            "backend": "CUDA0",
            "name": "NVIDIA H200",
            "memory_mib": 143_771,
        },
    }


def _runtime_asset_receipt() -> dict[str, object]:
    return {
        "protocol": "striatum-runtime-assets/1",
        "assets": {
            "protocol": "striatum-volume-assets/1",
            "manifest_sha256": (
                "2d56aa53dc94146a01f044b04d7d161015c2f848f575779b49fa5307fe295ff8"
            ),
            "files": 41,
            "bytes": 142_993_858_696,
        },
        "census": {
            "protocol": "qwen35b-target-census/1",
            "model": {"id": MODEL.model_id, "revision": MODEL.revision},
            "census": {
                "linear_attention": 150,
                "attention": 40,
                "shared_expert": 120,
                "router": 40,
                "shared_expert_gate": 40,
                "routed_expert": 80,
            },
        },
    }


def _base_preparation_receipt() -> dict[str, object]:
    return {
        "protocol": "striatum-moe-kbit-preparation/1",
        "model_type": "qwen3_5_moe",
        "loaded_in_4bit": True,
        "base_trainable_parameters": 0,
        "fused_experts": {
            "parameter_count": 80,
            "elements": 32_212_254_720,
            "bytes": 64_424_509_440,
            "dtype": "torch.bfloat16",
            "spec_sha256": FUSED_EXPERT_SPEC_SHA256,
        },
        "quantized_parameter_count": 310,
        "quantized_adapter_target_count": 310,
        "converted_to_fp32": {
            "parameter_count": 200,
            "elements": 1000,
        },
        "remaining_half_precision_non_expert_parameters": 0,
        "gradient_checkpointing": {
            "enabled": True,
            "use_reentrant": False,
        },
        "cuda_memory": {
            "allocated_bytes": 80_000_000_000,
            "reserved_bytes": 82_000_000_000,
            "free_bytes": 68_000_000_000,
            "total_bytes": 150_000_000_000,
        },
    }


def _tokenization_census() -> dict[str, object]:
    return json.loads((JOB / "training-config.json").read_text())[
        "tokenization_contract"
    ]


def _longest_training_selection() -> dict[str, object]:
    census = _tokenization_census()
    longest = census["longest_example"]
    assert isinstance(longest, dict)
    return {
        "mode": "longest-tokenized-authorized",
        "candidates": 1_268,
        "selected_global_index": longest["selected_global_index"],
        "dispatch_id": (
            "6722f680dcf58f22c6165ed3569f02f456e5e2a22e05de0ad2dfc3df6097891b"
        ),
        "raw_token_count": longest["raw_token_count"],
        "effective_token_count": longest["effective_token_count"],
        "max_raw_token_count": longest["raw_token_count"],
        "max_effective_token_count": longest["effective_token_count"],
        "token_length_census_sha256": census["full_length_census_sha256"],
        "cutoff": 40_960,
        "tie_break": "effective-length,raw-length,earliest-global-index",
        "tokenization": census,
        "prompt_token_count": longest["prompt_token_count"],
        "assistant_token_count": longest["assistant_token_count"],
        "supervised_token_count": longest["supervised_token_count"],
        "truncation_mode": longest["truncation_mode"],
    }


def test_moe_kbit_preparation_accepts_frozen_bf16_fused_experts() -> None:
    receipt = _base_preparation_receipt()

    assert validate_base_preparation_receipt(receipt) == receipt


def test_moe_kbit_preparation_preserves_only_exact_fused_experts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeTensor:
        def __init__(self, dtype: str, shape: tuple[int, ...]) -> None:
            self.dtype = dtype
            self.shape = shape

        def to(self, dtype: str) -> FakeTensor:
            return FakeTensor(dtype, self.shape)

        def numel(self) -> int:
            total = 1
            for dimension in self.shape:
                total *= dimension
            return total

        def element_size(self) -> int:
            return {
                "torch.uint8": 1,
                "torch.bfloat16": 2,
                "torch.float16": 2,
                "torch.float32": 4,
            }[self.dtype]

    class FakeParameter:
        def __init__(self, dtype: str, shape: tuple[int, ...]) -> None:
            self.data = FakeTensor(dtype, shape)
            self.requires_grad = True

        @property
        def dtype(self) -> str:
            return self.data.dtype

        @property
        def shape(self) -> tuple[int, ...]:
            return self.data.shape

        def numel(self) -> int:
            return self.data.numel()

        def element_size(self) -> int:
            return self.data.element_size()

    class Params4bit(FakeParameter):
        pass

    class FakeCuda:
        def __init__(self) -> None:
            self.cache_cleared = False

        def empty_cache(self) -> None:
            self.cache_cleared = True

        def memory_allocated(self) -> int:
            return 80_000_000_000

        def memory_reserved(self) -> int:
            return 82_000_000_000

        def mem_get_info(self) -> tuple[int, int]:
            return 68_000_000_000, 150_000_000_000

    fake_cuda = FakeCuda()
    fake_torch = SimpleNamespace(
        bfloat16="torch.bfloat16",
        float16="torch.float16",
        float32="torch.float32",
        cuda=fake_cuda,
    )
    monkeypatch.setitem(sys.modules, "torch", fake_torch)

    parameters: list[tuple[str, FakeParameter]] = []
    for layer in range(40):
        parameters.extend(
            [
                (
                    f"model.language_model.layers.{layer}.mlp.experts.gate_up_proj",
                    FakeParameter("torch.bfloat16", (256, 1024, 2048)),
                ),
                (
                    f"model.language_model.layers.{layer}.mlp.experts.down_proj",
                    FakeParameter("torch.bfloat16", (256, 2048, 512)),
                ),
            ]
        )
    normalization = FakeParameter("torch.bfloat16", (2048,))
    parameters.append(("model.language_model.norm.weight", normalization))
    modules: list[tuple[str, object]] = []
    quantized_parameters: list[tuple[str, FakeParameter]] = []

    def add_quantized_module(name: str, shape: tuple[int, ...]) -> None:
        weight = Params4bit("torch.uint8", shape)
        modules.append((name, SimpleNamespace(weight=weight)))
        quantized_parameters.append((f"{name}.weight", weight))

    for layer in range(30):
        for projection in (
            "in_proj_qkv",
            "in_proj_z",
            "in_proj_b",
            "in_proj_a",
            "out_proj",
        ):
            add_quantized_module(
                f"model.language_model.layers.{layer}.linear_attn.{projection}",
                (2048, 2048),
            )
    for layer in range(30, 40):
        for projection in ("q_proj", "k_proj", "v_proj", "o_proj"):
            add_quantized_module(
                f"model.language_model.layers.{layer}.self_attn.{projection}",
                (2048, 2048),
            )
    for layer in range(40):
        for projection in ("gate_proj", "up_proj", "down_proj"):
            add_quantized_module(
                f"model.language_model.layers.{layer}.mlp.shared_expert.{projection}",
                (2048, 512),
            )
    parameters.extend(quantized_parameters)
    quantized = quantized_parameters[0][1]

    class FakeModel:
        def __init__(self) -> None:
            self.config = SimpleNamespace(model_type="qwen3_5_moe")
            self.is_loaded_in_4bit = True
            self.is_gradient_checkpointing = False
            self.gradient_checkpointing_kwargs: dict[str, object] | None = None

        def named_parameters(self):  # noqa: ANN202
            return iter(parameters)

        def named_modules(self):  # noqa: ANN202
            return iter(modules)

        def gradient_checkpointing_enable(self, **kwargs) -> None:  # noqa: ANN003
            self.gradient_checkpointing_kwargs = kwargs
            self.is_gradient_checkpointing = True

    model = FakeModel()

    parameters[:] = [
        item for item in parameters if item not in quantized_parameters
    ]
    with pytest.raises(ContractError, match="registered model parameters"):
        prepare_base_for_lora_training(model)
    assert all(parameter.requires_grad for _, parameter in parameters)
    assert all(parameter.requires_grad for _, parameter in quantized_parameters)
    assert normalization.dtype == "torch.bfloat16"
    assert model.gradient_checkpointing_kwargs is None
    assert fake_cuda.cache_cleared is False
    parameters.extend(quantized_parameters)

    first_expert = parameters[0][1]
    first_expert.data = FakeTensor("torch.bfloat16", (256, 1024, 1024))
    with pytest.raises(ContractError, match="shape is invalid"):
        prepare_base_for_lora_training(model)
    assert all(parameter.requires_grad for _, parameter in parameters)
    assert normalization.dtype == "torch.bfloat16"
    assert model.gradient_checkpointing_kwargs is None
    assert fake_cuda.cache_cleared is False
    first_expert.data = FakeTensor("torch.bfloat16", (256, 1024, 2048))

    receipt = prepare_base_for_lora_training(model)

    assert validate_base_preparation_receipt(receipt) == receipt
    assert all(not parameter.requires_grad for _, parameter in parameters)
    assert all(
        parameter.dtype == "torch.bfloat16"
        for name, parameter in parameters
        if ".mlp.experts." in name
    )
    assert normalization.dtype == "torch.float32"
    assert quantized.dtype == "torch.uint8"
    assert model.gradient_checkpointing_kwargs == {
        "gradient_checkpointing_kwargs": {"use_reentrant": False}
    }
    assert fake_cuda.cache_cleared is True


def test_adapter_measurement_rejects_non_fp32_trainables() -> None:
    class FakeAdapterParameter:
        requires_grad = True
        dtype = "torch.bfloat16"

        def numel(self) -> int:
            return 8

        def element_size(self) -> int:
            return 2

    model = SimpleNamespace(
        named_parameters=lambda: iter(
            [
                (
                    "base_model.model.language_model.layers.0.linear_attn."
                    "in_proj_qkv.lora_A.default.weight",
                    FakeAdapterParameter(),
                )
            ]
        )
    )

    with pytest.raises(ContractError, match="FP32"):
        measure_adapter(model, LINEAR_ONLY)


def _write_closed_checkpoint(checkpoint: Path, step: int) -> dict[str, object]:
    _write_valid_adapter(checkpoint)
    _write_json(checkpoint / "trainer_state.json", {"global_step": step})
    _write_json(checkpoint / "checkpoint-complete.json", _checkpoint_manifest(checkpoint))
    return train_phase.verify_checkpoint(checkpoint, step).to_dict()


def _passing_summary(
    *, examples: int, selection: dict[str, object]
) -> dict[str, object]:
    return {
        "protocol": "striatum-evaluation-result/1",
        "selection": selection,
        "n": examples,
        "json_valid": 1.0,
        "verdict_legal": 1.0,
        "side_match": 1.0,
        "verdict_exact_match": 1.0,
        "verdict_distribution": {"accept": examples},
        "mean_seconds": 1.0,
        "available_gates": {
            "json_valid": True,
            "verdict_legal": True,
            "side_match": True,
        },
    }


def _write_passing_results(path: Path, summary: dict[str, object]) -> None:
    selection = summary["selection"]
    assert isinstance(selection, dict)
    dispatch_ids = selection["dispatch_ids"]
    assert isinstance(dispatch_ids, list)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(
            json.dumps(
                {
                    "dispatch_id": dispatch_id,
                    "seconds": 1.0,
                    "json_valid": True,
                    "verdict": "accept",
                    "verdict_legal": True,
                    "reference_verdict": "accept",
                    "verdict_exact_match": True,
                    "side_match": True,
                    "generated_tokens": [1],
                    "content": '{"verdict":"accept"}',
                }
            )
            + "\n"
            for dispatch_id in dispatch_ids
        )
    )


def test_evaluation_summary_is_bound_to_per_example_results(tmp_path: Path) -> None:
    summary = _passing_summary(
        examples=2,
        selection={"dispatch_ids": ["dispatch-a", "dispatch-b"]},
    )
    results = tmp_path / "results.jsonl"
    _write_passing_results(results, summary)

    assert verify_evaluation_results(summary, results)["verdict_legal"] == 1.0
    rows = results.read_text().splitlines()
    tampered = json.loads(rows[1])
    tampered["content"] = '{"verdict":"reject"}'
    rows[1] = json.dumps(tampered)
    results.write_text("\n".join(rows) + "\n")
    with pytest.raises(ContractError, match="claims disagree"):
        verify_evaluation_results(summary, results)


def _write_hf_reference(path: Path) -> None:
    _write_json(
        path,
        {
            "protocol": "hf-llama-parity-reference/1",
            "rendered_prompt": "prompt",
            "content": '{"verdict":"accept"}',
            "generated_tokens": [1, 2, 3],
            "seed": 42,
        },
    )


def _write_valid_adapter(adapter: Path, strategy: str = LINEAR_ONLY) -> None:
    adapter.mkdir(parents=True, exist_ok=True)
    expert_aware = strategy == EXPERT_AWARE
    _write_json(
        adapter / "adapter_config.json",
        {
            "base_model_name_or_path": MODEL.model_id,
            "revision": MODEL.revision,
            "peft_type": "LORA",
            "task_type": "CAUSAL_LM",
            "inference_mode": True,
            "r": 32,
            "lora_alpha": 64,
            "lora_dropout": 0.0 if expert_aware else 0.05,
            "bias": "none",
            "target_modules": LINEAR_TARGET_PATTERN,
            "target_parameters": (
                list(ROUTED_TARGET_PARAMETERS) if expert_aware else None
            ),
            "rank_pattern": (
                {target: 1 for target in ROUTED_TARGET_PARAMETERS}
                if expert_aware
                else {}
            ),
            "alpha_pattern": (
                {target: 2 for target in ROUTED_TARGET_PARAMETERS}
                if expert_aware
                else {}
            ),
        },
    )
    header = json.dumps(
        {
            "__metadata__": {"format": "pt"},
            "base_model.model.layer.lora_A.weight": {
                "dtype": "F32",
                "shape": [1],
                "data_offsets": [0, 4],
            },
        },
        separators=(",", ":"),
    ).encode()
    (adapter / "adapter_model.safetensors").write_bytes(
        struct.pack("<Q", len(header)) + header + b"\x00\x00\x00\x00"
    )


def test_peft_source_receipt_binds_a_semantically_valid_adapter(tmp_path: Path) -> None:
    adapter = tmp_path / "adapter"
    _write_valid_adapter(adapter)

    receipt = inspect_peft_adapter(adapter)

    assert receipt == {
        "path": str(adapter.resolve()),
        "strategy": "linear-only",
        "files": [
            {
                "path": "adapter_config.json",
                "size": (adapter / "adapter_config.json").stat().st_size,
                "sha256": sha256_file(adapter / "adapter_config.json"),
            },
            {
                "path": "adapter_model.safetensors",
                "size": (adapter / "adapter_model.safetensors").stat().st_size,
                "sha256": sha256_file(adapter / "adapter_model.safetensors"),
            },
        ],
    }


def test_lora_config_pins_the_exact_base_model_revision(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setitem(
        sys.modules,
        "peft",
        SimpleNamespace(LoraConfig=lambda **kwargs: kwargs),
    )

    config = lora_config(LINEAR_ONLY)

    assert config["base_model_name_or_path"] == MODEL.model_id
    assert config["revision"] == MODEL.revision


def test_peft_source_receipt_validates_expert_target_fields(tmp_path: Path) -> None:
    adapter = tmp_path / "expert-adapter"
    _write_valid_adapter(adapter, EXPERT_AWARE)

    assert inspect_peft_adapter(adapter)["strategy"] == EXPERT_AWARE


def test_packaging_rejects_adapter_tampered_after_export(tmp_path: Path) -> None:
    adapter = tmp_path / "adapter"
    _write_valid_adapter(adapter)
    gguf = tmp_path / "adapter-f32.gguf"
    receipt = tmp_path / "export.json"
    _write_export_receipt(receipt, gguf, adapter)
    validate_export_receipt(receipt, gguf, adapter)

    weights = adapter / "adapter_model.safetensors"
    tampered = bytearray(weights.read_bytes())
    tampered[-1] ^= 1
    weights.write_bytes(tampered)

    with pytest.raises(ContractError, match="does not bind the current PEFT"):
        validate_export_receipt(receipt, gguf, adapter)


def test_direct_export_receipt_binds_the_adapter_it_converted(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    adapter = tmp_path / "adapter"
    _write_valid_adapter(adapter)
    llama_cpp = tmp_path / "llama.cpp"
    converter = llama_cpp / "convert_lora_to_gguf.py"
    llama_cli = llama_cpp / "build/bin/llama-cli"
    converter.parent.mkdir(parents=True)
    llama_cli.parent.mkdir(parents=True)
    converter.touch()
    llama_cli.touch()
    base_gguf = tmp_path / "base.gguf"
    base_gguf.write_bytes(b"GGUF-base")
    reference = tmp_path / "hf-reference.json"
    _write_hf_reference(reference)
    output = tmp_path / "adapter-f32.gguf"

    def fake_run(command, **kwargs):  # noqa: ANN001, ANN003
        del kwargs
        if str(converter) in command:
            output.write_bytes(b"GGUF-adapter")
            return SimpleNamespace(stdout="")
        assert str(llama_cli) in command
        return SimpleNamespace(stdout='{"verdict":"accept"}\n')

    monkeypatch.setattr("jobs.qwen35b_moe.export._run", fake_run)
    args = argparse.Namespace(
        llama_cpp=llama_cpp,
        base_gguf=base_gguf,
        adapter=adapter,
        output=output,
        model_dir=tmp_path / "model",
        hf_reference=reference,
    )

    receipt = direct_export(args)

    assert receipt["source_adapter"] == inspect_peft_adapter(adapter)


def test_peft_adapter_rejects_malformed_and_wrong_revision_config(
    tmp_path: Path,
) -> None:
    adapter = tmp_path / "adapter"
    _write_valid_adapter(adapter)
    config_path = adapter / "adapter_config.json"

    config_path.write_text("{", encoding="utf-8")
    with pytest.raises(ContractError, match="not valid JSON"):
        inspect_peft_adapter(adapter)

    _write_valid_adapter(adapter)
    config = json.loads(config_path.read_text())
    config["revision"] = "f" * 40
    _write_json(config_path, config)
    with pytest.raises(ContractError, match="pinned model and strategy"):
        inspect_peft_adapter(adapter)

    _write_valid_adapter(adapter)
    config = json.loads(config_path.read_text())
    config["inference_mode"] = 1
    _write_json(config_path, config)
    with pytest.raises(ContractError, match="pinned model and strategy"):
        inspect_peft_adapter(adapter)


def test_peft_adapter_rejects_non_safetensors_weights(tmp_path: Path) -> None:
    adapter = tmp_path / "adapter"
    _write_valid_adapter(adapter)
    (adapter / "adapter_model.safetensors").write_bytes(b"not-safetensors")

    with pytest.raises(ContractError, match="safetensors"):
        inspect_peft_adapter(adapter)


def _write_export_receipt(path: Path, gguf: Path, adapter: Path) -> None:
    gguf.parent.mkdir(parents=True, exist_ok=True)
    gguf.write_bytes(b"GGUF-adapter")
    _write_json(
        path,
        {
            "protocol": "striatum-llama-export/2",
            "mode": "direct-peft-adapter",
            "source_adapter": inspect_peft_adapter(adapter),
            "adapter_gguf": str(gguf.resolve()),
            "adapter_sha256": sha256_file(gguf),
            "base_gguf": "/opt/models/base.gguf",
            "base_gguf_sha256": "b" * 64,
            "llama_cpp_commit": LLAMA_CPP_COMMIT,
            "llama_cpp_patch_sha256": LLAMA_CPP_PATCH_SHA256,
            "parity": "exact-text-match",
        },
    )


def _signed_checkpoint_ack(
    tmp_path: Path,
    checkpoint: Path,
    *,
    run_id: str = "run-checkpoint-ack",
) -> tuple[Path, Path, Path, Path, bytes]:
    storage_mount = tmp_path / "storage"
    run_root = storage_mount / "runpod-jobrunner" / "runs" / run_id
    key = tmp_path / "controller-key"
    subprocess.run(
        ["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-C", "", "-f", str(key)],
        check=True,
    )
    public_fields = key.with_suffix(".pub").read_text().strip().split()
    public_key = f"ssh-ed25519 {public_fields[1]}"
    key_blob = base64.b64decode(public_fields[1], validate=True)
    signer = {
        "algorithm": "ssh-ed25519",
        "identity": f"runpod-jobrunner:{run_id}",
        "key_id": "SHA256:"
        + base64.b64encode(hashlib.sha256(key_blob).digest()).decode().rstrip("="),
        "namespace": ACK_NAMESPACE,
        "public_key": public_key,
    }
    request = {
        "protocol": "run-request/1",
        "run_id": run_id,
        "bundle_hash": "a" * 64,
        "image_digest": f"example.invalid/qwen@sha256:{'b' * 64}",
        "supported_protocol_majors": {
            "artifact-manifest": [1],
            "incremental-mirror-ack": [1],
            "run-event": [1],
            "run-request": [1],
            "run-status": [1],
        },
        "incremental_mirror_ack": {
            "protocol": ACK_PROTOCOL,
            "directory": "control/incremental-acks",
            "timeout_seconds": 1,
            "signer": signer,
        },
    }
    run_root.mkdir(parents=True)
    request_path = run_root / "request.json"
    request_path.write_text(json.dumps(request))
    manifest_path = checkpoint / "checkpoint-complete.json"
    manifest = json.loads(manifest_path.read_text())
    manifest_relative = manifest_path.relative_to(storage_mount).as_posix()
    unsigned = {
        "protocol": ACK_PROTOCOL,
        "run_id": run_id,
        "bundle_hash": request["bundle_hash"],
        "image_digest": request["image_digest"],
        "manifest_path": manifest_relative,
        "manifest_size": manifest_path.stat().st_size,
        "manifest_sha256": sha256_file(manifest_path),
        "file_count": len(manifest["files"]),
        "file_bytes": sum(item["size"] for item in manifest["files"]),
        "local_receipt_sha256": "c" * 64,
        "signer": signer,
    }
    statement = tmp_path / "ack-statement.json"
    statement.write_bytes(_canonical_json(unsigned))
    subprocess.run(
        [
            "ssh-keygen",
            "-Y",
            "sign",
            "-f",
            str(key),
            "-n",
            ACK_NAMESPACE,
            str(statement),
        ],
        check=True,
        capture_output=True,
    )
    signature = statement.with_suffix(".json.sig").read_bytes()
    encoded = (
        _canonical_json({**unsigned, "signature": base64.b64encode(signature).decode()})
        + b"\n"
    )
    ack_name = hashlib.sha256(manifest_relative.encode()).hexdigest() + ".json"
    ack_path = run_root / "control/incremental-acks" / ack_name
    return request_path, run_root, storage_mount, ack_path, encoded


def test_input_manifest_is_the_exact_sft_only_allow_list() -> None:
    manifest = load_input_manifest(JOB / "input-manifest.json")

    assert [entry.path for entry in manifest] == [
        "sft/review.train.jsonl",
        "sft/review.eval.jsonl",
        "sft/implementation-planning.train.jsonl",
        "sft/design-convergence.train.jsonl",
        "sft/proposal-generation.train.jsonl",
    ]
    assert sum(entry.size for entry in manifest) == 119_218_345
    assert all(entry.path.startswith("sft/") for entry in manifest)
    assert not any("corpus" in entry.path for entry in manifest)
    assert [entry.sha256 for entry in manifest] == [
        "3578d14d5301a18eb4f081c427e326fc96877786ecb82d0ed05acdecef8ca8b7",
        "1de3ce2f185b37f86200be46365bcbac64862d4465ad5ba951573adefd2fb36d",
        "730f22ae1e18715952839fada76d08483b35904c985c21d54c9acf58c7c8cda9",
        "0bc7029702ab73ff046f8ff33ec8985eb90e0888bb0de28c49bf3e5a93b180ec",
        "22c092902c887dc184f49326575ef1c21145ace98cfeffcca1bae980470d133d",
    ]


def test_runtime_input_tree_rejects_symlinks_and_extra_files(tmp_path: Path) -> None:
    sft = tmp_path / "sft"
    sft.mkdir()
    regular = sft / "one.jsonl"
    regular.write_text("{}\n")
    entry = InputFile(
        path="sft/one.jsonl",
        size=regular.stat().st_size,
        sha256=sha256_file(regular),
    )
    verify_input_tree(tmp_path, (entry,))

    link = sft / "linked.jsonl"
    link.symlink_to(regular)
    with pytest.raises(ContractError, match="symlink"):
        verify_input_tree(tmp_path, (entry,))
    link.unlink()

    extra = sft / "extra.jsonl"
    extra.write_text("{}\n")
    with pytest.raises(ContractError, match="extra"):
        verify_input_tree(tmp_path, (entry,))


def test_base_gguf_receipts_bind_source_and_native_splits(
    tmp_path: Path,
) -> None:
    source = tmp_path / "base-bf16.gguf"
    source.write_bytes(b"source")
    source_receipt = {
        "protocol": "striatum-base-gguf-readiness/1",
        "model_revision": MODEL.revision,
        "llama_cpp_commit": LLAMA_CPP_COMMIT,
        "path": str(source),
        "size": source.stat().st_size,
        "sha256": sha256_file(source),
    }
    (tmp_path / "base-bf16.receipt.json").write_text(json.dumps(source_receipt))
    shards = (
        tmp_path / "base-bf16-00001-of-00002.gguf",
        tmp_path / "base-bf16-00002-of-00002.gguf",
    )
    shards[0].write_bytes(b"sou")
    shards[1].write_bytes(b"rce")
    split_receipt = {
        "protocol": "striatum-base-gguf-split/1",
        "model_revision": MODEL.revision,
        "llama_cpp_commit": LLAMA_CPP_COMMIT,
        "source_size": source_receipt["size"],
        "source_sha256": source_receipt["sha256"],
        "split_max_size": "4G",
        "first_shard": shards[0].name,
        "shards": [
            {
                "path": shard.name,
                "size": shard.stat().st_size,
                "sha256": sha256_file(shard),
            }
            for shard in shards
        ],
    }
    (tmp_path / "base-bf16.split-receipt.json").write_text(json.dumps(split_receipt))

    artifacts = validate_base_gguf_artifacts(tmp_path)
    assert artifacts.first_shard == shards[0]
    assert artifacts.shards == shards

    shards[1].write_bytes(b"bad")
    with pytest.raises(ContractError, match="receipt entry mismatch|hash mismatch"):
        validate_base_gguf_artifacts(tmp_path)


def test_checkpoint_completion_manifest_is_hash_complete(tmp_path: Path) -> None:
    checkpoint = tmp_path / "checkpoint-5"
    checkpoint.mkdir()
    state = checkpoint / "trainer_state.json"
    state.write_text('{"global_step": 5}\n')
    manifest = _checkpoint_manifest(checkpoint)
    (checkpoint / "checkpoint-complete.json").write_text(json.dumps(manifest))

    assert verify_checkpoint_manifest(checkpoint) == manifest

    state.write_text('{"global_step": 4}\n')
    with pytest.raises(ContractError, match="does not match"):
        verify_checkpoint_manifest(checkpoint)


def test_checkpoint_acknowledgement_waits_verifies_and_binds_resume(
    tmp_path: Path,
) -> None:
    checkpoint = tmp_path / "storage/checkpoints/checkpoint-159"
    checkpoint.mkdir(parents=True)
    (checkpoint / "trainer_state.json").write_text('{"global_step": 159}\n')
    (checkpoint / "checkpoint-complete.json").write_text(
        json.dumps(_checkpoint_manifest(checkpoint), indent=2, sort_keys=True) + "\n"
    )
    request_path, run_root, storage_mount, ack_path, encoded = _signed_checkpoint_ack(
        tmp_path, checkpoint
    )

    with pytest.raises(ContractError, match="not durably acknowledged"):
        require_checkpoint_acknowledgement(
            checkpoint,
            wait=False,
            request_path=request_path,
            run_root=run_root,
            storage_mount=storage_mount,
        )

    sleeps = 0

    def publish_after_first_poll(_: float) -> None:
        nonlocal sleeps
        sleeps += 1
        ack_path.parent.mkdir(parents=True, exist_ok=True)
        ack_path.write_bytes(encoded)

    acknowledgement = require_checkpoint_acknowledgement(
        checkpoint,
        wait=True,
        request_path=request_path,
        run_root=run_root,
        storage_mount=storage_mount,
        sleep=publish_after_first_poll,
    )
    assert sleeps == 1
    assert acknowledgement is not None
    assert acknowledgement["manifest_path"] == (
        "checkpoints/checkpoint-159/checkpoint-complete.json"
    )
    assert acknowledgement["run_id"] == "run-checkpoint-ack"

    tampered = json.loads(encoded)
    tampered["bundle_hash"] = "d" * 64
    ack_path.write_text(json.dumps(tampered))
    with pytest.raises(ContractError, match="bundle_hash binding mismatch"):
        require_checkpoint_acknowledgement(
            checkpoint,
            wait=False,
            request_path=request_path,
            run_root=run_root,
            storage_mount=storage_mount,
        )


def test_checkpoint_acknowledgement_waits_for_complete_atomic_publication(
    tmp_path: Path,
) -> None:
    checkpoint = tmp_path / "storage/checkpoints/checkpoint-159"
    checkpoint.mkdir(parents=True)
    (checkpoint / "trainer_state.json").write_text('{"global_step": 159}\n')
    (checkpoint / "checkpoint-complete.json").write_text(
        json.dumps(_checkpoint_manifest(checkpoint), indent=2, sort_keys=True) + "\n"
    )
    request_path, run_root, storage_mount, ack_path, encoded = _signed_checkpoint_ack(
        tmp_path, checkpoint
    )
    ack_path.parent.mkdir(parents=True, exist_ok=True)
    ack_path.write_bytes(b"")

    with pytest.raises(ContractError, match="acknowledgement is unreadable"):
        require_checkpoint_acknowledgement(
            checkpoint,
            wait=False,
            request_path=request_path,
            run_root=run_root,
            storage_mount=storage_mount,
        )

    sleeps = 0

    def finish_publication(_: float) -> None:
        nonlocal sleeps
        sleeps += 1
        ack_path.write_bytes(encoded)

    acknowledgement = require_checkpoint_acknowledgement(
        checkpoint,
        wait=True,
        request_path=request_path,
        run_root=run_root,
        storage_mount=storage_mount,
        sleep=finish_publication,
    )

    assert sleeps == 1
    assert acknowledgement is not None
    assert acknowledgement["run_id"] == "run-checkpoint-ack"


def test_production_adapter_evidence_records_the_exact_matched_module_count() -> None:
    class Measurement:
        def to_dict(self) -> dict[str, int]:
            return {"trainable_parameters": 42_332_160}

    evidence = _production_adapter_evidence(
        Measurement(),
        ("model.layer.0.q_proj", "model.layer.0.v_proj"),
        total_parameters=34_224_090_480,
    )

    assert evidence["matched_modules"] == [
        "model.layer.0.q_proj",
        "model.layer.0.v_proj",
    ]
    assert evidence["matched_module_count"] == 2
    assert evidence["total_parameters"] == 34_224_090_480


def test_paid_training_accepts_complete_production_adapter_evidence(
    tmp_path: Path,
) -> None:
    expected = expected_adapter_measurement(LINEAR_ONLY).to_dict()
    matched_modules = sorted(f"model.target.{index}" for index in range(310))
    result_path = tmp_path / "training-result.json"
    _write_json(
        result_path,
        {
            "protocol": "striatum-training-result/2",
            "strategy": LINEAR_ONLY,
            "global_step": 5,
            "resumed_from": None,
            "metrics": {"train_runtime": 349.5},
            "liger_fused_loss": _liger_proof(40),
            "base_preparation": _base_preparation_receipt(),
            "measurement": {
                **expected,
                "matched_modules": matched_modules,
                "matched_module_count": len(matched_modules),
                "total_parameters": 34_224_090_480,
            },
            "example_selection": {
                "mode": "all-authorized",
                "candidates": 1_268,
                "tokenization": _tokenization_census(),
            },
        },
    )

    result = _training_result(
        result_path,
        expected_step=5,
        expected_strategy=LINEAR_ONLY,
        expected_resumed_from=None,
    )

    assert result["measurement"]["matched_module_count"] == 310


def test_smoke_terminal_validation_names_a_missing_moe_module_count(
    tmp_path: Path,
) -> None:
    kernel = _flash_qla_receipt()
    resume = tmp_path / "checkpoint-2"
    preflight = {
        "protocol": "striatum-training-profile-preflight/1",
        "smoke": "passed",
        "flash_qla": kernel,
        "model": {"id": "Qwen/Qwen3.6-35B-A3B"},
    }
    training = {
        "protocol": "striatum-training-result/2",
        "global_step": 4,
        "resumed_from": str(resume),
        "optimization": {
            "optimizer_steps": 2,
            "backward_passes_with_adapter_gradients": 2,
            "nonzero_gradient_parameters": ["adapter.weight"],
        },
        "batch": {"image_count": 1, "supervised_tokens": 21},
        "measurement": {"trainable_parameters": 42_332_160},
        "metrics": {"train_loss": 2.1},
    }
    inference = {
        "protocol": "striatum-adapter-inference/1",
        "adapter_loaded": True,
    }

    failures = _terminal_evidence_failures(
        preflight,
        training,
        inference,
        kernel,
        {"status": "bound"},
        model_id="Qwen/Qwen3.6-35B-A3B",
        expected_resume=resume,
        expected_target_count=310,
        expected_trainable_parameters=42_332_160,
    )

    assert failures == ["measurement.matched_module_count"]


def test_forced_checkpoint_is_exact_and_validated() -> None:
    assert should_force_final_checkpoint(159, 159, True) is True
    assert should_force_final_checkpoint(318, 318, True) is True
    assert should_force_final_checkpoint(158, 159, True) is False
    assert should_force_final_checkpoint(159, 159, False) is False
    with pytest.raises(ContractError, match="positive max steps"):
        should_force_final_checkpoint(0, -1, True)
    with pytest.raises(ContractError, match="non-negative"):
        should_force_final_checkpoint(-1, 159, True)


def test_resume_uses_current_invocation_checkpoint_interval() -> None:
    training_args = SimpleNamespace(save_steps=25)
    restored_state = SimpleNamespace(save_steps=5)

    evidence = synchronize_trainer_save_interval(training_args, restored_state)

    assert restored_state.save_steps == 25
    assert evidence == {
        "checkpoint_save_steps_before": 5,
        "checkpoint_save_steps_requested": 25,
        "checkpoint_save_steps_changed": True,
    }

    with pytest.raises(ContractError, match="positive integer"):
        synchronize_trainer_save_interval(
            SimpleNamespace(save_steps=0), SimpleNamespace(save_steps=5)
        )


def test_resume_uses_current_invocation_scheduler_rate_before_first_step() -> None:
    optimizer = SimpleNamespace(
        param_groups=[{"lr": 0.0}, {"lr": 0.0}],
    )
    scheduler = SimpleNamespace(
        last_epoch=159,
        get_lr=lambda: [5.204e-5, 2.602e-5],
    )

    evidence = synchronize_resumed_optimizer_learning_rate(
        optimizer,
        scheduler,
        SimpleNamespace(global_step=159),
        max_steps=318,
    )

    assert [group["lr"] for group in optimizer.param_groups] == [
        5.204e-5,
        2.602e-5,
    ]
    assert evidence == {
        "global_step": 159,
        "scheduler_last_epoch": 159,
        "learning_rates_before": [0.0, 0.0],
        "learning_rates_applied": [5.204e-5, 2.602e-5],
    }

    with pytest.raises(ContractError, match="positive learning rate"):
        synchronize_resumed_optimizer_learning_rate(
            optimizer,
            SimpleNamespace(last_epoch=159, get_lr=lambda: [0.0, 0.0]),
            SimpleNamespace(global_step=159),
            max_steps=318,
        )


def test_preflight_selects_and_receipts_the_largest_tokenized_example(
    tmp_path: Path,
) -> None:
    assert (
        select_longest_tokenized_index([100, 40_960, 50_000, 60_000, 60_000], 40_960)
        == 3
    )
    selection = _longest_training_selection()
    result = tmp_path / "training-result.json"
    result.write_text(
        json.dumps(
            {
                "protocol": "striatum-training-result/2",
                "global_step": 1,
                "example_selection": selection,
            }
        )
    )
    assert verify_longest_example_receipt(result) == selection
    preflight_source = (JOB / "preflight.py").read_text()
    assert "--select-longest" in preflight_source
    assert '"longest-tokenized-authorized"' in preflight_source
    assert "verify_longest_evaluation_receipt" in preflight_source

    selection["selected_global_index"] = 4
    selection["raw_token_count"] = 59_999
    result.write_text(
        json.dumps(
            {
                "protocol": "striatum-training-result/2",
                "global_step": 1,
                "example_selection": selection,
            }
        )
    )
    with pytest.raises(ContractError, match="token counts are inconsistent"):
        verify_longest_example_receipt(result)


def test_chat_template_token_ids_requires_the_plain_list_contract() -> None:
    class Tokenizer:
        def apply_chat_template(self, messages, **kwargs):  # noqa: ANN001, ANN003
            assert messages == [{"role": "user", "content": "request"}]
            assert kwargs["tokenize"] is True
            assert kwargs["return_dict"] is False
            return [11, 12, 13]

    assert train_module._chat_template_token_ids(
        Tokenizer(),
        [{"role": "user", "content": "request"}],
        add_generation_prompt=True,
    ) == [11, 12, 13]

    class StructuredTokenizer:
        def apply_chat_template(self, messages, **kwargs):  # noqa: ANN001, ANN003
            del messages, kwargs
            return {"input_ids": [11, 12, 13], "attention_mask": [1, 1, 1]}

    with pytest.raises(ContractError, match="plain token-ID list"):
        train_module._chat_template_token_ids(
            StructuredTokenizer(),
            [{"role": "user", "content": "request"}],
            add_generation_prompt=True,
        )


def test_full_tokenization_census_normalizes_string_messages_for_processor(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    rows = [
        {
            "messages": [
                {"role": "user", "content": "request"},
                {"role": "assistant", "content": "response"},
            ],
            "meta": {"dispatch_id": "production-shaped-row"},
        }
    ]
    calls: list[list[dict[str, object]]] = []

    class FakeDataset(list):
        def select(self, indices):  # noqa: ANN001
            return FakeDataset([self[index] for index in indices])

    def load_dataset(*args, **kwargs):  # noqa: ANN002, ANN003
        del args, kwargs
        return FakeDataset(rows)

    def concatenate_datasets(datasets):  # noqa: ANN001
        return FakeDataset([row for dataset in datasets for row in dataset])

    monkeypatch.setitem(
        sys.modules,
        "datasets",
        SimpleNamespace(
            concatenate_datasets=concatenate_datasets,
            load_dataset=load_dataset,
        ),
    )
    monkeypatch.setattr(
        train_module,
        "validate_sft_tokenization_census",
        lambda value: value,
    )

    class Processor:
        def apply_chat_template(self, messages, **kwargs):  # noqa: ANN001, ANN003
            del kwargs
            calls.append(messages)
            assert all(isinstance(message["content"], list) for message in messages)
            assert all(
                block["type"] == "text"
                for message in messages
                for block in message["content"]
            )
            return [11, 12] if len(messages) == 1 else [11, 12, 13]

    dataset, selection = train_module._load_datasets(
        tmp_path,
        Processor(),
        cutoff=16,
        limit=0,
        select_longest=False,
        manifest_path=JOB / "smoke" / "input-manifest.json",
        expected_examples=1,
        strict_production=False,
    )

    assert len(dataset) == 1
    assert len(calls) == 2
    assert selection["mode"] == "all-authorized"


def test_sft_truncation_preserves_labels_and_salvages_prompt_overflow() -> None:
    assert train_module._truncate_sft_tokens(
        [1, 2, 3, 4], [1, 2], cutoff=5
    ) == {
        "input_ids": [1, 2, 3, 4],
        "attention_mask": [1, 1, 1, 1],
        "labels": [-100, -100, 3, 4],
    }
    assert train_module._truncate_sft_tokens(
        [1, 2, 3, 4, 5, 6], [1, 2, 3], cutoff=5
    ) == {
        "input_ids": [1, 2, 3, 4, 5],
        "attention_mask": [1, 1, 1, 1, 1],
        "labels": [-100, -100, -100, 4, 5],
    }
    assert train_module._truncate_sft_tokens(
        [1, 2, 3, 4, 5, 6, 7, 8], [1, 2, 3, 4, 5, 6], cutoff=5
    ) == {
        "input_ids": [4, 5, 6, 7, 8],
        "attention_mask": [1, 1, 1, 1, 1],
        "labels": [-100, -100, -100, 7, 8],
    }


def test_sft_truncation_fails_closed_for_invalid_or_unsalvageable_tokens() -> None:
    with pytest.raises(ContractError, match="exact prefix"):
        train_module._truncate_sft_tokens([1, 9, 3], [1, 2], cutoff=5)
    with pytest.raises(ContractError, match="no assistant tokens"):
        train_module._truncate_sft_tokens([1, 2], [1, 2], cutoff=5)
    with pytest.raises(ContractError, match="cannot preserve assistant tokens"):
        train_module._truncate_sft_tokens(
            [1, 2, 3, 4, 5, 6, 7, 8],
            [1, 2, 3, 4],
            cutoff=4,
        )


def test_preflight_reload_eval_selects_and_receipts_longest_prompt(
    tmp_path: Path,
) -> None:
    class Tokenizer:
        def apply_chat_template(self, messages, **kwargs):  # noqa: ANN001, ANN003
            assert kwargs["return_dict"] is False
            return list(range(int(messages[0]["content"])))

    examples = [
        {
            "messages": [
                {"role": "user", "content": str(length)},
                {"role": "assistant", "content": '{"verdict":"accept"}'},
            ],
            "meta": {"dispatch_id": f"dispatch-{index:03d}"},
        }
        for index, length in enumerate([100, 60_000, 50_000, 60_000] + [10] * 94)
    ]
    source = tmp_path / "review.eval.jsonl"
    source.write_text("\n".join(json.dumps(example) for example in examples) + "\n")

    selected, evidence = _read_examples(
        source,
        1,
        "longest-tokenized-authorized",
        tokenizer=Tokenizer(),
        cutoff=40_960,
        expected_source_sha=sha256_file(source),
    )

    assert selected[0]["meta"]["dispatch_id"] == "dispatch-001"
    assert evidence["selected_global_index"] == 1
    assert evidence["raw_token_count"] == 60_000
    assert evidence["effective_token_count"] == 40_960
    assert evidence["max_raw_token_count"] == 60_000
    assert evidence["max_effective_token_count"] == 40_960
    assert evidence["source_sha256"] == sha256_file(source)
    assert evidence["token_length_census_sha256"] == hashlib.sha256(
        json.dumps([100, 60_000, 50_000, 60_000] + [10] * 94, separators=(",", ":")).encode()
    ).hexdigest()
    assert verify_longest_evaluation_receipt(
        {
            "protocol": "striatum-evaluation-result/1",
            "n": 1,
            "selection": evidence,
        }
    ) == evidence

    evidence["raw_token_count"] = 59_999
    with pytest.raises(ContractError, match="token counts are inconsistent"):
        verify_longest_evaluation_receipt(
            {
                "protocol": "striatum-evaluation-result/1",
                "n": 1,
                "selection": evidence,
            }
        )


def test_preflight_runs_distinct_quantized_and_bf16_reload_commands(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    selection = {
        "method": "longest-tokenized-authorized",
        "candidates": 98,
        "examples": 1,
        "source_path": "sft/review.eval.jsonl",
        "source_sha256": "a" * 64,
        "selected_global_index": 4,
        "dispatch_id": "dispatch-eval-longest",
        "dispatch_ids": ["dispatch-eval-longest"],
        "raw_token_count": 50_000,
        "effective_token_count": 40_960,
        "max_raw_token_count": 50_000,
        "max_effective_token_count": 40_960,
        "token_length_census_sha256": "b" * 64,
        "cutoff": 40_960,
        "tie_break": "effective-length,raw-length,earliest-global-index",
        "tokenization_surface": "user-prompt-with-generation-marker-no-thinking",
    }
    quantized_output = tmp_path / "quantized-reload-eval"
    bf16_output = tmp_path / "bf16-parity-eval"
    _write_json(
        quantized_output / "summary.json",
        {
            "protocol": "striatum-evaluation-result/1",
            "base_load_mode": "bnb-4bit-nf4-double-quant",
            "n": 1,
            "selection": selection,
        },
    )
    _write_json(
        bf16_output / "summary.json",
        {
            "protocol": "striatum-evaluation-result/1",
            "base_load_mode": "bf16",
            "n": 1,
            "selection": selection,
        },
    )
    commands: list[list[str]] = []
    monkeypatch.setattr(preflight_module, "_run", commands.append)

    quantized_selection = preflight_module._run_reload_evaluation(
        model_dir=tmp_path / "model",
        input_dir=tmp_path / "input",
        checkpoint=tmp_path / "checkpoint-1",
        output=quantized_output,
        bf16_base=False,
    )
    bf16_selection = preflight_module._run_reload_evaluation(
        model_dir=tmp_path / "model",
        input_dir=tmp_path / "input",
        checkpoint=tmp_path / "checkpoint-1",
        output=bf16_output,
        bf16_base=True,
    )

    assert quantized_selection == selection
    assert bf16_selection == selection
    assert "--bf16-base" not in commands[0]
    assert "--bf16-base" in commands[1]
    assert all(
        command[command.index("--selection") + 1]
        == "longest-tokenized-authorized"
        for command in commands
    )


def test_preflight_child_failure_is_written_to_a_durable_log(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    log_path = tmp_path / "diagnostics" / "one-step-train.log"
    command = [
        sys.executable,
        "-c",
        (
            "import sys; "
            "print('child standard output', flush=True); "
            "print('child traceback marker', file=sys.stderr); "
            "raise SystemExit(23)"
        ),
    ]

    with pytest.raises(ContractError, match="exit 23"):
        preflight_module._run(command, log_path=log_path)

    assert log_path.read_text() == (
        "child standard output\nchild traceback marker\n"
    )
    assert "child traceback marker" in capsys.readouterr().err


def test_liger_runtime_proof_requires_bound_fused_loss_and_no_logits(
    tmp_path: Path,
) -> None:
    proof = _liger_proof()

    assert validate_liger_fused_loss_proof(proof) == proof
    require_no_full_logits(SimpleNamespace(loss=object(), logits=None))
    training_result = tmp_path / "training-result.json"
    training_result.write_text(
        json.dumps(
            {
                "protocol": "striatum-training-result/2",
                "global_step": 1,
                "liger_fused_loss": proof,
            }
        )
    )
    assert verify_liger_fused_loss_receipt(training_result) == proof

    with pytest.raises(ContractError, match="materialized logits"):
        require_no_full_logits(SimpleNamespace(loss=object(), logits=object()))
    proof["bound_forward_identity_verified"] = False
    with pytest.raises(ContractError, match="proof is invalid"):
        validate_liger_fused_loss_proof(proof)


def test_liger_training_keeps_fused_loss_but_disables_mixed_dtype_fused_moe() -> None:
    assert train_module.LIGER_KERNEL_CONFIG == {
        "cross_entropy": False,
        "fused_linear_cross_entropy": True,
        "swiglu": False,
    }


def test_liger_binding_callback_checks_after_trainer_applies_patch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    binding = _liger_proof(calls=0)
    binding["no_full_logits_observed"] = False
    model = object()
    observed: list[object] = []

    def fake_binding(candidate: object) -> dict[str, object]:
        observed.append(candidate)
        return binding.copy()

    monkeypatch.setattr(
        train_module, "_require_liger_fused_loss_binding", fake_binding
    )
    proof: dict[str, object] = {}
    verified: list[bool] = []
    callback = train_module._make_liger_binding_callback(
        object,
        proof,
        on_verified=lambda: verified.append(True),
    )
    control = object()

    assert callback.on_train_begin(None, None, control, model=model) is control
    assert observed == [model]
    assert proof == binding
    assert verified == [True]
    train_module._require_liger_binding_before_forward(proof)
    proof["observed_forward_calls"] = 1
    proof["no_full_logits_observed"] = True
    train_module._require_liger_binding_before_forward(proof)

    with pytest.raises(ContractError, match="before the first training forward"):
        train_module._require_liger_binding_before_forward({})


def test_checkpoint_25_subset_is_declared_and_reproducible() -> None:
    training = json.loads((JOB / "training-config.json").read_text())
    policy = training["quality_gate"]["checkpoint_25_mini"]
    source = ROOT / policy["source_path"]
    examples = [json.loads(line) for line in source.read_text().splitlines()]

    assert sha256_file(source) == policy["source_sha256"]
    assert (
        derive_checkpoint_25_dispatch_ids(examples, policy["examples"])
        == policy["dispatch_ids"]
    )


def test_preflight_and_full_materializations_have_distinct_reservations() -> None:
    import yaml

    full = yaml.safe_load(_render_job("full"))
    preflight = yaml.safe_load(_render_job("preflight-only"))

    expected_runner = {
        "version": "0.1.12",
        "git_commit": "144537205e3fd2e3b09b16179ef3872b13f14d8e",
    }
    for spec in (full, preflight):
        assert spec["runner"] == expected_runner
        assert spec["resources"]["gpu_types"] == ["NVIDIA H200"]

    assert full["limits"] == {
        "max_elapsed_seconds": 54_000,
        "max_cost_usd": "45.00",
        "usd_per_hour": "4.50",
    }
    assert full["phases"]["verify"]["timeout_seconds"] == 900
    assert "--check-production-tokenization" in full["phases"]["verify"]["argv"]
    assert full["phases"]["preflight"]["enabled"] is False
    assert full["phases"]["train"]["enabled"] is True
    assert full["phases"]["evaluate"]["enabled"] is True
    assert full["artifacts"]["incremental_manifest_glob"] == (
        "checkpoints/checkpoint-*/checkpoint-complete.json"
    )
    assert full["artifacts"]["incremental_mirror_ack"] == {
        "required": True,
        "directory": "control/incremental-acks",
        "timeout_seconds": 900,
    }
    assert preflight["limits"] == {
        "max_elapsed_seconds": 2_700,
        "max_cost_usd": "3.50",
        "usd_per_hour": "4.50",
    }
    assert preflight["phases"]["verify"]["timeout_seconds"] == 900
    assert preflight["phases"]["preflight"]["enabled"] is True
    assert preflight["phases"]["preflight"]["timeout_seconds"] == 900
    assert preflight["phases"]["train"]["enabled"] is False
    assert preflight["phases"]["evaluate"]["enabled"] is False
    assert preflight["phases"]["package"]["argv"][-1] == "--preflight-only"
    assert preflight["artifacts"]["incremental_manifest_glob"] == (
        "artifacts/preflight/one-step/checkpoint-*/checkpoint-complete.json"
    )
    assert preflight["artifacts"]["incremental_mirror_ack"] == {
        "required": True,
        "directory": "control/incremental-acks",
        "timeout_seconds": 120,
    }
    enabled_preflight_seconds = sum(
        phase["timeout_seconds"]
        for phase in preflight["phases"].values()
        if phase["enabled"]
    )
    assert enabled_preflight_seconds == 1_845
    assert (
        preflight["limits"]["max_elapsed_seconds"] - enabled_preflight_seconds
        == 855
    )
    assert (
        Decimal(preflight["limits"]["max_elapsed_seconds"])
        * Decimal(preflight["limits"]["usd_per_hour"])
        / Decimal(3_600)
        == Decimal("3.375")
    )
    assert (
        preflight["artifacts"]["incremental_mirror_ack"]["timeout_seconds"]
        < preflight["phases"]["preflight"]["timeout_seconds"]
    )
    dockerfile = (JOB / "Dockerfile").read_text()
    assert "openssh-client" in dockerfile
    assert "ssh-keygen -?" in dockerfile
    assert "-m pip check" in dockerfile
    for module in (
        "flash_attn",
        "fla",
        "flash_qla",
        "causal_conv1d",
        "bitsandbytes",
        "tilelang",
        "tvm_ffi",
        "liger_kernel.transformers.model.qwen3_5_moe",
    ):
        assert module in dockerfile
    assert Decimal(preflight["limits"]["max_cost_usd"]) + Decimal(
        full["limits"]["max_cost_usd"]
    ) == Decimal("48.50")


def test_smoke_ladder_materializations_use_the_same_h200_image_path() -> None:
    import yaml

    dense = yaml.safe_load(_render_job("hopper-dense-smoke"))
    moe = yaml.safe_load(_render_job("hopper-moe-smoke"))

    for spec in (dense, moe):
        assert spec["resources"]["gpu_types"] == ["NVIDIA H200"]
        assert spec["phases"]["verify"]["enabled"] is False
        assert spec["phases"]["preflight"]["enabled"] is True
        assert "--check-hopper-kernels" in spec["phases"]["preflight"]["argv"]
        assert spec["phases"]["train"]["enabled"] is False
        assert spec["phases"]["evaluate"]["enabled"] is False
        assert spec["phases"]["package"]["argv"][0].endswith("package-smoke")
        assert spec["artifacts"]["incremental_manifest_glob"] == (
            "artifacts/preflight/training/checkpoint-*/checkpoint-complete.json"
        )

    assert "Qwen3.5-0.8B-2fc06364" in " ".join(
        dense["phases"]["preflight"]["argv"]
    )
    assert dense["limits"]["max_cost_usd"] == "3.50"
    assert "moe-training-config.json" in " ".join(
        moe["phases"]["preflight"]["argv"]
    )
    assert moe["limits"]["max_cost_usd"] == "5.00"


def test_export_recovery_is_bounded_and_cannot_retrain() -> None:
    import yaml

    source_run_id = "run-20260802T043418-2e928c2a9cb5"
    spec = yaml.safe_load(_render_job("recover-export", source_run_id))

    assert spec["name"].endswith("export-recovery")
    assert spec["phases"]["verify"]["enabled"] is True
    assert "--check-production-tokenization" in spec["phases"]["verify"]["argv"]
    assert spec["phases"]["preflight"]["enabled"] is False
    assert spec["phases"]["train"]["enabled"] is False
    assert spec["phases"]["evaluate"]["enabled"] is False
    assert spec["phases"]["package"]["enabled"] is True
    assert spec["phases"]["package"]["argv"][-1] == source_run_id
    assert spec["limits"] == {
        "max_elapsed_seconds": 9_000,
        "max_cost_usd": "12.00",
        "usd_per_hour": "4.50",
    }
    assert "incremental_manifest_glob" not in spec["artifacts"]
    assert "incremental_mirror_ack" not in spec["artifacts"]

    with pytest.raises(ContractError, match="valid source run ID"):
        _render_job("recover-export", "../run-escape")


def test_export_recovery_reuses_validated_outputs_without_training(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source_run_id = "run-20260802T043418-2e928c2a9cb5"
    source = tmp_path / "runs" / source_run_id
    output = tmp_path / "runs" / "run-20260802T120000-aaaaaaaaaaaa"
    for relative, content in {
        "checkpoints/checkpoint-318/checkpoint-complete.json": b"checkpoint\n",
        "checkpoints/final-adapter/adapter_config.json": b"{}\n",
        "checkpoints/final-adapter/adapter_model.safetensors": b"adapter\n",
        "artifacts/train-phase/train-phase.json": b"{}\n",
        "eval/full/results.jsonl": b"{}\n",
        "eval/full/summary.json": b"{}\n",
    }.items():
        path = source / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    (output / "artifacts/runtime").mkdir(parents=True)
    (output / "artifacts/runtime/cuda-runtime.json").write_text("{}\n")
    (output / "artifacts/runtime/volume-assets.json").write_text("{}\n")

    validations: list[Path] = []
    commands: list[list[str]] = []
    monkeypatch.setattr(
        recover_export_module,
        "validate_completed_training_and_evaluation",
        lambda path: {"validated": str(path)},
    )
    monkeypatch.setattr(
        recover_export_module,
        "validate_runtime_evidence",
        lambda path: validations.append(path),
    )
    monkeypatch.setattr(recover_export_module, "_validate_hf_reference", lambda _: None)
    monkeypatch.setattr(
        recover_export_module, "validate_export_receipt", lambda *_: None
    )

    def fake_run(command: list[str]) -> None:
        commands.append(command)
        if "jobs.qwen35b_moe.evaluate" in command:
            parity = Path(command[command.index("--output") + 1])
            parity.mkdir(parents=True)
            (parity / "results.jsonl").write_text("{}\n")
            (parity / "summary.json").write_text("{}\n")
            (parity / "hf-reference.json").write_text("{}\n")
        else:
            gguf = Path(command[command.index("--output") + 1])
            receipt = Path(command[command.index("--receipt") + 1])
            gguf.parent.mkdir(parents=True)
            gguf.write_bytes(b"GGUF\n")
            receipt.write_text("{}\n")

    monkeypatch.setattr(recover_export_module, "_run", fake_run)
    manifest = recover_export_module.recover(
        source_run_root=source,
        source_run_id=source_run_id,
        output=output,
        model_dir=tmp_path / "model",
        input_dir=tmp_path / "inputs",
        base_gguf=tmp_path / "base.gguf",
        llama_cpp=tmp_path / "llama.cpp",
    )

    assert validations == [source.resolve(), output.resolve()]
    assert len(commands) == 2
    assert all("jobs.qwen35b_moe.train" not in command for command in commands)
    assert "--require-valid-output" in commands[0]
    assert commands[0][commands[0].index("--max-new-tokens") + 1] == "2048"
    assert manifest["recovered_from_run_id"] == source_run_id
    paths = {entry["path"] for entry in manifest["files"]}
    assert "checkpoints/checkpoint-318/checkpoint-complete.json" in paths
    assert "checkpoints/final-adapter/adapter_model.safetensors" in paths
    assert "eval/full/results.jsonl" in paths
    assert "eval/parity/hf-reference.json" in paths
    assert "artifacts/final/adapter-f32.gguf" in paths
    assert "artifacts/recovery/recovery.json" in paths


def test_dense_smoke_materialization_copies_only_the_tiny_manifest(
    tmp_path: Path,
) -> None:
    destination = tmp_path / "gate2"

    materialize(ROOT, destination, "hopper-dense-smoke")

    assert (destination / "inputs/sft/smoke.train.jsonl").read_bytes() == (
        JOB / "smoke/inputs/sft/smoke.train.jsonl"
    ).read_bytes()
    assert not (destination / "inputs/sft/review.train.jsonl").exists()
    assert "role" not in json.loads(
        (destination / "input-manifest.json").read_text()
    )["files"][0]


def test_ssh_keygen_capability_probe_accepts_help_exit_but_not_missing_y(
    tmp_path: Path,
) -> None:
    probe = (
        'ssh_keygen_help="$(ssh-keygen -? 2>&1 || :)" \\\n'
        '    && printf \'%s\\n\' "$ssh_keygen_help" | grep -Fq -- \'-Y sign\''
    )
    assert probe in (JOB / "Dockerfile").read_text()

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    fake_ssh_keygen = fake_bin / "ssh-keygen"
    fake_ssh_keygen.write_text(
        "#!/bin/sh\n"
        "printf '%s\\n' \"$SSH_KEYGEN_HELP\"\n"
        "exit 255\n"
    )
    fake_ssh_keygen.chmod(0o755)
    command = probe.replace("\\\n    ", "")
    env = {"PATH": f"{fake_bin}:/usr/bin:/bin"}

    supported = subprocess.run(
        ["bash", "-o", "pipefail", "-c", command],
        env={**env, "SSH_KEYGEN_HELP": "usage: ssh-keygen -Y sign"},
        check=False,
    )
    unsupported = subprocess.run(
        ["bash", "-o", "pipefail", "-c", command],
        env={**env, "SSH_KEYGEN_HELP": "usage: ssh-keygen -t type"},
        check=False,
    )

    assert supported.returncode == 0
    assert unsupported.returncode != 0


def test_flash_qla_pins_one_coherent_hopper_backend_stack() -> None:
    requirements = dict(
        line.split("==", maxsplit=1)
        for line in (
            (JOB / "requirements-common.in").read_text()
            + (JOB / "requirements.in").read_text()
        ).splitlines()
        if "==" in line
    )

    assert requirements["tilelang"] == "0.1.9"
    assert requirements["apache-tvm-ffi"] == "0.1.9"
    assert requirements["fla-core"] == "0.5.2"

    gpu_requirements = dict(
        line.split("==", maxsplit=1)
        for line in (JOB / "requirements-gpu.in").read_text().splitlines()
        if "==" in line
    )
    assert gpu_requirements["flash-linear-attention"] == "0.5.2"
    assert gpu_requirements["flash-qla"] == "0.1.2"

    dockerfile = (JOB / "Dockerfile").read_text()
    assert "'tilelang'" in dockerfile
    assert "flash_qla" in dockerfile
    assert "'tvm_ffi'" in dockerfile
    assert "jobs.qwen35b_moe.flash_qla_smoke" in dockerfile


def test_dependency_policy_separates_compatibility_constraints_from_release_lock() -> None:
    runtime_input = (JOB / "requirements-common.in").read_text()
    runtime_lock = (JOB / "requirements.lock").read_text()
    gpu_lock = (JOB / "requirements-gpu.lock").read_text()
    gpu_input = (JOB / "requirements-gpu.in").read_text()
    dockerfile = (JOB / "Dockerfile").read_text()

    assert "accelerate>=1.14,<2" in runtime_input
    assert "datasets>=5,<6" in runtime_input
    assert "torch==2.8.0" in runtime_input
    assert "--hash=sha256:" in runtime_lock
    assert "--hash=sha256:" in gpu_lock
    assert "ninja>=1.11,<2" in gpu_input
    assert "--require-hashes -r requirements.lock" in dockerfile
    assert "--require-hashes -r requirements-gpu.lock" in dockerfile


def test_fla_dispatch_patch_is_exact_idempotent_and_fail_closed() -> None:
    source = b"prefix\n" + PREIMAGE_DECORATORS + b"\nbody\n"
    expected = b"prefix\n" + POSTIMAGE_DECORATORS + b"\nbody\n"
    preimage_sha256 = hashlib.sha256(source).hexdigest()
    postimage_sha256 = hashlib.sha256(expected).hexdigest()

    patched, status = patch_source(
        source,
        preimage_sha256=preimage_sha256,
        postimage_sha256=postimage_sha256,
    )
    assert patched == expected
    assert status == "patched"

    repeated, repeated_status = patch_source(
        patched,
        preimage_sha256=preimage_sha256,
        postimage_sha256=postimage_sha256,
    )
    assert repeated == patched
    assert repeated_status == "already-patched"

    with pytest.raises(ContractError, match="refused unknown source"):
        patch_source(
            source + b"drift",
            preimage_sha256=preimage_sha256,
            postimage_sha256=postimage_sha256,
        )


def test_flash_qla_patch_adapts_production_inputs_and_is_fail_closed() -> None:
    source = b"prefix\n" + BACKEND_REJECTIONS + b"middle\n" + BACKEND_RETURN
    expected = b"prefix\n" + BACKEND_ADMISSION + b"middle\n" + BACKEND_ADAPTATION
    preimage_sha256 = hashlib.sha256(source).hexdigest()
    postimage_sha256 = hashlib.sha256(expected).hexdigest()

    patched, status = patch_backend_source(
        source,
        preimage_sha256=preimage_sha256,
        postimage_sha256=postimage_sha256,
    )
    assert patched == expected
    assert status == "patched"

    repeated, repeated_status = patch_backend_source(
        patched,
        preimage_sha256=preimage_sha256,
        postimage_sha256=postimage_sha256,
    )
    assert repeated == patched
    assert repeated_status == "already-patched"

    with pytest.raises(ContractError, match="refused unknown source"):
        patch_backend_source(
            source + b"drift",
            preimage_sha256=preimage_sha256,
            postimage_sha256=postimage_sha256,
        )


def test_worker_image_applies_fla_dispatch_patch_before_runtime_validation() -> None:
    dockerfile = (JOB / "Dockerfile").read_text()
    patch_command = "python -m jobs.qwen35b_moe.fla_dispatch_compat"
    validation_command = (
        "python -m jobs.qwen35b_moe.flash_qla_smoke --validate-install"
    )

    assert patch_command in dockerfile
    assert dockerfile.index(patch_command) < dockerfile.index(validation_command)


def test_worker_dependencies_are_cached_independently_of_runner_release() -> None:
    dockerfile = (JOB / "Dockerfile").read_text()

    assert "python3 -m venv /opt/striatum-qwen35b/venv" in dockerfile
    assert (
        "PATH=/opt/striatum-qwen35b/venv/bin:"
        "/opt/runpod-jobrunner/venv/bin:${PATH}"
    ) in dockerfile
    assert "/opt/striatum-qwen35b/venv/bin/python -m pip install" in dockerfile
    assert dockerfile.index("COPY --from=jobrunner /opt/runpod-jobrunner") > dockerfile.index(
        "cmake --build /opt/llama.cpp/build"
    )


def test_paid_preflight_requires_flash_qla_runtime_evidence() -> None:
    assert "flash-qla" in PACKAGES
    assert "fla-core" in PACKAGES
    source = (JOB / "preflight.py").read_text()
    assert "run_flash_qla_smoke" in source
    assert source.index(
        "receipt_flash_qla = run_flash_qla_smoke"
    ) < source.index("census = census_snapshot")


def test_preflight_materialization_stamps_single_quoted_yaml_hash(
    tmp_path: Path,
) -> None:
    bundle = tmp_path / "preflight"
    bundle.mkdir()
    (bundle / "job.yaml").write_text(_render_job("preflight-only"))
    (bundle / "input-manifest.json").write_text(
        (JOB / "input-manifest.json").read_text()
    )
    (bundle / "bundle-metadata.json").write_text(
        json.dumps({"image_digest_pinned": False})
    )

    receipt = tmp_path / "image-build-receipt.json"
    _write_json(
        receipt,
        {
            "protocol": "striatum-worker-image-build/2",
            "image": "ghcr.io/halbritt/striatum-tuner-qwen35b-moe:0.1.20",
            "source_commit": "b" * 40,
            "jobrunner_image": (
                "ghcr.io/halbritt/runpod-jobrunner-noop@sha256:" + "c" * 64
            ),
            "jobrunner_release": {
                "protocol": "runner-release/1",
                "runner_version": "0.1.12",
                "runner_git_commit": "144537205e3fd2e3b09b16179ef3872b13f14d8e",
                "supported_protocol_majors": {
                    "artifact-manifest": [1],
                    "incremental-mirror-ack": [1],
                    "launch-authorization": [1],
                    "run-event": [1],
                    "run-request": [1],
                    "run-status": [1],
                },
            },
            "network_volume_assets": {
                "manifest_sha256": "d" * 64,
                "files": 41,
                "bytes": 142_993_858_696,
            },
            "pushed": True,
            "digest": "sha256:" + "a" * 64,
            "immutable_image": (
                "ghcr.io/halbritt/striatum-tuner-qwen35b-moe@sha256:" + "a" * 64
            ),
        },
    )

    update(bundle, receipt)

    rendered = (bundle / "job.yaml").read_text()
    assert "REPLACE_WITH_IMAGE_DIGEST" not in rendered
    assert (
        "0000000000000000000000000000000000000000000000000000000000000000"
        not in rendered
    )
    assert (
        json.loads((bundle / "bundle-metadata.json").read_text())["image_digest_pinned"]
        is True
    )


def test_bundle_image_update_rejects_a_naked_digest(tmp_path: Path) -> None:
    with pytest.raises(ContractError, match="build receipt"):
        update(tmp_path, Path("sha256:" + "a" * 64))


def test_build_receipt_is_written_atomically(tmp_path: Path) -> None:
    target = tmp_path / "nested/image-build-receipt.json"
    receipt = {"protocol": "striatum-worker-image-build/2", "pushed": True}

    _write_receipt(target, receipt)

    assert json.loads(target.read_text()) == receipt
    assert list(target.parent.glob(f".{target.name}.*")) == []


def test_profile_preflight_runs_expensive_hopper_probe_last() -> None:
    source = (JOB / "preflight.py").read_text()
    profile_source = source[source.index("def _profile_preflight") : source.index("def _run_profile_smoke")]

    assert profile_source.index("verify_input_tree") < profile_source.index(
        "run_flash_qla_smoke"
    )
    assert profile_source.index("inject_on_meta") < profile_source.index(
        "run_flash_qla_smoke"
    )


def test_full_materialization_requires_gate3_acceptance(tmp_path: Path) -> None:
    with pytest.raises(ContractError, match="Gate 3 acceptance"):
        materialize(ROOT, tmp_path / "full", "full")


def test_full_materialization_uses_the_runner_input_manifest_schema(
    tmp_path: Path,
) -> None:
    digest = "sha256:" + "a" * 64
    acceptance = tmp_path / "gate3-acceptance.json"
    _write_json(
        acceptance,
        {
            "protocol": "striatum-gate-acceptance/1",
            "gate": 3,
            "accepted": True,
            "run_id": "run-20260801T230000-abcdef012345",
            "image_digest": (
                "ghcr.io/halbritt/striatum-tuner-qwen35b-moe@" + digest
            ),
            "image_source_commit": "b" * 40,
            "model": {
                "id": "Qwen/Qwen3.6-35B-A3B",
                "revision": "995ad96eacd98c81ed38be0c5b274b04031597b0",
                "model_type": "qwen3_5_moe",
            },
            "artifact_manifest_sha256": "c" * 64,
        },
    )

    bundle = materialize(ROOT, tmp_path / "full", "full", acceptance)
    manifest = json.loads((bundle / "input-manifest.json").read_text())
    gate_entry = next(
        item
        for item in manifest["files"]
        if item["path"] == "control/gate3-acceptance.json"
    )

    assert set(gate_entry) == {"path", "size", "sha256"}


def test_gate3_acceptance_is_bound_to_exact_image_and_moe_model(tmp_path: Path) -> None:
    digest = "sha256:" + "a" * 64
    receipt = tmp_path / "gate3-acceptance.json"
    _write_json(
        receipt,
        {
            "protocol": "striatum-gate-acceptance/1",
            "gate": 3,
            "accepted": True,
            "run_id": "run-20260801T230000-abcdef012345",
            "image_digest": (
                "ghcr.io/halbritt/striatum-tuner-qwen35b-moe@" + digest
            ),
            "image_source_commit": "b" * 40,
            "model": {
                "id": "Qwen/Qwen3.6-35B-A3B",
                "revision": "995ad96eacd98c81ed38be0c5b274b04031597b0",
                "model_type": "qwen3_5_moe",
            },
            "artifact_manifest_sha256": "c" * 64,
        },
    )

    value = validate_gate3_acceptance(receipt, expected_image_digest=digest)

    assert value["accepted"] is True
    with pytest.raises(ContractError, match="image digest"):
        validate_gate3_acceptance(
            receipt, expected_image_digest="sha256:" + "d" * 64
        )


def test_gate3_acceptance_resolves_verified_controller_recovery(tmp_path: Path) -> None:
    run_id = "run-20260802T022847-f6af8da54da6"
    image = (
        "ghcr.io/halbritt/striatum-tuner-qwen35b-moe@sha256:" + "a" * 64
    )
    remote_root = Path("/workspace/runpod-jobrunner/runs") / run_id
    artifact_root = tmp_path / "receipts/artifacts"
    manifest = tmp_path / "receipts/manifest/artifact-manifest.json"
    artifact_root.mkdir(parents=True)
    _write_json(manifest, {"protocol": "artifact-manifest/1"})
    _write_json(
        tmp_path / "request.json",
        {
            "protocol": "controller-request/1",
            "controller": {"remote_run_root": str(remote_root)},
            "provider": {"image": image},
            "remote": {"image_digest": image},
        },
    )
    _write_json(
        tmp_path / "state.json",
        {
            "protocol": "run-status/1",
            "run_id": run_id,
            "lifecycle": "closed",
            "workload_result": "succeeded",
            "closeout": {
                "artifact_disposition": {"status": "verified"},
                "current_spend_usd_per_hour": "0",
                "delete_acknowledged": True,
            },
        },
    )

    resolved = _resolve_controller_recovery(tmp_path, run_id, image)

    assert resolved == (
        artifact_root.resolve(),
        manifest.resolve(),
        remote_root / "artifacts/preflight/training/checkpoint-2",
    )


def test_gate3_acceptance_rejects_a_recovery_from_another_image(
    tmp_path: Path,
) -> None:
    run_id = "run-20260802T022847-f6af8da54da6"
    expected_image = (
        "ghcr.io/halbritt/striatum-tuner-qwen35b-moe@sha256:" + "a" * 64
    )
    _write_json(
        tmp_path / "request.json",
        {
            "protocol": "controller-request/1",
            "controller": {
                "remote_run_root": f"/workspace/runpod-jobrunner/runs/{run_id}"
            },
            "provider": {"image": expected_image.replace("a", "b")},
            "remote": {"image_digest": expected_image.replace("a", "b")},
        },
    )
    _write_json(
        tmp_path / "state.json",
        {
            "protocol": "run-status/1",
            "run_id": run_id,
            "lifecycle": "closed",
            "workload_result": "succeeded",
            "closeout": {
                "artifact_disposition": {"status": "verified"},
                "current_spend_usd_per_hour": "0",
                "delete_acknowledged": True,
            },
        },
    )
    (tmp_path / "receipts/artifacts").mkdir(parents=True)
    _write_json(
        tmp_path / "receipts/manifest/artifact-manifest.json",
        {"protocol": "artifact-manifest/1"},
    )

    with pytest.raises(ContractError, match="image digest"):
        _resolve_controller_recovery(tmp_path, run_id, expected_image)


def test_runtime_verify_consumes_gate3_control_receipt_after_validation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    input_root = tmp_path / "input"
    acceptance = input_root / "control/gate3-acceptance.json"
    _write_json(acceptance, {"accepted": True})
    request = tmp_path / "request.json"
    _write_json(request, {"image_digest": "sha256:" + "a" * 64})
    output = tmp_path / "output"
    observed: list[bool] = []

    monkeypatch.setenv("RUNPOD_JOBRUNNER_REQUEST_PATH", str(request))
    monkeypatch.setattr(
        sys,
        "argv",
        ["verify", str(input_root), "--require-gate3-acceptance"],
    )
    monkeypatch.setattr(verify_module, "inspect_cuda_runtime", lambda: {})
    monkeypatch.setattr(verify_module, "verify_runtime_assets", lambda *a, **k: {})
    monkeypatch.setattr(verify_module, "load_input_manifest", lambda path: ())
    monkeypatch.setattr(
        verify_module,
        "validate_gate3_acceptance",
        lambda path, **kwargs: {"accepted": True},
    )
    monkeypatch.setattr(
        verify_module,
        "verify_input_tree",
        lambda root, entries: observed.append(acceptance.is_file()),
    )
    monkeypatch.setattr(verify_module, "output_dir_from_env", lambda: output)

    verify_module.main()

    assert observed == [True]
    assert not acceptance.exists()


def test_runtime_verify_checks_inputs_and_tokenization_before_large_assets(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    input_root = tmp_path / "input"
    input_root.mkdir()
    output = tmp_path / "output"
    observed: list[str] = []

    monkeypatch.setattr(
        sys,
        "argv",
        ["verify", str(input_root), "--check-production-tokenization"],
    )
    monkeypatch.setattr(verify_module, "inspect_cuda_runtime", lambda: {})
    monkeypatch.setattr(verify_module, "load_input_manifest", lambda path: ())
    monkeypatch.setattr(
        verify_module,
        "verify_input_tree",
        lambda root, entries: observed.append("inputs"),
    )
    monkeypatch.setattr(
        verify_module,
        "verify_production_tokenization",
        lambda *args, **kwargs: observed.append("tokenization") or {},
    )
    monkeypatch.setattr(
        verify_module,
        "verify_runtime_assets",
        lambda *args, **kwargs: observed.append("assets") or {},
    )
    monkeypatch.setattr(verify_module, "output_dir_from_env", lambda: output)

    verify_module.main()

    assert observed == ["inputs", "tokenization", "assets"]
    assert (output / "artifacts/runtime/production-tokenization.json").is_file()


def test_preflight_packaging_requires_preflight_smoke_evidence(tmp_path: Path) -> None:
    root = tmp_path / "artifacts/preflight"
    _write_json(root / "preflight.json", {})
    with pytest.raises(ContractError, match="paid preflight"):
        build_manifest(tmp_path, preflight_only=True)

    training_selection = _longest_training_selection()
    evaluation_selection = {
        "method": "longest-tokenized-authorized",
        "candidates": 98,
        "examples": 1,
        "source_path": "sft/review.eval.jsonl",
        "source_sha256": "c" * 64,
        "selected_global_index": 4,
        "dispatch_id": "dispatch-eval-longest",
        "dispatch_ids": ["dispatch-eval-longest"],
        "raw_token_count": 50_000,
        "effective_token_count": 40_960,
        "max_raw_token_count": 50_000,
        "max_effective_token_count": 40_960,
        "token_length_census_sha256": "d" * 64,
        "cutoff": 40_960,
        "tie_break": "effective-length,raw-length,earliest-global-index",
        "tokenization_surface": "user-prompt-with-generation-marker-no-thinking",
    }
    _write_json(
        root / "preflight.json",
        {
            "protocol": "striatum-paid-preflight/3",
            "strategy": "linear-only",
            "measurement": expected_adapter_measurement(LINEAR_ONLY).to_dict(),
            "versions": {package: "test-version" for package in PACKAGES},
            "flash_qla": _flash_qla_receipt(),
            "smoke": "passed",
            "longest_training_example": training_selection,
            "quantized_longest_evaluation_example": evaluation_selection,
            "bf16_longest_evaluation_example": evaluation_selection,
            "liger_fused_loss": _liger_proof(),
            "base_preparation": _base_preparation_receipt(),
            "live_adapter_measurement": expected_adapter_measurement(
                LINEAR_ONLY
            ).to_dict(),
        },
    )
    _write_json(root / "flash-qla-smoke.json", _flash_qla_receipt())
    _write_json(
        root / "target-census.json",
        {
            "protocol": "qwen35b-target-census/1",
            "model": {"id": MODEL.model_id, "revision": MODEL.revision},
            "census": {
                "linear_attention": 150,
                "attention": 40,
                "shared_expert": 120,
                "router": 40,
                "shared_expert_gate": 40,
                "routed_expert": 80,
            },
        },
    )
    _write_json(
        root / "one-step/training-result.json",
        {
            "protocol": "striatum-training-result/2",
            "global_step": 1,
            "measurement": expected_adapter_measurement(LINEAR_ONLY).to_dict(),
            "example_selection": training_selection,
            "liger_fused_loss": _liger_proof(),
            "base_preparation": _base_preparation_receipt(),
        },
    )
    _write_closed_checkpoint(root / "one-step/checkpoint-1", 1)
    _write_json(
        root / "quantized-reload-eval/summary.json",
        {
            "protocol": "striatum-evaluation-result/1",
            "base_load_mode": "bnb-4bit-nf4-double-quant",
            "n": 1,
            "selection": evaluation_selection,
        },
    )
    _write_json(
        root / "bf16-parity-eval/summary.json",
        {
            "protocol": "striatum-evaluation-result/1",
            "base_load_mode": "bf16",
            "n": 1,
            "selection": evaluation_selection,
        },
    )
    _write_hf_reference(root / "bf16-parity-eval/hf-reference.json")
    gguf = root / "one-step-adapter-f32.gguf"
    _write_export_receipt(
        root / "one-step-export.json", gguf, root / "one-step/checkpoint-1"
    )
    _write_json(
        tmp_path / "artifacts/runtime/cuda-runtime.json", _cuda_runtime_receipt()
    )
    _write_json(
        tmp_path / "artifacts/runtime/volume-assets.json", _runtime_asset_receipt()
    )

    manifest = build_manifest(tmp_path, preflight_only=True)
    assert manifest["result"] == "preflight-succeeded"
    assert manifest["model_acceptance_requires_local_fate_scoring"] is False
    assert any(
        file["path"] == "artifacts/preflight/one-step-adapter-f32.gguf"
        and file["sha256"] == sha256_file(gguf)
        for file in manifest["files"]
    )

    training_result_path = root / "one-step/training-result.json"
    training_result = json.loads(training_result_path.read_text())
    training_result["measurement"]["trainable_parameters"] -= 1
    _write_json(training_result_path, training_result)
    with pytest.raises(ContractError, match="adapter measurement"):
        build_manifest(tmp_path, preflight_only=True)
    training_result["measurement"] = expected_adapter_measurement(
        LINEAR_ONLY
    ).to_dict()
    _write_json(training_result_path, training_result)

    cuda_receipt = tmp_path / "artifacts/runtime/cuda-runtime.json"
    cuda_receipt.unlink()
    with pytest.raises(ContractError, match="CUDA runtime receipt"):
        build_manifest(tmp_path, preflight_only=True)
    _write_json(cuda_receipt, _cuda_runtime_receipt())

    asset_receipt = tmp_path / "artifacts/runtime/volume-assets.json"
    asset_receipt.unlink()
    with pytest.raises(ContractError, match="volume asset receipt"):
        build_manifest(tmp_path, preflight_only=True)
    _write_json(asset_receipt, _runtime_asset_receipt())

    wrong_census = _runtime_asset_receipt()
    wrong_census["census"]["model"]["revision"] = "wrong-revision"
    _write_json(asset_receipt, wrong_census)
    with pytest.raises(ContractError, match="another model revision"):
        build_manifest(tmp_path, preflight_only=True)
    _write_json(asset_receipt, _runtime_asset_receipt())

    quantized_summary = root / "quantized-reload-eval/summary.json"
    quantized_summary.unlink()
    with pytest.raises(ContractError, match="quantized reload evaluation summary"):
        build_manifest(tmp_path, preflight_only=True)
    _write_json(
        quantized_summary,
        {
            "protocol": "striatum-evaluation-result/1",
            "base_load_mode": "bf16",
            "n": 1,
            "selection": evaluation_selection,
        },
    )
    with pytest.raises(ContractError, match="wrong base-load mode"):
        build_manifest(tmp_path, preflight_only=True)

    _write_json(
        quantized_summary,
        {
            "protocol": "striatum-evaluation-result/1",
            "base_load_mode": "bnb-4bit-nf4-double-quant",
            "n": 1,
            "selection": evaluation_selection,
        },
    )
    gguf.unlink()
    with pytest.raises(ContractError, match="exported adapter GGUF"):
        build_manifest(tmp_path, preflight_only=True)


def test_full_packaging_requires_epoch_one_gate_evidence(tmp_path: Path) -> None:
    receipt_path = tmp_path / "artifacts/train-phase/train-phase.json"
    _write_json(receipt_path, {})
    with pytest.raises(ContractError, match="terminal outcome"):
        build_manifest(tmp_path, preflight_only=False)

    training = json.loads((JOB / "training-config.json").read_text())
    quality = training["quality_gate"]
    mini = _passing_summary(
        examples=16, selection=quality["checkpoint_25_mini"]
    )
    epoch = _passing_summary(examples=98, selection=quality["epoch_one_full"])
    epoch["selection"] = {
        **epoch["selection"],
        "dispatch_ids": [f"dispatch-{index:03d}" for index in range(98)],
    }
    _write_json(tmp_path / "eval/checkpoint-25-mini/summary.json", mini)
    _write_json(tmp_path / "eval/epoch-one-full/summary.json", epoch)
    _write_json(tmp_path / "eval/full/summary.json", epoch)
    _write_passing_results(tmp_path / "eval/full/results.jsonl", epoch)
    baseline = quality["strictly_beat"]
    mini_gate = assess_available_gates(
        mini,
        baseline,
        expected_examples=16,
        expected_selection=quality["checkpoint_25_mini"],
    )
    epoch_gate = assess_available_gates(
        epoch,
        baseline,
        expected_examples=98,
        expected_selection=quality["epoch_one_full"],
    )
    checkpoint_evidence = [
        _write_closed_checkpoint(tmp_path / f"checkpoints/checkpoint-{step}", step)
        for step in EXPECTED_CHECKPOINT_STEPS
    ]
    stages = []
    for stage, step in (
        ("timing-5", 5),
        ("screening-checkpoint-25", 25),
        ("checkpoint-25-mini-evaluation", None),
        ("epoch-one-checkpoint-159", 159),
        ("epoch-one-full-evaluation", None),
        ("second-epoch-318", 318),
    ):
        item = {"stage": stage}
        if step is not None:
            item["global_step"] = step
            item["base_preparation"] = _base_preparation_receipt()
            item["adapter_measurement"] = expected_adapter_measurement(
                LINEAR_ONLY
            ).to_dict()
        stages.append(item)
    _write_json(
        receipt_path,
        {
            "protocol": "striatum-paid-training-phase/2",
            "outcome": "training-completed-full-evaluation-pending",
            "full_evaluation": "separate-evaluate-job-phase",
            "strategy": "linear-only",
            "policy": {
                "timing_steps": 5,
                "screening_checkpoint_step": 25,
                "epoch_one_checkpoint_step": 159,
                "total_steps": 318,
                "checkpoint_interval": 25,
                "mini_eval_examples": 16,
                "epoch_one_eval_examples": 98,
            },
            "timing_projection": {"passed": True},
            "timing_train_phase_projection": {"passed": True},
            "pre_epoch_one_projection": {"passed": True},
            "pre_epoch_one_train_phase_projection": {"passed": True},
            "pre_second_epoch_projection": {"passed": True},
            "pre_second_epoch_train_phase_projection": {"passed": True},
            "stages": stages,
            "checkpoint_25_gate": mini_gate,
            "epoch_one_gate": epoch_gate,
            "checkpoints": checkpoint_evidence,
        },
    )
    final_adapter = tmp_path / "checkpoints/final-adapter"
    _write_valid_adapter(final_adapter)
    _write_hf_reference(tmp_path / "eval/parity/hf-reference.json")
    gguf = tmp_path / "artifacts/final/adapter-f32.gguf"
    _write_export_receipt(
        tmp_path / "artifacts/final/export.json", gguf, final_adapter
    )
    _write_json(
        tmp_path / "artifacts/runtime/cuda-runtime.json", _cuda_runtime_receipt()
    )
    _write_json(
        tmp_path / "artifacts/runtime/volume-assets.json", _runtime_asset_receipt()
    )

    manifest = build_manifest(tmp_path, preflight_only=False)
    assert manifest["result"] == "workload-succeeded-model-acceptance-pending"
    assert any(
        file["path"] == "eval/epoch-one-full/summary.json" for file in manifest["files"]
    )

    mini["available_gates"]["side_match"] = False
    _write_json(tmp_path / "eval/checkpoint-25-mini/summary.json", mini)
    with pytest.raises(ContractError, match="reported gates disagree"):
        build_manifest(tmp_path, preflight_only=False)


def test_paid_projection_and_checkpoint_gate_fail_closed() -> None:
    assert optimizer_steps_per_epoch(1_268, 1, 8) == 159

    limits = PaidLimits(
        max_elapsed_seconds=54_000,
        max_cost_usd=Decimal("39.00"),
        usd_per_hour=Decimal("4.50"),
    )
    projection = project_paid_run(
        limits,
        measured_steps=5,
        completed_steps=5,
        target_steps=318,
        measured_train_runtime_seconds=50,
        measured_worker_wall_seconds=60,
        runner_elapsed_at_gate_seconds=600,
        future_training_worker_starts=2,
        evaluation_export_reserve_seconds=3_600,
    )
    assert projection.elapsed_per_step_seconds == 10
    assert projection.observed_worker_startup_seconds == 10
    assert projection.projected_total_elapsed_seconds == 7_350
    assert projection.projected_cost_usd == Decimal("9.1875")
    assert limits.cost_cap_elapsed_seconds == Decimal("31200")
    assert projection.passed is True

    with pytest.raises(ContractError, match="at least 5 optimizer steps"):
        project_paid_run(
            limits,
            measured_steps=4,
            completed_steps=4,
            target_steps=318,
            measured_train_runtime_seconds=40,
            measured_worker_wall_seconds=50,
            runner_elapsed_at_gate_seconds=600,
            future_training_worker_starts=2,
            evaluation_export_reserve_seconds=3_600,
        )

    baseline = {
        "json_valid": 0.9,
        "verdict_legal": 0.8,
        "side_match": 0.3,
    }
    summary = {
        "protocol": "striatum-evaluation-result/1",
        "n": 16,
        "json_valid": 0.9,
        "verdict_legal": 0.9,
        "side_match": 0.4,
        "available_gates": {
            "json_valid": False,
            "verdict_legal": True,
            "side_match": True,
        },
    }
    assessment = assess_available_gates(summary, baseline, expected_examples=16)
    with pytest.raises(
        ContractError, match="epoch-one full evaluation did not strictly improve"
    ):
        require_available_gate_improvement(
            assessment, gate_label="epoch-one full evaluation"
        )


@pytest.mark.parametrize("epoch_gate_passes", [True, False])
def test_train_phase_sequences_resume_gate_and_full_run_without_gpu(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    epoch_gate_passes: bool,
) -> None:
    run_root = tmp_path / "run"
    request_path = tmp_path / "run-request.json"
    request_path.write_text(
        json.dumps(
            {
                "protocol": "run-request/1",
                "run_id": "run-test-qwen",
                "bundle_hash": "a" * 64,
                "limits": {
                    "max_elapsed_seconds": 54_000,
                    "max_cost_usd": "39.00",
                    "usd_per_hour": "4.50",
                },
                "phases": {"train": {"enabled": True, "timeout_seconds": 43_200}},
            }
        )
    )
    child_labels: list[str] = []
    child_commands: list[list[str]] = []

    def write_checkpoint(checkpoints: Path, step: int) -> None:
        checkpoint = checkpoints / f"checkpoint-{step}"
        checkpoint.mkdir(parents=True, exist_ok=True)
        (checkpoint / "adapter_model.safetensors").write_bytes(
            f"adapter-{step}".encode()
        )
        (checkpoint / "trainer_state.json").write_text(
            json.dumps({"global_step": step}) + "\n"
        )
        (checkpoint / "checkpoint-complete.json").write_text(
            json.dumps(_checkpoint_manifest(checkpoint), sort_keys=True) + "\n"
        )

    def fake_child(command: list[str], label: str) -> float:
        child_labels.append(label)
        child_commands.append(command)
        if "jobs.qwen35b_moe.train" in command:
            checkpoints = Path(command[command.index("--output") + 1])
            step = int(command[command.index("--max-steps") + 1])
            if step in {5, 25, 159}:
                write_checkpoint(checkpoints, step)
            if step == 159:
                for checkpoint_step in range(50, 151, 25):
                    write_checkpoint(checkpoints, checkpoint_step)
            if step == 318:
                for checkpoint_step in range(175, 301, 25):
                    write_checkpoint(checkpoints, checkpoint_step)
                write_checkpoint(checkpoints, step)
            final_adapter = checkpoints / "final-adapter"
            final_adapter.mkdir(parents=True, exist_ok=True)
            (final_adapter / "adapter_config.json").write_text("{}\n")
            (final_adapter / "adapter_model.safetensors").write_bytes(b"adapter")
            runtime = {5: 50.0, 25: 200.0, 159: 1_340.0, 318: 1_590.0}[step]
            resumed_from = (
                command[command.index("--resume-from-checkpoint") + 1]
                if "--resume-from-checkpoint" in command
                else None
            )
            (checkpoints / "training-result.json").write_text(
                json.dumps(
                    {
                        "protocol": "striatum-training-result/2",
                        "strategy": "linear-only",
                        "global_step": step,
                        "resumed_from": resumed_from,
                        "metrics": {"train_runtime": runtime},
                        "liger_fused_loss": _liger_proof(step * 8),
                        "base_preparation": _base_preparation_receipt(),
                        "measurement": {
                            **expected_adapter_measurement(LINEAR_ONLY).to_dict(),
                            "matched_modules": [
                                f"model.target.{index:03d}" for index in range(310)
                            ],
                            "matched_module_count": 310,
                            "total_parameters": 34_224_090_480,
                        },
                        "example_selection": {
                            "mode": "all-authorized",
                            "candidates": 1_268,
                            "tokenization": _tokenization_census(),
                        },
                    }
                )
                + "\n"
            )
            return runtime + 10
        assert "jobs.qwen35b_moe.evaluate" in command
        output = Path(command[command.index("--output") + 1])
        output.mkdir(parents=True, exist_ok=True)
        adapter = command[command.index("--adapter") + 1]
        if adapter.endswith("checkpoint-25"):
            selection = json.loads((JOB / "training-config.json").read_text())[
                "quality_gate"
            ]["checkpoint_25_mini"]
            examples = 16
        else:
            assert adapter.endswith("checkpoint-159")
            selection = {
                "method": "all-authorized-source-order",
                "examples": 98,
                "source_path": "sft/review.eval.jsonl",
                "source_sha256": (
                    "1de3ce2f185b37f86200be46365bcbac64862d4465ad5ba951573adefd2fb36d"
                ),
                "dispatch_ids": [f"dispatch-{index}" for index in range(98)],
            }
            examples = 98
        json_valid = (
            1.0 if adapter.endswith("checkpoint-25") or epoch_gate_passes else 87 / 98
        )
        (output / "summary.json").write_text(
            json.dumps(
                {
                    "protocol": "striatum-evaluation-result/1",
                    "selection": selection,
                    "n": examples,
                    "json_valid": json_valid,
                    "verdict_legal": 1.0,
                    "side_match": 1.0,
                    "available_gates": {
                        "json_valid": json_valid > 87 / 98,
                        "verdict_legal": True,
                        "side_match": True,
                    },
                }
            )
            + "\n"
        )
        return 100.0

    monkeypatch.setattr(train_phase, "_run_child", fake_child)
    monkeypatch.delenv("RUNPOD_JOBRUNNER_STATUS_DIR", raising=False)
    args = argparse.Namespace(
        strategy="linear-only",
        model_dir=tmp_path / "model",
        input_dir=tmp_path / "inputs",
        output=run_root,
        receipt=None,
        request=request_path,
        seed=42,
    )

    if not epoch_gate_passes:
        with pytest.raises(
            ContractError,
            match="epoch-one full evaluation did not strictly improve",
        ):
            train_phase.run(args)
        assert child_labels == [
            "five-step timing",
            "checkpoint-25 training",
            "checkpoint-25 mini-evaluation",
            "epoch-one checkpoint-159 training",
            "epoch-one full evaluation",
        ]
        blocked = json.loads(
            (run_root / "artifacts/train-phase/train-phase.json").read_text()
        )
        assert blocked["outcome"] == "blocked"
        assert blocked["epoch_one_gate"]["json_valid"]["passed"] is False
        assert "pre_second_epoch_projection" not in blocked
        return

    receipt = train_phase.run(args)

    assert child_labels == [
        "five-step timing",
        "checkpoint-25 training",
        "checkpoint-25 mini-evaluation",
        "epoch-one checkpoint-159 training",
        "epoch-one full evaluation",
        "second-epoch training continuation",
    ]
    assert "--resume-from-checkpoint" not in child_commands[0]
    assert child_commands[1][
        child_commands[1].index("--resume-from-checkpoint") + 1
    ].endswith("checkpoint-5")
    assert child_commands[3][
        child_commands[3].index("--resume-from-checkpoint") + 1
    ].endswith("checkpoint-25")
    assert "--save-final-checkpoint" in child_commands[3]
    assert child_commands[5][
        child_commands[5].index("--resume-from-checkpoint") + 1
    ].endswith("checkpoint-159")
    assert "--save-final-checkpoint" in child_commands[5]
    assert "--limit" not in child_commands[4]
    assert child_commands[4][child_commands[4].index("--selection") + 1] == "prefix"
    assert receipt["outcome"] == "training-completed-full-evaluation-pending"
    assert all(
        gate["passed"] is True for gate in receipt["checkpoint_25_gate"].values()
    )
    assert all(gate["passed"] is True for gate in receipt["epoch_one_gate"].values())
    assert len(receipt["checkpoints"]) == 15
    persisted = json.loads(
        (run_root / "artifacts/train-phase/train-phase.json").read_text()
    )
    assert persisted["outcome"] == receipt["outcome"]


def test_shape_derived_adapter_arithmetic_and_caps() -> None:
    linear = expected_adapter_measurement(LINEAR_ONLY)
    expert = expected_adapter_measurement(EXPERT_AWARE)

    assert MODEL.linear_attention_layers == 30
    assert MODEL.full_attention_layers == 10
    assert MODEL.total_layers == 40
    assert MODEL.num_experts == 256
    assert linear.target_counts == {
        "linear_attention": 150,
        "attention": 40,
        "shared_expert": 120,
        "routed_expert": 0,
    }
    assert linear.category_parameters == {
        "linear_attention": 25_620_480,
        "attention": 6_881_280,
        "shared_expert": 9_830_400,
        "routed_expert": 0,
    }
    assert linear.trainable_parameters == 42_332_160
    assert linear.fp32_bytes == 169_328_640
    assert linear.trainable_parameters <= 50_000_000
    assert linear.fp32_bytes <= 200 * 1024 * 1024

    assert expert.target_counts["routed_expert"] == 80
    assert expert.category_parameters["routed_expert"] == 57_671_680
    assert expert.trainable_parameters == 100_003_840
    assert expert.fp32_bytes == 400_015_360
    assert expert.trainable_parameters <= 110_000_000
    assert expert.fp32_bytes <= 450 * 1024 * 1024


def test_census_must_find_every_target_family() -> None:
    valid = Census(
        linear_attention=150,
        attention=40,
        shared_expert=120,
        routers=40,
        shared_expert_gates=40,
        routed_expert_parameters=80,
    )
    validate_census(valid)

    with pytest.raises(ContractError, match="routed-expert"):
        validate_census(
            Census(
                linear_attention=150,
                attention=40,
                shared_expert=120,
                routers=40,
                shared_expert_gates=40,
                routed_expert_parameters=0,
            )
        )


def test_measured_adapter_must_match_prediction_and_freeze_base() -> None:
    expected = expected_adapter_measurement(LINEAR_ONLY)
    validate_adapter_measurement(expected, expected)

    with pytest.raises(ContractError, match="base parameters"):
        validate_adapter_measurement(
            AdapterMeasurement(
                strategy=LINEAR_ONLY,
                rank=32,
                expert_rank=None,
                trainable_parameters=expected.trainable_parameters,
                fp32_bytes=expected.fp32_bytes,
                base_trainable_parameters=1,
                target_counts=expected.target_counts,
                category_parameters=expected.category_parameters,
            ),
            expected,
        )

    with pytest.raises(ContractError, match="prediction"):
        validate_adapter_measurement(
            AdapterMeasurement(
                strategy=LINEAR_ONLY,
                rank=32,
                expert_rank=None,
                trainable_parameters=expected.trainable_parameters - 1,
                fp32_bytes=(expected.trainable_parameters - 1) * 4,
                base_trainable_parameters=0,
                target_counts=expected.target_counts,
                category_parameters=expected.category_parameters,
            ),
            expected,
        )


def test_naive_rank_32_routed_experts_is_rejected() -> None:
    expected = expected_adapter_measurement(EXPERT_AWARE)
    naive_routed = expected.category_parameters["routed_expert"] * 32
    measured = AdapterMeasurement(
        strategy=EXPERT_AWARE,
        rank=32,
        expert_rank=32,
        trainable_parameters=(
            expected.trainable_parameters
            - expected.category_parameters["routed_expert"]
            + naive_routed
        ),
        fp32_bytes=(
            expected.trainable_parameters
            - expected.category_parameters["routed_expert"]
            + naive_routed
        )
        * 4,
        base_trainable_parameters=0,
        target_counts=expected.target_counts,
        category_parameters={
            **expected.category_parameters,
            "routed_expert": naive_routed,
        },
    )

    with pytest.raises(ContractError, match="expert rank"):
        validate_adapter_measurement(measured, expected)


def test_training_and_job_specs_keep_the_paid_run_gates() -> None:
    training = json.loads((JOB / "training-config.json").read_text())
    job_yaml = (JOB / "job.yaml").read_text()
    dockerfile = (JOB / "Dockerfile").read_text()
    image_builder = (JOB / "build_image.py").read_text()
    dockerignore = (JOB / "Dockerfile.dockerignore").read_text()

    assert training["model"]["id"] == "Qwen/Qwen3.6-35B-A3B"
    assert training["model"]["revision"] == "995ad96eacd98c81ed38be0c5b274b04031597b0"
    assert training["cutoff_length"] == 40_960
    assert training["save_steps"] == 25
    assert training["train"]["epochs"] == 2
    assert training["train"]["expected_steps_per_epoch"] == 159
    assert training["train"]["expected_steps"] == 318
    assert training["train"]["liger_fused_loss"] is True
    assert training["strategies"]["linear-only"]["dropout"] == pytest.approx(0.05)
    assert training["strategies"]["expert-aware"]["dropout"] == 0
    assert training["quality_gate"]["strictly_beat"]["json_valid"] == pytest.approx(
        87 / 98
    )
    assert training["quality_gate"]["epoch_one_full"] == {
        "method": "all-authorized-source-order",
        "examples": 98,
        "source_path": "sft/review.eval.jsonl",
        "source_sha256": (
            "1de3ce2f185b37f86200be46365bcbac64862d4465ad5ba951573adefd2fb36d"
        ),
    }
    assert training["quality_gate"]["local_fate_analysis"] == {
        "source_path": "corpus/analysis.json",
        "source_sha256": (
            "092807c769a71d16361edb74828d02ecfba3ced46d6c0f50c9fe4822c66de7d4"
        ),
    }
    assert "job-spec/1" in job_yaml
    assert "verify -> preflight -> train -> evaluate -> package" in job_yaml
    assert "sha256:REPLACE_WITH_IMAGE_DIGEST" in job_yaml
    assert "encrypted: false" in job_yaml
    assert "network_volume_id: 7lno735a6g" in job_yaml
    assert "NVIDIA H200" in job_yaml
    assert "container_disk_gb: 220" in job_yaml
    assert "required_gb: 120" in job_yaml
    assert 'usd_per_hour: "4.50"' in job_yaml
    assert "COPY --from=model-snapshot" not in dockerfile
    assert "/opt/models" not in dockerfile
    assert "STRIATUM_MODEL_DIR=/workspace/models/Qwen3.6-35B-A3B-995ad96e" in dockerfile
    assert "STRIATUM_BASE_GGUF=/workspace/models/Qwen3.6-35B-A3B-995ad96e/gguf/" in dockerfile
    assert "-DCMAKE_CUDA_ARCHITECTURES=90" in dockerfile
    assert (
        "RUNPOD_JOBRUNNER_RELEASE_PATH=/opt/runpod-jobrunner/release.json" in dockerfile
    )
    assert "__BASE_GGUF_SHARD_COPIES__" not in dockerfile
    assert '"--model-snapshot"' not in image_builder
    assert "validate_base_gguf_artifacts" not in image_builder
    assert '"--provenance=mode=max"' in image_builder
    assert '"--sbom=true"' in image_builder
    assert "!network-volume-assets.sha256" in dockerignore


def test_worker_image_rejects_mismatched_jobrunner_release() -> None:
    job = {
        "runner": {
            "version": "0.1.7",
            "git_commit": "e" * 40,
        }
    }
    old_release = {
        "protocol": "runner-release/1",
        "runner_version": "0.1.2",
        "runner_git_commit": "c" * 40,
        "supported_protocol_majors": {"run-request": [1]},
    }

    with pytest.raises(ContractError, match="runner version"):
        _validate_jobrunner_release(old_release, job)


def test_worker_image_accepts_exact_jobrunner_release() -> None:
    job = {
        "runner": {
            "version": "0.1.7",
            "git_commit": "e" * 40,
        }
    }
    release = {
        "protocol": "runner-release/1",
        "runner_version": "0.1.7",
        "runner_git_commit": "e" * 40,
        "supported_protocol_majors": {"run-request": [1]},
    }

    assert _validate_jobrunner_release(release, job) == release


def test_worker_image_requires_preloaded_network_volume_assets() -> None:
    dockerfile = (JOB / "Dockerfile").read_text()
    image_builder = (JOB / "build_image.py").read_text()

    assert "COPY --from=model-snapshot" not in dockerfile
    assert "build-context" not in image_builder
    assert '"--model-snapshot"' not in image_builder
    assert "validate_base_gguf_artifacts" not in image_builder
    assert (
        "STRIATUM_MODEL_DIR=/workspace/models/Qwen3.6-35B-A3B-995ad96e"
        in dockerfile
    )
    assert (
        "STRIATUM_BASE_GGUF=/workspace/models/Qwen3.6-35B-A3B-995ad96e/gguf/"
        "base-bf16.gguf"
        in dockerfile
    )


def test_runtime_defaults_keep_assets_shared_and_outputs_run_scoped(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("STRIATUM_MODEL_DIR", raising=False)
    monkeypatch.delenv("STRIATUM_BASE_GGUF", raising=False)
    monkeypatch.delenv("STRIATUM_OUTPUT_DIR", raising=False)
    monkeypatch.setenv(
        "RUNPOD_JOBRUNNER_RUN_ROOT",
        "/workspace/runpod-jobrunner/runs/run-network-volume",
    )

    model = Path("/workspace/models/Qwen3.6-35B-A3B-995ad96e")
    assert model_dir_from_env() == model
    assert base_gguf_from_env() == model / "gguf/base-bf16.gguf"
    assert output_dir_from_env() == Path(
        "/workspace/runpod-jobrunner/runs/run-network-volume"
    )


def test_volume_asset_manifest_rejects_tampering(tmp_path: Path) -> None:
    root = tmp_path / "assets"
    gguf = root / "gguf"
    gguf.mkdir(parents=True)
    config = root / "config.json"
    base = gguf / "base-bf16.gguf"
    config.write_bytes(b'{"model_type":"qwen3_5_moe"}\n')
    base.write_bytes(b"GGUF-test")
    manifest = tmp_path / "assets.sha256"
    manifest.write_text(
        f"{sha256_file(config)}  config.json\n"
        f"{sha256_file(base)}  gguf/base-bf16.gguf\n"
    )
    manifest_sha256 = sha256_file(manifest)

    receipt = verify_asset_manifest(
        root,
        manifest_path=manifest,
        expected_manifest_sha256=manifest_sha256,
    )
    assert receipt["files"] == 2
    assert receipt["bytes"] == config.stat().st_size + base.stat().st_size

    base.write_bytes(b"GGUF-tampered")
    with pytest.raises(ContractError, match="hash mismatch"):
        verify_asset_manifest(
            root,
            manifest_path=manifest,
            expected_manifest_sha256=manifest_sha256,
        )

    base.write_bytes(b"GGUF-test")
    extra = root / "unexpected.bin"
    extra.write_bytes(b"unexpected")
    with pytest.raises(ContractError, match="missing or extra"):
        verify_asset_manifest(
            root,
            manifest_path=manifest,
            expected_manifest_sha256=manifest_sha256,
        )

    extra.unlink()
    linked = root / "linked-config.json"
    linked.symlink_to(config)
    with pytest.raises(ContractError, match="contains a symlink"):
        verify_asset_manifest(
            root,
            manifest_path=manifest,
            expected_manifest_sha256=manifest_sha256,
        )


def test_volume_asset_manifest_rejects_an_unsafe_path(tmp_path: Path) -> None:
    root = tmp_path / "assets"
    root.mkdir()
    outside = tmp_path / "outside.bin"
    outside.write_bytes(b"outside")
    manifest = tmp_path / "assets.sha256"
    manifest.write_text(f"{sha256_file(outside)}  ../outside.bin\n")

    with pytest.raises(ContractError, match="unsafe path"):
        verify_asset_manifest(
            root,
            manifest_path=manifest,
            expected_manifest_sha256=sha256_file(manifest),
        )


def test_runtime_asset_gate_combines_hash_manifest_and_model_census(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "assets"
    root.mkdir()
    config = root / "config.json"
    config.write_bytes(b"{}\n")
    manifest = tmp_path / "assets.sha256"
    manifest.write_text(f"{sha256_file(config)}  config.json\n")
    census = {"protocol": "qwen35b-target-census/1", "snapshot": {"shards": 26}}
    monkeypatch.setattr(verify_module, "census_snapshot", lambda path: census)

    receipt = verify_module.verify_runtime_assets(
        root,
        manifest_path=manifest,
        expected_manifest_sha256=sha256_file(manifest),
    )

    assert receipt["assets"]["files"] == 1
    assert receipt["census"] == census


def test_pinned_volume_asset_receipt_contract() -> None:
    receipt = {
        "protocol": "striatum-volume-assets/1",
        "manifest_sha256": (
            "2d56aa53dc94146a01f044b04d7d161015c2f848f575779b49fa5307fe295ff8"
        ),
        "files": 41,
        "bytes": 142_993_858_696,
    }

    assert validate_asset_receipt(receipt) == receipt
    receipt["files"] = 40
    with pytest.raises(ContractError, match="volume asset receipt"):
        validate_asset_receipt(receipt)


def test_checked_in_volume_asset_manifest_is_well_formed() -> None:
    entries = _manifest_entries(JOB / "network-volume-assets.sha256")

    assert len(entries) == 41


def test_image_build_receipt_binds_the_runtime_asset_manifest(tmp_path: Path) -> None:
    manifest = JOB / "network-volume-assets.sha256"
    assert _asset_manifest_receipt(manifest) == {
        "manifest_sha256": (
            "2d56aa53dc94146a01f044b04d7d161015c2f848f575779b49fa5307fe295ff8"
        ),
        "files": 41,
        "bytes": 142_993_858_696,
    }

    tampered = tmp_path / manifest.name
    tampered.write_bytes(manifest.read_bytes() + b"\n")
    with pytest.raises(ContractError, match="asset manifest"):
        _asset_manifest_receipt(tampered)


def test_worker_image_uses_cuda_driver_stub_only_for_build_linking() -> None:
    dockerfile = (JOB / "Dockerfile").read_text()

    assert "cuda_stub_dir=/usr/local/cuda/lib64/stubs" in dockerfile
    symlink = 'ln -s libcuda.so "$cuda_stub_dir/libcuda.so.1"'
    linker_flag = '-DCMAKE_EXE_LINKER_FLAGS="-Wl,-rpath-link,$cuda_stub_dir"'
    build = "cmake --build /opt/llama.cpp/build"
    cleanup = 'rm "$cuda_stub_dir/libcuda.so.1"'
    absence = 'test ! -e "$cuda_stub_dir/libcuda.so.1"'
    assert symlink in dockerfile
    assert linker_flag in dockerfile
    assert cleanup in dockerfile
    assert dockerfile.index(symlink) < dockerfile.index(linker_flag)
    assert dockerfile.index(linker_flag) < dockerfile.index(build)
    assert dockerfile.index(build) < dockerfile.index(cleanup)
    assert dockerfile.index(cleanup) < dockerfile.index(
        absence, dockerfile.index(cleanup)
    )
    assert "readelf -d /opt/llama.cpp/build/bin/libggml-cuda.so" in dockerfile
    assert "readelf -d /opt/llama.cpp/build/bin/llama-cli" in dockerfile
    assert "LD_LIBRARY_PATH=$cuda_stub_dir" not in dockerfile
    assert "-Wl,-rpath," not in dockerfile
    assert "CMAKE_BUILD_RPATH" not in dockerfile
    assert "CMAKE_INSTALL_RPATH" not in dockerfile
    assert dockerfile.count('! grep -Fq "$cuda_stub_dir"') == 2


def test_worker_image_applies_the_pinned_qwen_lora_reorder_patch() -> None:
    dockerfile = (JOB / "Dockerfile").read_text()
    dockerignore = (JOB / "Dockerfile.dockerignore").read_text()
    patch = (JOB / "llama-qwen35-lora-reorder.patch").read_text()

    assert "!llama-qwen35-lora-reorder.patch" in dockerignore
    assert "COPY llama-qwen35-lora-reorder.patch /opt/striatum-qwen35b/patches/" in dockerfile
    native_build = "cmake --build /opt/llama.cpp/build"
    patch_copy = "COPY llama-qwen35-lora-reorder.patch"
    assert dockerfile.index(native_build) < dockerfile.index(patch_copy)
    assert "git -C /opt/llama.cpp apply --check" in dockerfile
    assert dockerfile.index('checkout "$LLAMA_CPP_COMMIT"') < dockerfile.index(
        "git -C /opt/llama.cpp apply --check"
    )
    assert "def index_select(self, dim: int, index: Tensor)" in patch
    assert "self._lora_A.index_select(-1, index)" in patch
    assert "self._lora_B.index_select(-2, index)" in patch
    assert "return torch.index_select(tensor, dim, indices)" in patch


def test_terminal_parity_inference_is_bounded_and_quality_gated() -> None:
    phase = (JOB / "evaluate_phase.py").read_text()

    assert "str(PARITY_MAX_NEW_TOKENS)" in phase
    assert PARITY_MAX_NEW_TOKENS == 2_048
    assert phase.count('"--enforce-available-gates"') == 1
    assert phase.count('"--require-valid-output"') == 1

    require_valid_inference({"json_valid": 1.0, "verdict_legal": 1.0})
    with pytest.raises(ContractError, match="valid JSON"):
        require_valid_inference({"json_valid": 0.0, "verdict_legal": 0.0})


def test_cuda_runtime_requires_real_h200_driver_resolution() -> None:
    ldd_output = """
        libcuda.so.1 => /usr/local/nvidia/lib64/libcuda.so.1 (0x00007f00)
    """
    devices_output = """
        Available devices:
          CUDA0: NVIDIA H200 (143771 MiB, 142000 MiB free)
    """

    receipt = validate_cuda_observations(ldd_output, devices_output)
    assert receipt == _cuda_runtime_receipt()
    assert validate_cuda_runtime_receipt(receipt) == receipt

    with pytest.raises(ContractError, match="stub"):
        validate_cuda_observations(
            ldd_output.replace("/usr/local/nvidia/lib64", "/usr/local/cuda/lib64/stubs"),
            devices_output,
        )
    with pytest.raises(ContractError, match="H200"):
        validate_cuda_observations(
            ldd_output,
            devices_output.replace("NVIDIA H200", "NVIDIA H100 80GB HBM3"),
        )


def _fate_fixture(
    tmp_path: Path, *, legal_count: int, agreement_count: int | None = None
) -> tuple[Path, Path, Path, dict[str, object]]:
    if agreement_count is None:
        agreement_count = legal_count
    examples = [
        {"meta": {"dispatch_id": f"dispatch-{index:03d}"}}
        for index in range(98)
    ]
    reviews = [
        {
            "dispatch_id": f"dispatch-{index:03d}",
            "fate": "final" if index % 2 == 0 else "revised",
        }
        for index in range(98)
    ]
    results = [
        {
            "dispatch_id": f"dispatch-{index:03d}",
            "verdict": (
                (
                    ("accept" if index % 2 == 0 else "reject")
                    if index < agreement_count
                    else ("reject" if index % 2 == 0 else "accept")
                )
                if index < legal_count
                else None
            ),
        }
        for index in range(98)
    ]
    eval_source_path = tmp_path / "review.eval.jsonl"
    analysis_path = tmp_path / "analysis.json"
    results_path = tmp_path / "results.jsonl"
    eval_source_path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in examples)
    )
    analysis_path.write_text(
        json.dumps({"reviews": reviews}, indent=2, sort_keys=True) + "\n"
    )
    results_path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in results)
    )
    policy: dict[str, object] = {
        "epoch_one_full": {
            "method": "all-authorized-source-order",
            "examples": 98,
            "source_path": "sft/review.eval.jsonl",
            "source_sha256": sha256_file(eval_source_path),
        },
        "local_fate_analysis": {
            "source_path": "corpus/analysis.json",
            "source_sha256": sha256_file(analysis_path),
        },
        "strictly_beat": {
            "verdict_legal": 85 / 98,
            "fate_agreement": 16 / 85,
        },
    }
    return results_path, analysis_path, eval_source_path, policy


def test_local_fate_gate_accepts_variable_legal_count_and_binds_inputs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    results, analysis, eval_source, policy = _fate_fixture(
        tmp_path, legal_count=86
    )
    monkeypatch.setattr(
        score_fate_module, "training_config", lambda: {"quality_gate": policy}
    )

    receipt = score_fate_module.score_fate(
        results_path=results,
        analysis_path=analysis,
        eval_source_path=eval_source,
    )

    assert receipt["fate_scored"] == 86
    assert receipt["required_min_fate_scored"] == 86
    assert receipt["results_count"] == 98
    assert receipt["matched_fate_records"] == 98
    assert receipt["results_sha256"] == sha256_file(results)
    assert receipt["analysis_sha256"] == sha256_file(analysis)
    assert receipt["eval_source_sha256"] == sha256_file(eval_source)
    assert receipt["verdict_legal_passed"] is True
    assert receipt["fate_agreement_passed"] is True
    assert receipt["passed"] is True


def test_local_fate_gate_records_old_baseline_legal_count_rejection(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    results, analysis, eval_source, policy = _fate_fixture(
        tmp_path, legal_count=85
    )
    output = tmp_path / "fate-gate.json"
    monkeypatch.setattr(
        score_fate_module, "training_config", lambda: {"quality_gate": policy}
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "score_fate.py",
            "--results",
            str(results),
            "--analysis",
            str(analysis),
            "--eval-source",
            str(eval_source),
            "--output",
            str(output),
        ],
    )

    with pytest.raises(ContractError, match="legal verdict count did not strictly beat"):
        score_fate_module.main()

    receipt = json.loads(output.read_text())
    assert receipt["fate_scored"] == 85
    assert receipt["verdict_legal_passed"] is False
    assert receipt["passed"] is False


def test_local_fate_gate_rejects_duplicate_result_identity(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    results, analysis, eval_source, policy = _fate_fixture(
        tmp_path, legal_count=86
    )
    rows = [json.loads(line) for line in results.read_text().splitlines()]
    rows[-1]["dispatch_id"] = rows[0]["dispatch_id"]
    results.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows)
    )
    monkeypatch.setattr(
        score_fate_module, "training_config", lambda: {"quality_gate": policy}
    )

    with pytest.raises(
        ContractError,
        match="dispatch IDs do not match the authorized evaluation source",
    ):
        score_fate_module.score_fate(
            results_path=results,
            analysis_path=analysis,
            eval_source_path=eval_source,
        )


def test_local_fate_gate_rejects_unpinned_analysis_content(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    results, analysis, eval_source, policy = _fate_fixture(
        tmp_path, legal_count=86
    )
    document = json.loads(analysis.read_text())
    document["reviews"][0]["fate"] = "revised"
    analysis.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
    monkeypatch.setattr(
        score_fate_module, "training_config", lambda: {"quality_gate": policy}
    )

    with pytest.raises(ContractError, match="analysis source hash"):
        score_fate_module.score_fate(
            results_path=results,
            analysis_path=analysis,
            eval_source_path=eval_source,
        )


@pytest.mark.parametrize(("agreements", "passed"), [(16, False), (17, True)])
def test_local_fate_gate_uses_strict_fate_agreement_boundary(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    agreements: int,
    passed: bool,
) -> None:
    results, analysis, eval_source, policy = _fate_fixture(
        tmp_path,
        legal_count=86,
        agreement_count=agreements,
    )
    monkeypatch.setattr(
        score_fate_module, "training_config", lambda: {"quality_gate": policy}
    )

    receipt = score_fate_module.score_fate(
        results_path=results,
        analysis_path=analysis,
        eval_source_path=eval_source,
    )

    assert receipt["fate_agreement"] == pytest.approx(agreements / 86)
    assert receipt["fate_agreement_passed"] is passed
    assert receipt["passed"] is passed
