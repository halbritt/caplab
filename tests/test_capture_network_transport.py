"""Restricted routing through actual capture handoff in a disconnected outer net."""

from contextlib import ExitStack
import hashlib
import json
import os
from pathlib import Path
import queue
import socket
import subprocess
import sys
import tempfile
import threading
import time
import unittest

from caplab.process_capture import capture_process
from caplab.capture_network_policy import build_capture_network_policy
from test_capture_network_policy import network_handoff
from caplab.revbench.codex import ExactSecretStreamQuarantine

REPO = Path(__file__).resolve().parents[1]
PRODUCER = r"""
import array,json,os,socket
with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as channel:
    channel.settimeout(10);channel.connect('/control.sock')
    fds=[os.open(p,os.O_RDONLY|os.O_DIRECTORY) for p in ('/scratch','/tmp','/dev/shm','/work','/episode')]
    try:channel.sendmsg([b'R'],[(socket.SOL_SOCKET,socket.SCM_RIGHTS,array.array('i',fds))])
    finally:
        for fd in fds:os.close(fd)
    assert channel.recv(1)==b'1','no release'
print('workload-released',flush=True)
outcomes={}
for name,host,port in [('allowed','198.18.0.1',39071),('wrong-port','198.18.0.1',39072),('internal','100.64.0.1',39071)]:
    try:
        with socket.create_connection((host,port),timeout=.5) as s:
            outcomes[name]=s.recv(1)==b'W'
    except TimeoutError:outcomes[name]=False
assert outcomes=={'allowed':True,'wrong-port':False,'internal':False},outcomes
print(json.dumps(outcomes),flush=True)
"""


def namespaces():
    return {k: os.readlink("/proc/self/ns/" + k) for k in ("user", "net", "pid")}


def outer(root, host, mode, namespace_profile="workload-user/v1"):
    from caplab.capture_network_transport import capture_routed_network

    own = namespaces()
    assert all(own[k] != host[k] for k in own)
    links = json.loads(subprocess.check_output(["/usr/sbin/ip", "-j", "link"]))
    routes = json.loads(subprocess.check_output(["/usr/sbin/ip", "-j", "route"]))
    assert [x["ifname"] for x in links] == ["lo"] and routes == []
    subprocess.run(["/usr/sbin/ip", "link", "set", "lo", "up"], check=True)
    for address in ("198.18.0.1", "100.64.0.1"):
        subprocess.run(
            ["/usr/sbin/ip", "addr", "add", address + "/32", "dev", "lo"], check=True
        )
    stop = threading.Event()
    errors = queue.Queue()
    listeners, threads = [], []

    def serve(listener):
        try:
            while not stop.is_set():
                try:
                    connection, _ = listener.accept()
                except socket.timeout:
                    continue
                with connection:
                    connection.settimeout(0.5)
                    connection.sendall(b"W")
        except Exception as error:
            errors.put(error)

    before_fds = set(os.listdir("/proc/self/fd"))
    result = {
        "host_namespaces": host,
        "outer_namespaces": own,
        "mode": mode,
        "initial_interfaces": links,
        "initial_routes": routes,
    }
    try:
        targets = [("198.18.0.1", 39071), ("198.18.0.1", 39072), ("100.64.0.1", 39071)]
        for target in targets:
            listener = socket.socket()
            listeners.append(listener)
            listener.bind(target)
            listener.listen(4)
            listener.settimeout(0.1)
            thread = threading.Thread(target=serve, args=(listener,))
            thread.start()
            threads.append(thread)
        for target in targets:
            with socket.create_connection(target, timeout=0.5) as connection:
                assert connection.recv(1) == b"W"
        plan = build_capture_network_policy([{"address": "198.18.0.1", "port": 39071}])
        try:
            with ExitStack() as stack:

                def install(
                    plan,
                    *,
                    expected_policy_sha256,
                    peer_pid,
                    output_dir,
                    quarantine_factory,
                ):
                    ready = stack.enter_context(
                        capture_routed_network(
                            plan,
                            expected_policy_sha256=expected_policy_sha256,
                            peer_pid=peer_pid,
                            output_dir=output_dir,
                            timeout_seconds=2 if mode == "timeout" else 8,
                            quarantine_factory=quarantine_factory,
                            namespace_profile=namespace_profile,
                        )
                    )
                    if mode == "body-error":
                        raise RuntimeError("fixture body failed after readiness")
                    return ready

                handoff, process = network_handoff(
                    root,
                    installer=install,
                    plan=plan,
                    producer=PRODUCER.replace(
                        "print('workload-released'",
                        "import subprocess;subprocess.run(['/usr/bin/bwrap','--unshare-user','--ro-bind','/','/','--proc','/proc','--','/usr/bin/true'],check=True,timeout=3)\nprint('workload-released'",
                    )
                    if namespace_profile == "parent-user/v1"
                    else PRODUCER,
                    root_mapping=True,
                    parent_user_namespace=namespace_profile == "parent-user/v1",
                    command_prefix=(
                        "/usr/bin/setpriv",
                        "--bounding-set=-all",
                        "--inh-caps=-all",
                        "--ambient-caps=-all",
                        "--no-new-privs",
                    ),
                    quarantine_factory=(
                        lambda: ExactSecretStreamQuarantine((b"--disable-dns",))
                    )
                    if mode == "quarantine"
                    else None,
                )
                assert process["return_code"] == 0 and process["streams_complete"], (
                    process
                )
                result.update(handoff=handoff, process=process)
                if mode == "timeout":
                    time.sleep(2.2)
        except (RuntimeError, ValueError, TimeoutError) as error:
            if mode == "normal":
                raise
            result["error"] = {"type": type(error).__name__, "message": str(error)}
        else:
            assert mode == "normal", "fixture failure was not propagated"
        assert namespaces() == own
        result["baseline_targets"] = targets
    finally:
        stop.set()
        for thread in threads:
            thread.join(2)
            assert not thread.is_alive()
        for listener in listeners:
            listener.close()
    assert errors.empty(), list(errors.queue)
    assert before_fds == set(os.listdir("/proc/self/fd"))
    result["descriptor_population_preserved"] = True
    (root / "result.json").write_text(json.dumps(result, indent=2) + "\n")


