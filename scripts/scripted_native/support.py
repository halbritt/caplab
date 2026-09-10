import hashlib, os, re, socket, struct, time
from pathlib import Path
from caplab.codex_child_configuration import (
    CodexChildSourceEvidence,
    prepare_codex_child_configuration,
)
from caplab.native_child_process import observe_frozen_native_child
from caplab.exec_provenance import observe_exec_tracer
from caplab.native_launch_configuration import (
    NativeLaunchContext,
    build_native_launch_configuration,
)
from probe_cgroup_resource_limits import MOUNTS, inspect_nested_procfs, require


def expected_invocation(policy, plan, port, *, profile="codex-scripted-local/v1"):
    return build_native_launch_configuration(
        policy,
        plan,
        expected_invocation_sha256=plan["invocation_sha256"],
        context=NativeLaunchContext(profile, port),
    )


def combine_routed_summary(native, fixture):
    """Join separate captured native and supervisor-fixture outcomes without editing either."""
    require(isinstance(native, dict) and isinstance(fixture, dict)
            and type(fixture.get('peer_pid')) is int and fixture['peer_pid'] > 0
            and type(fixture.get('finished_monotonic_ns')) is int and fixture['finished_monotonic_ns'] > 0
            and type(fixture.get('port')) is int and 1 <= fixture['port'] <= 65535,
            'invalid supervisor fixture identity')
    endpoint = {"address": "198.18.0.1", "port": fixture["port"]}
    require(native.get("external_fixture") == endpoint
            and fixture.get("bind_address") == endpoint["address"]
            and fixture.get("schema") == "caplab.supervised-scripted-fixture/v1"
            and fixture.get("fixture_thread_joined") is True
            and fixture.get("fixture_closed") is True
            and fixture.get("study_eligible") is False,
            "routed fixture outcome identity differs")
    require(native["requests"] == [] and native["errors"] == []
            and native["websocket_messages"] == [] and native["library_events"] == []
            and native["scripted_generated_responses"] == 0
            and native["deferred_close"] is None and native["fixture_stop_reason"] is None,
            "routed bootstrap claimed supervisor fixture observations")
    return native | {key: fixture[key] for key in ("requests", "errors", "websocket_messages",
        "library_events", "scripted_generated_responses", "deferred_close", "fixture_stop_reason")}


NATIVE_RELATIVE = (
    "node_modules/@openai/codex-linux-x64/vendor/x86_64-unknown-linux-musl/bin/codex"
)


def prepare_binary(context, launch):
    (record,) = [
        x
        for x in context["selected"]["harness_manifest"]["entries"]
        if x["path"] == NATIVE_RELATIVE
    ]
    prepared = prepare_codex_child_configuration(
        context["policy"],
        context["selected"]["plan"],
        launch,
        context["source"],
        evidence=CodexChildSourceEvidence(
            context["selected"]["plan"]["invocation_sha256"],
            launch["launch_configuration_sha256"],
            record["sha256"],
            1024**3,
        ),
    )
    context["seal"](
        context["root"], context["name"] + "-child-configuration.json", prepared
    )
    return prepared


def mounted_files(peer, source):
    specs = {
        "launcher": (source / "bin/codex.js", "/opt/native/bin/codex.js"),
        "node": (Path("/usr/bin/node"), "/usr/bin/node"),
        "binary": (source / NATIVE_RELATIVE, "/opt/native/" + NATIVE_RELATIVE),
    }
    observed = {}
    require(
        os.readlink(f"/proc/{peer}/root/toolbin/codex") == "/opt/native/bin/codex.js",
        "launcher link differs",
    )
    for name, (host, namespace) in specs.items():
        actual = Path(f"/proc/{peer}/root", namespace.lstrip("/")).stat()
        expected = host.stat()
        require(
            (actual.st_dev, actual.st_ino, actual.st_size)
            == (expected.st_dev, expected.st_ino, expected.st_size),
            "mounted executable identity differs",
        )
        observed[name] = {
            "namespace_path": namespace,
            "host_source": str(host),
            "device": actual.st_dev,
            "inode": actual.st_ino,
            "bytes": actual.st_size,
        }
    return observed


