"""Exact destination policy identity and kernel enforcement before release."""

from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor
import json
import hashlib
import os
from pathlib import Path
import socket
import tempfile
import unittest

from caplab import capture_network_policy as network
from caplab.capture_network_policy import build_capture_network_policy
from caplab.process_capture import capture_process
from caplab.revbench.codex import ExactSecretStreamQuarantine
from caplab.supervised_task_capture import SupervisedTaskCapture
from caplab.task_capture import TaskCaptureLimits
from test_mount_capture_quarantine import probe


PRODUCER = r"""
import array,json,os,socket,threading
from pathlib import Path
stop=threading.Event()
listeners=[];threads=[]
def serve(listener):
    while not stop.is_set():
        try:connection,_=listener.accept()
        except socket.timeout:continue
        with connection:
            connection.settimeout(.1)
            while not stop.is_set():
                try:data=connection.recv(1)
                except socket.timeout:continue
                if not data:break
                connection.sendall(b'W')
def exchange(port, source=None):
    with socket.socket() as s:
        s.settimeout(.5)
        if source:s.bind(('127.0.0.1',source))
        s.connect(('127.0.0.1',port));s.sendall(b'P')
        assert s.recv(1)==b'W'
try:
    for port in (39071,39072):
        s=socket.socket();s.bind(('127.0.0.1',port));s.listen(4);s.settimeout(.1)
        listeners.append(s)
        t=threading.Thread(target=serve,args=(s,));t.start();threads.append(t)
    exchange(39071);exchange(39072)
    with socket.create_connection(('127.0.0.1',39072),timeout=.5) as existing:
        with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as channel:
            channel.settimeout(10);channel.connect('/control.sock')
            fds=[os.open(p,os.O_RDONLY|os.O_DIRECTORY) for p in ('/scratch','/tmp','/dev/shm','/work','/episode')]
            try:channel.sendmsg([b'R'],[(socket.SOL_SOCKET,socket.SCM_RIGHTS,array.array('i',fds))])
            finally:
                for fd in fds:os.close(fd)
            assert channel.recv(1)==b'1','no release'
        print('workload-released',flush=True)
        exchange(39071,39073)
        denied=[]
        try:exchange(39072)
        except TimeoutError:denied.append('new')
        try:
            existing.sendall(b'P');existing.recv(1)
        except TimeoutError:denied.append('established')
        assert denied==['new','established'],denied
    Path('/work/network-witness').write_text('only selected destinations replied')
    print(json.dumps({'released':True,'denied':denied}))
finally:
    stop.set()
    for t in threads:t.join(2);assert not t.is_alive()
    for s in listeners:s.close()
"""


