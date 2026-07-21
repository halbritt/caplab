#!/usr/bin/env python3
"""Run the separately preregistered CAPLAB-16 r2 qualification or training."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import random
import sys
import time
from pathlib import Path
from typing import Any


def _load_r1_module() -> Any:
    path = Path(__file__).with_name("caplab_qwen27b_qlora.py")
    spec = importlib.util.spec_from_file_location("caplab_qwen27b_qlora_r1", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("r1_trainer_module_unavailable")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


R1 = _load_r1_module()


def load_contract(
    experiment_path: Path,
    corpus_path: Path,
    model_dir: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    experiment = json.loads(experiment_path.read_text(encoding="utf-8"))
    R1.require(
        experiment.get("schema") == "caplab.training.experiment-preregistration/v1",
        "experiment_schema_mismatch",
    )
    R1.require(
        experiment.get("experiment_id") == "caplab-review-dissent-qwen27b-qlora-r2",
        "experiment_id_mismatch",
    )
    R1.require(experiment.get("authority") == "adr-0053", "preregistration_authority_mismatch")
    R1.require(
        R1.sha256_file(corpus_path) == experiment["training_data"]["file_sha256"],
        "corpus_sha256_mismatch",
    )
    R1.require(
        R1.sha256_file(model_dir / "model.safetensors.index.json")
        == experiment["base_checkpoint"]["index_sha256"],
        "checkpoint_index_sha256_mismatch",
    )
    corpus = json.loads(corpus_path.read_text(encoding="utf-8"))
    R1.require(
        corpus.get("corpus_sha256") == experiment["training_data"]["semantic_sha256"],
        "corpus_semantic_sha256_mismatch",
    )
    wanted = experiment["training_data"]["record_ids"]
    records = [record for record in corpus.get("records", []) if record.get("record_id") in wanted]
    R1.require([record["record_id"] for record in records] == wanted, "training_record_order_mismatch")
    R1.require(
        all(record.get("split") == "train" and record.get("task_family") == "RD-D01" for record in records),
        "training_family_mismatch",
    )
    return experiment, {"records": records}


def adapter_digest(model: Any) -> str:
    import torch

    digest = hashlib.sha256()
    for name, parameter in model.named_parameters():
        if parameter.requires_grad:
            digest.update(name.encode("utf-8") + b"\0")
            digest.update(
                parameter.detach().contiguous().view(torch.uint8).cpu().numpy().tobytes()
            )
    return digest.hexdigest()


def qualify(args: argparse.Namespace) -> int:
    import numpy
    import torch

    output = args.output.resolve()
    R1.require(not output.exists(), "output_root_exists")
    output.mkdir(parents=True)
    experiment, corpus = load_contract(args.experiment, args.corpus, args.model_dir)
    R1.exclusive_json(output / "environment.json", R1.verify_environment(experiment))

    seed = experiment["method"]["seed"]
    random.seed(seed)
    numpy.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True

    model, tokenizer, trainable = R1.load_model_and_adapter(experiment, args.model_dir)
    rows = R1.build_rows(
        tokenizer,
        corpus["records"],
        experiment["method"]["max_sequence_tokens"],
    )
    batch = R1.PadCollator(tokenizer.pad_token_id)([R1.ThreeRowDataset(rows)[0]])
    batch = {key: value.to("cuda:0") for key, value in batch.items()}
    model.train()

    initial_smoke = model(**batch)
    R1.require(torch.isfinite(initial_smoke.loss).item(), "nonfinite_preflight_loss")
    initial_smoke.loss.backward()
    R1.require(
        all(
            parameter.grad is None or torch.isfinite(parameter.grad).all().item()
            for parameter in model.parameters()
            if parameter.requires_grad
        ),
        "nonfinite_preflight_gradient",
    )
    model.zero_grad(set_to_none=True)
    R1.exclusive_json(output / "preflight.json", {
        "schema": "caplab.training.qlora-preflight/v1",
        "experiment_id": experiment["experiment_id"],
        "record_token_counts": {row.record_id: len(row.input_ids) for row in rows},
        "trainable_parameter_names": trainable,
        "trainable_parameter_count": sum(
            parameter.numel() for parameter in model.parameters() if parameter.requires_grad
        ),
        "loss": format(initial_smoke.loss.detach().float().item(), ".12g"),
        "gpu_allocated_mib": torch.cuda.max_memory_allocated() // (1024 * 1024),
    })

    qualification_seconds = experiment["host_qualification"]["no_update_seconds"]
    before = adapter_digest(model)
    losses: list[str] = []
    iterations = 0
    started = time.monotonic()
    while time.monotonic() - started < qualification_seconds:
        probe = model(**batch)
        R1.require(torch.isfinite(probe.loss).item(), "nonfinite_qualification_loss")
        probe.loss.backward()
        R1.require(
            all(
                parameter.grad is None or torch.isfinite(parameter.grad).all().item()
                for parameter in model.parameters()
                if parameter.requires_grad
            ),
            "nonfinite_qualification_gradient",
        )
        losses.append(format(probe.loss.detach().float().item(), ".12g"))
        iterations += 1
        model.zero_grad(set_to_none=True)
    duration = time.monotonic() - started
    after = adapter_digest(model)
    R1.require(before == after, "qualification_updated_adapter")
    R1.exclusive_json(output / "qualification.json", {
        "schema": "caplab.training.host-qualification/v1",
        "experiment_id": experiment["experiment_id"],
        "duration_seconds": format(duration, ".6f"),
        "iterations": iterations,
        "losses": losses,
        "adapter_sha256_before": before,
        "adapter_sha256_after": after,
        "peak_gpu_allocated_mib": torch.cuda.max_memory_allocated() // (1024 * 1024),
        "optimizer_steps": 0,
    })
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("qualify", "train"), required=True)
    parser.add_argument("--experiment", type=Path, required=True)
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument("--model-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    R1.load_contract = load_contract
    try:
        return qualify(args) if args.mode == "qualify" else R1.run(args)
    except Exception as error:
        print(f"caplab_qwen27b_qlora_r2: {type(error).__name__}: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
