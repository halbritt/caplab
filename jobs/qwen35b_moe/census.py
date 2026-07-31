"""Enumerate the pinned snapshot's target tensors without allocating weights."""

from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
import re
import struct
from typing import Any

from .contract import (
    ATTENTION_SHAPES,
    EXPERT_AWARE,
    LINEAR_ATTENTION_SHAPES,
    LINEAR_ONLY,
    MODEL,
    SHARED_EXPERT_SHAPES,
    Census,
    ContractError,
    expected_adapter_measurement,
    validate_census,
)


LANGUAGE_LAYER = r"model\.language_model\.layers\.(\d+)\."
LINEAR_ATTENTION_RE = re.compile(
    LANGUAGE_LAYER
    + r"linear_attn\.(in_proj_qkv|in_proj_z|in_proj_b|in_proj_a|out_proj)\.weight$"
)
ATTENTION_RE = re.compile(
    LANGUAGE_LAYER + r"self_attn\.(q_proj|k_proj|v_proj|o_proj)\.weight$"
)
SHARED_EXPERT_RE = re.compile(
    LANGUAGE_LAYER + r"mlp\.shared_expert\.(gate_proj|up_proj|down_proj)\.weight$"
)
ROUTER_RE = re.compile(LANGUAGE_LAYER + r"mlp\.gate\.weight$")
SHARED_EXPERT_GATE_RE = re.compile(LANGUAGE_LAYER + r"mlp\.shared_expert_gate\.weight$")
ROUTED_EXPERT_RE = re.compile(
    LANGUAGE_LAYER + r"mlp\.experts\.(gate_up_proj|down_proj)$"
)


def _read_safetensors_header(path: Path) -> dict[str, Any]:
    with path.open("rb") as handle:
        raw_size = handle.read(8)
        if len(raw_size) != 8:
            raise ContractError(f"invalid safetensors header: {path}")
        header_size = struct.unpack("<Q", raw_size)[0]
        if header_size <= 2 or header_size > 64 * 1024 * 1024:
            raise ContractError(
                f"unsafe safetensors header size in {path}: {header_size}"
            )
        raw_header = handle.read(header_size)
    try:
        return json.loads(raw_header)
    except json.JSONDecodeError as error:
        raise ContractError(
            f"invalid safetensors metadata in {path}: {error}"
        ) from error


def _load_headers(model_dir: Path, shards: set[str]) -> dict[str, dict[str, Any]]:
    headers: dict[str, dict[str, Any]] = {}
    for shard in sorted(shards):
        path = model_dir / shard
        if not path.is_file() or path.is_symlink():
            raise ContractError(f"model shard is missing or not a regular file: {path}")
        headers[shard] = _read_safetensors_header(path)
    return headers


def _require_revision_receipt(model_dir: Path) -> None:
    receipt = model_dir / "snapshot-revision.txt"
    if not receipt.is_file() or receipt.is_symlink():
        raise ContractError(f"missing model revision receipt: {receipt}")
    revision = receipt.read_text().strip()
    if revision != MODEL.revision:
        raise ContractError(
            f"model revision receipt mismatch: {revision!r} != {MODEL.revision!r}"
        )


