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
    MODEL_METADATA,
    _render_dockerfile,
    _stage_model_context,
)
from jobs.qwen35b_moe.cuda_runtime import (  # noqa: E402
    validate_cuda_observations,
    validate_cuda_runtime_receipt,
)
from jobs.qwen35b_moe.export import (  # noqa: E402
    LLAMA_CPP_COMMIT,
    direct_export,
    inspect_peft_adapter,
)
from jobs.qwen35b_moe.evaluate import (  # noqa: E402
    _read_examples,
    derive_checkpoint_25_dispatch_ids,
    verify_longest_evaluation_receipt,
)
from jobs.qwen35b_moe.materialize import _render_job  # noqa: E402
from jobs.qwen35b_moe.peft_config import (  # noqa: E402
    LINEAR_TARGET_PATTERN,
    ROUTED_TARGET_PARAMETERS,
    lora_config,
)
from jobs.qwen35b_moe.package import (  # noqa: E402
    EXPECTED_CHECKPOINT_STEPS,
    build_manifest,
    validate_export_receipt,
)
from jobs.qwen35b_moe.preflight import (  # noqa: E402
    PACKAGES,
    verify_liger_fused_loss_receipt,
    verify_longest_example_receipt,
)
from jobs.qwen35b_moe import preflight as preflight_module  # noqa: E402
from jobs.qwen35b_moe.train import (  # noqa: E402
    ACK_NAMESPACE,
    ACK_PROTOCOL,
    _checkpoint_manifest,
    require_checkpoint_acknowledgement,
    require_no_full_logits,
    select_longest_tokenized_index,
    should_force_final_checkpoint,
    validate_liger_fused_loss_proof,
    verify_checkpoint_manifest,
)
from jobs.qwen35b_moe import train_phase  # noqa: E402
from jobs.qwen35b_moe.train_phase import (  # noqa: E402
    PaidLimits,
    assess_available_gates,
    optimizer_steps_per_epoch,
    project_paid_run,
    require_available_gate_improvement,
)
from jobs.qwen35b_moe.update_image_digest import update  # noqa: E402


JOB = ROOT / "jobs" / "qwen35b_moe"


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
            "name": "NVIDIA H100 80GB HBM3",
            "memory_mib": 81_559,
        },
    }


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
        "available_gates": {
            "json_valid": True,
            "verdict_legal": True,
            "side_match": True,
        },
    }


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
            "protocol": "striatum-llama-export/1",
            "mode": "direct-peft-adapter",
            "source_adapter": inspect_peft_adapter(adapter),
            "adapter_gguf": str(gguf.resolve()),
            "adapter_sha256": sha256_file(gguf),
            "base_gguf": "/opt/models/base.gguf",
            "base_gguf_sha256": "b" * 64,
            "llama_cpp_commit": LLAMA_CPP_COMMIT,
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


