"""One fixed offline native tool exchange with bounded capture; not a model measurement."""

import base64
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import uuid

from caplab.capture_quarantine import (
    CaptureQuarantineError,
    check_capture_bytes,
    check_capture_document,
)
from caplab.native_collection import NativeRuntimeDescriptor, collect_native_outputs
from caplab.native_runtime import prepare_native_runtime
from caplab.process_capture import (
    ProcessCaptureQuarantineError,
    capture_process,
    seal_capture_json,
)
from caplab.revbench.codex import ExactSecretStreamQuarantine, _sealed_data_memfd
from caplab.supervised_task_capture import SupervisedTaskCapture
from caplab.task_capture import TaskCaptureLimits
from probe_cgroup_resource_limits import (
    JOIN,
    MIB,
    MOUNTS,
    cleanup_group,
    receive_mount,
    require,
    retain_mount,
    snapshot,
)
from probe_native_capture_startup import (
    harness_manifest,
    inspect_traced_peer,
    stop_writers,
)

REPO = Path(__file__).resolve().parents[2]
CODE = Path(__file__).resolve().parent
from . import support
from .lifecycle import read_preparation, check_inputs
from caplab.native_child_process import FrozenNativeChildEvidence

SCRIPT = REPO / "scripts/probe_scripted_native_capture.py"
BOOTSTRAP = (CODE / "bootstrap.py").read_text()
POLICY = REPO / "docs/product/contracts/native-agent-systems.json"
SUPPORT = CODE / "support.py"
ENV = {"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8"}
ACCOUNT = "synthetic-account-00000001"
SUBJECT = "synthetic-subject-00000001"
SECRET = b"fabricated-native-quarantine-echo-only"


def auth_document():
    def encoded(value):
        return (
            base64.urlsafe_b64encode(json.dumps(value, sort_keys=True).encode())
            .rstrip(b"=")
            .decode()
        )

    token = ".".join(
        (
            encoded({"alg": "RS256", "kid": "synthetic-key-000001", "typ": "JWT"}),
            encoded(
                {
                    "sub": SUBJECT,
                    "iss": "https://auth.openai.com",
                    "aud": ["https://api.openai.com/v1"],
                    "iat": 946684800,
                    "exp": 4102444800,
                    "email": "synthetic@example.invalid",
                }
            ),
            base64.urlsafe_b64encode(b"not-a-provider-signature").rstrip(b"=").decode(),
        )
    )
    return {
        "auth_mode": "chatgptAuthTokens",
        "OPENAI_API_KEY": None,
        "tokens": {
            "id_token": token,
            "access_token": "synthetic-access-token-only",
            "refresh_token": "",
            "account_id": ACCOUNT,
        },
        "last_refresh": "2026-09-09T00:00:00Z",
    }


def secret_values():
    tokens = auth_document()["tokens"]
    return (
        SECRET,
        tokens["id_token"].encode(),
        tokens["access_token"].encode(),
        ACCOUNT.encode(),
        SUBJECT.encode(),
        b"synthetic@example.invalid",
    )


def factory():
    return ExactSecretStreamQuarantine(secret_values())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def seal(root, name, document):
    for path in (root / name, root / ("." + name.removesuffix(".json") + ".pending")):
        check_capture_bytes(factory, os.fsencode(path))
    check_capture_document(factory, document)
    return seal_capture_json(root, name, document)


def guarded(stage, operation, refusals):
    try:
        return operation()
    except (CaptureQuarantineError, ProcessCaptureQuarantineError) as error:
        require(
            str(error) == "capture output quarantined",
            "unexpected guarded-capture failure",
        )
        refusals.append(stage)
        return None


