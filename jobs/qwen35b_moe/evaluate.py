"""Separate-process adapter generation and evaluation."""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
from pathlib import Path
import re
import time
from typing import Any, Mapping

from .contract import ContractError, sha256_file
from .runtime import (
    input_dir_from_env,
    load_bf16_base,
    load_quantized_base,
    model_dir_from_env,
    output_dir_from_env,
    training_config,
)
from .train import select_longest_tokenized_index


ACCEPTING = {"accept", "accept_with_findings"}
VERDICTS = {"accept", "accept_with_findings", "needs_revision", "reject"}


def extract_json(content: str) -> Any:
    for match in re.finditer(r"```(?:json)?\s*\n(.*?)```", content, re.DOTALL):
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            continue
    decoder = json.JSONDecoder()
    for index, character in enumerate(content):
        if character in "{[":
            try:
                document, _ = decoder.raw_decode(content[index:])
                return document
            except json.JSONDecodeError:
                continue
    return None


def side(verdict: Any) -> str | None:
    if verdict in ACCEPTING:
        return "accepting"
    if verdict in VERDICTS:
        return "refusing"
    return None


def derive_checkpoint_25_dispatch_ids(
    examples: list[dict[str, Any]], count: int
) -> list[str]:
    """Derive the declared mini subset from the lowest dispatch-ID hashes."""
    if isinstance(count, bool) or count <= 0 or count > len(examples):
        raise ContractError("checkpoint-25 subset size is invalid")
    dispatch_ids = []
    for example in examples:
        metadata = example.get("meta")
        dispatch_id = (
            metadata.get("dispatch_id") if isinstance(metadata, dict) else None
        )
        if not isinstance(dispatch_id, str) or not dispatch_id:
            raise ContractError("evaluation example has no dispatch_id")
        dispatch_ids.append(dispatch_id)
    if len(set(dispatch_ids)) != len(dispatch_ids):
        raise ContractError("evaluation dispatch_ids are not unique")
    return sorted(
        dispatch_ids,
        key=lambda dispatch_id: (
            hashlib.sha256(dispatch_id.encode()).hexdigest(),
            dispatch_id,
        ),
    )[:count]


