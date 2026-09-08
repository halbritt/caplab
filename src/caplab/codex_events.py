"""Identity and completion evidence from a single native Codex invocation."""

import json
from typing import Any


class CodexEventError(ValueError):
    """The supplied stream cannot establish the requested execution fact."""


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate object key")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValueError("non-JSON numeric constant")


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
            event = json.loads(line, object_pairs_hook=_unique_object, parse_constant=_reject_constant)
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


def require_completed_codex_turn(stream: str | bytes) -> str:
    """Return the thread ID only for one complete, failure-free captured turn."""
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
    return thread_id