def case(root, group, name, selected):
    plan = selected["plan"]
    SOURCE = Path(selected["harness_manifest"]["source"])
    task, prepared = root / (name + "-task"), root / (name + "-prepared")
    task.mkdir(mode=0o700)
    # Preparation receives only the fixed secret-free plan and empty host task.
    check_capture_document(factory, plan)
    prepare_native_runtime(
        POLICY,
        plan,
        expected_invocation_sha256=plan["invocation_sha256"],
        task_root=task,
        output_dir=prepared,
    )
    preparation = json.loads((prepared / "preparation.json").read_bytes())
    child = group / ("fixture-" + name)
    child.mkdir()
    descriptors = []
    socket_path = root / (name + "-control.sock")
    native_path = root / (name + "-native.sock")
    trace_path = root / (name + "-exec.trace")
    native_listener = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)
    observation_path = root / (name + "-child-observation.sock")
    observation_listener = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)
    context = {}
    refusals = []
    process = None
    try:
        observation_listener.bind(str(observation_path))
        observation_path.chmod(0o600)
        observation_listener.listen(1)
        observation_listener.settimeout(30)
        native_listener.bind(str(native_path))
        native_path.chmod(0o600)
        native_listener.listen(1)
        native_listener.settimeout(5)
        limits = {
            "memory.max": str(256 * MIB),
            "memory.swap.max": "0",
            "memory.oom.group": "1",
            "pids.max": "128",
        }
        for key, value in limits.items():
            (child / key).write_text(value)
        before = snapshot(child)
        require(
            all(
                before["limits_and_usage"][key] == value
                for key, value in limits.items()
            ),
            "child limits differ",
        )
        payload = (json.dumps(auth_document(), sort_keys=True) + "\n").encode()
        control = (
            json.dumps(
                {
                    "case": name,
                    "echo_value": SECRET.decode(),
                    "directories": preparation["directories"],
                },
                sort_keys=True,
            )
            + "\n"
        ).encode()
        with (
            _sealed_data_memfd("synthetic-native-auth", payload) as auth_fd,
            _sealed_data_memfd("synthetic-native-control", control) as control_fd,
        ):
            command = [
                "/usr/bin/python3",
                "-B",
                "-c",
                JOIN,
                str(child),
                "/usr/bin/bwrap",
                "--unshare-all",
                "--cap-add",
                "CAP_NET_ADMIN",
                "--die-with-parent",
                "--new-session",
                "--clearenv",
                "--ro-bind",
                "/usr",
                "/usr",
                "--symlink",
                "usr/bin",
                "/bin",
                "--symlink",
                "usr/lib",
                "/lib",
                "--symlink",
                "usr/lib64",
                "/lib64",
                "--proc",
                "/proc",
                "--dir",
                "/dev",
                "--dev-bind",
                "/dev/null",
                "/dev/null",
                "--dev-bind",
                "/dev/urandom",
                "/dev/urandom",
                "--dev-bind",
                "/dev/zero",
                "/dev/zero",
                "--dev-bind",
                "/dev/full",
                "/dev/full",
                "--dev-bind",
                "/dev/random",
                "/dev/random",
                "--dev-bind",
                "/dev/tty",
                "/dev/tty",
                "--ro-bind",
                str(SOURCE),
                "/opt/native",
                "--ro-bind",
                selected["dependency_root"],
                "/fixture-deps/websockets",
                "--dir",
                "/toolbin",
                "--symlink",
                "/opt/native/bin/codex.js",
                "/toolbin/codex",
            ]
            for filename in ("bootstrap.py", "fixture.py", "payload.py", "guard.py"):
                command += [
                    "--ro-bind",
                    str(CODE / filename),
                    "/fixture-code/" + filename,
                ]
            for mount in MOUNTS:
                command += ["--size", str(64 * MIB), "--tmpfs", mount]
            command += [
                "--ro-bind-data",
                str(auth_fd),
                "/auth-input/auth.json",
                "--ro-bind-data",
                str(control_fd),
                "/fixture/input.json",
                "--ro-bind",
                str(socket_path),
                "/control.sock",
                "--ro-bind",
                str(observation_path),
                "/child-observation.sock",
                "--ro-bind",
                str(native_path),
                "/native-control.sock",
                "--chdir",
                "/work",
                "--remount-ro",
                "/",
                "--",
                "/usr/bin/python3",
                "-B",
                "-c",
                BOOTSTRAP,
                hashlib.sha256(payload).hexdigest(),
                json.dumps(plan),
            ]
            command = [
                "/usr/bin/prlimit",
                "--fsize=2097152:8388608",
                "--core=0",
                "--",
                "/usr/bin/strace",
                "-f",
                "-v",
                "-xx",
                "-s",
                "65536",
                "--decode-pids=pidns",
                "-e",
                "trace=execve,execveat,clone,clone3,fork,vfork",
                "-o",
                str(trace_path),
                "--",
            ] + command
            seal(
                root,
                name + "-launch.json",
                {
                    "command": command,
                    "environment": ENV,
                    "plan": plan,
                    "before": before,
                    "quarantine_policy": selected["quarantine_policy"],
                },
            )
            stage = "handoff"
            try:
                with SupervisedTaskCapture(
                    command,
                    task_root=task,
                    namespace_root="/work",
                    environment=ENV,
                    output_dir=root / name,
                    limits=TaskCaptureLimits(300000, MIB, 1000, 45),
                    max_process_receipt_bytes=30000,
                    quarantine_factory=factory,
                ) as recorder:
                    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as listener:
                        listener.bind(str(socket_path))
                        socket_path.chmod(0o600)
                        listener.listen(1)
                        listener.settimeout(5)
                        with ThreadPoolExecutor(max_workers=1) as pool:
                            future = pool.submit(
                                capture_process,
                                command,
                                cwd=task,
                                environment=ENV,
                                output_dir=root / name / "process",
                                max_stream_bytes=300000,
                                timeout_seconds=45,
                                pass_fds=(auth_fd, control_fd),
                                quarantine_factory=factory,
                            )
                            descriptors, handoff = receive_mount(
                                listener,
                                child,
                                recorder,
                                inspect_peer=lambda pid: inspect_traced_peer(
                                    pid, trace_path
                                ),
                                usable_devices="bwrap-basic-v1",
                                quarantine_factory=factory,
                                nested_userns=True,
                                task_input=selected.get("task_input"),
                            )
                            context = {
                                "root": root,
                                "name": name,
                                "handoff": handoff,
                                "group": child,
                                "source": SOURCE,
                                "trace": trace_path,
                                "seal": seal,
                                "policy": POLICY,
                                "selected": selected,
                            }
                            exec_observation = support.receive_native_exec(
                                native_listener,
                                context,
                                lambda port: support.expected_invocation(
                                    POLICY, plan, port
                                ),
                            )
                            (binary,) = [
                                x
                                for x in selected["harness_manifest"]["entries"]
                                if x["path"] == support.NATIVE_RELATIVE
                            ]
                            support.receive_child_observation(
                                observation_listener,
                                group=child,
                                expected_peer=handoff["peer_pid"],
                                evidence=FrozenNativeChildEvidence(
                                    exec_observation["peer_pid"],
                                    context["parent_proc_descriptor"],
                                    SOURCE / support.NATIVE_RELATIVE,
                                    binary["sha256"],
                                    1024**3,
                                    128,
                                ),
                                seal_observation=lambda document: seal(
                                    root, name + "-child-observation.json", document
                                ),
                            )
                            stage = "process"
                            process = future.result(timeout=51)
                    forced = stop_writers(child)
                    after = snapshot(child)
                    seal(
                        root,
                        name + "-resource-exit.json",
                        {
                            "before": before,
                            "after": after,
                            "process": process,
                            "forced_group_kill": forced,
                            "guarded_refusals": refusals,
                        },
                    )
                    require(
                        process["streams_complete"]
                        and process["termination"] == "exited",
                        "incomplete child",
                    )
                    stage = "task"
                    recorder.finish(
                        expected_process_sha256=digest(
                            root / name / "process/capture.json"
                        )
                    )
            except (CaptureQuarantineError, ProcessCaptureQuarantineError) as error:
                require(
                    stage in ("process", "task")
                    and str(error) == "capture output quarantined",
                    "unexpected pre-release or guarded-capture failure",
                )
                refusals.append(stage)
                forced = stop_writers(child)
                after = snapshot(child)
                seal(
                    root,
                    name + "-resource-exit.json",
                    {
                        "before": before,
                        "after": after,
                        "process": process,
                        "forced_group_kill": forced,
                        "guarded_refusals": refusals,
                    },
                )
            for fd, raw in ((auth_fd, payload), (control_fd, control)):
                require(
                    not os.get_inheritable(fd), "parent descriptor became inheritable"
                )
                os.lseek(fd, 0, os.SEEK_SET)
                require(
                    os.read(fd, len(raw) + 1) == raw, "sealed fixture input changed"
                )
        index = MOUNTS.index("/episode")
        identity = handoff["mounts"][index]
        guarded(
            "native",
            lambda: collect_native_outputs(
                POLICY,
                prepared,
                expected_preparation_sha256=digest(prepared / "preparation.json"),
                output_dir=root / (name + "-collection"),
                max_receipt_bytes=100000,
                max_artifact_bytes=8 * MIB,
                max_entries=1000,
                runtime_descriptor=NativeRuntimeDescriptor(
                    descriptors[index], identity["source_dev"], identity["source_ino"]
                ),
                quarantine_factory=factory,
            ),
            refusals,
        )
        retained = root / (name + "-retained")
        retained.mkdir(mode=0o700)
        inventories, bytes_left, entries_left = [], 40 * MIB, 2000
        for index, (descriptor, identity) in enumerate(
            zip(descriptors, handoff["mounts"], strict=True)
        ):
            result = guarded(
                "mount:" + identity["source_root"],
                lambda: retain_mount(
                    descriptor,
                    retained / str(index),
                    identity,
                    bytes_left,
                    entries_left,
                    quarantine_factory=factory,
                ),
                refusals,
            )
            if result is None:
                break
            sha, bytes_left, entries_left = result
            inventories.append(
                {"source_root": identity["source_root"], "inventory_sha256": sha}
            )
        require(
            trace_path.stat().st_size < 2 * MIB, "host exec trace reached file limit"
        )
        report = {
            "native_exec": exec_observation,
            "native_exec_sha256": digest(root / (name + "-native-exec.json")),
            "host_exec_trace_sha256": digest(trace_path),
            "harness": name,
            "native_harness": "codex",
            "before": before,
            "after": after,
            "process": process,
            "handoff": handoff,
            "forced_group_kill": forced,
            "inventories": inventories,
            "retained_bytes": 40 * MIB - bytes_left,
            "retained_entries": 2000 - entries_left,
            "guarded_refusals": refusals,
            "selected_capture_retained": not refusals,
            "anchors": {"handoff_sha256": digest(root / (name + "-handoff.json"))},
        }
        for key, path in (
            ("attempt_sha256", root / name / "attempt.json"),
            ("collection_sha256", root / (name + "-collection") / "collection.json"),
        ):
            if path.is_file():
                report["anchors"][key] = digest(path)
        summaries = [
            json.loads(line)["fixture_summary"]
            for line in (root / name / "process/native.stderr")
            .read_bytes()
            .splitlines()
            if line.startswith(b'{"fixture_summary":')
        ]
        require(len(summaries) <= 1, "multiple fixture summaries")
        report["fixture_summary"] = summaries[0] if summaries else None
        report["native_attempt_succeeded"] = bool(
            summaries
            and not refusals
            and process["return_code"] == 0
            and summaries[0]["native_return_code"] == 0
            and not summaries[0]["native_timed_out"]
            and not summaries[0]["errors"]
            and summaries[0]["fixture_stop_reason"] is None
            and summaries[0]["scripted_generated_responses"] == 2
        )
        report["binding_complete"] = False
        report["study_eligible"] = False
        seal(root, name + "-observations.json", report)
        return report
    finally:
        for descriptor in descriptors:
            os.close(descriptor)
        if "parent_proc_descriptor" in context:
            os.close(context["parent_proc_descriptor"])
        observation_listener.close()
        observation_path.unlink(missing_ok=True)
        native_listener.close()
        native_path.unlink(missing_ok=True)
        socket_path.unlink(missing_ok=True)
        cleanup_group(child)


