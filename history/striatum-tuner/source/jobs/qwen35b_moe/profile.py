"""Validated configuration seam shared by production and smoke training."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Any, Mapping, Sequence

from .contract import ContractError


@dataclass(frozen=True)
class TrainingProfile:
    path: Path
    raw: dict[str, Any]
    model_id: str
    model_revision: str
    model_type: str
    input_manifest: Path
    cutoff_length: int
    maximum_examples: int
    liger_fused_loss: bool
    strict_input_manifest: bool

    @property
    def train(self) -> dict[str, Any]:
        return dict(self.raw["train"])

    @property
    def runtime(self) -> dict[str, Any]:
        value = self.raw.get("runtime", {})
        return dict(value) if isinstance(value, Mapping) else {}

    @property
    def processing(self) -> dict[str, Any]:
        value = self.raw.get("processing", {})
        return dict(value) if isinstance(value, Mapping) else {}

    def strategy(self, name: str) -> dict[str, Any]:
        strategies = self.raw.get("strategies")
        if not isinstance(strategies, Mapping) or not isinstance(
            strategies.get(name), Mapping
        ):
            raise ContractError(f"training profile has no strategy {name!r}")
        return dict(strategies[name])


def _required_string(value: Mapping[str, Any], key: str, label: str) -> str:
    item = value.get(key)
    if not isinstance(item, str) or not item:
        raise ContractError(f"{label} {key} must be a non-empty string")
    return item


def _positive_int(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ContractError(f"{label} must be a positive integer")
    return value


def load_training_profile(path: Path) -> TrainingProfile:
    """Load one explicit profile without mutating the production default."""

    path = path.resolve()
    if path.is_symlink() or not path.is_file():
        raise ContractError(f"training profile is not a regular file: {path}")
    try:
        value: object = json.loads(path.read_text())
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ContractError(f"training profile is unreadable: {path}") from error
    if not isinstance(value, Mapping):
        raise ContractError("training profile must be a JSON object")
    raw = dict(value)
    model = raw.get("model")
    train = raw.get("train")
    if not isinstance(model, Mapping) or not isinstance(train, Mapping):
        raise ContractError("training profile requires model and train objects")
    runtime = raw.get("runtime", {})
    if not isinstance(runtime, Mapping):
        raise ContractError("training profile runtime must be an object")
    hopper_backend = runtime.get("hopper_linear_attention_backend")
    if hopper_backend not in {None, "flash_qla"}:
        raise ContractError(
            "runtime.hopper_linear_attention_backend must be 'flash_qla' "
            "when configured"
        )
    model_id = _required_string(model, "id", "model")
    model_revision = _required_string(model, "revision", "model")
    model_type = _required_string(model, "expected_model_type", "model")
    cutoff = _positive_int(raw.get("cutoff_length"), "cutoff_length")
    maximum_examples = _positive_int(
        raw.get("maximum_examples", train.get("expected_examples")),
        "maximum_examples",
    )
    manifest_value = raw.get("input_manifest", "input-manifest.json")
    if not isinstance(manifest_value, str) or not manifest_value:
        raise ContractError("input_manifest must be a non-empty relative path")
    manifest_relative = Path(manifest_value)
    if manifest_relative.is_absolute() or ".." in manifest_relative.parts:
        raise ContractError("input_manifest must remain inside the profile directory")
    manifest = (path.parent / manifest_relative).resolve()
    liger = train.get("liger_fused_loss")
    if not isinstance(liger, bool):
        raise ContractError("train.liger_fused_loss must be boolean")
    return TrainingProfile(
        path=path,
        raw=raw,
        model_id=model_id,
        model_revision=model_revision,
        model_type=model_type,
        input_manifest=manifest,
        cutoff_length=cutoff,
        maximum_examples=maximum_examples,
        liger_fused_loss=liger,
        strict_input_manifest=bool(raw.get("strict_input_manifest", True)),
    )


def matched_lora_modules(model: Any, pattern: str) -> tuple[str, ...]:
    """Return the exact full-path LoRA targets and fail closed on no match."""

    try:
        compiled = re.compile(pattern)
    except re.error as error:
        raise ContractError(f"LoRA target pattern is invalid: {error}") from error
    names = tuple(
        sorted(name for name, _ in model.named_modules() if compiled.fullmatch(name))
    )
    if not names:
        raise ContractError(f"LoRA target pattern matched zero modules: {pattern}")
    return names


def resolve_multimodal_paths(
    messages: Sequence[Mapping[str, Any]], input_root: Path
) -> list[dict[str, Any]]:
    """Resolve local image/video paths while confining them to the input tree."""

    root = input_root.resolve()
    resolved = deepcopy(list(messages))
    for message in resolved:
        content = message.get("content")
        if isinstance(content, str):
            message["content"] = [{"type": "text", "text": content}]
            content = message["content"]
        if not isinstance(content, list):
            raise ContractError("message content must be text or typed content blocks")
        for block in content:
            if not isinstance(block, dict) or block.get("type") not in {
                "image",
                "video",
            }:
                continue
            raw_path = block.get("path")
            if raw_path is None:
                continue
            if not isinstance(raw_path, str) or not raw_path:
                raise ContractError("multimodal path must be a non-empty string")
            candidate = Path(raw_path)
            if not candidate.is_absolute():
                candidate = root / candidate
            try:
                candidate = candidate.resolve(strict=True)
                candidate.relative_to(root)
            except (OSError, ValueError) as error:
                raise ContractError(
                    f"multimodal path is absent or outside the input root: {raw_path}"
                ) from error
            if candidate.is_symlink() or not candidate.is_file():
                raise ContractError(
                    f"multimodal path is not a regular file: {raw_path}"
                )
            block["path"] = str(candidate)
    return resolved
