"""Direct Transformers + PEFT QLoRA training entrypoint."""

from __future__ import annotations

import argparse
import base64
from collections.abc import Callable, Mapping
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import tempfile
import time
from typing import Any, Sequence

from .contract import (
    STRATEGIES,
    ContractError,
    expected_adapter_measurement,
    load_input_manifest,
    sha256_file,
    validate_adapter_measurement,
    verify_input_tree,
)


from .peft_config import (
    LINEAR_TARGET_PATTERN,
    adapter_evidence,
    bind_adapter_source,
    lora_config,
    measure_adapter,
    prepare_base_for_lora_training,
)
from .data import (
    MultimodalSFTCollator,
    _truncate_sft_tokens as _shared_truncate_sft_tokens,
)
from .profile import (
    load_training_profile,
    matched_lora_modules,
    resolve_multimodal_paths,
)
from .hopper_backend import (
    bind_required_hopper_backend,
    validate_hopper_backend_evidence,
)
from .runtime import (
    input_dir_from_env,
    load_quantized_base,
    model_dir_from_env,
    output_dir_from_env,
    training_config,
)


ACK_PROTOCOL = "incremental-mirror-ack/1"
ACK_NAMESPACE = "runpod-jobrunner-incremental-mirror"
LIGER_PROOF_PROTOCOL = "striatum-liger-fused-loss-proof/1"
TOKENIZATION_CENSUS_PROTOCOL = "striatum-sft-tokenization-census/1"
_SHA256_LENGTH = 64
LIGER_KERNEL_CONFIG = {
    "cross_entropy": False,
    "fused_linear_cross_entropy": True,
    # Liger 0.8.1's fused MoE Triton kernel requires its activation and frozen
    # expert weights to share a dtype. This QLoRA path intentionally has FP32
    # activations and BF16 expert weights, so retain Transformers' native
    # mixed-dtype-aware grouped expert path and Liger's fused no-logits loss.
    "swiglu": False,
}


class _AcknowledgementNotReady(ContractError):
    """A published acknowledgement path does not yet contain complete JSON."""


def _production_adapter_evidence(
    measured: Any,
    matched_modules: Sequence[str],
    *,
    total_parameters: int,
) -> dict[str, Any]:
    """Complete the strict MoE measurement with its exact module census."""

    measurement = dict(measured.to_dict())
    measurement["matched_modules"] = list(matched_modules)
    measurement["matched_module_count"] = len(matched_modules)
    measurement["total_parameters"] = total_parameters
    return measurement


def require_no_full_logits(outputs: object) -> None:
    """Fail unless one real training forward returned fused loss without logits."""

    if not hasattr(outputs, "loss") or getattr(outputs, "loss") is None:
        raise ContractError("Liger training forward returned no loss")
    if not hasattr(outputs, "logits"):
        raise ContractError("Liger training output does not expose logits state")
    if getattr(outputs, "logits") is not None:
        raise ContractError("Liger training forward materialized logits")


def validate_liger_fused_loss_proof(value: object) -> dict[str, Any]:
    """Validate the exact runtime proof emitted by every training process."""

    if not isinstance(value, Mapping):
        raise ContractError("Liger fused-loss proof is invalid")
    proof = dict(value)
    expected_fields = {
        "protocol",
        "model_type",
        "implementation_module",
        "implementation_name",
        "bound_forward_identity_verified",
        "fused_linear_cross_entropy",
        "training_logits",
        "no_full_logits_observed",
        "observed_forward_calls",
    }
    calls = proof.get("observed_forward_calls")
    if (
        set(proof) != expected_fields
        or proof.get("protocol") != LIGER_PROOF_PROTOCOL
        or proof.get("model_type") != "qwen3_5_moe"
        or proof.get("implementation_module")
        != "liger_kernel.transformers.model.qwen3_5_moe"
        or proof.get("implementation_name")
        != "lce_forward_conditional_generation"
        or proof.get("bound_forward_identity_verified") is not True
        or proof.get("fused_linear_cross_entropy") is not True
        or proof.get("training_logits") != "not-materialized"
        or proof.get("no_full_logits_observed") is not True
        or isinstance(calls, bool)
        or not isinstance(calls, int)
        or calls <= 0
    ):
        raise ContractError("Liger fused-loss proof is invalid")
    return proof


def _require_liger_fused_loss_binding(model: object) -> dict[str, Any]:
    """Prove Transformers bound the pinned Qwen MoE fused-loss forward."""

    try:
        from liger_kernel.transformers.model.qwen3_5_moe import (
            lce_forward_conditional_generation,
        )
        from transformers.trainer_utils import unwrap_peft_model
    except ImportError as error:
        raise ContractError("the pinned Liger integration is unavailable") from error
    base_model = unwrap_peft_model(model)
    model_type = getattr(getattr(base_model, "config", None), "model_type", None)
    actual_forward = getattr(getattr(base_model, "forward", None), "__func__", None)
    if (
        model_type != "qwen3_5_moe"
        or actual_forward is not lce_forward_conditional_generation
    ):
        raise ContractError(
            "Transformers did not bind Qwen3.5-MoE Liger fused linear cross entropy"
        )
    return {
        "protocol": LIGER_PROOF_PROTOCOL,
        "model_type": model_type,
        "implementation_module": lce_forward_conditional_generation.__module__,
        "implementation_name": lce_forward_conditional_generation.__name__,
        "bound_forward_identity_verified": True,
        "fused_linear_cross_entropy": True,
        "training_logits": "not-materialized",
        "no_full_logits_observed": False,
        "observed_forward_calls": 0,
    }


