"""Pure contract and adapter-budget arithmetic for the Qwen MoE job.

This module deliberately imports no training libraries.  It is used by the
local bundle checks and by the paid preflight, where its shape-derived result
must agree exactly with PEFT's measured trainable parameter count.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence


LINEAR_ONLY = "linear-only"
EXPERT_AWARE = "expert-aware"
STRATEGIES = (LINEAR_ONLY, EXPERT_AWARE)


class ContractError(ValueError):
    """A fail-closed job contract violation."""


@dataclass(frozen=True)
class ModelContract:
    model_id: str = "Qwen/Qwen3.6-35B-A3B"
    revision: str = "995ad96eacd98c81ed38be0c5b274b04031597b0"
    model_type: str = "qwen3_5_moe"
    total_layers: int = 40
    linear_attention_layers: int = 30
    full_attention_layers: int = 10
    hidden_size: int = 2_048
    num_experts: int = 256
    experts_per_token: int = 8
    expert_intermediate_size: int = 512
    shared_expert_intermediate_size: int = 512


MODEL = ModelContract()


@dataclass(frozen=True)
class InputFile:
    path: str
    size: int
    sha256: str

    @property
    def role(self) -> str:
        return "eval" if self.path == "sft/review.eval.jsonl" else "train"


@dataclass(frozen=True)
class Census:
    linear_attention: int
    attention: int
    shared_expert: int
    routers: int
    shared_expert_gates: int
    routed_expert_parameters: int


@dataclass(frozen=True)
class AdapterMeasurement:
    strategy: str
    rank: int
    expert_rank: int | None
    trainable_parameters: int
    fp32_bytes: int
    base_trainable_parameters: int
    target_counts: Mapping[str, int]
    category_parameters: Mapping[str, int]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# Shapes are (out_features, in_features), read from the pinned snapshot's
# safetensors headers.  DeltaNet's 32-wide in_proj_a and in_proj_b are real
# Linear modules and must not be silently discarded from the budget.
LINEAR_ATTENTION_SHAPES = (
    (8_192, 2_048),  # in_proj_qkv
    (4_096, 2_048),  # in_proj_z
    (32, 2_048),  # in_proj_b
    (32, 2_048),  # in_proj_a
    (2_048, 4_096),  # out_proj
)
ATTENTION_SHAPES = (
    (8_192, 2_048),  # q_proj (includes the output gate)
    (512, 2_048),  # k_proj
    (512, 2_048),  # v_proj
    (2_048, 4_096),  # o_proj
)
SHARED_EXPERT_SHAPES = (
    (512, 2_048),  # gate_proj
    (512, 2_048),  # up_proj
    (2_048, 512),  # down_proj
)


def _linear_lora_parameters(
    shapes: Sequence[tuple[int, int]], rank: int, layers: int
) -> int:
    return (
        layers
        * rank
        * sum(out_features + in_features for out_features, in_features in shapes)
    )


def expected_adapter_measurement(strategy: str) -> AdapterMeasurement:
    """Return the shape-derived PEFT budget for one accepted strategy."""
    if strategy not in STRATEGIES:
        raise ContractError(f"unknown PEFT strategy: {strategy}")

    rank = 32
    category_parameters = {
        "linear_attention": _linear_lora_parameters(
            LINEAR_ATTENTION_SHAPES, rank, MODEL.linear_attention_layers
        ),
        "attention": _linear_lora_parameters(
            ATTENTION_SHAPES, rank, MODEL.full_attention_layers
        ),
        "shared_expert": _linear_lora_parameters(
            SHARED_EXPERT_SHAPES, rank, MODEL.total_layers
        ),
        "routed_expert": 0,
    }
    target_counts = {
        "linear_attention": MODEL.linear_attention_layers
        * len(LINEAR_ATTENTION_SHAPES),
        "attention": MODEL.full_attention_layers * len(ATTENTION_SHAPES),
        "shared_expert": MODEL.total_layers * len(SHARED_EXPERT_SHAPES),
        "routed_expert": 0,
    }
    expert_rank: int | None = None

    if strategy == EXPERT_AWARE:
        expert_rank = 1
        # PEFT treats each [experts, out, in] target_parameters tensor as one
        # LoRA pair per expert.  gate_up_proj has out=2*moe_intermediate_size;
        # down_proj reverses hidden and moe_intermediate dimensions.
        gate_up = (
            MODEL.num_experts
            * expert_rank
            * (2 * MODEL.expert_intermediate_size + MODEL.hidden_size)
        )
        down = (
            MODEL.num_experts
            * expert_rank
            * (MODEL.hidden_size + MODEL.expert_intermediate_size)
        )
        category_parameters["routed_expert"] = MODEL.total_layers * (gate_up + down)
        target_counts["routed_expert"] = MODEL.total_layers * 2

    trainable = sum(category_parameters.values())
    return AdapterMeasurement(
        strategy=strategy,
        rank=rank,
        expert_rank=expert_rank,
        trainable_parameters=trainable,
        fp32_bytes=trainable * 4,
        base_trainable_parameters=0,
        target_counts=target_counts,
        category_parameters=category_parameters,
    )


def validate_census(census: Census) -> None:
    expected = Census(
        linear_attention=150,
        attention=40,
        shared_expert=120,
        routers=40,
        shared_expert_gates=40,
        routed_expert_parameters=80,
    )
    fields = asdict(census)
    expected_fields = asdict(expected)
    for field, count in fields.items():
        if count != expected_fields[field]:
            label = field.replace("_", "-")
            raise ContractError(
                f"{label} census mismatch: found {count}, expected {expected_fields[field]}"
            )


def validate_adapter_measurement(
    measured: AdapterMeasurement, expected: AdapterMeasurement
) -> None:
    if measured.strategy != expected.strategy:
        raise ContractError("measured strategy does not match requested strategy")
    if measured.base_trainable_parameters:
        raise ContractError(
            f"base parameters remain trainable: {measured.base_trainable_parameters}"
        )
    if measured.strategy == EXPERT_AWARE and measured.expert_rank != 1:
        raise ContractError(
            f"expert rank must be 1, found {measured.expert_rank}; naive rank 32 is forbidden"
        )
    if measured.trainable_parameters <= 0:
        raise ContractError("PEFT injected zero trainable parameters")
    if measured.trainable_parameters != expected.trainable_parameters:
        raise ContractError(
            "measured PEFT trainables do not match the shape-derived prediction: "
            f"{measured.trainable_parameters} != {expected.trainable_parameters}"
        )
    if dict(measured.target_counts) != dict(expected.target_counts):
        raise ContractError("measured target counts do not match the target contract")

    parameter_cap = 50_000_000 if measured.strategy == LINEAR_ONLY else 110_000_000
    byte_cap = (200 if measured.strategy == LINEAR_ONLY else 450) * 1024 * 1024
    if measured.trainable_parameters > parameter_cap:
        raise ContractError(
            f"adapter parameter cap exceeded: {measured.trainable_parameters} > {parameter_cap}"
        )
    if measured.fp32_bytes > byte_cap:
        raise ContractError(
            f"adapter fp32 size cap exceeded: {measured.fp32_bytes} > {byte_cap}"
        )


def load_input_manifest(path: Path) -> tuple[InputFile, ...]:
    raw = json.loads(path.read_text())
    if raw.get("protocol") != "input-manifest/1":
        raise ContractError("input manifest protocol must be input-manifest/1")
    if raw.get("root") != "inputs":
        raise ContractError("input manifest root must be inputs")
    entries = tuple(InputFile(**entry) for entry in raw.get("files", ()))
    expected_paths = (
        "sft/review.train.jsonl",
        "sft/review.eval.jsonl",
        "sft/implementation-planning.train.jsonl",
        "sft/design-convergence.train.jsonl",
        "sft/proposal-generation.train.jsonl",
    )
    if tuple(entry.path for entry in entries) != expected_paths:
        raise ContractError("input manifest is not the exact five-file SFT allow-list")
    if sum(entry.size for entry in entries) != 119_218_345:
        raise ContractError("input manifest total is not 119,218,345 bytes")
    for entry in entries:
        pure_path = PurePosixPath(entry.path)
        if (
            pure_path.is_absolute()
            or ".." in pure_path.parts
            or pure_path.parts[0] != "sft"
            or "corpus" in pure_path.parts
        ):
            raise ContractError(
                f"input path is outside the SFT allow-list: {entry.path}"
            )
        if len(entry.sha256) != 64 or any(
            c not in "0123456789abcdef" for c in entry.sha256
        ):
            raise ContractError(f"invalid sha256 for {entry.path}")
        if entry.size <= 0:
            raise ContractError(f"invalid size for {entry.path}")
    return entries


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_input_tree(root: Path, entries: Sequence[InputFile]) -> None:
    """Verify exact regular-file inputs; symlinks and additional files fail."""
    expected = {PurePosixPath(entry.path) for entry in entries}
    actual: set[PurePosixPath] = set()
    for path in root.rglob("*"):
        if path.is_symlink():
            raise ContractError(f"input symlink is forbidden: {path}")
        if path.is_file():
            actual.add(PurePosixPath(path.relative_to(root).as_posix()))
    if actual != expected:
        missing = sorted(str(path) for path in expected - actual)
        extra = sorted(str(path) for path in actual - expected)
        raise ContractError(f"input tree mismatch; missing={missing}, extra={extra}")
    for entry in entries:
        path = root / entry.path
        stat = path.stat()
        if stat.st_size != entry.size:
            raise ContractError(
                f"size mismatch for {entry.path}: {stat.st_size} != {entry.size}"
            )
        digest = sha256_file(path)
        if digest != entry.sha256:
            raise ContractError(
                f"sha256 mismatch for {entry.path}: {digest} != {entry.sha256}"
            )