def receive_native_exec(listener, context, build_expected):
    channel, _ = listener.accept()
    received_ns = time.monotonic_ns()
    with channel:
        channel.settimeout(3)
        peer, uid, gid = struct.unpack(
            "3i", channel.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, 12)
        )
        require((uid, gid) == (os.getuid(), os.getgid()), "native peer owner differs")
        raw, _, flags, _ = channel.recvmsg(32)
        require(
            flags == 0 and re.fullmatch(rb"[1-9][0-9]{0,4}", raw) is not None,
            "invalid fixture port packet",
        )
        port = int(raw)
        require(port <= 65535, "invalid fixture port packet")
        status = dict(
            line.split(":", 1)
            for line in Path(f"/proc/{peer}/status").read_text().splitlines()
            if ":" in line
        )
        require(int(status["Tgid"]) == peer, "authenticated peer is not process leader")
        files = mounted_files(peer, context["source"])
        fields = Path(f"/proc/{peer}/stat").read_text().rsplit(")", 1)[1].split()
        require(
            int(fields[1]) == context["handoff"]["peer_pid"],
            "native peer parent differs",
        )
        require(int(fields[4]) == 0, "native peer has controlling terminal")
        member = Path(f"/proc/{peer}/cgroup").read_text().strip()
        require(
            member == "0::/" + str(context["group"].relative_to("/sys/fs/cgroup")),
            "native peer cgroup differs",
        )
        procfs = inspect_nested_procfs(peer)
        for name, pair in context["handoff"]["nested_procfs"]["namespaces"].items():
            require(
                procfs["namespaces"][name]["peer"] == pair["peer"],
                "native peer namespace differs",
            )
        task = context["handoff"]["mounts"][MOUNTS.index("/work")]
        cwd = Path(f"/proc/{peer}/cwd").stat()
        require(
            (cwd.st_dev, cwd.st_ino) == (task["source_dev"], task["source_ino"]),
            "native peer cwd differs",
        )
        mounted = Path(f"/proc/{peer}/root/opt/native").stat()
        source = context["source"].stat()
        require(
            (mounted.st_dev, mounted.st_ino) == (source.st_dev, source.st_ino),
            "native installation mount differs",
        )
        tracer = observe_exec_tracer(
            peer, context["trace"], expected_tracer_executable=Path("/usr/bin/strace")
        )
        launch = build_expected(port)
        prepared = prepare_binary(context, launch)
        context["parent_proc_descriptor"] = os.open(
            f"/proc/{peer}", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
        )
        invocation = {key: launch[key] for key in ("command", "environment", "cwd")}
        launch_name = context["name"] + "-launch-configuration.json"
        context["seal"](context["root"], launch_name, launch)
        launch_sha = hashlib.sha256(
            (context["root"] / launch_name).read_bytes()
        ).hexdigest()
        observation = {
            "schema": "caplab.private-native-exec-handoff/v3",
            "diagnostic_clock": {
                "accepted_monotonic_ns": received_ns,
                "before_observation_seal_monotonic_ns": time.monotonic_ns(),
            },
            "process_leader_verified": True,
            "mounted_executables": files,
            "expected_native_binary": {
                key: prepared[key] for key in ("executable", "command", "environment")
            },
            "child_configuration_sha256": prepared["child_configuration_sha256"],
            "child_configuration_file_sha256": hashlib.sha256(
                (
                    context["root"] / (context["name"] + "-child-configuration.json")
                ).read_bytes()
            ).hexdigest(),
            "launch_configuration_file_sha256": launch_sha,
            "launch_configuration_sha256": launch["launch_configuration_sha256"],
            "peer_pid": peer,
            "parent_pid": int(fields[1]),
            "peer_uid": uid,
            "peer_gid": gid,
            "port": port,
            "cgroup": member,
            "procfs": procfs,
            "task_identity": task,
            "installation_root": {"device": source.st_dev, "inode": source.st_ino},
            "tracer": tracer,
            "expected": invocation,
        }
        context["seal"](
            context["root"], context["name"] + "-native-exec.json", observation
        )
        channel.sendall(b"1")
        return observation


def await_frozen(group, expected):
    deadline = time.monotonic() + 2
    while (
        dict(
            line.split() for line in (group / "cgroup.events").read_text().splitlines()
        ).get("frozen")
        != expected
    ):
        if time.monotonic() >= deadline:
            raise TimeoutError("owned workload freeze transition timed out")
        time.sleep(0.01)


def receive_child_observation(
    listener, *, group, expected_peer, evidence, seal_observation
):
    """Own one authenticated handshake and freeze/thaw; borrow listener and evidence FD."""
    channel, _ = listener.accept()
    with channel:
        channel.settimeout(5)
        peer, uid, gid = struct.unpack(
            "3i", channel.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, 12)
        )
        require(
            (peer, uid, gid) == (expected_peer, os.getuid(), os.getgid()),
            "child observation peer differs",
        )
        raw, ancillary, flags, _ = channel.recvmsg(64)
        require(
            not ancillary
            and flags == 0
            and re.fullmatch(rb"[0-9a-f]{64}", raw) is not None,
            "invalid child observation packet",
        )
        clock = {"accepted_monotonic_ns": time.monotonic_ns()}
        record = {
            "schema": "caplab.private-child-observation-handshake/v1",
            "peer_pid": peer,
            "request_sha256": raw.decode("ascii"),
            "clock": clock,
            "observation": None,
            "binding_complete": False,
            "study_eligible": False,
        }
        try:
            try:
                clock["freeze_requested_monotonic_ns"] = time.monotonic_ns()
                (group / "cgroup.freeze").write_text("1")
                await_frozen(group, "1")
                clock["frozen_monotonic_ns"] = time.monotonic_ns()
                record["observation"] = observe_frozen_native_child(
                    group, evidence=evidence
                )
            finally:
                clock["thaw_requested_monotonic_ns"] = time.monotonic_ns()
                (group / "cgroup.freeze").write_text("0")
                await_frozen(group, "0")
                clock["thawed_monotonic_ns"] = time.monotonic_ns()
        except Exception as error:
            record["error"] = {
                "type": type(error).__name__,
                "message": str(error)[:256],
            }
            seal_observation(record)
            raise
        clock["before_seal_monotonic_ns"] = time.monotonic_ns()
        seal_observation(record)
        channel.sendall(b"1")
        return record
