"""Executable contract for behavior-bearing native agent-system identities."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Mapping, Sequence


class NativeAgentSystemContractError(ValueError):
    """A study tried to substitute a proxy for its declared agent system."""


_SCHEMA = "caplab.native-agent-systems/v1"
CANONICAL_NATIVE_AGENT_SYSTEM_POLICY_SHA256 = (
    "56bd254c2500d4d5913460aae307cbf5b81aafdb1830d5fe66a7d429432fc5d2"
)
_REQUIRED_PROXY_MARKERS = frozenset({"openrouter", "harbor", "terminus"})
_IDENTITY_ENVIRONMENT_MARKERS = (
    "MODEL",
    "EFFORT",
    "PROVIDER",
    "ENDPOINT",
    "BASE_URL",
    "API_BASE",
)
_IDENTITY_OPTIONS = frozenset(
    {
        "-m",
        "--model",
        "--effort",
        "--fallback-model",
        "--provider",
        "--model-provider",
        "--local-provider",
        "--oss",
        "-c",
        "--config",
    }
)


def load_native_agent_system_policy(path: str | os.PathLike[str]) -> dict[str, Any]:
    policy_path = Path(path)
    try:
        value = json.loads(policy_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise NativeAgentSystemContractError(
            f"native_agent_policy_unreadable:{error}"
        ) from error
    if not isinstance(value, dict) or value.get("schema") != _SCHEMA:
        raise NativeAgentSystemContractError("invalid_native_agent_policy_schema")
    systems = value.get("systems")
    if not isinstance(systems, dict) or not systems:
        raise NativeAgentSystemContractError("native_agent_policy_has_no_systems")
    if value.get("exceptions") != []:
        raise NativeAgentSystemContractError(
            "native_agent_policy_exception_requires_new_contract"
        )
    return value


def _unwrap_env(command: Sequence[str]) -> tuple[list[str], list[str]]:
    tokens = list(command)
    assignments: list[str] = []
    if tokens and tokens[0] == "/usr/bin/env":
        tokens.pop(0)
        while tokens and "=" in tokens[0] and not tokens[0].startswith("="):
            assignments.append(tokens.pop(0))
    return assignments, tokens


def _has_identity_environment_override(assignments: Sequence[str]) -> bool:
    seen: set[str] = set()
    for assignment in assignments:
        name, _, _ = assignment.partition("=")
        normalized = name.upper()
        if not name or name in seen:
            return True
        seen.add(name)
        if any(marker in normalized for marker in _IDENTITY_ENVIRONMENT_MARKERS):
            return True
    return False


def _has_identity_option(tokens: Sequence[str]) -> bool:
    for token in tokens:
        option = token.split("=", 1)[0]
        if option in _IDENTITY_OPTIONS:
            return True
    return False


def validate_native_agent_systems(
    policy: Mapping[str, Any],
    subjects: Mapping[str, Mapping[str, Any]],
) -> None:
    """Require every subject to be its declared native harness/model/effort tuple."""

    systems = policy.get("systems")
    markers = policy.get("forbidden_proxy_markers")
    if not isinstance(systems, Mapping) or not isinstance(markers, list):
        raise NativeAgentSystemContractError("invalid_native_agent_policy")
    if not all(isinstance(marker, str) for marker in markers):
        raise NativeAgentSystemContractError("invalid_native_agent_policy")
    if not subjects:
        raise NativeAgentSystemContractError("native_agent_subjects_missing")

    for subject_id, subject in subjects.items():
        tuple_id = subject.get("tuple_id")
        expected = systems.get(tuple_id) if isinstance(tuple_id, str) else None
        if not isinstance(expected, Mapping):
            raise NativeAgentSystemContractError(
                f"unknown_native_agent_tuple:{subject_id}"
            )
        for field in ("model_id", "native_harness_id", "effort"):
            if subject.get(field) != expected.get(field):
                raise NativeAgentSystemContractError(
                    f"native_agent_tuple_mismatch:{subject_id}:{field}"
                )
        command = subject.get("command")
        version_command = subject.get("version_command")
        if not isinstance(command, list) or not all(
            isinstance(token, str) for token in command
        ):
            raise NativeAgentSystemContractError(
                f"native_agent_command_missing:{subject_id}"
            )
        if not isinstance(version_command, list) or not all(
            isinstance(token, str) for token in version_command
        ):
            raise NativeAgentSystemContractError(
                f"native_agent_version_probe_missing:{subject_id}"
            )
        executable = expected.get("executable")
        command_environment, unwrapped_command = _unwrap_env(command)
        if _has_identity_environment_override(command_environment):
            raise NativeAgentSystemContractError(
                f"native_agent_environment_identity_override:{subject_id}"
            )
        command_executable = unwrapped_command[0] if unwrapped_command else ""
        if command_executable != executable:
            raise NativeAgentSystemContractError(
                f"native_agent_executable_mismatch:{subject_id}"
            )
        required = expected.get("required_command_tokens")
        if not isinstance(required, list) or not all(
            isinstance(token, str) for token in required
        ):
            raise NativeAgentSystemContractError(
                f"native_agent_command_tuple_mismatch:{subject_id}"
            )
        command_arguments = unwrapped_command[1:]
        if command_arguments[: len(required)] != required:
            raise NativeAgentSystemContractError(
                f"native_agent_command_tuple_mismatch:{subject_id}"
            )
        if _has_identity_option(command_arguments[len(required) :]):
            raise NativeAgentSystemContractError(
                f"native_agent_command_identity_override:{subject_id}"
            )
        version_environment, unwrapped_version = _unwrap_env(version_command)
        if _has_identity_environment_override(version_environment):
            raise NativeAgentSystemContractError(
                f"native_agent_environment_identity_override:{subject_id}"
            )
        if not unwrapped_version or unwrapped_version != expected.get(
            "version_command"
        ):
            raise NativeAgentSystemContractError(
                f"native_agent_version_probe_mismatch:{subject_id}"
            )
        encoded = " ".join([*command, *version_command]).casefold()
        effective_markers = _REQUIRED_PROXY_MARKERS | {
            marker.casefold() for marker in markers
        }
        if any(marker in encoded for marker in effective_markers):
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