def inside(root, unit, expected_preparation_sha256):
    require(
        re.fullmatch(r"caplab-scripted-native-[0-9a-f]{32}\.service", unit),
        "wrong owned unit",
    )
    membership = Path("/proc/self/cgroup").read_text().strip()
    require(
        membership.startswith("0::/") and "\n" not in membership,
        "unified cgroup required",
    )
    current = Path("/sys/fs/cgroup") / membership[3:].lstrip("/")
    group = current.parent
    require(
        current.name == "supervisor" and group.name == unit, "wrong delegated cgroup"
    )
    limits = {
        key: (group / key).read_text().strip()
        for key in ("memory.max", "memory.swap.max", "pids.max")
    }
    require(
        limits
        == {"memory.max": str(512 * MIB), "memory.swap.max": "0", "pids.max": "192"},
        "unit limits differ",
    )
    (group / "cgroup.subtree_control").write_text("+memory +pids")
    selected = json.loads((root / "selection.json").read_bytes())
    prepared = read_preparation(
        root.parent, expected_sha256=expected_preparation_sha256
    )
    check_inputs(prepared)
    consumed = json.loads((root.parent / "consumption.json").read_bytes())
    require(
        consumed["preparation_sha256"] == expected_preparation_sha256
        and consumed["attempts_consumed"] == 1,
        "worker lacks matching consumed allowance",
    )
    require(
        selected["plan"] == prepared["invocation"]
        and selected["harness_manifest"] == prepared["harness_manifest"]
        and selected["dependency_root"] == prepared["dependency_manifest"]["source"]
        and selected.get("task_input") == prepared.get("task_input"),
        "worker selection differs",
    )
    require(
        json.loads((root / "intent.json").read_bytes())["unit"] == unit,
        "worker unit differs from intent",
    )
    SOURCE = Path(selected["harness_manifest"]["source"])
    require(digest(SUPPORT) == selected["support_sha256"], "exec support changed")
    require(
        harness_manifest(SOURCE) == selected["harness_manifest"], "installation differs"
    )
    reports = [case(root, group, name, selected) for name in ("safe",)]
    require(digest(SUPPORT) == selected["support_sha256"], "exec support changed")
    require(
        harness_manifest(SOURCE) == selected["harness_manifest"], "installation changed"
    )
    for path in root.rglob("*"):
        check_capture_bytes(factory, os.fsencode(path))
        if path.is_file():
            check_capture_bytes(factory, path.read_bytes())
    seal(
        root,
        "observations.json",
        {
            "unit": unit,
            "delegated_cgroup": str(group),
            "limits": limits,
            "reports": reports,
            "provider_authentication_verified": False,
            "study_eligible": False,
        },
    )


