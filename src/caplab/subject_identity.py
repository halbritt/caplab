"""Executable contract for behavior-bearing native agent-system identities."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Mapping, Sequence


class NativeAgentSystemContractError(ValueError):
    """A study tried to substitute a proxy for its declared agent system."""


_SCHEMA = "caplab.native-agent-systems/v1"


def load_native_agent_system_policy(path: str | os.PathLike[str]) -> dict[str, Any]:
    policy_path = Path(path)
    try:
        value = json.loads(policy_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise NativeAgentSystemContractError(f"native_agent_policy_unreadable:{error}") from error
    if not isinstance(value, dict) or value.get("schema") != _SCHEMA:
        raise NativeAgentSystemContractError("invalid_native_agent_policy_schema")
    systems = value.get("systems")
    if not isinstance(systems, dict) or not systems:
        raise NativeAgentSystemContractError("native_agent_policy_has_no_systems")
    if value.get("exceptions") != []:
        raise NativeAgentSystemContractError("native_agent_policy_exception_requires_new_contract")
    return value


def _ordered_subsequence(required: Sequence[str], command: Sequence[str]) -> bool:
    position = 0
    for token in command:
        if position < len(required) and token == required[position]:
            position += 1
    return position == len(required)


def _unwrap_env(command: Sequence[str]) -> list[str]:
    tokens = list(command)
    if tokens and Path(tokens[0]).name == "env":
        tokens.pop(0)
        while tokens and "=" in tokens[0] and not tokens[0].startswith("="):
            tokens.pop(0)
    return tokens


def validate_native_agent_systems(
    policy: Mapping[str, Any],
    subjects: Mapping[str, Mapping[str, Any]],
) -> None:
    """Require every subject to be its declared native harness/model/effort tuple."""

    systems = policy.get("systems")
    markers = policy.get("forbidden_proxy_markers")
    if not isinstance(systems, Mapping) or not isinstance(markers, list):
        raise NativeAgentSystemContractError("invalid_native_agent_policy")
    if not subjects:
        raise NativeAgentSystemContractError("native_agent_subjects_missing")

    for subject_id, subject in subjects.items():
        tuple_id = subject.get("tuple_id")
        expected = systems.get(tuple_id) if isinstance(tuple_id, str) else None
        if not isinstance(expected, Mapping):
            raise NativeAgentSystemContractError(f"unknown_native_agent_tuple:{subject_id}")
        for field in ("model_id", "native_harness_id", "effort"):
            if subject.get(field) != expected.get(field):
                raise NativeAgentSystemContractError(
                    f"native_agent_tuple_mismatch:{subject_id}:{field}"
                )
        command = subject.get("command")
        version_command = subject.get("version_command")
        if not isinstance(command, list) or not all(isinstance(token, str) for token in command):
            raise NativeAgentSystemContractError(f"native_agent_command_missing:{subject_id}")
        if not isinstance(version_command, list) or not all(
            isinstance(token, str) for token in version_command
        ):
            raise NativeAgentSystemContractError(f"native_agent_version_probe_missing:{subject_id}")
        executable = expected.get("executable")
        unwrapped_command = _unwrap_env(command)
        command_executable = Path(unwrapped_command[0]).name if unwrapped_command else ""
        if command_executable != executable:
            raise NativeAgentSystemContractError(
                f"native_agent_executable_mismatch:{subject_id}"
            )
        required = expected.get("required_command_tokens")
        if not isinstance(required, list) or not _ordered_subsequence(
            required, unwrapped_command[1:]
        ):
            raise NativeAgentSystemContractError(
                f"native_agent_command_tuple_mismatch:{subject_id}"
            )
        unwrapped_version = _unwrap_env(version_command)
        if not unwrapped_version or [
            Path(unwrapped_version[0]).name,
            *unwrapped_version[1:],
        ] != expected.get("version_command"):
            raise NativeAgentSystemContractError(
                f"native_agent_version_probe_mismatch:{subject_id}"
            )
        encoded = " ".join(command).casefold()
        if any(str(marker).casefold() in encoded for marker in markers):
            raise NativeAgentSystemContractError(
                f"proxy_harness_substitution:{subject_id}"
            )


def validate_active_native_manifest(
    policy_path: str | os.PathLike[str], manifest: Mapping[str, Any]
) -> None:
    """Refuse withdrawn manifests and validate every declared agent system."""

    if manifest.get("status") != "active":
        raise NativeAgentSystemContractError("live_authorization_withdrawn")
    policy = load_native_agent_system_policy(policy_path)
    validate_native_agent_systems(policy, manifest.get("agent_systems", {}))
