"""Identity and completion evidence from a single native Codex invocation."""

import json
from dataclasses import dataclass
from typing import Any


class CodexEventError(ValueError):
    """The supplied stream cannot establish the requested execution fact."""


@dataclass(frozen=True)
class CodexAgentMessage:
    thread_id: str
    event_index: int
    item_id: str
    text: str


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate object key")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValueError("non-JSON numeric constant")


def parse_native_json(text: str) -> Any:
    """Parse native JSON without duplicate keys or non-JSON constants."""
    try:
        return json.loads(text, object_pairs_hook=_unique_object, parse_constant=_reject_constant)
    except ValueError as error:
        raise CodexEventError("native JSON is malformed or ambiguous") from error


def _events(stream: str | bytes) -> tuple[str, list[dict[str, Any]]]:
    if isinstance(stream, bytes):
        try:
            stream = stream.decode("utf-8")
        except UnicodeDecodeError as error:
            raise CodexEventError("native event stream is not valid UTF-8") from error
    events = []
    lines = stream.split("\n")
    if lines[-1] == "":
        lines.pop()
    for number, line in enumerate(lines, start=1):
        try:
            event = parse_native_json(line)
        except ValueError as error:
            raise CodexEventError(f"native event stream has invalid JSON at line {number}") from error
        if not isinstance(event, dict):
            raise CodexEventError("native event stream record must be an object")
        if not isinstance(event.get("type"), str) or not event["type"].strip():
            raise CodexEventError("native event stream record lacks event type")
        events.append(event)
    return stream, events


def _thread_id(events: list[dict[str, Any]]) -> str:
    starts = [i for i, event in enumerate(events) if event["type"] == "thread.started"]
    if starts != [0]:
        raise CodexEventError("native event stream requires one initial thread.started")
    thread_id = events[0].get("thread_id")
    if not isinstance(thread_id, str) or not thread_id.strip():
        raise CodexEventError("native event stream lacks thread.started identifier")
    return thread_id


def codex_thread_id(stream: str | bytes) -> str:
    """Return an unambiguous thread identity without claiming turn completion."""
    _, events = _events(stream)
    return _thread_id(events)


def is_codex_model_reroute(event: dict[str, Any]) -> bool:
    """Recognize the native ModelRerouted envelope without parsing model names."""
    item = event.get("item")
    return (
        event.get("type") == "item.completed"
        and isinstance(item, dict)
        and item.get("type") == "error"
        and isinstance(item.get("message"), str)
        and item["message"].startswith("model rerouted: ")
    )


def require_no_codex_model_reroutes(stream: str | bytes) -> None:
    """Reject explicit reroutes; absence does not establish model identity."""
    _, events = _events(stream)
    if any(is_codex_model_reroute(event) for event in events):
        raise CodexEventError("native event stream reports model reroute")


def _completed_events(stream: str | bytes) -> tuple[str, list[dict[str, Any]]]:
    text, events = _events(stream)
    for event in events:
        if event["type"] in {"error", "turn.failed", "thread.error"}:
            raise CodexEventError(f"native event stream reports {event['type']}")
        rate_limit = event.get("rate_limit_info")
        if isinstance(rate_limit, dict) and rate_limit.get("status") == "rejected":
            raise CodexEventError("native event stream reports rejected rate_limit")
    if not text.endswith("\n"):
        raise CodexEventError("native event stream lacks final newline")
    thread_id = _thread_id(events)
    starts = [i for i, event in enumerate(events) if event["type"] == "turn.started"]
    if len(starts) != 1 or starts[0] == 0:
        raise CodexEventError("native event stream requires one turn.started")
    completed = [i for i, event in enumerate(events) if event["type"] == "turn.completed"]
    if completed != [len(events) - 1]:
        raise CodexEventError("native event stream requires one final turn.completed")
    return thread_id, events


def require_completed_codex_turn(stream: str | bytes) -> str:
    """Return the thread ID only for one complete, failure-free captured turn."""
    thread_id, _ = _completed_events(stream)
    return thread_id


def final_codex_message(stream: str | bytes) -> CodexAgentMessage:
    """Select the last completed agent message inside a completed native turn."""
    thread_id, events = _completed_events(stream)
    turn_start = next(i for i, event in enumerate(events) if event["type"] == "turn.started")
    selected = None
    message_ids = set()
    for index, event in enumerate(events[:-1]):
        if event["type"] != "item.completed":
            continue
        item = event.get("item")
        if not isinstance(item, dict) or not isinstance(item.get("type"), str):
            raise CodexEventError("native completed item is malformed")
        if item["type"] != "agent_message":
            continue
        if index <= turn_start:
            raise CodexEventError("native agent message is outside the completed turn")
        item_id, text = item.get("id"), item.get("text")
        if not isinstance(item_id, str) or not item_id.strip() or not isinstance(text, str):
            raise CodexEventError("native agent message lacks item identity or text")
        if item_id in message_ids:
            raise CodexEventError("native completed agent message identity is duplicated")
        message_ids.add(item_id)
        selected = CodexAgentMessage(thread_id, index, item_id, text)
    if selected is None:
        raise CodexEventError("native completed turn has no agent message")
    return selected