def _read_examples(
    path: Path,
    limit: int,
    selection: str,
    *,
    tokenizer: Any | None = None,
    cutoff: int = 40_960,
    expected_source_sha: str | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    examples = [json.loads(line) for line in path.read_text().splitlines()]
    if selection == "checkpoint-25-mini":
        policy = training_config()["quality_gate"]["checkpoint_25_mini"]
        count = policy["examples"]
        if limit not in {0, count}:
            raise ContractError(
                f"checkpoint-25 selection requires limit {count}, found {limit}"
            )
        if len(examples) != 98:
            raise ContractError(
                f"expected 98 evaluation examples, found {len(examples)}"
            )
        if policy["source_path"] != "sft/review.eval.jsonl":
            raise ContractError("checkpoint-25 policy names an unexpected source")
        if sha256_file(path) != policy["source_sha256"]:
            raise ContractError("checkpoint-25 source hash does not match policy")
        derived = derive_checkpoint_25_dispatch_ids(examples, count)
        if policy["derivation"] != "lowest-sha256-dispatch-id":
            raise ContractError("checkpoint-25 subset derivation is unexpected")
        if policy["dispatch_ids"] != derived:
            raise ContractError(
                "declared checkpoint-25 subset does not match derivation"
            )
        by_dispatch_id = {
            example["meta"]["dispatch_id"]: example for example in examples
        }
        return [by_dispatch_id[dispatch_id] for dispatch_id in derived], dict(policy)
    if selection == "longest-tokenized-authorized":
        if limit != 1:
            raise ContractError(
                "longest-tokenized evaluation selection requires limit 1"
            )
        if tokenizer is None:
            raise ContractError(
                "longest-tokenized evaluation selection requires the tokenizer"
            )
        if len(examples) != 98:
            raise ContractError(
                f"expected 98 evaluation examples, found {len(examples)}"
            )
        expected_hash = expected_source_sha or training_config()["quality_gate"][
            "epoch_one_full"
        ]["source_sha256"]
        source_sha = sha256_file(path)
        if source_sha != expected_hash:
            raise ContractError("longest evaluation source hash does not match policy")
        raw_lengths = []
        for example in examples:
            messages = example.get("messages")
            if (
                not isinstance(messages, list)
                or len(messages) != 2
                or messages[0].get("role") != "user"
                or messages[1].get("role") != "assistant"
            ):
                raise ContractError(
                    "evaluation examples must contain one user and one assistant message"
                )
            raw_lengths.append(
                len(
                    tokenizer.apply_chat_template(
                        messages[:1],
                        tokenize=True,
                        add_generation_prompt=True,
                        enable_thinking=False,
                    )
                )
            )
        selected_index = select_longest_tokenized_index(raw_lengths, cutoff)
        selected = examples[selected_index]
        metadata = selected.get("meta")
        dispatch_id = (
            metadata.get("dispatch_id") if isinstance(metadata, dict) else None
        )
        if not isinstance(dispatch_id, str) or not dispatch_id:
            raise ContractError("longest evaluation example has no dispatch_id")
        evidence = {
            "method": "longest-tokenized-authorized",
            "candidates": len(examples),
            "examples": 1,
            "source_path": "sft/review.eval.jsonl",
            "source_sha256": source_sha,
            "selected_global_index": selected_index,
            "dispatch_id": dispatch_id,
            "dispatch_ids": [dispatch_id],
            "raw_token_count": raw_lengths[selected_index],
            "effective_token_count": min(raw_lengths[selected_index], cutoff),
            "max_raw_token_count": max(raw_lengths),
            "max_effective_token_count": max(
                min(length, cutoff) for length in raw_lengths
            ),
            "token_length_census_sha256": hashlib.sha256(
                json.dumps(raw_lengths, separators=(",", ":")).encode()
            ).hexdigest(),
            "cutoff": cutoff,
            "tie_break": "effective-length,raw-length,earliest-global-index",
            "tokenization_surface": (
                "user-prompt-with-generation-marker-no-thinking"
            ),
        }
        return [selected], evidence
    if selection != "prefix":
        raise ContractError(f"unknown evaluation selection: {selection}")
    if not limit and len(examples) != 98:
        raise ContractError(f"expected 98 evaluation examples, found {len(examples)}")
    selected = examples[:limit] if limit else examples
    return selected, {
        "method": "prefix" if limit else "all-authorized-source-order",
        "examples": len(selected),
        "source_path": "sft/review.eval.jsonl",
        "source_sha256": sha256_file(path),
        "dispatch_ids": [example["meta"]["dispatch_id"] for example in selected],
    }


def verify_longest_evaluation_receipt(
    summary: Mapping[str, object],
) -> dict[str, Any]:
    """Validate exact evidence for the maximum-risk held-out prompt."""

    if summary.get("protocol") != "striatum-evaluation-result/1" or summary.get(
        "n"
    ) != 1:
        raise ContractError("longest evaluation summary contract is invalid")
    raw_selection = summary.get("selection")
    if not isinstance(raw_selection, Mapping):
        raise ContractError("longest evaluation selection evidence is absent")
    selection = dict(raw_selection)
    expected_fields = {
        "method",
        "candidates",
        "examples",
        "source_path",
        "source_sha256",
        "selected_global_index",
        "dispatch_id",
        "dispatch_ids",
        "raw_token_count",
        "effective_token_count",
        "max_raw_token_count",
        "max_effective_token_count",
        "token_length_census_sha256",
        "cutoff",
        "tie_break",
        "tokenization_surface",
    }
    if set(selection) != expected_fields:
        raise ContractError("longest evaluation selection fields are not exact")
    if (
        selection.get("method") != "longest-tokenized-authorized"
        or selection.get("candidates") != 98
        or selection.get("examples") != 1
        or selection.get("source_path") != "sft/review.eval.jsonl"
        or selection.get("cutoff") != 40_960
        or selection.get("tie_break")
        != "effective-length,raw-length,earliest-global-index"
        or selection.get("tokenization_surface")
        != "user-prompt-with-generation-marker-no-thinking"
    ):
        raise ContractError("longest evaluation selection policy is invalid")
    index = selection.get("selected_global_index")
    raw = selection.get("raw_token_count")
    effective = selection.get("effective_token_count")
    if (
        isinstance(index, bool)
        or not isinstance(index, int)
        or not 0 <= index < 98
        or isinstance(raw, bool)
        or not isinstance(raw, int)
        or raw <= 0
        or isinstance(effective, bool)
        or not isinstance(effective, int)
        or effective != min(raw, 40_960)
        or raw != selection.get("max_raw_token_count")
        or effective != selection.get("max_effective_token_count")
    ):
        raise ContractError("longest evaluation token counts are inconsistent")
    dispatch_id = selection.get("dispatch_id")
    if (
        not isinstance(dispatch_id, str)
        or not dispatch_id
        or selection.get("dispatch_ids") != [dispatch_id]
    ):
        raise ContractError("longest evaluation dispatch evidence is invalid")
    for field in ("source_sha256", "token_length_census_sha256"):
        digest = selection.get(field)
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ContractError(f"longest evaluation {field} is invalid")
    return selection


def run(args: argparse.Namespace) -> dict[str, Any]:
    try:
        import torch
        from peft import PeftModel
        from transformers import set_seed
    except ImportError as error:
        raise ContractError(
            "torch, transformers, and PEFT are required for evaluation"
        ) from error

    set_seed(args.seed)
    load_base = load_bf16_base if args.bf16_base else load_quantized_base
    model, tokenizer = load_base(args.model_dir.resolve())
    model = PeftModel.from_pretrained(model, args.adapter.resolve(), is_trainable=False)
    model.eval()
    examples, selection_evidence = _read_examples(
        args.input_dir / "sft/review.eval.jsonl",
        args.limit,
        args.selection,
        tokenizer=tokenizer,
        cutoff=training_config()["cutoff_length"],
    )
    args.output.mkdir(parents=True, exist_ok=True)
    results_path = args.output / "results.jsonl"
    rows = []
    with results_path.open("w") as output:
        for index, example in enumerate(examples):
            started = time.monotonic()
            messages = example["messages"]
            reference = json.loads(messages[1]["content"])
            rendered_prompt = tokenizer.apply_chat_template(
                messages[:1],
                tokenize=False,
                add_generation_prompt=True,
                enable_thinking=False,
            )
            encoded = tokenizer(
                rendered_prompt,
                return_tensors="pt",
                add_special_tokens=False,
                truncation=True,
                max_length=40_960,
            ).to(model.device)
            generation_kwargs = {
                "max_new_tokens": args.max_new_tokens,
                "pad_token_id": tokenizer.pad_token_id,
                "eos_token_id": tokenizer.eos_token_id,
                "use_cache": True,
            }
            if args.deterministic:
                generation_kwargs.update(do_sample=False)
            else:
                generation_kwargs.update(do_sample=True, temperature=0.6)
            with torch.inference_mode():
                generated = model.generate(**encoded, **generation_kwargs)
            generated_ids = generated[0, encoded["input_ids"].shape[1] :]
            content = tokenizer.decode(generated_ids, skip_special_tokens=True)
            document = extract_json(content)
            verdict = document.get("verdict") if isinstance(document, dict) else None
            row = {
                "dispatch_id": example["meta"]["dispatch_id"],
                "seconds": round(time.monotonic() - started, 3),
                "json_valid": isinstance(document, dict),
                "verdict": verdict,
                "verdict_legal": verdict in VERDICTS,
                "reference_verdict": reference.get("verdict"),
                "verdict_exact_match": verdict == reference.get("verdict"),
                "side_match": side(verdict) is not None
                and side(verdict) == side(reference.get("verdict")),
                "generated_tokens": generated_ids.tolist(),
                "content": content,
            }
            output.write(json.dumps(row, ensure_ascii=False) + "\n")
            output.flush()
            rows.append(row)
            print(
                f"[{index + 1}/{len(examples)}] {row['dispatch_id'][:12]} verdict={verdict}",
                flush=True,
            )

    total = len(rows)
    summary = {
        "protocol": "striatum-evaluation-result/1",
        "selection": selection_evidence,
        "n": total,
        "json_valid": sum(row["json_valid"] for row in rows) / total if total else None,
        "verdict_legal": sum(row["verdict_legal"] for row in rows) / total
        if total
        else None,
        "verdict_exact_match": (
            sum(row["verdict_exact_match"] for row in rows) / total if total else None
        ),
        "side_match": sum(row["side_match"] for row in rows) / total if total else None,
        "fate_agreement": None,
        "fate_scored": 0,
        "fate_gate_status": "deferred-to-local-recovery",
        "verdict_distribution": dict(
            collections.Counter(str(row["verdict"]) for row in rows)
        ),
        "mean_seconds": (
            round(sum(row["seconds"] for row in rows) / total, 3) if total else None
        ),
    }
    baseline = training_config()["quality_gate"]["strictly_beat"]
    summary["available_gates"] = {
        metric: summary[metric] > baseline[metric]
        for metric in ("json_valid", "verdict_legal", "side_match")
    }
    (args.output / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
    )
    if args.deterministic and rows:
        (args.output / "hf-reference.json").write_text(
            json.dumps(
                {
                    "protocol": "hf-llama-parity-reference/1",
                    "rendered_prompt": tokenizer.apply_chat_template(
                        examples[0]["messages"][:1],
                        tokenize=False,
                        add_generation_prompt=True,
                        enable_thinking=False,
                    ),
                    "content": rows[0]["content"],
                    "generated_tokens": rows[0]["generated_tokens"],
                    "seed": args.seed,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n"
        )
    if args.enforce_available_gates and not all(summary["available_gates"].values()):
        raise ContractError(
            f"available quality gate failed: {summary['available_gates']}"
        )
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-dir", type=Path, default=model_dir_from_env())
    parser.add_argument("--input-dir", type=Path, default=input_dir_from_env())
    parser.add_argument(
        "--adapter",
        type=Path,
        default=output_dir_from_env() / "checkpoints/final-adapter",
    )
    parser.add_argument("--output", type=Path, default=output_dir_from_env() / "eval")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument(
        "--selection",
        choices=("prefix", "checkpoint-25-mini", "longest-tokenized-authorized"),
        default="prefix",
    )
    parser.add_argument("--max-new-tokens", type=int, default=32_768)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--deterministic", action="store_true")
    parser.add_argument("--bf16-base", action="store_true")
    parser.add_argument("--enforce-available-gates", action="store_true")
    return parser.parse_args()


def main() -> None:
    print(json.dumps(run(parse_args()), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
