"""Verify one anchored diagnostic without converting transport failure to success."""

import json
import os
from pathlib import Path
import re
import shlex
import subprocess
from caplab.capture_quarantine import check_capture_bytes
from caplab.codex_capture_link import link_codex_root, link_codex_final_message
from caplab.exec_trace import inspect_exec_trace
from caplab.exec_provenance import verify_exec_tracer
from caplab.native_launch_configuration import (
    NativeLaunchTraceEvidence,
    NativeChildTraceEvidence,
    inspect_native_child_trace,
)
from caplab.codex_child_configuration import (
    CodexChildSourceEvidence,
    prepare_codex_child_configuration,
)
from caplab.native_tool_pairs import inspect_captured_tool_pairs
from probe_native_capture_startup import inspect_custody, harness_manifest
from . import payload as helper
from . import runner as p
from .lifecycle import read_preparation, read_document, digest, require


def inspect(output, *, expected_preparation_sha256, expected_result_sha256):
    output = Path(output)
    preparation = read_preparation(output, expected_sha256=expected_preparation_sha256)
    result = read_document(output / "result.json", expected_result_sha256)
    require(
        result.get("schema") == "caplab.scripted-native-result/v1"
        and result.get("preparation_sha256") == expected_preparation_sha256,
        "result preparation differs",
    )
    require(
        digest(output / "consumption.json") == result.get("consumption_sha256"),
        "consumption hash differs",
    )
    require(
        result.get("verification_performed") is False
        and result.get("binding_complete") is False
        and result.get("study_eligible") is False,
        "raw result cannot claim verification or eligibility",
    )
    consumed = read_document(output / "consumption.json", result["consumption_sha256"])
    require(
        consumed.get("schema") == "caplab.scripted-native-consumption/v1"
        and consumed.get("preparation_sha256") == expected_preparation_sha256
        and consumed.get("custody_root") == str(output)
        and type(consumed.get("attempts_consumed")) is int
        and consumed["attempts_consumed"] == 1,
        "consumption scope differs",
    )
    root = output / "run"
    capture = result.get("capture_manifest")
    if capture is None:
        return {
            "schema": "caplab.scripted-native-inspection/v1",
            "status": "unavailable",
            "reason": "capture manifest unavailable",
            "outcome": result["outcome"],
            "binding_complete": False,
            "study_eligible": False,
        }
    require(capture == harness_manifest(root), "capture manifest differs")
    required = [
        "selection.json",
        "intent.json",
        "cleanup.json",
        "safe-native-exec.json",
        "safe-handoff.json",
        "safe-launch-configuration.json",
        "safe-resource-exit.json",
        "safe-child-configuration.json",
        "safe-child-observation.json",
        "safe-exec.trace",
        "safe/attempt.json",
        "safe-collection/collection.json",
        "safe-observations.json",
    ]
    if preparation.get("resource_profile") == "cgroup-usage/v1":
        required += ["safe-resource-before.json", "safe-resource-after.json"]
    missing = [name for name in required if not (root / name).is_file()]
    if preparation.get("launch_profile") in (
        "codex-scripted-routed/v1",
        "codex-scripted-routed/v2",
    ):
        missing += [
            name
            for name in (
                "outer-launch.json",
                "outer-network.json",
                "safe-fixture.json",
                "safe-network-policy.json",
                "safe-network/terminal.json",
            )
            if not (root / name).is_file()
        ]
    if missing:
        return {
            "schema": "caplab.scripted-native-inspection/v1",
            "status": "unavailable",
            "missing_artifacts": missing,
            "outcome": result["outcome"],
            "binding_complete": False,
            "study_eligible": False,
        }
    return _inspect_complete(root, preparation, result)


