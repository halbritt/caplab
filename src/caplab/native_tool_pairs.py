"""Observed native stdout associations, without inferring successful work."""

import hashlib
import re

from caplab.codex_events import parse_native_json


FORMATS = ("codex-exec-jsonl", "claude-stream-jsonl")


def _identifier(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"invalid {field}")
    return value


def build_native_tool_pair_report(content: bytes, *, format: str,
                                 expected_sha256: str, expected_root_id: str,
                                 max_bytes: int) -> dict:
    """Inspect exact bounded bytes; hashes identify input, not its execution origin.

    Complete JSONL framing is required, but a terminal native record is not.
    All returned mappings are owned. The input bytes are never executed.
    """
    if format not in FORMATS or type(max_bytes) is not int or max_bytes <= 0:
        raise ValueError("invalid format or byte limit")
    _identifier(expected_root_id, "expected root ID")
    if (not isinstance(content, bytes) or not content or len(content) > max_bytes
            or not content.endswith(b"\n")):
        raise ValueError("input must be bounded nonempty newline-terminated JSONL bytes")
    if (not isinstance(expected_sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_sha256)
            or hashlib.sha256(content).hexdigest() != expected_sha256):
        raise ValueError("source digest mismatch")
    records = []
    offset = 0
    for line, body in enumerate(content.split(b"\n")[:-1], 1):
        raw = body + b"\n"
        try:
            event = parse_native_json(raw.decode("utf-8"))
        except (ValueError, UnicodeError, RecursionError) as error:
            raise ValueError(f"invalid native JSONL at line {line}") from error
        if not isinstance(event, dict):
            raise ValueError(f"native event at line {line} must be an object")
        kind = _identifier(event.get("type"), "event type")
        records.append((event, {"line": line, "byte_offset": offset, "bytes": len(raw),
                                "sha256": hashlib.sha256(raw).hexdigest(), "type": kind}))
        offset += len(raw)
    first = records[0][0]
    if format == "codex-exec-jsonl":
        if first.get("type") != "thread.started" or first.get("thread_id") != expected_root_id:
            raise ValueError("source lacks the expected initial Codex thread")
    elif (first.get("type"), first.get("subtype"), first.get("session_id")) != (
            "system", "init", expected_root_id):
        raise ValueError("source lacks the expected initial Claude session")
    elif first.get("parent_tool_use_id") is not None:
        raise ValueError("Claude initialization must be in root scope")

    groups, unclassified, terminals, compactions = {}, [], [], []
    event_index = []

    def add(session, parent, native_id, phase, ref, *, kind=None, name=None, outcome=None):
        key = (session, parent, _identifier(native_id, "native item/tool ID"))
        group = groups.setdefault(key, {"session_id": session, "parent_tool_use_id": parent,
            "native_id": native_id, "kinds": [], "tool_names": [],
            "requests": [], "results": [], "partials": [], "updates": []})
        for field, value in (("kinds", kind), ("tool_names", name)):
            if value is not None and value not in group[field]:
                group[field].append(value)
        group[phase].append(ref if outcome is None else {**ref, "reported_outcome": outcome})

    for event, locator in records:
        kind, line = event["type"], locator["line"]
        classes = []
        def ref(pointer=""):
            return {"line": line, "pointer": pointer}
        def unknown(pointer, value):
            unclassified.append({**ref(pointer), "type": value})
            classes.append("unclassified")

        if format == "codex-exec-jsonl":
            if "thread_id" in event and event["thread_id"] != expected_root_id:
                raise ValueError("Codex event differs from expected thread")
            if kind == "thread.started":
                if line != 1:
                    raise ValueError("multiple Codex thread initializations")
                classes.append("initialization")
            elif kind in ("item.started", "item.updated", "item.completed"):
                item = event.get("item")
                if not isinstance(item, dict):
                    raise ValueError("Codex item must be an object")
                item_kind = _identifier(item.get("type"), "item type")
                if item_kind in ("command_execution", "file_change", "mcp_tool_call", "web_search"):
                    phase = {"item.started": "requests", "item.updated": "updates",
                             "item.completed": "results"}[kind]
                    status, code = item.get("status"), item.get("exit_code")
                    if status is not None and not isinstance(status, str):
                        raise ValueError("invalid reported item status")
                    if code is not None and type(code) is not int:
                        raise ValueError("invalid reported exit code")
                    outcome = {"status": status, "exit_code": code} if phase == "results" else None
                    add(expected_root_id, None, item.get("id"), phase, ref("/item"),
                        kind=item_kind, outcome=outcome)
                    classes.append(phase)
                elif item_kind in ("agent_message", "reasoning", "todo_list"):
                    classes.append("non_tool_item")
                else:
                    unknown("/item", item_kind)
            elif kind in ("turn.completed", "turn.failed", "error"):
                terminals.append({**ref(), "type": kind})
                classes.append("turn_outcome_or_error")
            elif kind == "turn.started":
                classes.append("turn_start")
            else:
                unknown("", kind)
        else:
            session = _identifier(event.get("session_id"), "Claude event session ID")
            parent = event.get("parent_tool_use_id")
            if parent is not None:
                _identifier(parent, "parent tool ID")
            elif session != expected_root_id:
                raise ValueError("Claude root event differs from expected session")
            if kind == "system" and event.get("subtype") == "init":
                if line != 1:
                    raise ValueError("multiple Claude session initializations")
                classes.append("initialization")
            elif kind in ("assistant", "user"):
                message = event.get("message")
                if not isinstance(message, dict):
                    raise ValueError("Claude message must be an object")
                blocks = message.get("content")
                if isinstance(blocks, str):
                    classes.append("non_tool_content")
                elif isinstance(blocks, list):
                    for index, block in enumerate(blocks):
                        pointer = f"/message/content/{index}"
                        if not isinstance(block, dict):
                            raise ValueError("Claude content block must be an object")
                        block_kind = _identifier(block.get("type"), "content block type")
                        if block_kind == "tool_use":
                            if kind != "assistant" or not isinstance(block.get("input"), dict):
                                raise ValueError("invalid completed Claude tool request")
                            name = _identifier(block.get("name"), "tool name")
                            add(session, parent, block.get("id"), "requests", ref(pointer),
                                kind="tool_use", name=name)
                            classes.append("requests")
                        elif block_kind == "tool_result":
                            error = block.get("is_error")
                            if kind != "user" or (error is not None and type(error) is not bool):
                                raise ValueError("invalid Claude tool result")
                            add(session, parent, block.get("tool_use_id"), "results", ref(pointer),
                                outcome={"is_error": error})
                            classes.append("results")
                        elif block_kind in ("text", "thinking", "redacted_thinking", "image"):
                            classes.append("non_tool_content")
                        else:
                            unknown(pointer, block_kind)
                    if not blocks:
                        classes.append("empty_content")
                else:
                    raise ValueError("invalid Claude message content")
            elif kind == "stream_event":
                partial = event.get("event")
                if not isinstance(partial, dict):
                    raise ValueError("invalid Claude partial event")
                block = partial.get("content_block")
                if partial.get("type") == "content_block_start" and isinstance(block, dict) and block.get("type") == "tool_use":
                    add(session, parent, block.get("id"), "partials", ref("/event/content_block"),
                        kind="tool_use", name=_identifier(block.get("name"), "partial tool name"))
                    classes.append("partials")
                else:
                    unknown("/event", _identifier(partial.get("type"), "partial event type"))
            elif kind == "result":
                terminals.append({**ref(), "type": kind, "session_id": session,
                                  "parent_tool_use_id": parent, "subtype": event.get("subtype")})
                classes.append("session_result")
            elif kind == "system" and event.get("subtype") == "compact_boundary":
                compactions.append(ref())
                classes.append("compaction")
            else:
                unknown("", kind)
        event_index.append({**locator, "classifications": list(dict.fromkeys(classes))})

    counts = {}
    for group in groups.values():
        requests, results = group["requests"], group["results"]
        issues = []
        for name, values in (("request", requests), ("result", results)):
            if len(values) > 1:
                issues.append(f"duplicate_{name}")
        if len(group["kinds"]) > 1 or len(group["tool_names"]) > 1:
            issues.append("conflicting_identity")
        if requests and results and results[0]["line"] <= requests[-1]["line"]:
            issues.append("result_not_after_request")
        if issues:
            status = "ambiguous"
        elif requests and results:
            status = "paired"
        elif requests:
            status = "request_without_result"
        elif results:
            status = "result_without_request"
        else:
            status = "partial_or_update_only"
        group.update(status=status, issues=issues)
        counts[status] = counts.get(status, 0) + 1
    return {"schema": "caplab.native-tool-pairs/v1", "format": format,
            "source_sha256": expected_sha256, "source_bytes": len(content),
            "expected_root_id": expected_root_id, "events": event_index,
            "groups": list(groups.values()), "status_counts": counts,
            "unclassified": unclassified, "outcome_records": terminals, "compaction_records": compactions,
            "native_execution_linked": False, "capture_complete": None, "work_correctness": None,
            "interpretation": "Observed IDs and record order only. Codex item lifecycles and Claude tool "
            "blocks are different units. A pair or native terminal event does not establish successful "
            "work, complete capture, test passage, child ancestry, blinding or study eligibility."}
