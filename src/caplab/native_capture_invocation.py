"""Prospective persisted native commands, separate from frozen legacy launchers."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path, PurePosixPath
from uuid import UUID

from caplab.codex_events import parse_native_json
from caplab.subject_identity import NativeAgentSystemContractError, validate_native_agent_systems


# This builder supports the repository's named policy bytes, not caller-edited tuples.
_POLICY_SHA256 = "1245d7ddda6045d0476a177cd937697be2ed5cd83438b647cdfeade39f70e5d9"


def _digest(document: dict) -> str:
    return hashlib.sha256(json.dumps(document, sort_keys=True, ensure_ascii=True,
                                     separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def _namespace_path(value: str, name: str) -> str:
    if (not isinstance(value, str) or not value.startswith("/") or value == "/"
            or "\0" in value or str(PurePosixPath(value)) != value
            or ".." in value.split("/") or value.startswith("//")):
        raise NativeAgentSystemContractError(f"invalid_capture_{name}")
    return value


@dataclass(frozen=True)
class NativeCaptureContext:
    """Paths are in the future execution namespace; no filesystem is prepared."""
    task_root: str
    runtime_root: str
    prompt: bytes
    session_id: str | None = None


def _profile(harness: str) -> dict:
    common = {"HOME": "{runtime_root}/home", "PATH": "/toolbin:/usr/bin:/bin", "LANG": "C.UTF-8"}
    if harness == "codex":
        return {"schema": "caplab.native-capture-profile/v1", "id": "codex-persisted-events/1",
                "native_harness_id": harness,
                "arguments": ["--sandbox", "workspace-write", "--skip-git-repo-check", "--json",
                              "--color", "never", "-c", "hide_agent_reasoning=false",
                              "-c", 'model_reasoning_summary="detailed"',
                              "--output-last-message", "{runtime_root}/final-message.txt",
                              "-C", "{task_root}"],
                "environment": common | {"CODEX_HOME": "{runtime_root}/codex"},
                "capture_locations": {"session_search_root": "{runtime_root}/codex/sessions",
                                      "diagnostic_search_root": "{runtime_root}/codex/log",
                                      "final_message": "{runtime_root}/final-message.txt"},
                "external_containment_required": True}
    if harness == "claude-code":
        return {"schema": "caplab.native-capture-profile/v1", "id": "claude-persisted-events/1",
                "native_harness_id": harness,
                "arguments": ["--output-format", "stream-json", "--verbose", "--include-partial-messages",
                              "--include-hook-events", "--dangerously-skip-permissions",
                              "--session-id", "{session_id}", "--debug-file", "{runtime_root}/debug.log"],
                "environment": common | {"CLAUDE_CONFIG_DIR": "{runtime_root}/claude"},
                "capture_locations": {"session_search_root": "{runtime_root}/claude/projects",
                                      "diagnostic_file": "{runtime_root}/debug.log"},
                "external_containment_required": True}
    raise NativeAgentSystemContractError("unsupported_native_capture_harness")


def build_native_capture_invocation(
    policy_path: Path, tuple_id: str, *, context: NativeCaptureContext,
) -> dict:
    """Build and hash a prospective command; never launch or authorize one.

    The plan is incomplete until executable, config, account, containment and
    storage bindings are independently frozen. Native emission is unverified.
    """
    policy_raw = Path(policy_path).read_bytes()
    if hashlib.sha256(policy_raw).hexdigest() != _POLICY_SHA256:
        raise NativeAgentSystemContractError("capture_native_policy_digest_mismatch")
    policy = parse_native_json(policy_raw.decode("utf-8"))
    expected = policy["systems"].get(tuple_id) if isinstance(tuple_id, str) else None
    if expected is None:
        raise NativeAgentSystemContractError("unknown_capture_native_tuple")
    if not isinstance(context, NativeCaptureContext):
        raise NativeAgentSystemContractError("invalid_capture_context")
    task = _namespace_path(context.task_root, "task_root")
    runtime = _namespace_path(context.runtime_root, "runtime_root")
    if PurePosixPath(task).is_relative_to(runtime) or PurePosixPath(runtime).is_relative_to(task):
        raise NativeAgentSystemContractError("capture_task_runtime_overlap")
    if not isinstance(context.prompt, bytes) or not context.prompt or b"\0" in context.prompt:
        raise NativeAgentSystemContractError("invalid_capture_prompt")
    try:
        prompt = context.prompt.decode("utf-8")
    except UnicodeError as error:
        raise NativeAgentSystemContractError("capture_prompt_not_utf8") from error
    harness = expected["native_harness_id"]
    if harness == "claude-code":
        try:
            if not isinstance(context.session_id, str) or str(UUID(context.session_id)) != context.session_id:
                raise ValueError("noncanonical UUID")
        except ValueError as error:
            raise NativeAgentSystemContractError("capture_requires_canonical_session_uuid") from error
    elif context.session_id is not None:
        raise NativeAgentSystemContractError("codex_session_id_must_come_from_native_output")
    subject = {key: expected[key] for key in ("model_id", "native_harness_id", "effort", "version_command")}
    subject.update(tuple_id=tuple_id, command=[expected["executable"], *expected["required_command_tokens"]])
    validate_native_agent_systems(policy, {"subject": subject})
    profile = _profile(harness)
    values = {"runtime_root": runtime, "task_root": task, "session_id": context.session_id}
    plan = {"schema": "caplab.native-capture-invocation/v1", "policy_sha256": _POLICY_SHA256,
            "base_subject": subject, "profile": profile, "profile_sha256": _digest(profile),
            "cwd": task, "runtime_root": runtime, "session_id": context.session_id,
            "command": subject["command"] + [arg.format_map(values) for arg in profile["arguments"]] + ["--", prompt],
            "version_command": list(subject["version_command"]),
            "environment": {key: value.format_map(values) for key, value in profile["environment"].items()},
            "capture_locations": {key: value.format_map(values) for key, value in profile["capture_locations"].items()},
            "prompt_sha256": hashlib.sha256(context.prompt).hexdigest(), "prompt_bytes": len(context.prompt),
            "execution_authorized": False, "binding_complete": False,
            "interpretation": "prospective native command configuration; no launch, containment or capture verification"}
    plan["invocation_sha256"] = _digest(plan)
    return plan
