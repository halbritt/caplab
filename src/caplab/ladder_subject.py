"""Native subject identity and disposition rules for ladder continuation."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Iterable, Sequence

from caplab.codex_events import (
    CodexEventError, require_completed_codex_turn, require_no_codex_model_reroutes,
)

from caplab.subject_identity import (
    NativeAgentSystemContractError,
    load_native_agent_system_policy,
    validate_native_agent_systems,
)


class NativeSubjectError(ValueError):
    """Raised before preparation when a ladder subject is not authorized."""


def subject_slot(
    scenario: str,
    arm: str,
    model: str,
    effort: str,
    trial: int,
    replacement: int | None = None,
) -> str:
    if arm not in {"none", "injection"}:
        raise NativeSubjectError(f"unknown arm: {arm}")
    if trial < 1 or trial > 5:
        raise NativeSubjectError(f"trial outside adaptive design: {trial}")
    if replacement is not None and replacement < 1:
        raise NativeSubjectError(f"invalid replacement number: {replacement}")
    suffix = f"t{trial}" + (f"r{replacement}" if replacement is not None else "")
    return f"{scenario}--{arm}--{model.removeprefix('gpt-5.6-')}-{effort}--{suffix}"


def validate_ladder_subject(
    base_policy_path: Path,
    tuple_policy_path: Path,
    model: str,
    effort: str,
    command: Sequence[str],
    *,
    observed_harness_version: str | None = None,
) -> None:
    """Validate one historical model/native-Codex/effort/version tuple."""
    model_name = model.removeprefix("gpt-5.6-")
    tuple_id = f"codex-{model_name}-{effort}"
    subject = {
        "tuple_id": tuple_id,
        "model_id": model,
        "native_harness_id": "codex",
        "effort": effort,
        "command": list(command),
        "version_command": ["codex", "--version"],
    }
    try:
        base_policy = load_native_agent_system_policy(base_policy_path)
        tuple_policy = load_native_agent_system_policy(tuple_policy_path)
        expected_base = tuple_policy.get("base_policy", {})
        actual_base_sha256 = hashlib.sha256(base_policy_path.read_bytes()).hexdigest()
        if expected_base.get("sha256") != actual_base_sha256:
            raise NativeSubjectError("base_native_agent_policy_digest_mismatch")
        if tuple_policy.get("policy") != base_policy.get("policy"):
            raise NativeSubjectError("native_agent_policy_invariant_mismatch")
        if tuple_policy.get("forbidden_proxy_markers") != base_policy.get(
            "forbidden_proxy_markers"
        ):
            raise NativeSubjectError("native_agent_proxy_markers_mismatch")
        validate_native_agent_systems(tuple_policy, {tuple_id: subject})
        expected = tuple_policy["systems"][tuple_id]
        expected_command = [
            expected["executable"],
            *expected["required_command_tokens"],
        ]
        if list(command) != expected_command:
            raise NativeSubjectError("native_ladder_command_mismatch")
        expected_version = tuple_policy.get("native_harness_version")
        if not isinstance(expected_version, str) or not expected_version:
            raise NativeSubjectError("native_harness_version_policy_missing")
        if observed_harness_version != expected_version:
            raise NativeSubjectError("native_harness_version_mismatch")
    except (NativeAgentSystemContractError, OSError) as error:
        raise NativeSubjectError(str(error)) from error


def classify_subject_attempt(
    events_jsonl: str | bytes,
    return_code: int,
    write_set: Iterable[str],
    *,
    pin_ok: bool,
) -> tuple[str, str | None]:
    """Separate behavioral attempts from native-harness infrastructure failure."""
    if not pin_ok:
        return "infrastructure", "native tuple attestation mismatch"
    try:
        require_no_codex_model_reroutes(events_jsonl)
        require_completed_codex_turn(events_jsonl)
    except CodexEventError as error:
        return "infrastructure", str(error)
    if return_code != 0:
        return "infrastructure", f"native harness exited {return_code}"
    return (
        ("behavioural-attempt", None)
        if list(write_set)
        else ("behavioural-no-attempt", None)
    )
