import ctypes
import errno
import fcntl
import hashlib
from http.client import HTTPConnection
import json
import os
from pathlib import Path
import resource
import signal
import socket
import struct
import subprocess
import sys
import threading
import time

resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
resource.setrlimit(resource.RLIMIT_FSIZE, (8388608, 8388608))
plan = json.loads(sys.argv[2])
control_document = json.loads(Path("/fixture/input.json").read_bytes())
external_fixture = control_document.get("external_fixture")
namespace_profile = control_document.get("namespace_profile")
if "namespace_profile" in control_document and (
    namespace_profile != "parent-user/v1" or external_fixture is None
):
    raise ValueError("invalid native workload namespace selection")
if external_fixture is not None:
    if (
        not isinstance(external_fixture, dict)
        or set(external_fixture) != {"address", "port"}
        or external_fixture["address"] != "198.18.0.1"
        or type(external_fixture["port"]) is not int
        or not 1 <= external_fixture["port"] <= 65535
    ):
        raise ValueError("invalid routed fixture endpoint")
for relative in control_document["directories"]:
    Path("/episode", *Path(relative).parts[1:]).mkdir(mode=448, exist_ok=True)
Path("/episode/home").mkdir(exist_ok=True)
Path("/episode/codex").mkdir(exist_ok=True)
os.symlink("/auth-input/auth.json", "/episode/codex/auth.json")
auth_path = Path("/episode/codex/auth.json")
payload = auth_path.read_bytes()
if not hashlib.sha256(payload).hexdigest() == sys.argv[1]:
    raise AssertionError()
fixture = json.loads(payload)
try:
    fd = os.open(auth_path, os.O_WRONLY)
except OSError as error:
    if not error.errno == errno.EROFS:
        raise AssertionError()
else:
    os.close(fd)
    raise RuntimeError("input mount writable")
interfaces = [
    line.split(":", 1)[0].strip()
    for line in Path("/proc/net/dev").read_text().splitlines()[2:]
]
if not interfaces == ["lo"]:
    raise AssertionError()
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as control:
    request = struct.pack("16sH14x", b"lo", 0)
    observed = fcntl.ioctl(control.fileno(), 35091, request)
    flags = struct.unpack("16sH14x", observed)[1]
    fcntl.ioctl(control.fileno(), 35092, struct.pack("16sH14x", b"lo", flags | 1))
if namespace_profile == "parent-user/v1":
    sys.path.insert(0, "/fixture-code")
    from workload_identity import enter_parent_owned_workload

    enter_parent_owned_workload()
libc = ctypes.CDLL(None, use_errno=True)


class Header(ctypes.Structure):
    _fields_ = [("version", ctypes.c_uint32), ("pid", ctypes.c_int)]


class Caps(ctypes.Structure):
    _fields_ = [
        ("effective", ctypes.c_uint32),
        ("permitted", ctypes.c_uint32),
        ("inheritable", ctypes.c_uint32),
    ]


header = Header(537396514, 0)
capabilities = (Caps * 2)()
if not libc.prctl(38, 1, 0, 0, 0) == 0:
    raise AssertionError()
if external_fixture is not None:
    if libc.prctl(47, 4, 0, 0, 0) != 0:
        raise OSError(ctypes.get_errno(), "clear routed workload ambient capabilities")
    for capability in range(64):
        if libc.prctl(24, capability, 0, 0, 0) != 0:
            error = ctypes.get_errno()
            if error == errno.EINVAL:
                break
            raise OSError(error, "drop routed workload bounding capability")
    else:
        raise RuntimeError("unsupported capability range")
if not libc.capset(ctypes.byref(header), ctypes.byref(capabilities)) == 0:
    raise AssertionError()
status = dict(
    (
        line.split(":", 1)
        for line in Path("/proc/self/status").read_text().splitlines()
        if ":" in line
    )
)
capabilities_observed = {
    key: status[key].strip()
    for key in (
        ("CapEff", "CapPrm", "CapInh", "CapBnd", "CapAmb", "NoNewPrivs")
        if external_fixture is not None
        else ("CapEff", "CapPrm", "CapInh", "NoNewPrivs")
    )
}
if not all(
    (int(capabilities_observed[key], 16) == 0 for key in ("CapEff", "CapPrm", "CapInh"))
):
    raise AssertionError()