def run(root, prepared, expected_preparation_sha256):
    require(
        root.is_absolute()
        and root.parent.resolve() == root.parent
        and not root.exists(),
        "fresh resolved root required",
    )
    check_capture_bytes(factory, os.fsencode(root))
    root.mkdir(mode=0o700)
    plan = prepared["invocation"]
    selected = {
        "plan": plan,
        "harness_manifest": prepared["harness_manifest"],
        "dependency_root": prepared["dependency_manifest"]["source"],
        "quarantine_policy": {
            "id": "synthetic-native-exact-values/v1",
            "secret_value_count": len(secret_values()),
            "implementation_source_sha256": digest(
                REPO / "src/caplab/revbench/codex.py"
            ),
        },
        "script_sha256": digest(SCRIPT),
        "support_sha256": digest(SUPPORT),
    }
    if "task_input" in prepared:
        selected["task_input"] = prepared["task_input"]
    seal(root, "selection.json", selected)
    unit = "caplab-scripted-native-" + uuid.uuid4().hex + ".service"
    environment = ENV | {
        "XDG_RUNTIME_DIR": f"/run/user/{os.getuid()}",
        "DBUS_SESSION_BUS_ADDRESS": f"unix:path=/run/user/{os.getuid()}/bus",
    }
    command = [
        "/usr/bin/systemd-run",
        "--user",
        "--unit=" + unit,
        "--wait",
        "--pipe",
        "--collect",
        "--service-type=exec",
        "--property=Delegate=memory pids",
        "--property=DelegateSubgroup=supervisor",
        "--property=MemoryMax=536870912",
        "--property=MemorySwapMax=0",
        "--property=TasksMax=192",
        "--property=RuntimeMaxSec=90",
        "--property=KillMode=control-group",
        "--property=LimitCORE=0",
        "--",
        "/usr/bin/env",
        "-i",
        "PATH=/usr/bin:/bin",
        "LANG=C.UTF-8",
        "PYTHONPATH=" + str(REPO / "src") + ":" + str(REPO / "scripts"),
        "/usr/bin/python3",
        "-B",
        str(SCRIPT),
        "worker",
        str(root),
        "--unit",
        unit,
        "--preparation-sha256",
        expected_preparation_sha256,
    ]
    seal(
        root,
        "intent.json",
        {
            "unit": unit,
            "command": command,
            "environment": environment,
            "selection_sha256": digest(root / "selection.json"),
            "script_sha256": digest(SCRIPT),
            "support_sha256": digest(SUPPORT),
        },
    )
    try:
        process = capture_process(
            command,
            cwd=root,
            environment=environment,
            output_dir=root / "service",
            max_stream_bytes=200000,
            timeout_seconds=100,
            quarantine_factory=factory,
        )
        observed = (
            json.loads((root / "observations.json").read_bytes())
            if (root / "observations.json").is_file()
            else None
        )
    finally:
        stopped = subprocess.run(
            ["/usr/bin/systemctl", "--user", "stop", unit],
            env=environment,
            capture_output=True,
            timeout=5,
        )
        state = subprocess.run(
            [
                "/usr/bin/systemctl",
                "--user",
                "show",
                unit,
                "--property=LoadState",
                "--value",
            ],
            env=environment,
            capture_output=True,
            timeout=5,
        )
        seal(
            root,
            "cleanup.json",
            {
                "unit": unit,
                "stop_return_code": stopped.returncode,
                "load_state": state.stdout.decode().strip(),
                "show_return_code": state.returncode,
            },
        )
        require(
            state.returncode == 0 and state.stdout.strip() == b"not-found",
            "owned native unit remains",
        )
    if observed is not None:
        require(not Path(observed["delegated_cgroup"]).exists(), "owned cgroup remains")
    return {
        "service_process": process,
        "observations_available": observed is not None,
        "unit": unit,
        "native_attempt_succeeded": bool(
            observed and observed["reports"][0]["native_attempt_succeeded"]
        ),
    }