def _require_liger_binding_before_forward(proof: Mapping[str, object]) -> None:
    """Fail unless the train-begin callback verified the exact Liger binding."""

    expected_binding = {
        "protocol": LIGER_PROOF_PROTOCOL,
        "model_type": "qwen3_5_moe",
        "implementation_module": "liger_kernel.transformers.model.qwen3_5_moe",
        "implementation_name": "lce_forward_conditional_generation",
        "bound_forward_identity_verified": True,
        "fused_linear_cross_entropy": True,
        "training_logits": "not-materialized",
    }
    calls = proof.get("observed_forward_calls")
    logits_observed = proof.get("no_full_logits_observed")
    if (
        set(proof) != {*expected_binding, "no_full_logits_observed", "observed_forward_calls"}
        or any(proof.get(key) != value for key, value in expected_binding.items())
        or isinstance(calls, bool)
        or not isinstance(calls, int)
        or calls < 0
        or (calls == 0 and logits_observed is not False)
        or (calls > 0 and logits_observed is not True)
    ):
        raise ContractError(
            "Liger binding was not verified before the first training forward"
        )


def _make_liger_binding_callback(
    callback_base: type[Any],
    proof: dict[str, Any],
    *,
    on_verified: Callable[[], None] | None = None,
) -> Any:
    """Build a callback that checks Liger after Trainer applies its patch."""

    class LigerBindingCallback(callback_base):
        def on_train_begin(self, args, state, control, **kwargs):  # noqa: ANN001
            model = kwargs.get("model")
            if model is None:
                raise ContractError("Trainer did not expose its model at train begin")
            if proof:
                raise ContractError("Liger binding was verified more than once")
            proof.update(_require_liger_fused_loss_binding(model))
            _require_liger_binding_before_forward(proof)
            if on_verified is not None:
                on_verified()
            return control

    return LigerBindingCallback()


def _atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, raw_temp = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temp = Path(raw_temp)
    try:
        with os.fdopen(descriptor, "w") as handle:
            json.dump(value, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, path)
        directory_descriptor = os.open(
            path.parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
        )
        try:
            os.fsync(directory_descriptor)
        finally:
            os.close(directory_descriptor)
    except BaseException:
        temp.unlink(missing_ok=True)
        raise


def _checkpoint_manifest(checkpoint: Path) -> dict[str, Any]:
    files = []
    for path in sorted(checkpoint.rglob("*")):
        if path.name == "checkpoint-complete.json":
            continue
        if path.is_symlink():
            raise ContractError(f"checkpoint symlink is forbidden: {path}")
        if path.is_file():
            files.append(
                {
                    "path": path.relative_to(checkpoint).as_posix(),
                    "size": path.stat().st_size,
                    "sha256": sha256_file(path),
                }
            )
    return {
        "protocol": "striatum-checkpoint-completion/1",
        "checkpoint": checkpoint.name,
        "files": files,
    }