def _inspect_complete(root, preparation, result):
    sha = lambda path: digest(path, 1024**3)
    read = lambda path: json.loads(Path(path).read_bytes())
    source = Path(preparation["harness_manifest"]["source"])
    require(
        result["outcome"].get("service_process") == read(root / "service/capture.json"),
        "service outcome differs from captured receipt",
    )
    selection = read(root / "selection.json")
    routed = preparation.get("launch_profile") in (
        "codex-scripted-routed/v1",
        "codex-scripted-routed/v2",
    )
    require(
        selection.get("launch_profile") == preparation.get("launch_profile"),
        "selected launch profile differs from preparation",
    )
    require(
        selection.get("resource_profile") == preparation.get("resource_profile"),
        "selected resource profile differs from preparation",
    )
    require(
        selection.get("task_input") == preparation.get("task_input"),
        "selected task input differs from preparation",
    )
    intent = read(root / "intent.json")
    guard = read(root / "safe-native-exec.json")
    handoff = read(root / "safe-handoff.json")
    launch = read(root / "safe-launch-configuration.json")
    resource = read(root / "safe-resource-exit.json")
    if not selection["plan"] == preparation["invocation"]:
        raise AssertionError()
    if (
        not selection["harness_manifest"]
        == preparation["harness_manifest"]
        == harness_manifest(source)
    ):
        raise AssertionError()
    if not selection["dependency_root"] == preparation["dependency_manifest"]["source"]:
        raise AssertionError()
    if not sha(root / "selection.json") == intent["selection_sha256"]:
        raise AssertionError()
    (binary_record,) = [
        x
        for x in preparation["harness_manifest"]["entries"]
        if x["path"] == p.support.NATIVE_RELATIVE
    ]
    f = {"binary_sha256": binary_record["sha256"]}
    if (
        not sha(root / "safe-launch-configuration.json")
        == guard["launch_configuration_file_sha256"]
    ):
        raise AssertionError()
    if not (
        guard["parent_pid"] == handoff["peer_pid"]
        and guard["process_leader_verified"] is True
    ):
        raise AssertionError()
    for entry in guard["mounted_executables"].values():
        info = Path(entry["host_source"]).stat()
        if not (info.st_dev, info.st_ino, info.st_size) == (
            entry["device"],
            entry["inode"],
            entry["bytes"],
        ):
            raise AssertionError()
    trace = root / "safe-exec.trace"
    raw = trace.read_bytes()
    anchor = sha(trace)
    if not (len(raw) < 2 * 1024 * 1024 and raw.endswith(b"\n")):
        raise AssertionError()
    expected = guard["expected"]
    plan = selection["plan"]
    require(
        launch
        == p.support.expected_invocation(
            p.POLICY,
            plan,
            guard["port"],
            profile=preparation.get("launch_profile", "codex-scripted-local/v1"),
        ),
        "native launch differs from prepared diagnostic profile",
    )
    tracer = verify_exec_tracer(guard["tracer"], trace, expected_pid=guard["peer_pid"])
    node = inspect_exec_trace(
        trace,
        expected_trace_sha256=anchor,
        expected_pid=guard["peer_pid"],
        expected_executable="/usr/bin/node",
        expected_command=["node", "/toolbin/codex"] + expected["command"][1:],
        expected_environment=expected["environment"],
        max_trace_bytes=2 * 1024 * 1024,
    )
    prepared = read(root / "safe-child-configuration.json")
    if (
        not sha(root / "safe-child-configuration.json")
        == guard["child_configuration_file_sha256"]
    ):
        raise AssertionError()
    if (
        not prepared["child_configuration_sha256"]
        == guard["child_configuration_sha256"]
    ):
        raise AssertionError()
    if not prepared == prepare_codex_child_configuration(
        p.POLICY,
        plan,
        launch,
        source,
        evidence=CodexChildSourceEvidence(
            plan["invocation_sha256"],
            launch["launch_configuration_sha256"],
            f["binary_sha256"],
            1024**3,
        ),
    ):
        raise AssertionError()
    binary = {k: prepared[k] for k in ("executable", "command", "environment")}
    if not binary == guard["expected_native_binary"]:
        raise AssertionError()
    handshake = read(root / "safe-child-observation.json")
    observed = handshake["observation"]
    fixed = read(root / "safe-fixture.json") if routed else None
    supervisor_observation = (
        preparation.get("child_observation_profile") == "supervisor-poll/v1"
    )
    require(
        selection.get("child_observation_profile")
        == preparation.get("child_observation_profile"),
        "selected child observation profile differs",
    )
    if supervisor_observation:
        from caplab.native_child_observation import inspect_supervisor_child_observation

        require(handshake["timeout_seconds"] == 5, "child wait timeout differs")
        observation_timing = inspect_supervisor_child_observation(
            handshake,
            expected_parent_pid=guard["peer_pid"],
            expected_supervisor_pid=fixed["peer_pid"],
            not_before_monotonic_ns=guard["diagnostic_clock"][
                "before_observation_seal_monotonic_ns"
            ],
            not_after_monotonic_ns=resource["process"]["finished_monotonic_ns"],
        )
    else:
        expected_request_peer = fixed["peer_pid"] if routed else handoff["peer_pid"]
        require(
            handshake["peer_pid"] == expected_request_peer and "error" not in handshake,
            "child observation peer differs",
        )
    if not (
        observed["parent_pid"] == guard["peer_pid"]
        and observed["child_status"]["PPid"] == guard["peer_pid"]
    ):
        raise AssertionError()
    if not observed["executable"]["sha256"] == f["binary_sha256"]:
        raise AssertionError()
    info = (source / p.support.NATIVE_RELATIVE).stat()
    if not (observed["executable"]["device"], observed["executable"]["inode"]) == (
        info.st_dev,
        info.st_ino,
    ):
        raise AssertionError()
    if not (
        observed["cgroup"]["frozen"] and observed["live_child_executable_observed"]
    ):
        raise AssertionError()
    if not (not observed["study_eligible"] and (not observed["binding_complete"])):
        raise AssertionError()
    child_link = inspect_native_child_trace(
        p.POLICY,
        plan,
        launch,
        trace,
        evidence=NativeLaunchTraceEvidence(
            plan["invocation_sha256"],
            launch["launch_configuration_sha256"],
            anchor,
            guard["peer_pid"],
            2 * 1024 * 1024,
        ),
        child=NativeChildTraceEvidence(
            observed["child_pid"],
            binary["executable"],
            binary["command"],
            binary["environment"],
        ),
    )
    (summary,) = [
        json.loads(l)["fixture_summary"]
        for l in (root / "safe/process/native.stderr").read_bytes().splitlines()
        if l.startswith(b'{"fixture_summary":')
    ]
    if routed:
        summary = p.support.combine_routed_summary(summary, fixed)
    reported = read(root / "safe-observations.json")
    require(
        reported["fixture_summary"] == summary
        and reported["process"] == resource["process"],
        "reported native outcome differs",
    )
    require(
        reported["native_attempt_succeeded"]
        == result["outcome"]["native_attempt_succeeded"],
        "result native outcome differs",
    )
    if not (
        summary["native_return_code"] == 0 and summary["native_timed_out"] is False
    ):
        raise AssertionError()
    if not (
        summary["errors"]
        in ([], ["ConnectionClosedError: no close frame received or sent"])
        and summary["scripted_generated_responses"] == 2
        and summary["auth_unchanged"]
        and (summary["fixture_stop_reason"] is None)
    ):
        raise AssertionError()
    if not (
        resource["process"]["return_code"]
        == (0 if routed else int(bool(summary["errors"])))
        and resource["process"]["streams_complete"]
        and (not resource["guarded_refusals"])
    ):
        raise AssertionError()
    if not (
        not resource["forced_group_kill"]
        and resource["after"]["limits_and_usage"]["pids.current"] == "0"
    ):
        raise AssertionError()
    for phase in ("before", "after"):
        if not resource[phase]["pids_events"]["values"]["max"] == 0:
            raise AssertionError()
        if not all(
            (
                resource[phase]["memory_events"]["values"][k] == 0
                for k in ("max", "oom", "oom_kill")
            )
        ):
            raise AssertionError()
    anchors = {
        "attempt_sha256": sha(root / "safe/attempt.json"),
        "collection_sha256": sha(root / "safe-collection/collection.json"),
        "handoff_sha256": sha(root / "safe-handoff.json"),
    }
    inventories = []
    total_bytes = total_entries = 0
    for index, mount in enumerate(handoff["mounts"]):
        inv = root / "safe-retained" / str(index) / "inventory.json"
        d = read(inv)
        inventories.append(
            {"source_root": mount["source_root"], "inventory_sha256": sha(inv)}
        )
        total_bytes += sum((e.get("bytes", 0) for e in d["entries"]))
        total_entries += len(d["entries"])
    report = {
        "harness": "safe",
        "handoff": handoff,
        "process": resource["process"],
        "inventories": inventories,
        "retained_bytes": total_bytes,
        "retained_entries": total_entries,
        "anchors": anchors,
    }
    expected_routing = None
    if routed:
        from caplab.capture_network_policy import build_capture_network_policy

        policy = build_capture_network_policy(
            [{"address": "198.18.0.1", "port": guard["port"]}]
        )
        require(
            read(root / "safe-network-policy.json") == policy,
            "native network policy differs",
        )
        require(
            fixed["port"] == guard["port"], "native and supervisor fixture ports differ"
        )
        (terminal_pin,) = [
            entry
            for entry in result["capture_manifest"]["entries"]
            if entry["path"] == "safe-network/terminal.json"
        ]
        expected_routing = {"plan": policy, "terminal_sha256": terminal_pin["sha256"]}
        if preparation["launch_profile"] == "codex-scripted-routed/v2":
            expected_routing["namespace_profile"] = "parent-user/v1"
        outer = read(root / "outer-network.json")
        launch_outer = read(root / "outer-launch.json")
        from .routed_network import outer_command
        import sys

        group = Path("/sys/fs/cgroup") / guard["cgroup"][4:]
        expected_outer = outer_command(
            root,
            source=source,
            dependency=Path(selection["dependency_root"]),
            group=group.parent,
            task_input=Path(preparation["task_input"]["custody"])
            if preparation.get("task_input") is not None
            else None,
            child_command=[
                sys.executable,
                "-B",
                str(p.SCRIPT),
                "worker",
                str(root),
                "--unit",
                intent["unit"],
                "--preparation-sha256",
                result["preparation_sha256"],
            ],
        )
        require(
            launch_outer["command"] == expected_outer
            and launch_outer["preparation_sha256"] == result["preparation_sha256"],
            "outer launch differs from selected profile",
        )
        require(
            outer["parent_namespaces"] == launch_outer["parent_namespaces"]
            and outer["initial_routes"] == []
            and [i["ifname"] for i in outer["initial_links"]] == ["lo"]
            and outer["fixture_address"] == "198.18.0.1"
            and all(
                outer["namespaces"][k] != outer["parent_namespaces"][k]
                for k in ("user", "net", "pid")
            ),
            "outer namespace observations disagree",
        )
        require(
            outer["namespaces"]["net"]
            == handoff["peer_checks"]["supervisor_network_namespace"],
            "routing supervisor namespace differs from outer fixture network",
        )
    custody = inspect_custody(
        root,
        report,
        expected_task_input=preparation.get("task_input"),
        expected_routing=expected_routing,
    )
    kwargs = {
        "expected_attempt_sha256": anchors["attempt_sha256"],
        "expected_collection_sha256": anchors["collection_sha256"],
        "max_receipt_bytes": 300000,
        "max_identity_bytes": 8 * 1024 * 1024,
    }
    link = link_codex_root(p.POLICY, root / "safe", root / "safe-collection", **kwargs)
    pairs = inspect_captured_tool_pairs(
        root / "safe",
        expected_attempt_sha256=anchors["attempt_sha256"],
        format="codex-exec-jsonl",
        expected_root_id=link["rollout"]["thread_id"],
        max_receipt_bytes=300000,
        max_event_bytes=300000,
    )
    (pair,) = pairs["tool_pair_report"]["groups"]
    if not (
        pair["status"] == "paired"
        and pair["results"][0]["reported_outcome"]
        == {"status": "completed", "exit_code": 0}
    ):
        raise AssertionError()
    rows = [
        json.loads(l)
        for l in (root / "safe/process/native.stdout").read_bytes().splitlines()
    ]
    if not rows[-1]["type"] == "turn.completed":
        raise AssertionError()
    (final_message,) = [
        r["item"]["text"]
        for r in rows
        if r["type"] == "item.completed" and r["item"]["type"] == "agent_message"
    ]
    if not final_message == "CAPLAB SCRIPTED TOOL DIAGNOSTIC COMPLETE":
        raise AssertionError()
    collection = read(root / "safe-collection/collection.json")
    (final,) = [e for e in collection["entries"] if e["path"] == "final_message"]
    if (
        not (root / "safe-collection/objects" / final["object"]).read_bytes()
        == final_message.encode()
    ):
        raise AssertionError()
    if not collection["missing_locations"] == []:
        raise AssertionError()
    after = read(root / "safe/after/inventory.json")
    if preparation.get("task_input") is not None:
        require(
            custody["task"]["changes"]
            == [{"path": "capture-witness.txt", "change": "added"}],
            "diagnostic changed the prepared task",
        )
        witnesses = [e for e in after["entries"] if e["path"] == "capture-witness.txt"]
    else:
        witnesses = [e for e in after["entries"] if e["kind"] == "file"]
    (witness,) = witnesses
    if not (
        witness["path"] == "capture-witness.txt"
        and (root / "safe/after" / witness["object"]).read_bytes()
        == "CAPLAB café tool witness\n".encode()
    ):
        raise AssertionError()
    strict = link_codex_final_message(
        p.POLICY, root / "safe", root / "safe-collection", **kwargs
    )
    if not strict["final_message_agrees"] is True:
        raise AssertionError()
    unit = intent["unit"]
    state = subprocess.run(
        [
            "/usr/bin/systemctl",
            "--user",
            "show",
            unit,
            "--property=LoadState",
            "--value",
        ],
        capture_output=True,
        check=True,
    )
    if not state.stdout.strip() == b"not-found":
        raise AssertionError()
    cgroup = Path("/sys/fs/cgroup") / guard["cgroup"][4:]
    if not (
        cgroup.name == "fixture-safe"
        and cgroup.parent.name == unit
        and (not cgroup.parent.exists())
    ):
        raise AssertionError()
    scanned = 0
    for file in root.rglob("*"):
        check_capture_bytes(p.factory, os.fsencode(file))
        if file.is_file():
            check_capture_bytes(p.factory, file.read_bytes())
            scanned += 1
    hexes = re.findall(b'"((?:\\\\x[0-9a-f]{2})*)"', raw)
    for value in hexes:
        check_capture_bytes(
            p.factory, bytes.fromhex(value.replace(b"\\x", b"").decode())
        )
    if not (
        len(summary["requests"]) <= 32 and summary["scripted_generated_responses"] == 2
    ):
        raise AssertionError()
    handshakes = [r for r in summary["requests"] if r["path"] == "/responses"]
    if not (
        len(handshakes) == 1
        and handshakes[0]["method"] == "GET"
        and (handshakes[0]["status"] == 101)
    ):
        raise AssertionError()
    if not all(
        (e["classification"] == "handled-http-post" for e in summary["library_events"])
    ):
        raise AssertionError()
    requests = summary["websocket_messages"]
    if not 2 <= len(requests) <= 3:
        raise AssertionError()
    first = requests[0]
    pause = handshake["clock"]
    if supervisor_observation:
        require(
            all(
                "child_observation_requested_monotonic_ns" not in request
                and "child_observation_acknowledged_monotonic_ns" not in request
                for request in requests
            ),
            "supervisor observation still depends on fixture handshake",
        )
    else:
        if not handshake["request_sha256"] == first["sha256"]:
            raise AssertionError()
        if (
            not sum(
                (
                    "child_observation_requested_monotonic_ns" in request
                    for request in requests
                )
            )
            == 1
        ):
            raise AssertionError()
        pause = handshake["clock"]
        ordered = [
            first["received_monotonic_ns"],
            first["child_observation_requested_monotonic_ns"],
            pause["accepted_monotonic_ns"],
            pause["freeze_requested_monotonic_ns"],
            pause["frozen_monotonic_ns"],
            observed["started_monotonic_ns"],
            observed["finished_monotonic_ns"],
            pause["thaw_requested_monotonic_ns"],
            pause["thawed_monotonic_ns"],
            pause["before_seal_monotonic_ns"],
            first["child_observation_acknowledged_monotonic_ns"],
            first["written_monotonic_ns"],
        ]
        if not ordered == sorted(ordered):
            raise AssertionError()
        if (
            not pause["frozen_monotonic_ns"] - pause["freeze_requested_monotonic_ns"]
            <= 2 * 10**9
        ):
            raise AssertionError()
        if (
            not pause["thawed_monotonic_ns"] - pause["thaw_requested_monotonic_ns"]
            <= 2 * 10**9
        ):
            raise AssertionError()
        if (
            not first["child_observation_acknowledged_monotonic_ns"]
            - first["child_observation_requested_monotonic_ns"]
            < 5 * 10**9
        ):
            raise AssertionError()
    inventory = read(root / "safe-retained/4/inventory.json")
    entries = {e["path"]: e for e in inventory["entries"] if e["kind"] == "file"}
    last_id = None
    warmup_input = None
    generated = 0
    generated_requests = []
    for number, request in enumerate(requests):
        artifacts = {}
        for field, suffix in [
            ("request_artifact", "request.json"),
            ("events_artifact", "events.jsonl"),
        ]:
            name = str(number) + "." + suffix
            metadata = request[field]
            if not metadata["path"] == name:
                raise AssertionError()
            if routed:
                (entry,) = [
                    e
                    for e in result["capture_manifest"]["entries"]
                    if e["path"] == "safe-fixture-requests/" + name
                ]
                artifact_path = root / "safe-fixture-requests" / name
            else:
                entry = entries["fixture-requests/" + name]
                artifact_path = root / "safe-retained/4" / entry["object"]
            raw = artifact_path.read_bytes()
            if not (
                len(raw) == entry["bytes"] == metadata["bytes"] and len(raw) <= 1048576
            ):
                raise AssertionError()
            if not sha(artifact_path) == entry["sha256"] == metadata["sha256"]:
                raise AssertionError()
            artifacts[field] = raw
        document = json.loads(artifacts["request_artifact"])
        identity = helper.request_identity(
            document,
            {
                "model": plan["base_subject"]["model_id"],
                "effort": plan["base_subject"]["effort"],
                "summary": "detailed",
            },
        )
        require(
            request.get("request_identity") == identity,
            "request identity observation differs",
        )
        events = [
            json.loads(line) for line in artifacts["events_artifact"].splitlines()
        ]
        if not (
            document["type"] == "response.create"
            and document.get("previous_response_id") == last_id
        ):
            raise AssertionError()
        if not (
            request["bytes"] == len(artifacts["request_artifact"])
            and request["sha256"] == request["request_artifact"]["sha256"]
        ):
            raise AssertionError()
        if not request["written_monotonic_ns"] >= request["received_monotonic_ns"]:
            raise AssertionError()
        if document.get("generate") is False:
            if not (number == 0 and warmup_input is None and (generated == 0)):
                raise AssertionError()
            if not [e["type"] for e in events] == [
                "response.created",
                "response.completed",
            ]:
                raise AssertionError()
            if not (
                events[-1]["response"]["id"] == "resp_caplab_warmup"
                and events[-1]["response"]["output"] == []
            ):
                raise AssertionError()
            warmup_input = document["input"]
        else:
            effective = document
            if generated == 0 and warmup_input is not None:
                effective = document | {"input": warmup_input + document["input"]}
            generated += 1
            expected = [
                json.loads(line[6:])
                for line in helper.scripted_response(effective, generated).splitlines()
                if line.startswith(b"data: ")
            ]
            if not events == expected:
                raise AssertionError()
            generated_requests.append({"document": document, "events": events})
        last_id = events[-1]["response"]["id"]
    if not generated == 2:
        raise AssertionError()
    errors = [
        r
        for r in rows
        if r["type"] == "error" or r.get("item", {}).get("type") == "error"
    ]
    if not not errors:
        raise AssertionError()
    for termination in (
        child_link["launch"]["entrypoint_termination"]["termination"],
        child_link["child_execution"]["termination"],
    ):
        if not (termination["kind"] == "exited" and termination["exit_code"] == 0):
            raise AssertionError()
    start_item = rows[pair["requests"][0]["line"] - 1]["item"]
    finish_item = rows[pair["results"][0]["line"] - 1]["item"]
    if not shlex.split(start_item["command"]) == [
        "/usr/bin/bash",
        "-lc",
        helper.TOOL_COMMAND,
    ]:
        raise AssertionError()
    if not (
        start_item["command"] == finish_item["command"]
        and finish_item["aggregated_output"] == helper.WITNESS
    ):
        raise AssertionError()
    (rollout_entry,) = [
        e
        for e in collection["entries"]
        if e["kind"] == "file" and "rollout-" in e["path"]
    ]
    rollout = [
        json.loads(line)
        for line in (root / "safe-collection/objects" / rollout_entry["object"])
        .read_bytes()
        .splitlines()
    ]
    (call,) = [
        r["payload"]
        for r in rollout
        if r.get("type") == "response_item"
        and r["payload"].get("type") == "custom_tool_call"
    ]
    (output,) = [
        r["payload"]
        for r in rollout
        if r.get("type") == "response_item"
        and r["payload"].get("type") == "custom_tool_call_output"
    ]
    if not (
        call["namespace"] == "functions"
        and call["name"] == "exec"
        and (call["input"] == helper.TOOL_JAVASCRIPT)
        and (call["call_id"] == output["call_id"] == "call_caplab_fixed")
    ):
        raise AssertionError()
    blocks = output["output"]
    if not (len(blocks) == 2 and all((x["type"] == "input_text" for x in blocks))):
        raise AssertionError()
    command_result = json.loads(blocks[1]["text"])
    if not (
        command_result["exit_code"] == 0 and command_result["output"] == helper.WITNESS
    ):
        raise AssertionError()
    if (
        not [
            json.loads(line[6:])
            for line in helper.scripted_response({"input": [output]}, 2).splitlines()
            if line.startswith(b"data: ")
        ]
        == generated_requests[-1]["events"]
    ):
        raise AssertionError()
    close = summary["deferred_close"]
    clock = summary["diagnostic_clock"]
    if not (clock["return_before_cleanup"] == 0 and clock["timeout_state"] is None):
        raise AssertionError()
    if summary["errors"]:
        if not (
            close["error_index"] == 0
            and close["error"] == summary["errors"][0]
            and (close["generated_responses"] == 2)
        ):
            raise AssertionError()
        if not (
            close["received_close_code"] is None and close["sent_close_code"] is None
        ):
            raise AssertionError()
        if (
            not requests[-1]["written_monotonic_ns"]
            <= close["observed_monotonic_ns"]
            <= (
                fixed["finished_monotonic_ns"]
                if routed
                else clock["poll_end_monotonic_ns"]
            )
        ):
            raise AssertionError()
    elif not close is None:
        raise AssertionError()
    if (
        not clock["poll_end_monotonic_ns"] - clock["after_spawn_monotonic_ns"]
        < 30 * 10**9
    ):
        raise AssertionError()
    resource_fields = {}
    if preparation.get("resource_profile") == "cgroup-usage/v1":
        resource_fields["resource_usage"] = inspect_resource_usage(
            root,
            capture_manifest=result["capture_manifest"],
            expected_cgroup={
                key: handshake["observation"]["cgroup"][key]
                for key in ("path", "device", "inode")
            },
            process=resource["process"],
        )
    return {
        "schema": "caplab.scripted-native-inspection/v1",
        **resource_fields,
        "status": "verified-observation",
        "normal_native_shutdown_verified": True,
        "transport_errors": summary["errors"],
        "native_attempt_succeeded": not summary["errors"],
        "bootstrap_return_code": resource["process"]["return_code"],
        "child_configuration": prepared,
        "child_observation": handshake,
        "child_trace_link": child_link,
        "tracer_check": tracer,
        "node_exec": node,
        "custody_checks": custody,
        "root_link": link,
        "tool_pairs": pairs,
        "strict_final_link": strict,
        "raw_protocol_verified": True,
        "request_configuration_verified": True,
        "exact_task_bytes_agree": True,
        "pause_milliseconds": (
            pause["thawed_monotonic_ns"] - pause["freeze_requested_monotonic_ns"]
        )
        / 1000000.0,
        **(
            {"supervisor_observation_timing": observation_timing}
            if supervisor_observation
            else {
                "handshake_milliseconds": (
                    first["child_observation_acknowledged_monotonic_ns"]
                    - first["child_observation_requested_monotonic_ns"]
                )
                / 1000000.0
            }
        ),
        "trace_sha256": anchor,
        "trace_bytes": trace.stat().st_size,
        "retained_mount_bytes": total_bytes,
        "retained_mount_entries": total_entries,
        "scanned_files": scanned,
        "decoded_trace_strings_scanned": len(hexes),
        "unit": unit,
        "cgroup_absent": True,
        "binding_complete": False,
        "native_capture_complete": None,
        "study_eligible": False,
    }