if not capabilities_observed["NoNewPrivs"] == "1":
    raise AssertionError()
if external_fixture is not None and not all(
    capabilities_observed[key] == "0000000000000000"
    for key in ("CapEff", "CapPrm", "CapInh", "CapBnd", "CapAmb")
):
    raise RuntimeError("routed workload retains capabilities")
for name in os.listdir("/proc/self/fd"):
    try:
        target = os.readlink("/proc/self/fd/" + name)
    except FileNotFoundError:
        continue
    if not "memfd:" not in target:
        raise AssertionError()
import array

with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as channel:
    channel.settimeout(25 if external_fixture is not None else 5)
    channel.connect("/control.sock")
    roots = []
    try:
        for path in ("/scratch", "/tmp", "/dev/shm", "/work", "/episode"):
            roots.append(os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW))
        channel.sendmsg(
            [b"R"], [(socket.SOL_SOCKET, socket.SCM_RIGHTS, array.array("i", roots))]
        )
    finally:
        for fd in roots:
            os.close(fd)
    if channel.recv(1) != b"1":
        raise RuntimeError("supervisor refused startup")


def timeout_state(pid):

    def read(relative):
        try:
            with open("/proc/" + relative, "rb") as source:
                raw = source.read(4097)
            if len(raw) > 4096:
                return {"unavailable": "byte_limit"}
            return raw.decode("ascii")
        except (OSError, UnicodeError) as error:
            return {"unavailable": type(error).__name__}

    children = read(str(pid) + "/task/" + str(pid) + "/children")
    ids = [int(s) for s in children.split()] if isinstance(children, str) else []
    result = {
        "observed_monotonic_ns": time.monotonic_ns(),
        "omitted_children": max(0, len(ids) - 7),
        "processes": [],
    }
    for target in [pid] + ids[:7]:
        status = read(str(target) + "/status")
        selected = (
            {
                k: v.strip()
                for line in status.splitlines()
                if ":" in line
                for k, v in [line.split(":", 1)]
                if k in ("State", "Tgid", "PPid", "Threads")
            }
            if isinstance(status, str)
            else status
        )
        result["processes"].append(
            {"pid": target, "status": selected, "wchan": read(str(target) + "/wchan")}
        )
    return result


import asyncio

sys.path.insert(0, "/fixture-code")
from payload import scripted_response

NATIVE_GUARD = Path("/fixture-code/guard.py").read_text()
sys.path.insert(0, "/fixture-deps")
import fixture as fixture_module

requests = []
errors = []
response_posts = 0
websocket_messages = []
library_events = []
deferred_close = None
stop_event = threading.Event()
ready = threading.Event()
state = {}
stop_reason = None


async def fixture_worker():
    global \
        requests, \
        errors, \
        response_posts, \
        websocket_messages, \
        library_events, \
        stop_reason, \
        deferred_close
    try:
        async with fixture_module.Fixture(
            scripted_response,
            expected_identity={
                "model": plan["base_subject"]["model_id"],
                "effort": plan["base_subject"]["effort"],
                "summary": "detailed",
            },
            capture_dir=Path("/episode/fixture-requests"),
            observation_socket="/child-observation.sock",
        ) as fixed:
            requests = fixed.http_requests
            errors = fixed.errors
            websocket_messages = fixed.messages
            library_events = fixed.library_events
            state["port"] = fixed.server.sockets[0].getsockname()[1]
            ready.set()
            while not stop_event.is_set():
                response_posts = fixed.generated
                deferred_close = fixed.deferred_close
                if fixed.stop_required:
                    stop_reason = "fixture_error"
                    stop_event.set()
                    break
                await asyncio.sleep(0.05)
            response_posts = fixed.generated
            deferred_close = fixed.deferred_close
    except Exception as error:
        errors.append(
            {
                "stage": "fixture_worker",
                "type": type(error).__name__,
                "message": str(error)[:256],
            }
        )
        stop_reason = "fixture_error"
        stop_event.set()
        state["failed"] = True
    finally:
        ready.set()