def test_baked_base_gguf_receipts_bind_source_and_native_splits(
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
    rendered = _render_dockerfile(JOB, artifacts)
    assert rendered.count("COPY --from=model-snapshot /base-bf16-") == 2
    assert "__BASE_GGUF_SHARD_COPIES__" not in rendered
    for name in MODEL_METADATA:
        (tmp_path / name).touch(exist_ok=True)
    for index in range(1, 27):
        (tmp_path / f"model-{index:05d}-of-00026.safetensors").touch()
    staged = tmp_path / "staged"
    _stage_model_context(
        tmp_path,
        staged,
        artifacts,
        expected_license_sha256=hashlib.sha256(b"").hexdigest(),
        expected_model_card_sha256=hashlib.sha256(b"").hexdigest(),
    )
    assert not (staged / "base-bf16.gguf").exists()
    assert (staged / shards[0].name).stat().st_ino == shards[0].stat().st_ino

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


def test_forced_checkpoint_is_exact_and_validated() -> None:
    assert should_force_final_checkpoint(159, 159, True) is True
    assert should_force_final_checkpoint(318, 318, True) is True
    assert should_force_final_checkpoint(158, 159, True) is False
    assert should_force_final_checkpoint(159, 159, False) is False
    with pytest.raises(ContractError, match="positive max steps"):
        should_force_final_checkpoint(0, -1, True)
    with pytest.raises(ContractError, match="non-negative"):
        should_force_final_checkpoint(-1, 159, True)


def test_preflight_selects_and_receipts_the_largest_tokenized_example(
    tmp_path: Path,
) -> None:
    assert (
        select_longest_tokenized_index([100, 40_960, 50_000, 60_000, 60_000], 40_960)
        == 3
    )
    selection = {
        "mode": "longest-tokenized-authorized",
        "candidates": 1_268,
        "selected_global_index": 3,
        "dispatch_id": "dispatch-worst-case",
        "raw_token_count": 60_000,
        "effective_token_count": 40_960,
        "max_raw_token_count": 60_000,
        "max_effective_token_count": 40_960,
        "token_length_census_sha256": "a" * 64,
        "cutoff": 40_960,
        "tie_break": "effective-length,raw-length,earliest-global-index",
    }
    result = tmp_path / "training-result.json"
    result.write_text(
        json.dumps(
            {
                "protocol": "striatum-training-result/1",
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
                "protocol": "striatum-training-result/1",
                "global_step": 1,
                "example_selection": selection,
            }
        )
    )
    with pytest.raises(ContractError, match="token counts are inconsistent"):
        verify_longest_example_receipt(result)


def test_preflight_reload_eval_selects_and_receipts_longest_prompt(
    tmp_path: Path,
) -> None:
    class Tokenizer:
        def apply_chat_template(self, messages, **kwargs):  # noqa: ANN001, ANN003
            del kwargs
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
                "protocol": "striatum-training-result/1",
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

    assert full["limits"] == {
        "max_elapsed_seconds": 54_000,
        "max_cost_usd": "47.00",
        "usd_per_hour": "3.15",
    }
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
        "max_elapsed_seconds": 600,
        "max_cost_usd": "2.00",
        "usd_per_hour": "3.15",
    }
    assert preflight["phases"]["preflight"]["enabled"] is True
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
    assert (
        preflight["limits"]["max_elapsed_seconds"] - enabled_preflight_seconds
        >= 30
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
        "causal_conv1d",
        "bitsandbytes",
        "tilelang",
        "tvm_ffi",
        "liger_kernel.transformers.model.qwen3_5_moe",
    ):
        assert module in dockerfile
    assert (
        0.50
        + float(preflight["limits"]["max_cost_usd"])
        + float(full["limits"]["max_cost_usd"])
        == 49.50
    )


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


def test_tilelang_pins_its_bundled_tvm_ffi_compatibility_release() -> None:
    requirements = dict(
        line.split("==", maxsplit=1)
        for line in (JOB / "requirements.txt").read_text().splitlines()
    )

    assert requirements["tilelang"] == "0.1.8"
    assert requirements["apache-tvm-ffi"] == "0.1.11"

    dockerfile = (JOB / "Dockerfile").read_text()
    assert "'tilelang'" in dockerfile
    assert "'tvm_ffi'" in dockerfile


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

    update(bundle, "a" * 64)

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