def run_outer(root, mode="normal", *, namespace_profile="workload-user/v1"):
    host = namespaces()
    (root / "etc").mkdir()
    (root / "etc/resolv.conf").write_text("nameserver 198.18.0.53\n")
    command = [
        "/usr/bin/bwrap",
        "--unshare-user",
        "--unshare-net",
        "--unshare-pid",
        "--unshare-ipc",
        "--unshare-uts",
        "--die-with-parent",
        "--new-session",
        "--clearenv",
    ]
    for cap in ("SYS_ADMIN", "NET_ADMIN", "SETPCAP", "NET_BIND_SERVICE"):
        command += ["--cap-add", "CAP_" + cap]
    command += [
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
        "--ro-bind",
        "/sys/fs/cgroup",
        "/sys/fs/cgroup",
        "--ro-bind",
        str(REPO),
        str(REPO),
        "--bind",
        str(root),
        str(root),
        "--ro-bind",
        str(root / "etc"),
        "/etc",
        "--dir",
        "/run",
    ]
    for device in ("/dev/null", "/dev/urandom", "/dev/net/tun"):
        if mode == "missing-tun" and device == "/dev/net/tun":
            continue
        command += ["--dev-bind", device, device]
    env = {
        "PATH": "/usr/bin:/usr/sbin:/bin",
        "LANG": "C.UTF-8",
        "PYTHONPATH": str(REPO / "src") + ":" + str(REPO / "tests"),
    }
    for key, value in env.items():
        command += ["--setenv", key, value]
    command += [
        "--",
        "/usr/bin/python3",
        "-B",
        str(Path(__file__).resolve()),
        "outer",
        str(root),
        json.dumps(host),
        mode,
        namespace_profile,
    ]
    (root / "command.json").write_text(
        json.dumps({"command": command, "environment": env}, indent=2) + "\n"
    )
    process = capture_process(
        command,
        cwd=root,
        environment=env,
        output_dir=root / "outer",
        max_stream_bytes=128 * 1024,
        timeout_seconds=30,
    )
    assert namespaces() == host
    return process