def network_handoff(
    root,
    *,
    existing_policy=False,
    retain_privileges=False,
    quarantine_factory=None,
    installer=None,
    plan=None,
    producer=PRODUCER,
    command_prefix=(),
    root_mapping=False,
    task_input=None,
    parent_user_namespace=False,
):
    if installer is None:
        installer = network.install_capture_network_policy
    task = root / "task"
    task.mkdir()
    attempt = root / "attempt"
    socket_path = root / "control.sock"
    member = Path("/proc/self/cgroup").read_text().strip()
    child = Path("/sys/fs/cgroup") / member[3:].lstrip("/")
    receipt_name = child.name.removeprefix("fixture-") + "-handoff.json"
    plan = (
        plan
        if plan is not None
        else build_capture_network_policy(
            [
                {"address": "127.0.0.1", "port": 39071},
                {"address": "127.0.0.1", "port": 39073},
            ]
        )
    )
    command = [
        "/usr/bin/bwrap",
        "--unshare-all",
        *(["--uid", "0", "--gid", "0"] if root_mapping else []),
        "--die-with-parent",
        "--new-session",
        "--clearenv",
        "--cap-add",
        "CAP_NET_ADMIN",
        "--cap-add",
        "CAP_SETPCAP",
        *(["--cap-add", "CAP_SETFCAP"] if parent_user_namespace else []),
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
    ]
    for mount in probe.MOUNTS:
        command += ["--size", str(64 * probe.MIB), "--tmpfs", mount]
    setup = "import os,subprocess,sys;subprocess.run(['/usr/sbin/ip','link','set','lo','up'],check=True);os.execv('/usr/bin/setpriv',['/usr/bin/setpriv','--bounding-set=-all','--inh-caps=-all','--ambient-caps=-all','--no-new-privs','/usr/bin/python3','-B','-c',sys.argv[1]])"
    if parent_user_namespace:
        from test_capture_network_identity import USER_NAMESPACE_SETUP

        assert root_mapping
        setup = "import subprocess;subprocess.run(['/usr/sbin/ip','link','set','lo','up'],check=True)\n"
        setup += USER_NAMESPACE_SETUP.replace("mode=sys.argv[1]", "mode='parent'")
        setup += (
            "\nos.execv('/usr/bin/python3',['/usr/bin/python3','-B','-c',sys.argv[1]])"
        )
    if existing_policy:
        setup = setup.replace(
            "os.execv(",
            "subprocess.run(['/usr/sbin/nft','add','table','inet','existing'],check=True);os.execv(",
        )
    if retain_privileges:
        setup = "import os,subprocess,sys;subprocess.run(['/usr/sbin/ip','link','set','lo','up'],check=True);os.execv('/usr/bin/python3',['/usr/bin/python3','-B','-c',sys.argv[1]])"
    command += [
        "--ro-bind",
        str(socket_path),
        "/control.sock",
        "--chdir",
        "/work",
        *([] if parent_user_namespace else ["--remount-ro", "/proc"]),
        "--remount-ro",
        "/",
        "--",
        "/usr/bin/python3",
        "-B",
        "-c",
        setup,
        producer,
    ]
    command = [*command_prefix, *command]
    with SupervisedTaskCapture(
        command,
        task_root=task,
        namespace_root="/work",
        environment={},
        output_dir=attempt,
        limits=TaskCaptureLimits(10000, 2000, 40, 15),
        max_process_receipt_bytes=10000,
    ) as recorder:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as listener:
            listener.bind(str(socket_path))
            listener.listen(1)
            listener.settimeout(5)
            with ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(
                    capture_process,
                    command,
                    cwd=task,
                    environment={},
                    output_dir=attempt / "process",
                    max_stream_bytes=10000,
                    timeout_seconds=15,
                )
                descriptors, handoff = probe.receive_mount(
                    listener,
                    child,
                    recorder,
                    usable_devices=True,
                    task_input=task_input,
                    nested_userns=parent_user_namespace,
                    inspect_peer=lambda pid: installer(
                        plan,
                        expected_policy_sha256=plan["network_policy_sha256"],
                        peer_pid=pid,
                        output_dir=root / "network",
                        quarantine_factory=quarantine_factory,
                    ),
                )
                try:
                    assert json.loads((root / receipt_name).read_bytes()) == handoff
                finally:
                    for fd in descriptors:
                        os.close(fd)
                process = future.result(timeout=17)
        recorder.finish(
            expected_process_sha256=probe.digest(attempt / "process/capture.json")
        )
    return handoff, process


