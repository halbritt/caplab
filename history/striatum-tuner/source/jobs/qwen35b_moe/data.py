"""Shared multimodal SFT encoding and collation."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import math
from pathlib import Path
from typing import Any

from .contract import ContractError
from .profile import resolve_multimodal_paths


def _single_sequence(value: object, label: str) -> list[int]:
    if hasattr(value, "tolist"):
        value = value.tolist()
    if (
        isinstance(value, list)
        and len(value) == 1
        and isinstance(value[0], list)
    ):
        value = value[0]
    if (
        not isinstance(value, list)
        or not value
        or any(
            isinstance(item, bool) or not isinstance(item, int) or item < 0
            for item in value
        )
    ):
        raise ContractError(f"processor {label} is not one token-ID sequence")
    return value


def _truncate_sft_tokens(
    full_ids: Sequence[int], prompt_ids: Sequence[int], *, cutoff: int
) -> dict[str, list[int]]:
    if isinstance(cutoff, bool) or not isinstance(cutoff, int) or cutoff <= 0:
        raise ContractError("token cutoff must be positive")
    full = list(full_ids)
    prompt = list(prompt_ids)
    if not full or not prompt:
        raise ContractError("SFT token sequences must be non-empty")
    if full[: len(prompt)] != prompt:
        raise ContractError("SFT prompt tokens are not an exact prefix")
    assistant = full[len(prompt) :]
    if not assistant:
        raise ContractError("SFT example has no assistant tokens")
    if len(prompt) >= cutoff:
        if len(assistant) >= cutoff:
            raise ContractError(
                "token cutoff cannot preserve assistant tokens after prompt overflow"
            )
        prompt_budget = cutoff - len(assistant)
        input_ids = prompt[-prompt_budget:] + assistant
        labels = [-100] * prompt_budget + assistant
    else:
        input_ids = full[:cutoff]
        masked = min(len(prompt), len(input_ids))
        labels = [-100] * masked + input_ids[masked:]
    if not labels or all(label == -100 for label in labels):
        raise ContractError("token truncation removed every assistant token")
    return {
        "input_ids": input_ids,
        "attention_mask": [1] * len(input_ids),
        "labels": labels,
    }


def _processor_kwargs(processing: Mapping[str, Any]) -> dict[str, Any]:
    shortest = processing.get("image_shortest_edge")
    longest = processing.get("image_longest_edge")
    if shortest is None and longest is None:
        return {}
    if (
        isinstance(shortest, bool)
        or not isinstance(shortest, int)
        or shortest <= 0
        or isinstance(longest, bool)
        or not isinstance(longest, int)
        or longest < shortest
    ):
        raise ContractError("image pixel bounds are invalid")
    return {
        "images_kwargs": {
            "size": {"shortest_edge": shortest, "longest_edge": longest}
        }
    }


def encode_sft_example(
    processor: Any,
    example: Mapping[str, Any],
    *,
    input_root: Path,
    cutoff: int,
    processing: Mapping[str, Any],
) -> dict[str, Any]:
    """Apply the model processor and construct assistant-only labels."""

    messages = example.get("messages")
    if (
        not isinstance(messages, list)
        or len(messages) != 2
        or not isinstance(messages[0], Mapping)
        or not isinstance(messages[1], Mapping)
        or messages[0].get("role") != "user"
        or messages[1].get("role") != "assistant"
    ):
        raise ContractError(
            "SFT examples must contain one user and one assistant message"
        )
    resolved = resolve_multimodal_paths(messages, input_root)
    common = {
        "tokenize": True,
        "enable_thinking": False,
        "return_dict": True,
        "return_tensors": None,
        "processor_kwargs": _processor_kwargs(processing),
    }
    full = processor.apply_chat_template(
        resolved, add_generation_prompt=False, **common
    )
    prompt = processor.apply_chat_template(
        resolved[:1], add_generation_prompt=True, **common
    )
    if not isinstance(full, Mapping) or not isinstance(prompt, Mapping):
        raise ContractError("processor chat template did not return a mapping")
    full_ids = _single_sequence(full.get("input_ids"), "input_ids")
    prompt_ids = _single_sequence(prompt.get("input_ids"), "prompt input_ids")
    encoded: dict[str, Any] = _truncate_sft_tokens(
        full_ids, prompt_ids, cutoff=cutoff
    )
    if len(full_ids) > cutoff and any(
        key in full for key in ("pixel_values", "pixel_values_videos")
    ):
        raise ContractError(
            "multimodal SFT rows must fit the configured cutoff without truncation"
        )
    mm_ids = full.get("mm_token_type_ids")
    if mm_ids is not None:
        unwrapped = _single_sequence(mm_ids, "mm_token_type_ids")
        encoded["mm_token_type_ids"] = unwrapped[: len(encoded["input_ids"])]
    for key in (
        "pixel_values",
        "image_grid_thw",
        "pixel_values_videos",
        "video_grid_thw",
    ):
        if key in full:
            encoded[key] = full[key]
    return encoded


def encode_inference_prompt(
    processor: Any,
    messages: Sequence[Mapping[str, Any]],
    *,
    input_root: Path,
    processing: Mapping[str, Any],
) -> Any:
    """Apply the same processor and path policy to one generation prompt."""

    resolved = resolve_multimodal_paths(messages, input_root)
    encoded = processor.apply_chat_template(
        resolved,
        tokenize=True,
        add_generation_prompt=True,
        enable_thinking=False,
        return_dict=True,
        return_tensors="pt",
        processor_kwargs=_processor_kwargs(processing),
    )
    if not isinstance(encoded, Mapping) or "input_ids" not in encoded:
        raise ContractError("processor did not construct an inference batch")
    return encoded


class MultimodalSFTCollator:
    """Batch the exact encoded model inputs and retain first-batch evidence."""

    def __init__(
        self,
        processor: Any,
        *,
        input_root: Path,
        cutoff: int,
        processing: Mapping[str, Any],
        pad_to_multiple_of: int = 8,
    ) -> None:
        self.processor = processor
        self.input_root = input_root
        self.cutoff = cutoff
        self.processing = dict(processing)
        self.pad_to_multiple_of = pad_to_multiple_of
        self.receipt: dict[str, Any] | None = None

    def __call__(self, examples: list[Mapping[str, Any]]) -> dict[str, Any]:
        try:
            import torch
        except ImportError as error:
            raise ContractError("torch is required for SFT collation") from error
        if not examples:
            raise ContractError("cannot collate an empty SFT batch")
        rows = [
            encode_sft_example(
                self.processor,
                example,
                input_root=self.input_root,
                cutoff=self.cutoff,
                processing=self.processing,
            )
            for example in examples
        ]
        maximum = max(len(row["input_ids"]) for row in rows)
        padded = int(
            math.ceil(maximum / self.pad_to_multiple_of) * self.pad_to_multiple_of
        )
        tokenizer = getattr(self.processor, "tokenizer", None)
        pad_id = getattr(tokenizer, "pad_token_id", None)
        if not isinstance(pad_id, int) or pad_id < 0:
            raise ContractError("processor tokenizer has no valid pad token")
        batch: dict[str, Any] = {}
        for key, fill in (
            ("input_ids", pad_id),
            ("attention_mask", 0),
            ("labels", -100),
            ("mm_token_type_ids", 0),
        ):
            if key == "mm_token_type_ids" and not any(key in row for row in rows):
                continue
            values = []
            for row in rows:
                value = list(row.get(key, [0] * len(row["input_ids"])))
                values.append(value + [fill] * (padded - len(value)))
            batch[key] = torch.tensor(values, dtype=torch.long)
        for key in (
            "pixel_values",
            "image_grid_thw",
            "pixel_values_videos",
            "video_grid_thw",
        ):
            values = [torch.as_tensor(row[key]) for row in rows if key in row]
            if values:
                batch[key] = torch.cat(values, dim=0)
        if self.receipt is None:
            loss_labels = batch["labels"] != -100
            image_count = (
                int(batch["image_grid_thw"].shape[0])
                if "image_grid_thw" in batch
                else 0
            )
            self.receipt = {
                "protocol": "striatum-multimodal-batch/1",
                "batch_size": len(rows),
                "sequence_length": int(batch["input_ids"].shape[1]),
                "supervised_tokens": int(loss_labels.sum().item()),
                "image_count": image_count,
                "keys": sorted(batch),
            }
        return batch
