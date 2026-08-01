"""One adapter-backed inference through the configured production runtime."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

from .contract import ContractError
from .data import encode_inference_prompt
from .profile import load_training_profile
from .runtime import load_quantized_base, model_dir_from_env, output_dir_from_env


def _first_training_example(profile_path: Path, input_root: Path) -> dict[str, Any]:
    profile = load_training_profile(profile_path)
    manifest = json.loads(profile.input_manifest.read_text())
    files = manifest.get("files")
    if not isinstance(files, list):
        raise ContractError("input manifest has no file list")
    selected = next(
        (
            item
            for item in files
            if isinstance(item, Mapping) and item.get("role", "train") == "train"
        ),
        None,
    )
    if not isinstance(selected, Mapping) or not isinstance(selected.get("path"), str):
        raise ContractError("input manifest has no training dataset")
    dataset = input_root / str(selected["path"])
    try:
        line = next(line for line in dataset.read_text().splitlines() if line.strip())
        example: object = json.loads(line)
    except (OSError, StopIteration, json.JSONDecodeError) as error:
        raise ContractError("inference example is unreadable") from error
    if not isinstance(example, dict):
        raise ContractError("inference example must be an object")
    return example


def run(args: argparse.Namespace) -> dict[str, Any]:
    try:
        import torch
        from peft import PeftModel
    except ImportError as error:
        raise ContractError("torch and PEFT are required for inference") from error
    profile = load_training_profile(args.config)
    model, processor = load_quantized_base(args.model_dir.resolve(), profile)
    model = PeftModel.from_pretrained(
        model, args.adapter.resolve(), is_trainable=False, local_files_only=True
    )
    model.eval()
    example = _first_training_example(profile.path, args.input_dir.resolve())
    messages = example.get("messages")
    if not isinstance(messages, list) or len(messages) < 1:
        raise ContractError("inference example has no messages")
    encoded = encode_inference_prompt(
        processor,
        messages[:1],
        input_root=args.input_dir.resolve(),
        processing=profile.processing,
    )
    encoded = encoded.to(model.device)
    with torch.inference_mode():
        generated = model.generate(
            **encoded,
            max_new_tokens=args.max_new_tokens,
            do_sample=False,
            use_cache=True,
            pad_token_id=processor.tokenizer.pad_token_id,
            eos_token_id=processor.tokenizer.eos_token_id,
        )
    prompt_length = encoded["input_ids"].shape[1]
    generated_ids = generated[:, prompt_length:]
    content = processor.batch_decode(
        generated_ids,
        skip_special_tokens=True,
        clean_up_tokenization_spaces=False,
    )[0]
    receipt = {
        "protocol": "striatum-adapter-inference/1",
        "model": {
            "id": profile.model_id,
            "revision": profile.model_revision,
            "model_type": profile.model_type,
        },
        "adapter": str(args.adapter.resolve()),
        "adapter_loaded": True,
        "model_class": type(model).__name__,
        "processor_class": type(processor).__name__,
        "input_keys": sorted(encoded),
        "prompt_tokens": int(prompt_length),
        "generated_tokens": generated_ids[0].tolist(),
        "content": content,
    }
    if not receipt["generated_tokens"]:
        raise ContractError("adapter-backed inference generated zero tokens")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return receipt


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--model-dir", type=Path, default=model_dir_from_env())
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--adapter", type=Path, required=True)
    parser.add_argument(
        "--output", type=Path, default=output_dir_from_env() / "inference.json"
    )
    parser.add_argument("--max-new-tokens", type=int, default=32)
    return parser.parse_args()


def main() -> None:
    run(parse_args())


if __name__ == "__main__":
    main()