class CaptureNetworkPolicyTests(unittest.TestCase):
    def test_authenticated_handoff_installs_policy_before_releasing_workload(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            handoff, process = network_handoff(root)
            self.assertEqual(process["return_code"], 0)
            self.assertTrue(process["streams_complete"])
            self.assertEqual(
                handoff["peer_checks"]["schema"],
                "caplab.capture-network-installation/v1",
            )
            installation = handoff["peer_checks"]
            self.assertEqual(
                installation,
                json.loads((root / "network/installation.json").read_bytes()),
            )
            for name in ("initial", "install", "readback"):
                command_path = root / "network" / (name + "-command.json")
                self.assertEqual(
                    hashlib.sha256(command_path.read_bytes()).hexdigest(),
                    installation["command_sha256"][name],
                )
                self.assertEqual(
                    probe.digest(root / "network" / name / "capture.json"),
                    installation["command_receipt_sha256"][name],
                )
            output = (root / "attempt/process/native.stdout").read_bytes().splitlines()
            self.assertEqual(output[0], b"workload-released")
            self.assertEqual(
                json.loads(output[1]),
                {"released": True, "denied": ["new", "established"]},
            )
            observed = json.loads(
                (root / "network/readback/native.stdout").read_bytes()
            )
            plan = build_capture_network_policy(
                [
                    {"address": "127.0.0.1", "port": 39071},
                    {"address": "127.0.0.1", "port": 39073},
                ]
            )
            for change in (
                "accept-default",
                "extra-table",
                "missing-rule",
                "extra-accept",
                "bad-counter",
                "wrong-port",
            ):
                altered = deepcopy(observed)
                objects = altered["nftables"]
                chain = next(item["chain"] for item in objects if "chain" in item)
                rules = [item["rule"] for item in objects if "rule" in item]
                if change == "accept-default":
                    chain["policy"] = "accept"
                elif change == "extra-table":
                    objects.append(
                        {"table": {"family": "inet", "name": "foreign", "handle": 900}}
                    )
                elif change == "missing-rule":
                    objects.pop()
                elif change == "extra-accept":
                    rules[-1]["expr"] = [{"accept": None}]
                elif change == "bad-counter":
                    rules[-1]["expr"][0]["counter"]["packets"] = True
                elif change == "wrong-port":
                    rules[0]["expr"][1]["match"]["right"] = 39072
                with self.subTest(change=change), self.assertRaises(ValueError):
                    network.verify_capture_network_rules(
                        plan,
                        altered,
                        expected_policy_sha256=plan["network_policy_sha256"],
                    )
            self.assertEqual(
                observed,
                json.loads((root / "network/readback/native.stdout").read_bytes()),
            )

    def test_unsafe_peer_or_quarantine_refusal_withholds_release(self):
        for mode in ("existing", "pending-path", "privileged"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                factory = (
                    (lambda: ExactSecretStreamQuarantine((b".policy.pending",)))
                    if mode == "pending-path"
                    else None
                )
                with self.assertRaisesRegex(
                    (ValueError, RuntimeError),
                    "already has nft policy|quarantined|retains privileges",
                ):
                    network_handoff(
                        root,
                        existing_policy=mode == "existing",
                        retain_privileges=mode == "privileged",
                        quarantine_factory=factory,
                    )
                self.assertFalse((root / "network/install").exists())
                self.assertFalse((root / "network/installation.json").exists())
                if mode == "privileged":
                    self.assertFalse((root / "network").exists())
                self.assertNotIn(
                    b"workload-released",
                    (root / "attempt/process/native.stdout").read_bytes(),
                )

    def test_bad_configuration_and_supervisor_namespace_fail_before_custody_creation(
        self,
    ):
        plan = build_capture_network_policy([{"address": "127.0.0.1", "port": 443}])
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "network"
            for anchor, pid in (
                ("0" * 64, 2147483647),
                (plan["network_policy_sha256"], os.getpid()),
            ):
                with self.subTest(anchor=anchor), self.assertRaises(ValueError):
                    network.install_capture_network_policy(
                        plan,
                        expected_policy_sha256=anchor,
                        peer_pid=pid,
                        output_dir=output,
                    )
                self.assertFalse(output.exists())

    def test_endpoint_order_preserves_identity_without_borrowing_mutable_inputs(self):
        endpoints = [
            {"address": "127.0.0.1", "port": 39073},
            {"address": "127.0.0.1", "port": 39071},
        ]
        original = deepcopy(endpoints)
        plan = build_capture_network_policy(endpoints)
        self.assertEqual(plan, build_capture_network_policy(list(reversed(endpoints))))
        self.assertEqual(endpoints, original)
        endpoints[0]["port"] = 443
        self.assertEqual(plan["destinations"], list(reversed(original)))
        self.assertFalse(plan["execution_authorized"])
        self.assertFalse(plan["study_eligible"])
        self.assertNotEqual(
            plan["network_policy_sha256"],
            build_capture_network_policy(endpoints)["network_policy_sha256"],
        )

    def test_ambiguous_or_unbounded_destination_selections_are_refused(self):
        valid = {"address": "127.0.0.1", "port": 443}
        invalid = [None, {}, [], [valid, valid], [valid] * 65]
        invalid += [
            [{**valid, "port": value}] for value in (True, 443.0, "443", 0, -1, 65536)
        ]
        invalid += [
            [{**valid, "address": value}]
            for value in (
                None,
                1,
                "localhost",
                "127.0.0.1/32",
                "127.1",
                "01.2.3.4",
                "::1",
                "0.0.0.0",
                "224.0.0.1",
                "255.255.255.255",
            )
        ]
        invalid += [[{"address": "127.0.0.1"}], [{**valid, "protocol": "udp"}]]
        for value in invalid:
            with self.subTest(value=value), self.assertRaises(ValueError):
                build_capture_network_policy(value)
