import hashlib, json


def identity_expectation(expected):
    """Copy the three explicitly selected request fields; do not infer defaults."""
    if (
        not isinstance(expected, dict)
        or set(expected) != {"model", "effort", "summary"}
        or not all(isinstance(v, str) and 0 < len(v) <= 256 for v in expected.values())
    ):
        raise ValueError("invalid request identity expectation")
    return dict(expected)


def request_identity(document, expected):
    """Compare native request metadata, without authenticating a served model."""
    expected = identity_expectation(expected)
    if not isinstance(document, dict):
        raise ValueError("invalid request document")
    if document.get("model") != expected["model"]:
        raise ValueError("request model differs")
    reasoning = document.get("reasoning")
    if not isinstance(reasoning, dict):
        raise ValueError("request reasoning is missing or malformed")
    for field in ("effort", "summary"):
        if reasoning.get(field) != expected[field]:
            raise ValueError("request reasoning " + field + " differs")
    return {
        "model": document["model"],
        "effort": reasoning["effort"],
        "summary": reasoning["summary"],
    }


WITNESS = "CAPLAB café tool witness\n"
FINAL = "CAPLAB SCRIPTED TOOL DIAGNOSTIC COMPLETE"
TOOL_COMMAND = "python3 -c 'from pathlib import Path; p=Path('\"'\"'capture-witness.txt'\"'\"'); p.write_text('\"'\"'CAPLAB café tool witness\\n'\"'\"', encoding='\"'\"'utf-8'\"'\"'); print(p.read_text(encoding='\"'\"'utf-8'\"'\"'), end='\"'\"''\"'\"')'"


def declared_functions(document):
    inputs = document.get("input")
    if not isinstance(inputs, list) or len(inputs) > 100:
        raise ValueError("invalid input items")
    namespaces = []
    for item in inputs:
        if not isinstance(item, dict) or "tools" not in item:
            continue
        if not isinstance(item["tools"], list) or len(item["tools"]) > 40:
            raise ValueError("invalid input tools")
        namespaces += [
            tool
            for tool in item["tools"]
            if isinstance(tool, dict)
            and tool.get("type") == "namespace"
            and (tool.get("name") == "functions")
        ]
    if len(namespaces) != 1:
        raise ValueError("requires one functions namespace")
    tools = namespaces[0].get("tools")
    if (
        not isinstance(tools, list)
        or len(tools) > 40
        or (not all((isinstance(t, dict) for t in tools)))
    ):
        raise ValueError("invalid namespace tools")
    return tools


def selected_command_schema(tools):
    matches = [
        tool
        for tool in tools
        if tool.get("type") == "custom" and tool.get("name") == "exec"
    ]
    if len(matches) != 1:
        raise ValueError("requires one declared custom exec tool")
    tool = matches[0]
    description = tool.get("description")
    if (
        not isinstance(description, str)
        or len(description.encode()) > 65536
        or "tools.exec_command" not in description
    ):
        raise ValueError("exec does not declare nested command access")
    return {
        "sha256": hashlib.sha256(json.dumps(tool, sort_keys=True).encode()).hexdigest(),
        "format": tool.get("format"),
        "declares_exec_command": True,
    }


def returned_text(output):
    if isinstance(output, str):
        return output
    if isinstance(output, list) and all(
        (
            isinstance(i, dict)
            and i.get("type") in ("text", "input_text", "output_text")
            and isinstance(i.get("text"), str)
            for i in output
        )
    ):
        return "".join((i["text"] for i in output))
    raise ValueError("unsupported returned content")


TOOL_JAVASCRIPT = (
    "text(await tools.exec_command("
    + json.dumps(
        {"cmd": TOOL_COMMAND, "yield_time_ms": 1000, "max_output_tokens": 1000}
    )
    + "));"
)


def scripted_response(document, number):
    if not isinstance(document, dict):
        raise AssertionError()
    if number == 1:
        selected_command_schema(declared_functions(document))
        item = {
            "type": "custom_tool_call",
            "id": "fc_caplab_fixed",
            "call_id": "call_caplab_fixed",
            "name": "exec",
            "namespace": "functions",
            "input": TOOL_JAVASCRIPT,
            "status": "completed",
        }
    else:
        if not number == 2:
            raise AssertionError()
        outputs = [
            i
            for i in document.get("input", [])
            if isinstance(i, dict)
            and i.get("type") == "custom_tool_call_output"
            and (i.get("call_id") == "call_caplab_fixed")
        ]
        if not (
            len(outputs) == 1
            and WITNESS.strip() in returned_text(outputs[0].get("output"))
        ):
            raise AssertionError()
        item = {
            "type": "message",
            "id": "msg_caplab_fixed",
            "role": "assistant",
            "status": "completed",
            "content": [{"type": "output_text", "text": FINAL, "annotations": []}],
        }
    response = {
        "id": "resp_caplab_" + str(number),
        "object": "response",
        "created_at": 1788912000,
        "status": "in_progress",
        "model": "synthetic-protocol-fixture",
        "output": [],
        "error": None,
        "incomplete_details": None,
    }
    added = {**item, "status": "in_progress"}
    if item["type"] == "custom_tool_call":
        added["input"] = ""
    else:
        added["content"] = []
    events = [
        {"type": "response.created", "response": response},
        {"type": "response.output_item.added", "output_index": 0, "item": added},
    ]
    if item["type"] == "custom_tool_call":
        events += [
            {
                "type": "response.custom_tool_call_input.delta",
                "item_id": item["id"],
                "output_index": 0,
                "delta": item["input"],
            },
            {
                "type": "response.custom_tool_call_input.done",
                "item_id": item["id"],
                "output_index": 0,
                "name": item["name"],
                "input": item["input"],
            },
        ]
    else:
        part = {"type": "output_text", "text": "", "annotations": []}
        events += [
            {
                "type": "response.content_part.added",
                "item_id": item["id"],
                "output_index": 0,
                "content_index": 0,
                "part": part,
            },
            {
                "type": "response.output_text.delta",
                "item_id": item["id"],
                "output_index": 0,
                "content_index": 0,
                "delta": FINAL,
            },
            {
                "type": "response.output_text.done",
                "item_id": item["id"],
                "output_index": 0,
                "content_index": 0,
                "text": FINAL,
            },
            {
                "type": "response.content_part.done",
                "item_id": item["id"],
                "output_index": 0,
                "content_index": 0,
                "part": item["content"][0],
            },
        ]
    events += [
        {"type": "response.output_item.done", "output_index": 0, "item": item},
        {
            "type": "response.completed",
            "response": {
                **response,
                "status": "completed",
                "output": [item],
                "usage": {
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_tokens": 0,
                    "input_tokens_details": {"cached_tokens": 0},
                    "output_tokens_details": {"reasoning_tokens": 0},
                },
            },
        },
    ]
    return b"".join(
        (
            (
                "event: "
                + event["type"]
                + "\ndata: "
                + json.dumps(event | {"sequence_number": index})
                + "\n\n"
            ).encode()
            for index, event in enumerate(events)
        )
    )