def census_snapshot(model_dir: Path) -> dict[str, Any]:
    """Census target names and tensor shapes from index/header metadata only."""
    _require_revision_receipt(model_dir)
    config_path = model_dir / "config.json"
    index_path = model_dir / "model.safetensors.index.json"
    if not config_path.is_file() or not index_path.is_file():
        raise ContractError("model config or safetensors index is missing")

    config = json.loads(config_path.read_text())
    text = config.get("text_config", {})
    layer_types = text.get("layer_types", [])
    if config.get("model_type") != MODEL.model_type:
        raise ContractError(f"unexpected model_type: {config.get('model_type')!r}")
    if len(layer_types) != MODEL.total_layers:
        raise ContractError(f"unexpected layer count: {len(layer_types)}")
    if layer_types.count("linear_attention") != MODEL.linear_attention_layers:
        raise ContractError("unexpected DeltaNet layer count")
    if layer_types.count("full_attention") != MODEL.full_attention_layers:
        raise ContractError("unexpected full-attention layer count")
    expected_config = {
        "hidden_size": MODEL.hidden_size,
        "num_experts": MODEL.num_experts,
        "num_experts_per_tok": MODEL.experts_per_token,
        "moe_intermediate_size": MODEL.expert_intermediate_size,
        "shared_expert_intermediate_size": MODEL.shared_expert_intermediate_size,
    }
    for key, expected in expected_config.items():
        if text.get(key) != expected:
            raise ContractError(f"unexpected {key}: {text.get(key)!r} != {expected!r}")

    index = json.loads(index_path.read_text())
    weight_map: dict[str, str] = index.get("weight_map", {})
    expected_total_size = 71_903_645_408
    if int(index.get("metadata", {}).get("total_size", -1)) != expected_total_size:
        raise ContractError("safetensors index has an unexpected total tensor size")
    all_shards = set(weight_map.values())
    headers = _load_headers(model_dir, all_shards)

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    classifiers = (
        ("linear_attention", LINEAR_ATTENTION_RE),
        ("attention", ATTENTION_RE),
        ("shared_expert", SHARED_EXPERT_RE),
        ("router", ROUTER_RE),
        ("shared_expert_gate", SHARED_EXPERT_GATE_RE),
        ("routed_expert", ROUTED_EXPERT_RE),
    )
    for name, shard in weight_map.items():
        for category, pattern in classifiers:
            match = pattern.fullmatch(name)
            if match:
                metadata = headers[shard].get(name)
                if not isinstance(metadata, dict) or "shape" not in metadata:
                    raise ContractError(f"tensor metadata is absent for {name}")
                grouped[category].append(
                    {"name": name, "shape": metadata["shape"], "shard": shard}
                )
                break

    census = Census(
        linear_attention=len(grouped["linear_attention"]),
        attention=len(grouped["attention"]),
        shared_expert=len(grouped["shared_expert"]),
        routers=len(grouped["router"]),
        shared_expert_gates=len(grouped["shared_expert_gate"]),
        routed_expert_parameters=len(grouped["routed_expert"]),
    )
    validate_census(census)
    _validate_shapes(grouped, layer_types)

    return {
        "protocol": "qwen35b-target-census/1",
        "model": {"id": MODEL.model_id, "revision": MODEL.revision},
        "snapshot": {
            "model_type": config["model_type"],
            "tensor_bytes": expected_total_size,
            "shards": len(all_shards),
        },
        "census": {
            "linear_attention": census.linear_attention,
            "attention": census.attention,
            "shared_expert": census.shared_expert,
            "router": census.routers,
            "shared_expert_gate": census.shared_expert_gates,
            "routed_expert": census.routed_expert_parameters,
        },
        "targets": dict(grouped),
        "adapter_predictions": {
            LINEAR_ONLY: expected_adapter_measurement(LINEAR_ONLY).to_dict(),
            EXPERT_AWARE: expected_adapter_measurement(EXPERT_AWARE).to_dict(),
        },
        "excluded": [
            "routers",
            "shared-expert gates",
            "embeddings and lm_head",
            "normalization parameters",
            "DeltaNet conv1d, A_log, and dt_bias",
            "vision tower",
        ],
    }


def _validate_shapes(
    grouped: dict[str, list[dict[str, Any]]], layer_types: list[str]
) -> None:
    expected_by_name = {
        "in_proj_qkv": LINEAR_ATTENTION_SHAPES[0],
        "in_proj_z": LINEAR_ATTENTION_SHAPES[1],
        "in_proj_b": LINEAR_ATTENTION_SHAPES[2],
        "in_proj_a": LINEAR_ATTENTION_SHAPES[3],
        "out_proj": LINEAR_ATTENTION_SHAPES[4],
        "q_proj": ATTENTION_SHAPES[0],
        "k_proj": ATTENTION_SHAPES[1],
        "v_proj": ATTENTION_SHAPES[2],
        "o_proj": ATTENTION_SHAPES[3],
        "gate_proj": SHARED_EXPERT_SHAPES[0],
        "up_proj": SHARED_EXPERT_SHAPES[1],
        "down_proj": SHARED_EXPERT_SHAPES[2],
    }
    for category in ("linear_attention", "attention", "shared_expert"):
        for target in grouped[category]:
            leaf = target["name"].rsplit(".", 2)[-2]
            shape = tuple(target["shape"])
            if shape != expected_by_name[leaf]:
                raise ContractError(
                    f"unexpected shape for {target['name']}: {shape} != {expected_by_name[leaf]}"
                )

    routed_shapes = {
        "gate_up_proj": (
            MODEL.num_experts,
            2 * MODEL.expert_intermediate_size,
            MODEL.hidden_size,
        ),
        "down_proj": (
            MODEL.num_experts,
            MODEL.hidden_size,
            MODEL.expert_intermediate_size,
        ),
    }
    for target in grouped["routed_expert"]:
        leaf = target["name"].rsplit(".", 1)[-1]
        shape = tuple(target["shape"])
        if shape != routed_shapes[leaf]:
            raise ContractError(
                f"unexpected shape for {target['name']}: {shape} != {routed_shapes[leaf]}"
            )

    # A target name in the wrong architecture family is a contract breach even
    # when aggregate counts happen to match.
    for target in grouped["linear_attention"]:
        layer = int(LINEAR_ATTENTION_RE.fullmatch(target["name"]).group(1))
        if layer_types[layer] != "linear_attention":
            raise ContractError(f"DeltaNet target found in non-DeltaNet layer {layer}")
    for target in grouped["attention"]:
        layer = int(ATTENTION_RE.fullmatch(target["name"]).group(1))
        if layer_types[layer] != "full_attention":
            raise ContractError(
                f"attention target found in non-attention layer {layer}"
            )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = census_snapshot(args.model_dir)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered)
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