def inspect_resource_usage(root, *, capture_manifest, expected_cgroup, process):
    """Inspect resource files anchored by the caller's verified capture manifest."""
    from caplab.capture_resources import verify_cgroup_resource_interval
    from caplab.codex_events import parse_native_json
    from caplab.task_capture_verify import _read_file

    snapshots, hashes = [], {}
    for phase in ("before", "after"):
        name = "safe-resource-" + phase + ".json"
        matches = [
            entry for entry in capture_manifest["entries"] if entry["path"] == name
        ]
        require(
            len(matches) == 1 and matches[0]["kind"] == "file",
            "resource capture anchor missing or ambiguous",
        )
        hashes[phase] = matches[0]["sha256"]
        raw, _, observed = _read_file(None, root / name, 1024 * 1024, retain=True)
        require(observed == hashes[phase], "resource capture hash differs")
        snapshots.append(parse_native_json(raw.decode("utf-8")))
    report = verify_cgroup_resource_interval(
        *snapshots, expected_cgroup=expected_cgroup
    )
    start, finish = process["started_monotonic_ns"], process["finished_monotonic_ns"]
    require(
        type(start) is int and type(finish) is int and 0 < start <= finish,
        "invalid resource process interval",
    )
    require(
        snapshots[0]["finished_monotonic_ns"]
        <= start
        <= finish
        <= snapshots[1]["started_monotonic_ns"],
        "resource observations do not enclose captured process",
    )
    return {
        **report,
        "snapshot_sha256": hashes,
        "captured_process_interval_enclosed": True,
    }
