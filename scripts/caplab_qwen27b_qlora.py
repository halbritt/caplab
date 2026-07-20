#!/usr/bin/env python3
"""Run the one preregistered Qwen3.6-27B QLoRA attempt on peecee."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import random
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


EXPECTED_SCHEMA = "caplab.training.experiment-preregistration/v1"
EXPECTED_EXPERIMENT = "caplab-review-dissent-qwen27b-qlora-r1"


def canonical(value: object) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def exclusive_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(canonical(value) + b"\n")
        stream.flush()
        os.fsync(stream.fileno())


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise RuntimeError(reason)


@dataclass
class Row:
    record_id: str
    input_ids: list[int]
    attention_mask: list[int]
    labels: list[int]


class ThreeRowDataset:
    def __init__(self, rows: list[Row]) -> None:
        self.rows = rows

    def __len__(self) -> int:
        return len(self.rows)

    def __getitem__(self, index: int) -> dict[str, list[int]]:
        row = self.rows[index]
        return {
            "input_ids": row.input_ids,
            "attention_mask": row.attention_mask,
            "labels": row.labels,
        }


class PadCollator:
    def __init__(self, pad_token_id: int) -> None:
        self.pad_token_id = pad_token_id

    def __call__(self, features: list[dict[str, list[int]]]) -> dict[str, Any]:
        import torch

        width = max(len(item["input_ids"]) for item in features)
        inputs: list[list[int]] = []
        masks: list[list[int]] = []
        labels: list[list[int]] = []
        for item in features:
            padding = width - len(item["input_ids"])
            inputs.append(item["input_ids"] + [self.pad_token_id] * padding)
            masks.append(item["attention_mask"] + [0] * padding)
            labels.append(item["labels"] + [-100] * padding)
        return {
            "input_ids": torch.tensor(inputs, dtype=torch.long),
            "attention_mask": torch.tensor(masks, dtype=torch.long),
            "labels": torch.tensor(labels, dtype=torch.long),
        }


def load_contract(experiment_path: Path, corpus_path: Path, model_dir: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    experiment = json.loads(experiment_path.read_text(encoding="utf-8"))
    require(experiment.get("schema") == EXPECTED_SCHEMA, "experiment_schema_mismatch")
    require(experiment.get("experiment_id") == EXPECTED_EXPERIMENT, "experiment_id_mismatch")
    require(experiment.get("authority") == "adr-0049", "preregistration_authority_mismatch")
    require(sha256_file(corpus_path) == experiment["training_data"]["file_sha256"], "corpus_sha256_mismatch")
    require(
        sha256_file(model_dir / "model.safetensors.index.json")
        == experiment["base_checkpoint"]["index_sha256"],
        "checkpoint_index_sha256_mismatch",
    )
    corpus = json.loads(corpus_path.read_text(encoding="utf-8"))
    require(corpus.get("corpus_sha256") == experiment["training_data"]["semantic_sha256"], "corpus_semantic_sha256_mismatch")
    records = [record for record in corpus.get("records", []) if record.get("record_id") in experiment["training_data"]["record_ids"]]
    require([record["record_id"] for record in records] == experiment["training_data"]["record_ids"], "training_record_order_mismatch")
    require(all(record.get("split") == "train" and record.get("task_family") == "RD-D01" for record in records), "training_family_mismatch")
    return experiment, {"records": records}


def verify_environment(experiment: dict[str, Any]) -> dict[str, Any]:
    import torch

    packages = {
        name: importlib.metadata.version(name)
        for name in ("transformers", "peft", "trl", "bitsandbytes", "accelerate")
    }
    expected = experiment["toolchain"]
    require(platform.python_version().startswith(expected["python"] + "."), "python_version_mismatch")
    require(torch.__version__ == expected["torch"], "torch_version_mismatch")
    require(all(packages[name] == expected[name] for name in packages), "package_version_mismatch")
    require(torch.cuda.is_available() and torch.cuda.device_count() == 1, "single_cuda_gpu_required")
    properties = torch.cuda.get_device_properties(0)
    require(properties.name == experiment["compute_ceiling"]["gpu_model"], "gpu_model_mismatch")
    require(properties.total_memory // (1024 * 1024) >= experiment["compute_ceiling"]["gpu_memory_mib"] - 128, "gpu_memory_mismatch")
    return {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "torch": torch.__version__,
        "cuda": torch.version.cuda,
        "packages": packages,
        "gpu": properties.name,
        "gpu_total_mib": properties.total_memory // (1024 * 1024),
    }


def build_rows(tokenizer: Any, records: list[dict[str, Any]], maximum: int) -> list[Row]:
    rows: list[Row] = []
    for record in records:
        prompt_messages = [{"role": "user", "content": record["prompt"]}]
        full_messages = prompt_messages + [{
            "role": "assistant",
            "content": canonical(record["chosen"]).decode("utf-8"),
        }]
        prompt_text = tokenizer.apply_chat_template(
            prompt_messages, tokenize=False, add_generation_prompt=True
        )
        full_text = tokenizer.apply_chat_template(
            full_messages, tokenize=False, add_generation_prompt=False
        )
        prompt_ids = tokenizer(prompt_text, add_special_tokens=False)["input_ids"]
        input_ids = tokenizer(full_text, add_special_tokens=False)["input_ids"]
        require(len(input_ids) <= maximum, f"record_exceeds_sequence_ceiling:{record['record_id']}")
        require(len(prompt_ids) < len(input_ids), f"assistant_target_missing:{record['record_id']}")
        rows.append(Row(
            record_id=record["record_id"],
            input_ids=input_ids,
            attention_mask=[1] * len(input_ids),
            labels=[-100] * len(prompt_ids) + input_ids[len(prompt_ids):],
        ))
    return rows


def load_model_and_adapter(experiment: dict[str, Any], model_dir: Path) -> tuple[Any, Any, list[str]]:
    import torch
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    from transformers import AutoModelForImageTextToText, AutoTokenizer, BitsAndBytesConfig

    method = experiment["method"]
    tokenizer = AutoTokenizer.from_pretrained(model_dir, local_files_only=True)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
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
        device_map={"": 0},
        low_cpu_mem_usage=True,
    )
    model.config.use_cache = False
    model = prepare_model_for_kbit_training(
        model,
        use_gradient_checkpointing=True,
        gradient_checkpointing_kwargs={"use_reentrant": False},
    )
    targets = method["lora"]["target_modules"]
    available = {
        name.rsplit(".", 1)[-1]
        for name, _module in model.named_modules()
        if ".language_model." in name
    }
    require(set(targets) <= available, "frozen_adapter_target_missing")
    model = get_peft_model(model, LoraConfig(
        r=method["lora"]["rank"],
        lora_alpha=method["lora"]["alpha"],
        lora_dropout=float(method["lora"]["dropout"]),
        bias=method["lora"]["bias"],
        target_modules=targets,
        task_type="CAUSAL_LM",
    ))
    trainable = [name for name, parameter in model.named_parameters() if parameter.requires_grad]
    require(trainable, "no_trainable_adapter_parameters")
    require(all(".language_model." in name and "lora_" in name for name in trainable), "adapter_scope_escape")
    return model, tokenizer, trainable


def run(args: argparse.Namespace) -> int:
    import numpy
    import torch
    from transformers import Trainer, TrainerCallback, TrainingArguments

    output = args.output.resolve()
    require(not output.exists(), "output_root_exists")
    output.mkdir(parents=True)
    experiment, corpus = load_contract(args.experiment, args.corpus, args.model_dir)
    environment = verify_environment(experiment)
    exclusive_json(output / "environment.json", environment)

    seed = experiment["method"]["seed"]
    random.seed(seed)
    numpy.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True

    model, tokenizer, trainable = load_model_and_adapter(experiment, args.model_dir)
    rows = build_rows(tokenizer, corpus["records"], experiment["method"]["max_sequence_tokens"])
    collator = PadCollator(tokenizer.pad_token_id)
    batch = collator([ThreeRowDataset(rows)[0]])
    batch = {key: value.to("cuda:0") for key, value in batch.items()}
    model.train()
    smoke_started = time.monotonic()
    smoke = model(**batch)
    require(torch.isfinite(smoke.loss).item(), "nonfinite_preflight_loss")
    smoke.loss.backward()
    require(
        all(parameter.grad is None or torch.isfinite(parameter.grad).all().item() for parameter in model.parameters() if parameter.requires_grad),
        "nonfinite_preflight_gradient",
    )
    model.zero_grad(set_to_none=True)
    torch.cuda.empty_cache()
    preflight = {
        "schema": "caplab.training.qlora-preflight/v1",
        "experiment_id": experiment["experiment_id"],
        "record_token_counts": {row.record_id: len(row.input_ids) for row in rows},
        "trainable_parameter_names": trainable,
        "trainable_parameter_count": sum(parameter.numel() for parameter in model.parameters() if parameter.requires_grad),
        "loss": format(smoke.loss.detach().float().item(), ".12g"),
        "duration_seconds": format(time.monotonic() - smoke_started, ".6f"),
        "gpu_allocated_mib": torch.cuda.max_memory_allocated() // (1024 * 1024),
    }
    exclusive_json(output / "preflight.json", preflight)
    if args.mode == "preflight":
        return 0

    ceiling = experiment["compute_ceiling"]["training_wall_seconds"]

    class CeilingCallback(TrainerCallback):
        def __init__(self) -> None:
            self.started = time.monotonic()

        def on_step_end(self, _args, _state, control, **_kwargs):
            if time.monotonic() - self.started >= ceiling:
                control.should_training_stop = True
            return control

    training_output = output / "trainer"
    method = experiment["method"]
    training_args = TrainingArguments(
        output_dir=str(training_output),
        per_device_train_batch_size=method["per_device_batch"],
        gradient_accumulation_steps=method["gradient_accumulation"],
        num_train_epochs=method["epochs"],
        max_steps=method["optimizer_steps_max"],
        learning_rate=float(method["learning_rate"]),
        lr_scheduler_type="constant",
        warmup_steps=0,
        weight_decay=float(method["weight_decay"]),
        max_grad_norm=float(method["gradient_clip"]),
        optim="paged_adamw_8bit",
        bf16=True,
        tf32=True,
        gradient_checkpointing=True,
        gradient_checkpointing_kwargs={"use_reentrant": False},
        save_strategy="steps",
        save_steps=3,
        save_total_limit=4,
        logging_strategy="steps",
        logging_steps=1,
        report_to=[],
        seed=seed,
        data_seed=seed,
        dataloader_num_workers=0,
        remove_unused_columns=False,
    )
    callback = CeilingCallback()
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=ThreeRowDataset(rows),
        data_collator=collator,
        callbacks=[callback],
    )
    exclusive_json(output / "training-started.json", {
        "schema": "caplab.training.attempt-start/v1",
        "experiment_id": experiment["experiment_id"],
        "optimizer_step_ceiling": method["optimizer_steps_max"],
        "wall_seconds_ceiling": ceiling,
    })
    trained = trainer.train()
    duration = time.monotonic() - callback.started
    require(trainer.state.global_step == method["optimizer_steps_max"], "training_stopped_before_step_ceiling")
    require(duration <= ceiling, "training_wall_ceiling_exceeded")
    final_adapter = output / "final-adapter"
    model.save_pretrained(final_adapter, safe_serialization=True)
    tokenizer.save_pretrained(final_adapter)
    trainer.save_state()
    files = {
        path.relative_to(output).as_posix(): sha256_file(path)
        for path in sorted(output.rglob("*"))
        if path.is_file() and path.name != "result.json"
    }
    result = {
        "schema": "caplab.training.qlora-result/v1",
        "experiment_id": experiment["experiment_id"],
        "global_steps": trainer.state.global_step,
        "training_loss": format(trained.training_loss, ".12g"),
        "training_duration_seconds": format(duration, ".6f"),
        "peak_gpu_allocated_mib": torch.cuda.max_memory_allocated() // (1024 * 1024),
        "files": files,
    }
    result["result_sha256"] = hashlib.sha256(canonical(result)).hexdigest()
    exclusive_json(output / "result.json", result)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("preflight", "train"), required=True)
    parser.add_argument("--experiment", type=Path, required=True)
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument("--model-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        return run(args)
    except Exception as error:
        print(f"caplab_qwen27b_qlora: {type(error).__name__}: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