def verify_checkpoint_manifest(checkpoint: Path) -> dict[str, Any]:
    manifest_path = checkpoint / "checkpoint-complete.json"
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise ContractError(
            f"checkpoint has no regular completion manifest: {checkpoint}"
        )
    try:
        recorded = json.loads(manifest_path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise ContractError(
            f"checkpoint manifest is unreadable: {checkpoint}"
        ) from error
    measured = _checkpoint_manifest(checkpoint)
    if recorded != measured:
        raise ContractError(
            f"checkpoint manifest does not match its files: {checkpoint}"
        )
    return recorded


def should_force_final_checkpoint(
    global_step: int, max_steps: int, requested: bool
) -> bool:
    """Return whether this exact step needs an otherwise unscheduled save."""

    if not isinstance(requested, bool):
        raise ContractError("save-final-checkpoint request must be boolean")
    if isinstance(max_steps, bool) or not isinstance(max_steps, int) or max_steps <= 0:
        raise ContractError("forced final checkpoint requires positive max steps")
    if (
        isinstance(global_step, bool)
        or not isinstance(global_step, int)
        or global_step < 0
    ):
        raise ContractError("global step must be a non-negative integer")
    return requested and global_step == max_steps


def synchronize_trainer_save_interval(
    training_args: Any, state: Any
) -> dict[str, object]:
    """Make the current invocation authoritative after Trainer state restore.

    Transformers restores ``save_steps`` from ``trainer_state.json`` after it
    computes the current TrainingArguments schedule.  A staged run therefore
    otherwise inherits the previous stage's interval despite receiving a new
    explicit ``--save-steps`` value.
    """

    requested = getattr(training_args, "save_steps", None)
    previous = getattr(state, "save_steps", None)
    for value, label in ((requested, "requested"), (previous, "restored")):
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ContractError(
                f"{label} checkpoint save interval must be a positive integer"
            )
    state.save_steps = requested
    return {
        "checkpoint_save_steps_before": previous,
        "checkpoint_save_steps_requested": requested,
        "checkpoint_save_steps_changed": previous != requested,
    }


def require_checkpoint_acknowledgement(
    checkpoint: Path,
    *,
    wait: bool,
    request_path: Path | None = None,
    run_root: Path | None = None,
    storage_mount: Path | None = None,
    sleep: Callable[[float], None] = time.sleep,
    monotonic: Callable[[], float] = time.monotonic,
) -> dict[str, Any] | None:
    """Verify the controller-signed durable-mirror acknowledgement for a checkpoint.

    Jobs without the opt-in request field retain the passive v1 mirroring behavior.
    A configured job fails closed on invalid acknowledgement data.  Save callbacks
    wait for publication; resume checks are immediate so an expensive model load can
    never begin from an unacknowledged checkpoint.
    """

    request_path = request_path or _path_from_environment(
        "RUNPOD_JOBRUNNER_REQUEST_PATH"
    )
    if request_path is None:
        return None
    request = _read_json_object(request_path, "runner request")
    raw_config = request.get("incremental_mirror_ack")
    if raw_config is None:
        return None
    config = _object(raw_config, "incremental mirror acknowledgement configuration")
    _validate_ack_config(config, request)

    run_root = run_root or _required_environment_path("RUNPOD_JOBRUNNER_RUN_ROOT")
    storage_mount = storage_mount or _required_environment_path(
        "RUNPOD_JOBRUNNER_STORAGE_MOUNT"
    )
    manifest_path = checkpoint / "checkpoint-complete.json"
    manifest = verify_checkpoint_manifest(checkpoint)
    manifest_relative = _relative_regular_file(manifest_path, storage_mount)
    ack_directory = _safe_relative_path(config["directory"], "ack directory")
    ack_root = _contained_directory(run_root, ack_directory)
    ack_name = f"{hashlib.sha256(manifest_relative.encode()).hexdigest()}.json"
    ack_path = ack_root / ack_name
    expected = _ack_expectation(request, manifest, manifest_path, manifest_relative)
    timeout = _positive_number(config["timeout_seconds"], "ack timeout")
    deadline = monotonic() + timeout

    while True:
        if ack_path.is_symlink():
            raise ContractError("checkpoint acknowledgement cannot be a symlink")
        if ack_path.is_file():
            try:
                return _verify_checkpoint_ack(ack_path, expected, config)
            except _AcknowledgementNotReady:
                if not wait:
                    raise
        if not wait:
            raise ContractError(
                f"resume checkpoint is not durably acknowledged: {checkpoint}"
            )
        remaining = deadline - monotonic()
        if remaining <= 0:
            raise ContractError(
                f"checkpoint acknowledgement timed out after {timeout:g}s: {checkpoint}"
            )
        sleep(min(0.5, remaining))


def _ack_expectation(
    request: Mapping[str, object],
    manifest: Mapping[str, object],
    manifest_path: Path,
    manifest_relative: str,
) -> dict[str, object]:
    files = manifest.get("files")
    if not isinstance(files, list):
        raise ContractError("checkpoint manifest files are invalid")
    file_bytes = 0
    for index, raw_entry in enumerate(files):
        entry = _object(raw_entry, f"checkpoint manifest file {index}")
        size = entry.get("size")
        if isinstance(size, bool) or not isinstance(size, int) or size < 0:
            raise ContractError("checkpoint manifest file size is invalid")
        file_bytes += size
    return {
        "protocol": ACK_PROTOCOL,
        "run_id": _required_string(request, "run_id"),
        "bundle_hash": _required_sha256(request, "bundle_hash"),
        "image_digest": _required_string(request, "image_digest"),
        "manifest_path": manifest_relative,
        "manifest_size": manifest_path.stat().st_size,
        "manifest_sha256": sha256_file(manifest_path),
        "file_count": len(files),
        "file_bytes": file_bytes,
    }


def _verify_checkpoint_ack(
    path: Path,
    expected: Mapping[str, object],
    config: Mapping[str, object],
) -> dict[str, Any]:
    try:
        raw: object = json.loads(
            path.read_bytes(), object_pairs_hook=_object_without_duplicates
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise _AcknowledgementNotReady(
            "checkpoint acknowledgement is unreadable"
        ) from error
    record = _object(raw, "checkpoint acknowledgement")
    required_fields = {
        *expected,
        "local_receipt_sha256",
        "signer",
        "signature",
    }
    if set(record) != required_fields:
        raise ContractError("checkpoint acknowledgement fields are not exact")
    for key, value in expected.items():
        if record.get(key) != value:
            raise ContractError(f"checkpoint acknowledgement {key} binding mismatch")
    local_receipt = record.get("local_receipt_sha256")
    if not _is_sha256(local_receipt):
        raise ContractError("checkpoint acknowledgement receipt hash is invalid")
    signer = _object(config.get("signer"), "acknowledgement signer")
    if record.get("signer") != signer:
        raise ContractError("checkpoint acknowledgement signer binding mismatch")
    public_key, identity = _validate_signer(signer, expected["run_id"])
    signature_value = record.pop("signature")
    if not isinstance(signature_value, str):
        raise ContractError("checkpoint acknowledgement signature is absent")
    try:
        signature = base64.b64decode(signature_value, validate=True)
    except ValueError as error:
        raise ContractError(
            "checkpoint acknowledgement signature is invalid"
        ) from error

    unsigned = _canonical_json(record)
    with tempfile.TemporaryDirectory(prefix="striatum-ack-verify-") as raw_directory:
        directory = Path(raw_directory)
        allowed_signers = directory / "allowed_signers"
        signature_path = directory / "signature"
        allowed_signers.write_text(f"{identity} {public_key}\n", encoding="ascii")
        signature_path.write_bytes(signature)
        try:
            result = subprocess.run(
                [
                    "ssh-keygen",
                    "-Y",
                    "verify",
                    "-f",
                    str(allowed_signers),
                    "-I",
                    identity,
                    "-n",
                    ACK_NAMESPACE,
                    "-s",
                    str(signature_path),
                ],
                input=unsigned,
                check=False,
                capture_output=True,
            )
        except OSError as error:
            raise ContractError(
                "ssh-keygen is required to verify checkpoint acknowledgements"
            ) from error
    if result.returncode != 0:
        raise ContractError("checkpoint acknowledgement signature verification failed")
    return record


def _validate_ack_config(
    config: Mapping[str, object], request: Mapping[str, object]
) -> None:
    if set(config) != {"protocol", "directory", "timeout_seconds", "signer"}:
        raise ContractError(
            "incremental mirror acknowledgement configuration is not exact"
        )
    if config.get("protocol") != ACK_PROTOCOL:
        raise ContractError(
            "incremental mirror acknowledgement protocol is unsupported"
        )
    _safe_relative_path(config.get("directory"), "ack directory")
    _positive_number(config.get("timeout_seconds"), "ack timeout")
    supported = _object(
        request.get("supported_protocol_majors"), "supported protocol majors"
    )
    if supported.get("incremental-mirror-ack") != [1]:
        raise ContractError(
            "runner request does not pin incremental-mirror-ack major 1"
        )
    signer = _object(config.get("signer"), "acknowledgement signer")
    _validate_signer(signer, _required_string(request, "run_id"))


def _validate_signer(
    signer: Mapping[str, object], expected_run_id: object
) -> tuple[str, str]:
    if set(signer) != {
        "algorithm",
        "identity",
        "key_id",
        "namespace",
        "public_key",
    }:
        raise ContractError("acknowledgement signer fields are not exact")
    if signer.get("algorithm") != "ssh-ed25519":
        raise ContractError("acknowledgement signer algorithm is unsupported")
    if signer.get("namespace") != ACK_NAMESPACE:
        raise ContractError("acknowledgement signer namespace is unsupported")
    identity = signer.get("identity")
    if identity != f"runpod-jobrunner:{expected_run_id}":
        raise ContractError("acknowledgement signer identity is not run-bound")
    public_value = signer.get("public_key")
    if not isinstance(public_value, str):
        raise ContractError("acknowledgement public key is invalid")
    fields = public_value.strip().split()
    if len(fields) != 2 or fields[0] != "ssh-ed25519":
        raise ContractError("acknowledgement public key must be Ed25519")
    try:
        key_blob = base64.b64decode(fields[1], validate=True)
    except ValueError as error:
        raise ContractError("acknowledgement public key is malformed") from error
    public_key = f"ssh-ed25519 {fields[1]}"
    key_id = "SHA256:" + base64.b64encode(hashlib.sha256(key_blob).digest()).decode(
        "ascii"
    ).rstrip("=")
    if signer.get("key_id") != key_id:
        raise ContractError("acknowledgement signer key ID mismatch")
    return public_key, str(identity)


def _read_json_object(path: Path, label: str) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise ContractError(f"{label} is not a regular file")
    try:
        value: object = json.loads(
            path.read_bytes(), object_pairs_hook=_object_without_duplicates
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ContractError(f"{label} is unreadable") from error
    return _object(value, label)


def _object(value: object, label: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ContractError(f"{label} must be an object")
    return dict(value)


def _object_without_duplicates(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ContractError(f"JSON object contains duplicate key {key!r}")
        result[key] = value
    return result


def _canonical_json(value: Mapping[str, object]) -> bytes:
    try:
        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as error:
        raise ContractError(
            "checkpoint acknowledgement is not canonicalizable"
        ) from error


def _relative_regular_file(path: Path, root: Path) -> str:
    if path.is_symlink() or not path.is_file():
        raise ContractError(f"checkpoint manifest is not a regular file: {path}")
    try:
        relative = path.resolve().relative_to(root.resolve())
    except ValueError as error:
        raise ContractError(
            "checkpoint manifest is outside the storage mount"
        ) from error
    return relative.as_posix()


def _safe_relative_path(value: object, label: str) -> Path:
    if not isinstance(value, str) or not value or "\\" in value:
        raise ContractError(f"{label} is invalid")
    path = Path(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise ContractError(f"{label} is unsafe")
    if any(ord(character) < 32 or ord(character) == 127 for character in value):
        raise ContractError(f"{label} contains control characters")
    return path


def _contained_directory(root: Path, relative: Path) -> Path:
    candidate = root.joinpath(*relative.parts)
    try:
        candidate.resolve(strict=False).relative_to(root.resolve())
    except ValueError as error:
        raise ContractError("acknowledgement directory escapes the run root") from error
    return candidate


def _required_environment_path(name: str) -> Path:
    value = _path_from_environment(name)
    if value is None:
        raise ContractError(f"{name} is required for checkpoint acknowledgement")
    return value


def _path_from_environment(name: str) -> Path | None:
    raw = os.environ.get(name)
    return Path(raw) if raw else None


def _required_string(value: Mapping[str, object], key: str) -> str:
    item = value.get(key)
    if not isinstance(item, str) or not item:
        raise ContractError(f"runner request {key} is invalid")
    return item


def _required_sha256(value: Mapping[str, object], key: str) -> str:
    item = value.get(key)
    if not _is_sha256(item):
        raise ContractError(f"runner request {key} is invalid")
    return str(item)


def _is_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == _SHA256_LENGTH
        and all(character in "0123456789abcdef" for character in value)
    )


def _positive_number(value: object, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
        raise ContractError(f"{label} must be positive")
    return float(value)


def select_longest_tokenized_index(lengths: Sequence[int], cutoff: int) -> int:
    """Select maximum effective length, then raw length, then earliest index."""
    if isinstance(cutoff, bool) or cutoff <= 0:
        raise ContractError("token cutoff must be positive")
    if not lengths:
        raise ContractError("cannot select from an empty token-length census")
    for length in lengths:
        if isinstance(length, bool) or not isinstance(length, int) or length <= 0:
            raise ContractError("token-length census must contain positive integers")
    return max(
        range(len(lengths)),
        key=lambda index: (min(lengths[index], cutoff), lengths[index], -index),
    )


def _chat_template_token_ids(
    processor: Any,
    messages: Sequence[Mapping[str, Any]],
    *,
    add_generation_prompt: bool,
) -> list[int]:
    """Require the plain token-list surface from the pinned tokenizer API."""
    token_ids = processor.apply_chat_template(
        messages,
        tokenize=True,
        add_generation_prompt=add_generation_prompt,
        enable_thinking=False,
        return_dict=False,
    )
    if hasattr(token_ids, "tolist"):
        token_ids = token_ids.tolist()
    if (
        isinstance(token_ids, list)
        and len(token_ids) == 1
        and isinstance(token_ids[0], list)
    ):
        token_ids = token_ids[0]
    if (
        not isinstance(token_ids, list)
        or not token_ids
        or any(
            isinstance(token_id, bool)
            or not isinstance(token_id, int)
            or token_id < 0
            for token_id in token_ids
        )
    ):
        raise ContractError("chat template did not return a plain token-ID list")
    return token_ids


def _truncate_sft_tokens(
    full_ids: Sequence[int],
    prompt_ids: Sequence[int],
    *,
    cutoff: int,
) -> dict[str, list[int]]:
    """Fit one SFT row while preserving supervised assistant tokens."""
    return _shared_truncate_sft_tokens(full_ids, prompt_ids, cutoff=cutoff)


def _length_census_sha256(lengths: Sequence[int]) -> str:
    return hashlib.sha256(
        json.dumps(list(lengths), separators=(",", ":")).encode()
    ).hexdigest()


def _build_sft_tokenization_census(
    full_lengths: Sequence[int],
    prompt_lengths: Sequence[int],
    *,
    cutoff: int,
) -> dict[str, object]:
    if len(full_lengths) != len(prompt_lengths) or not full_lengths:
        raise ContractError("SFT tokenization census lengths are inconsistent")
    if isinstance(cutoff, bool) or not isinstance(cutoff, int) or cutoff <= 0:
        raise ContractError("token cutoff must be positive")
    assistant_lengths = []
    for full, prompt in zip(full_lengths, prompt_lengths, strict=True):
        if (
            isinstance(full, bool)
            or not isinstance(full, int)
            or isinstance(prompt, bool)
            or not isinstance(prompt, int)
            or prompt <= 0
            or full <= prompt
        ):
            raise ContractError("SFT tokenization census contains invalid lengths")
        assistant_lengths.append(full - prompt)
    prompt_tail_salvaged = sum(
        prompt >= cutoff and assistant < cutoff
        for prompt, assistant in zip(
            prompt_lengths, assistant_lengths, strict=True
        )
    )
    rows_without_labels = sum(
        (prompt >= cutoff and assistant >= cutoff)
        for prompt, assistant in zip(
            prompt_lengths, assistant_lengths, strict=True
        )
    )
    selected_index = select_longest_tokenized_index(full_lengths, cutoff)
    return {
        "protocol": TOKENIZATION_CENSUS_PROTOCOL,
        "policy": "prompt-tail-preserve-assistant-on-prompt-overflow",
        "tokenizer_output": "plain-token-id-list",
        "candidates": len(full_lengths),
        "cutoff": cutoff,
        "full_over_cutoff": sum(length > cutoff for length in full_lengths),
        "prompt_overflow": sum(length >= cutoff for length in prompt_lengths),
        "assistant_over_cutoff": sum(
            length >= cutoff for length in assistant_lengths
        ),
        "prompt_tail_salvaged": prompt_tail_salvaged,
        "prefix_mismatches": 0,
        "rows_without_labels": rows_without_labels,
        "full_length_census_sha256": _length_census_sha256(full_lengths),
        "prompt_length_census_sha256": _length_census_sha256(prompt_lengths),
        "assistant_length_census_sha256": _length_census_sha256(
            assistant_lengths
        ),
        "longest_example": {
            "selected_global_index": selected_index,
            "raw_token_count": full_lengths[selected_index],
            "effective_token_count": min(full_lengths[selected_index], cutoff),
            **_selection_token_observation(
                full_length=full_lengths[selected_index],
                prompt_length=prompt_lengths[selected_index],
                cutoff=cutoff,
            ),
        },
    }


def validate_sft_tokenization_census(value: object) -> dict[str, object]:
    if not isinstance(value, Mapping):
        raise ContractError("SFT tokenization census is invalid")
    observed = dict(value)
    expected = training_config().get("tokenization_contract")
    if not isinstance(expected, dict) or observed != expected:
        raise ContractError("SFT tokenization census does not match pinned contract")
    return observed


def _selection_token_observation(
    *,
    full_length: int,
    prompt_length: int,
    cutoff: int,
) -> dict[str, object]:
    assistant_length = full_length - prompt_length
    if prompt_length >= cutoff:
        if assistant_length >= cutoff:
            raise ContractError(
                "token cutoff cannot preserve assistant tokens after prompt overflow"
            )
        supervised = assistant_length
        mode = "prompt-tail-full-assistant"
    elif full_length > cutoff:
        supervised = cutoff - prompt_length
        mode = "assistant-prefix"
    else:
        supervised = assistant_length
        mode = "none"
    if supervised <= 0:
        raise ContractError("selected SFT example has no supervised tokens")
    return {
        "prompt_token_count": prompt_length,
        "assistant_token_count": assistant_length,
        "supervised_token_count": supervised,
        "truncation_mode": mode,
    }


def _load_datasets(
    input_dir: Path,
    processor: Any,
    cutoff: int,
    limit: int,
    select_longest: bool,
    *,
    manifest_path: Path | None = None,
    expected_examples: int = 1_268,
    strict_production: bool = True,
) -> tuple[Any, dict[str, Any]]:
    try:
        from datasets import concatenate_datasets, load_dataset
    except ImportError as error:
        raise ContractError("datasets is required for training") from error

    manifest = load_input_manifest(
        manifest_path or Path(__file__).with_name("input-manifest.json"),
        strict_production=strict_production,
    )
    train_paths = [
        str(input_dir / item.path) for item in manifest if item.role == "train"
    ]
    datasets = [
        load_dataset("json", data_files=path, split="train") for path in train_paths
    ]
    dataset = concatenate_datasets(datasets)
    if (not limit or select_longest) and len(dataset) != expected_examples:
        raise ContractError(
            f"expected {expected_examples} train examples, found {len(dataset)}"
        )
    raw_lengths: list[int] = []
    prompt_lengths: list[int] = []
    tokenization_census: dict[str, object] | None = None
    if not limit or select_longest:
        for example in dataset:
            messages = example["messages"]
            if (
                len(messages) != 2
                or messages[0].get("role") != "user"
                or messages[1].get("role") != "assistant"
            ):
                raise ContractError(
                    "SFT examples must contain one user and one assistant message"
                )
            processor_messages = resolve_multimodal_paths(messages, input_dir)
            full_ids = _chat_template_token_ids(
                processor,
                processor_messages,
                add_generation_prompt=False,
            )
            prompt_ids = _chat_template_token_ids(
                processor,
                processor_messages[:1],
                add_generation_prompt=True,
            )
            _truncate_sft_tokens(full_ids, prompt_ids, cutoff=cutoff)
            raw_lengths.append(len(full_ids))
            prompt_lengths.append(len(prompt_ids))
        tokenization_census = validate_sft_tokenization_census(
            _build_sft_tokenization_census(
                raw_lengths,
                prompt_lengths,
                cutoff=cutoff,
            )
        )

    selection: dict[str, Any]
    if select_longest:
        if limit != 1:
            raise ContractError("--select-longest requires --limit 1")
        if tokenization_census is None:
            raise ContractError("longest-example tokenization census is absent")
        selected_index = select_longest_tokenized_index(raw_lengths, cutoff)
        selected = dataset[selected_index]
        metadata = selected.get("meta")
        dispatch_id = (
            metadata.get("dispatch_id") if isinstance(metadata, dict) else None
        )
        selection = {
            "mode": "longest-tokenized-authorized",
            "candidates": len(dataset),
            "selected_global_index": selected_index,
            "dispatch_id": dispatch_id,
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
            "tokenization": tokenization_census,
            **_selection_token_observation(
                full_length=raw_lengths[selected_index],
                prompt_length=prompt_lengths[selected_index],
                cutoff=cutoff,
            ),
        }
        dataset = dataset.select([selected_index])
    elif limit:
        dataset = dataset.select(range(min(limit, len(dataset))))
        selection = {"mode": "prefix", "candidates": len(dataset), "limit": limit}
    else:
        if tokenization_census is None:
            raise ContractError("full-run tokenization census is absent")
        selection = {
            "mode": "all-authorized",
            "candidates": len(dataset),
            "tokenization": tokenization_census,
        }

    return dataset, selection


def run(args: argparse.Namespace) -> None:
    save_final_checkpoint = args.save_final_checkpoint
    if save_final_checkpoint and args.max_steps <= 0:
        raise ContractError("--save-final-checkpoint requires positive --max-steps")
    try:
        from peft import get_peft_model
        from transformers import (
            Trainer,
            TrainerCallback,
            TrainingArguments,
            set_seed,
        )
    except ImportError as error:
        raise ContractError(
            "transformers and PEFT are required for training"
        ) from error

    profile = load_training_profile(args.config)
    input_dir = args.input_dir.resolve()
    strict_production = profile.model_type == "qwen3_5_moe"
    entries = load_input_manifest(
        profile.input_manifest, strict_production=profile.strict_input_manifest
    )
    verify_input_tree(input_dir, entries)
    train_kwargs = profile.train
    set_seed(args.seed)

    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    resume_from_checkpoint = None
    resume_acknowledgement = None
    if args.resume_from_checkpoint is not None:
        resume_from_checkpoint = args.resume_from_checkpoint.resolve()
        verify_checkpoint_manifest(resume_from_checkpoint)
        if resume_from_checkpoint.parent != output:
            raise ContractError(
                "resume checkpoint must be inside the selected output directory"
            )
        resume_acknowledgement = require_checkpoint_acknowledgement(
            resume_from_checkpoint,
            wait=False,
        )

    base, processor = load_quantized_base(args.model_dir.resolve(), profile)
    hopper_backend_evidence = bind_required_hopper_backend(base, profile.runtime)
    print(
        json.dumps({"event": "hopper-backend", **hopper_backend_evidence}, sort_keys=True),
        flush=True,
    )
    strategy_config = profile.strategy(args.strategy)
    target_pattern = strategy_config.get("target_pattern", LINEAR_TARGET_PATTERN)
    if not isinstance(target_pattern, str):
        raise ContractError("training profile has no LoRA target pattern")
    matched_modules = matched_lora_modules(base, target_pattern)
    expected_targets = strategy_config.get("expected_target_count", 310)
    if len(matched_modules) != expected_targets:
        raise ContractError(
            f"LoRA target count mismatch: {len(matched_modules)} != {expected_targets}"
        )
    predicted_trainable = strategy_config.get("expected_trainable_parameters")
    if strict_production and predicted_trainable is None:
        predicted_trainable = expected_adapter_measurement(
            args.strategy
        ).trainable_parameters
    if (
        isinstance(predicted_trainable, bool)
        or not isinstance(predicted_trainable, int)
        or predicted_trainable <= 0
    ):
        raise ContractError("profile has no positive expected LoRA trainable count")
    print(
        json.dumps(
            {
                "event": "lora-targets",
                "matched_modules": list(matched_modules),
                "matched_module_count": len(matched_modules),
                "predicted_trainable_parameters": predicted_trainable,
            },
            sort_keys=True,
        ),
        flush=True,
    )
    base_preparation = prepare_base_for_lora_training(base, profile)
    base.config.use_cache = False
    _atomic_json(output / "base-preparation.json", base_preparation)
    model = get_peft_model(base, lora_config(args.strategy, profile))
    bind_adapter_source(model, profile)
    if strict_production:
        measured = measure_adapter(model, args.strategy)
        validate_adapter_measurement(
            measured, expected_adapter_measurement(args.strategy)
        )
        measurement = _production_adapter_evidence(
            measured,
            matched_modules,
            total_parameters=sum(parameter.numel() for parameter in model.parameters()),
        )
    else:
        measurement = adapter_evidence(
            model,
            matched_modules,
            predicted_trainable,
            profile,
            args.strategy,
        )
    print(json.dumps({"event": "adapter", **measurement}, sort_keys=True), flush=True)
    dataset, example_selection = _load_datasets(
        input_dir,
        processor,
        profile.cutoff_length,
        args.limit,
        args.select_longest,
        manifest_path=profile.input_manifest,
        expected_examples=train_kwargs["expected_examples"],
        strict_production=profile.strict_input_manifest,
    )

    acknowledged_checkpoints: list[dict[str, Any]] = []
    checkpoint_schedule: dict[str, object] = {}

    class CompletionCallback(TrainerCallback):
        def on_train_begin(  # noqa: ANN001
            self, training_args, state, control, **kwargs
        ):
            checkpoint_schedule.update(
                synchronize_trainer_save_interval(training_args, state)
            )
            print(
                json.dumps(
                    {"event": "checkpoint-schedule", **checkpoint_schedule},
                    sort_keys=True,
                ),
                flush=True,
            )
            return control

        def on_step_end(  # noqa: ANN001
            self, training_args, state, control, **kwargs
        ):
            if save_final_checkpoint and should_force_final_checkpoint(
                state.global_step, args.max_steps, save_final_checkpoint
            ):
                control.should_save = True
            return control

        def on_save(self, training_args, state, control, **kwargs):  # noqa: ANN001
            checkpoint = (
                Path(training_args.output_dir) / f"checkpoint-{state.global_step}"
            )
            _atomic_json(
                checkpoint / "checkpoint-complete.json",
                _checkpoint_manifest(checkpoint),
            )
            acknowledgement = require_checkpoint_acknowledgement(
                checkpoint,
                wait=True,
            )
            if acknowledgement is not None:
                acknowledged_checkpoints.append(acknowledgement)
            return control

    liger_proof: dict[str, Any] = {}
    gradient_evidence: dict[str, Any] = {
        "optimizer_steps": 0,
        "backward_passes_with_adapter_gradients": 0,
        "nonzero_gradient_parameters": set(),
    }

    class OptimizationEvidenceCallback(TrainerCallback):
        def on_pre_optimizer_step(self, training_args, state, control, **kwargs):  # noqa: ANN001
            import torch

            observed = set()
            model_for_step = kwargs.get("model")
            if model_for_step is None:
                raise ContractError("Trainer did not expose the model before optimizer step")
            for name, parameter in model_for_step.named_parameters():
                if not parameter.requires_grad or parameter.grad is None:
                    continue
                if not torch.isfinite(parameter.grad).all():
                    raise ContractError(f"non-finite adapter gradient: {name}")
                if torch.count_nonzero(parameter.grad).item():
                    observed.add(name)
            if not observed:
                raise ContractError("backward produced no nonzero adapter gradients")
            gradient_evidence["backward_passes_with_adapter_gradients"] += 1
            gradient_evidence["nonzero_gradient_parameters"].update(observed)
            return control

        def on_optimizer_step(self, training_args, state, control, **kwargs):  # noqa: ANN001
            gradient_evidence["optimizer_steps"] += 1
            return control

    class FusedLossTrainer(Trainer):
        def compute_loss(  # noqa: ANN001
            self,
            model,
            inputs,
            return_outputs=False,
            num_items_in_batch=None,
        ):
            if profile.liger_fused_loss:
                _require_liger_binding_before_forward(liger_proof)
            loss, outputs = super().compute_loss(
                model,
                inputs,
                return_outputs=True,
                num_items_in_batch=num_items_in_batch,
            )
            if profile.liger_fused_loss:
                require_no_full_logits(outputs)
                liger_proof["observed_forward_calls"] = (
                    int(liger_proof["observed_forward_calls"]) + 1
                )
                liger_proof["no_full_logits_observed"] = True
            return (loss, outputs) if return_outputs else loss

    collator = MultimodalSFTCollator(
        processor,
        input_root=input_dir,
        cutoff=profile.cutoff_length,
        processing=profile.processing,
    )

    trainer_args = TrainingArguments(
        output_dir=str(output),
        per_device_train_batch_size=train_kwargs["per_device_batch_size"],
        gradient_accumulation_steps=train_kwargs["gradient_accumulation_steps"],
        learning_rate=train_kwargs["learning_rate"],
        num_train_epochs=train_kwargs["epochs"],
        max_steps=args.max_steps,
        lr_scheduler_type=train_kwargs["scheduler"],
        warmup_ratio=train_kwargs["warmup_ratio"],
        bf16=train_kwargs["bf16"],
        gradient_checkpointing=profile.runtime.get("gradient_checkpointing", True),
        logging_steps=1 if args.max_steps > 0 else 5,
        save_strategy="steps",
        save_steps=args.save_steps,
        save_total_limit=None,
        report_to=[],
        remove_unused_columns=False,
        seed=args.seed,
        data_seed=args.seed,
        optim=profile.runtime.get("optimizer", "paged_adamw_8bit"),
        use_liger_kernel=profile.liger_fused_loss,
        liger_kernel_config=LIGER_KERNEL_CONFIG,
    )
    trainer = FusedLossTrainer(
        model=model,
        args=trainer_args,
        train_dataset=dataset,
        data_collator=collator,
        callbacks=[
            CompletionCallback(),
            OptimizationEvidenceCallback(),
            *(
                [_make_liger_binding_callback(TrainerCallback, liger_proof)]
                if profile.liger_fused_loss
                else []
            ),
        ],
    )
    result = trainer.train(
        resume_from_checkpoint=(
            str(resume_from_checkpoint) if resume_from_checkpoint is not None else None
        )
    )
    train_loss = result.metrics.get("train_loss")
    if not isinstance(train_loss, (int, float)) or not math.isfinite(train_loss):
        raise ContractError(f"training loss is not finite: {train_loss!r}")
    if gradient_evidence["optimizer_steps"] <= 0:
        raise ContractError("Trainer completed without an optimizer step")
    if collator.receipt is None:
        raise ContractError("Trainer completed without constructing a batch")
    validated_hopper_backend = validate_hopper_backend_evidence(
        hopper_backend_evidence
    )
    validated_liger_proof = (
        validate_liger_fused_loss_proof(liger_proof)
        if profile.liger_fused_loss
        else {"enabled": False, "reason": "profile-disabled"}
    )
    final_adapter = output / "final-adapter"
    model.save_pretrained(final_adapter, safe_serialization=True)
    processor.save_pretrained(final_adapter)
    _atomic_json(
        output / "training-result.json",
        {
            "protocol": "striatum-training-result/2",
            "strategy": args.strategy,
            "base_preparation": base_preparation,
            "profile": str(profile.path),
            "model_load": {
                "model_class": type(base).__name__,
                "processor_class": type(processor).__name__,
                "model_type": profile.model_type,
                "quantization": profile.runtime.get("quantization"),
                "attention_implementation": profile.runtime.get(
                    "attention_implementation", "flash_attention_2"
                ),
            },
            "measurement": measurement,
            "metrics": result.metrics,
            "batch": collator.receipt,
            "optimization": {
                **gradient_evidence,
                "nonzero_gradient_parameters": sorted(
                    gradient_evidence["nonzero_gradient_parameters"]
                ),
            },
            "example_selection": example_selection,
            "global_step": trainer.state.global_step,
            "resumed_from": (
                str(resume_from_checkpoint)
                if resume_from_checkpoint is not None
                else None
            ),
            "resume_acknowledgement": resume_acknowledgement,
            "acknowledged_checkpoints": acknowledged_checkpoints,
            "checkpoint_schedule": checkpoint_schedule,
            "liger_fused_loss": validated_liger_proof,
            "hopper_linear_attention": validated_hopper_backend,
            "final_adapter": str(final_adapter),
        },
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strategy", choices=STRATEGIES, default="linear-only")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(__file__).with_name("training-config.json"),
    )
    parser.add_argument("--model-dir", type=Path, default=model_dir_from_env())
    parser.add_argument("--input-dir", type=Path, default=input_dir_from_env())
    parser.add_argument(
        "--output", type=Path, default=output_dir_from_env() / "checkpoints"
    )
    parser.add_argument("--max-steps", type=int, default=-1)
    parser.add_argument("--resume-from-checkpoint", type=Path)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--select-longest", action="store_true")
    parser.add_argument("--save-steps", type=int, default=25)
    parser.add_argument("--save-final-checkpoint", action="store_true")
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def main() -> None:
    run(parse_args())


if __name__ == "__main__":
    main()