def serve_fixture():
    asyncio.run(fixture_worker())


thread = None
if external_fixture is None:
    thread = threading.Thread(target=serve_fixture, daemon=True)
    thread.start()
    if not (ready.wait(5) and (not state.get("failed")) and ("port" in state)):
        raise AssertionError()
else:
    state["port"] = external_fixture["port"]
process = None
timed_out = False
clock = {}
try:
    port = state["port"]
    address = "127.0.0.1" if external_fixture is None else external_fixture["address"]
    connection = HTTPConnection(address, port, timeout=2)
    try:
        connection.request("GET", "/__fixture_check")
        response = connection.getresponse()
        if not (
            response.version == 11
            and response.status == 200
            and (response.read() == b'{"fixture":true}')
        ):
            raise AssertionError()
    finally:
        connection.close()
    command = plan["command"][:]
    marker = command.index("--")
    command[marker:marker] = [
        "-c",
        'chatgpt_base_url="http://' + address + ":" + str(port) + '"',
        "-c",
        'openai_base_url="http://' + address + ":" + str(port) + '"',
        "-c",
        "check_for_update_on_startup=false",
    ]
    environment = plan["environment"] | {
        "CODEX_REFRESH_TOKEN_URL_OVERRIDE": "http://"
        + address
        + ":"
        + str(port)
        + "/oauth/token",
        "RUST_LOG": "codex_core::stream_events_utils=trace,codex_core::tools::router=trace,codex_core::tools::code_mode=trace,codex_core::codex=debug",
    }
    print(
        json.dumps(
            {
                "fixture_start": {
                    "command": command,
                    "environment": environment,
                    "interfaces": interfaces,
                    "capabilities": capabilities_observed,
                    "input_sha256": hashlib.sha256(payload).hexdigest(),
                    "write_errno": 30,
                    "inherited_memfd": False,
                }
            }
        ),
        flush=True,
        file=sys.stderr,
    )
    clock["before_spawn_monotonic_ns"] = time.monotonic_ns()
    process = subprocess.Popen(
        ["/usr/bin/python3", "-B", "-c", NATIVE_GUARD, str(port), json.dumps(command)],
        cwd="/work",
        env=environment,
        stdin=subprocess.DEVNULL,
        start_new_session=True,
    )
    clock["after_spawn_monotonic_ns"] = time.monotonic_ns()
    deadline = time.monotonic() + 30
    while process.poll() is None:
        if stop_event.wait(0.05):
            break
        if time.monotonic() >= deadline:
            timed_out = True
            break
finally:
    clock["poll_end_monotonic_ns"] = time.monotonic_ns()
    clock["return_before_cleanup"] = None if process is None else process.poll()
    clock["timeout_state"] = (
        timeout_state(process.pid) if timed_out and process is not None else None
    )
    if process is not None:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait(timeout=5)
    clock["after_wait_monotonic_ns"] = time.monotonic_ns()
    stop_event.set()
    if thread is not None:
        thread.join(timeout=3)
        if thread.is_alive():
            raise AssertionError()
    print(
        json.dumps(
            {
                "fixture_summary": {
                    **(
                        {"external_fixture": external_fixture}
                        if external_fixture is not None
                        else {}
                    ),
                    "diagnostic_clock": clock,
                    "native_return_code": None
                    if process is None
                    else process.returncode,
                    "native_timed_out": timed_out,
                    "requests": requests,
                    "errors": errors,
                    "scripted_generated_responses": response_posts,
                    "websocket_messages": websocket_messages,
                    "library_events": library_events,
                    "deferred_close": deferred_close,
                    "fixture_stop_reason": stop_reason,
                    "auth_unchanged": auth_path.read_bytes() == payload,
                }
            }
        ),
        flush=True,
        file=sys.stderr,
    )
if not (
    process is not None
    and (not timed_out)
    and (not errors)
    and (stop_reason is None)
    and (external_fixture is not None or response_posts == 2)
    and (process.returncode == 0)
):
    raise AssertionError()