class CaptureNetworkTransportTests(unittest.TestCase):
    def test_routed_handoff_enforces_destinations_and_stops_helper_normally(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            process = run_outer(root)
            self.assertEqual(
                process["return_code"], 0, (root / "outer/native.stderr").read_text()
            )
            self.assertTrue(process["streams_complete"])
            result = json.loads((root / "result.json").read_bytes())
            self.assertTrue(result["descriptor_population_preserved"])
            terminal = json.loads((root / "network/terminal.json").read_bytes())
            self.assertTrue(terminal["normal_shutdown"])
            self.assertTrue(terminal["body_completed"])
            ready = root / "network/ready.json"
            self.assertEqual(
                terminal["ready_sha256"], hashlib.sha256(ready.read_bytes()).hexdigest()
            )
            self.assertEqual(
                result["handoff"]["peer_checks"], json.loads(ready.read_bytes())
            )
            command = root / "network/command.json"
            self.assertEqual(
                terminal["command_sha256"],
                hashlib.sha256(command.read_bytes()).hexdigest(),
            )
            captured = root / "network/process/capture.json"
            self.assertEqual(
                terminal["capture_sha256"],
                hashlib.sha256(captured.read_bytes()).hexdigest(),
            )
            policy_capture = json.loads(
                (root / "network/policy/readback/capture.json").read_bytes()
            )
            self.assertLessEqual(
                policy_capture["finished_monotonic_ns"],
                json.loads(captured.read_bytes())["started_monotonic_ns"],
            )
            output = (root / "attempt/process/native.stdout").read_text().splitlines()
            self.assertEqual(output[0], "workload-released")
            self.assertEqual(
                json.loads(output[1]),
                {"allowed": True, "wrong-port": False, "internal": False},
            )

    def test_failure_paths_preserve_errors_and_close_owned_transport(self):
        for mode in ("missing-tun", "body-error", "timeout", "quarantine"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                process = run_outer(root, mode)
                self.assertEqual(
                    process["return_code"],
                    0,
                    (root / "outer/native.stderr").read_text(),
                )
                self.assertTrue(process["streams_complete"])
                result = json.loads((root / "result.json").read_bytes())
                self.assertTrue(result["descriptor_population_preserved"])
                expected = (
                    "fixture body failed"
                    if mode == "body-error"
                    else "quarantined"
                    if mode == "quarantine"
                    else "did not stop normally"
                )
                self.assertIn(expected, result["error"]["message"])
                if mode != "timeout":
                    self.assertNotIn(
                        b"workload-released",
                        (root / "attempt/process/native.stdout").read_bytes(),
                    )
                if mode == "quarantine":
                    self.assertFalse((root / "network/process").exists())
                    self.assertFalse((root / "network/terminal.json").exists())
                    continue
                terminal = json.loads((root / "network/terminal.json").read_bytes())
                self.assertEqual(terminal["normal_shutdown"], mode == "body-error")
                self.assertEqual(terminal["body_completed"], mode == "timeout")
                capture = json.loads(
                    (root / "network/process/capture.json").read_bytes()
                )
                if mode == "timeout":
                    self.assertEqual(capture["termination"], "timeout")
                    self.assertFalse(capture["streams_complete"])
                else:
                    self.assertTrue(capture["streams_complete"])
                if mode == "missing-tun":
                    self.assertIsNone(terminal["ready_sha256"])
                    self.assertFalse((root / "network/ready.json").exists())

    def test_invalid_lifetime_or_policy_is_refused_before_peer_access(self):
        from caplab.capture_network_transport import capture_routed_network

        plan = build_capture_network_policy([{"address": "198.18.0.1", "port": 443}])
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "network"
            for lifetime in (True, 0, -1, 301, float("nan"), float("inf"), "8"):
                with self.subTest(lifetime=lifetime), self.assertRaises(ValueError):
                    with capture_routed_network(
                        plan,
                        expected_policy_sha256=plan["network_policy_sha256"],
                        peer_pid=2147483647,
                        output_dir=output,
                        timeout_seconds=lifetime,
                    ):
                        self.fail("invalid lifetime reached the body")
                self.assertFalse(output.exists())
            with self.assertRaises(ValueError):
                with capture_routed_network(
                    plan,
                    expected_policy_sha256="0" * 64,
                    peer_pid=2147483647,
                    output_dir=output,
                    timeout_seconds=8,
                ):
                    self.fail("unanchored policy reached the body")
            self.assertFalse(output.exists())


if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "outer":
    outer(Path(sys.argv[2]), json.loads(sys.argv[3]), sys.argv[4], sys.argv[5])