def test_preflight_packaging_requires_preflight_smoke_evidence(tmp_path: Path) -> None:
    root = tmp_path / "artifacts/preflight"
    _write_json(root / "preflight.json", {})
    with pytest.raises(ContractError, match="paid preflight"):
        build_manifest(tmp_path, preflight_only=True)

    training_selection = {
        "mode": "longest-tokenized-authorized",
        "candidates": 1_268,
        "selected_global_index": 3,
        "dispatch_id": "dispatch-train-longest",
        "raw_token_count": 60_000,
        "effective_token_count": 40_960,
        "max_raw_token_count": 60_000,
        "max_effective_token_count": 40_960,
        "token_length_census_sha256": "a" * 64,
        "cutoff": 40_960,
        "tie_break": "effective-length,raw-length,earliest-global-index",
    }
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
            "protocol": "striatum-paid-preflight/2",
            "strategy": "linear-only",
            "measurement": expected_adapter_measurement(LINEAR_ONLY).to_dict(),
            "versions": {package: "test-version" for package in PACKAGES},
            "smoke": "passed",
            "longest_training_example": training_selection,
            "quantized_longest_evaluation_example": evaluation_selection,
            "bf16_longest_evaluation_example": evaluation_selection,
            "liger_fused_loss": _liger_proof(),
        },
    )
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
            "protocol": "striatum-training-result/1",
            "global_step": 1,
            "example_selection": training_selection,
            "liger_fused_loss": _liger_proof(),
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

    manifest = build_manifest(tmp_path, preflight_only=True)
    assert manifest["result"] == "preflight-succeeded"
    assert manifest["model_acceptance_requires_local_fate_scoring"] is False
    assert any(
        file["path"] == "artifacts/preflight/one-step-adapter-f32.gguf"
        and file["sha256"] == sha256_file(gguf)
        for file in manifest["files"]
    )

    cuda_receipt = tmp_path / "artifacts/runtime/cuda-runtime.json"
    cuda_receipt.unlink()
    with pytest.raises(ContractError, match="CUDA runtime receipt"):
        build_manifest(tmp_path, preflight_only=True)
    _write_json(cuda_receipt, _cuda_runtime_receipt())

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
    _write_json(tmp_path / "eval/checkpoint-25-mini/summary.json", mini)
    _write_json(tmp_path / "eval/epoch-one-full/summary.json", epoch)
    _write_json(tmp_path / "eval/full/summary.json", epoch)
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
        stages.append(item)
    _write_json(
        receipt_path,
        {
            "protocol": "striatum-paid-training-phase/1",
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
        max_cost_usd=Decimal("47.00"),
        usd_per_hour=Decimal("3.15"),
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
                    "max_cost_usd": "47.00",
                    "usd_per_hour": "3.15",
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
                        "protocol": "striatum-training-result/1",
                        "strategy": "linear-only",
                        "global_step": step,
                        "resumed_from": resumed_from,
                        "metrics": {"train_runtime": runtime},
                        "liger_fused_loss": _liger_proof(step * 8),
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
    assert "job-spec/1" in job_yaml
    assert "verify -> preflight -> train -> evaluate -> package" in job_yaml
    assert "sha256:REPLACE_WITH_IMAGE_DIGEST" in job_yaml
    assert "encrypted: true" in job_yaml
    assert "NVIDIA H100 80GB HBM3" in job_yaml
    assert "container_disk_gb: 220" in job_yaml
    assert "required_gb: 120" in job_yaml
    assert 'usd_per_hour: "3.15"' in job_yaml
    assert dockerfile.count("COPY --from=model-snapshot /model-") == 26
    assert "/opt/models/Qwen3.6-35B-A3B-995ad96e" in dockerfile
    assert "STRIATUM_MODEL_DIR=/opt/models/Qwen3.6-35B-A3B-995ad96e" in dockerfile
    assert "STRIATUM_BASE_GGUF=" in dockerfile
    assert "-DCMAKE_CUDA_ARCHITECTURES=90" in dockerfile
    assert (
        "RUNPOD_JOBRUNNER_RELEASE_PATH=/opt/runpod-jobrunner/release.json" in dockerfile
    )
    assert "/LICENSE /README.md /config.json" in dockerfile
    assert (
        "50cbab8a892c5f2993b8c7351a99182507472def3b1374558308605d99b86b32" in dockerfile
    )
    assert (
        "c4ddaa065649ff6352648f64747a16eda31726f3e34add94ce04abb461c77b75" in dockerfile
    )
    assert "__BASE_GGUF_SHARD_COPIES__" in dockerfile
    assert '"--model-snapshot"' in image_builder
    assert "validate_base_gguf_artifacts" in image_builder
    assert '"--provenance=mode=max"' in image_builder
    assert '"--sbom=true"' in image_builder


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


def test_cuda_runtime_requires_real_h100_driver_resolution() -> None:
    ldd_output = """
        libcuda.so.1 => /usr/local/nvidia/lib64/libcuda.so.1 (0x00007f00)
    """
    devices_output = """
        Available devices:
          CUDA0: NVIDIA H100 80GB HBM3 (81559 MiB, 80500 MiB free)
    """

    receipt = validate_cuda_observations(ldd_output, devices_output)
    assert receipt == _cuda_runtime_receipt()
    assert validate_cuda_runtime_receipt(receipt) == receipt

    with pytest.raises(ContractError, match="stub"):
        validate_cuda_observations(
            ldd_output.replace("/usr/local/nvidia/lib64", "/usr/local/cuda/lib64/stubs"),
            devices_output,
        )
    with pytest.raises(ContractError, match="H100"):
        validate_cuda_observations(
            ldd_output,
            devices_output.replace("NVIDIA H100 80GB HBM3", "NVIDIA A100-SXM4-80GB"),
        )
