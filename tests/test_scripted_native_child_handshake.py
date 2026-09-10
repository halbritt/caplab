"""Real frozen cgroups establish child identity without consuming trace text."""

from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import re
import socket
import struct
import subprocess
import sys
import tempfile
import time
import unittest
import uuid

from caplab.native_child_process import FrozenNativeChildEvidence
from caplab.exec_provenance import observe_exec_tracer

REPO = Path(__file__).resolve().parents[1]
CGROUP = Path("/sys/fs/cgroup")
ENV = {"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8"}
JOIN = "import os,sys;from pathlib import Path;Path(sys.argv[1],'cgroup.procs').write_text(str(os.getpid()));os.execv(sys.argv[2],sys.argv[2:])"
LAUNCHER = """import os,socket,subprocess,sys
with socket.socket(socket.AF_UNIX,socket.SOCK_SEQPACKET) as channel:
 channel.settimeout(10);channel.connect('/control.sock');channel.sendall(b'P')
 mode=channel.recv(1)
 if mode==b'G':
  readfd,writefd=os.pipe()
  code="import os,signal,subprocess,sys;p=subprocess.Popen(['/usr/bin/sleep','20']);signal.signal(signal.SIGTERM,lambda *_:p.terminate());os.write(int(sys.argv[1]),b'R');os.close(int(sys.argv[1]));p.wait()"
  children=[subprocess.Popen(['/usr/bin/python3','-B','-c',code,str(writefd)],pass_fds=(writefd,))]
  os.close(writefd);assert os.read(readfd,1)==b'R';os.close(readfd)
 else:children=[subprocess.Popen(['/usr/bin/sleep','20'],env={'PATH':'/usr/bin:/bin','LANG':'C.UTF-8'}) for _ in range(int(mode))]
 channel.sendall(b'R');channel.recv(1)
 for child in children:child.terminate()
 for child in children:child.wait(timeout=2)
 channel.sendall(b'D');channel.recv(1)
"""


def await_field(path, key, expected):
    deadline = time.monotonic() + 2
    while (
        dict(line.split() for line in path.read_text().splitlines()).get(key)
        != expected
    ):
        if time.monotonic() >= deadline:
            raise RuntimeError("owned cgroup did not reach " + key + "=" + expected)
        time.sleep(0.01)


@contextmanager
def frozen(group):
    (group / "cgroup.freeze").write_text("1")
    try:
        await_field(group / "cgroup.events", "frozen", "1")
        yield
    finally:
        (group / "cgroup.freeze").write_text("0")
        await_field(group / "cgroup.events", "frozen", "0")


@contextmanager
def launcher(group, root, count):
    control = root / "control.sock"
    trace = root / ("trace-" + str(count))
    with socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET) as listener:
        listener.bind(str(control))
        listener.listen(1)
        listener.settimeout(5)
        command = [
            "/usr/bin/python3",
            "-B",
            "-c",
            JOIN,
            str(group),
            "/usr/bin/prlimit",
            "--fsize=65536:65536",
            "--core=0",
            "--",
            "/usr/bin/bwrap",
            "--unshare-all",
            "--die-with-parent",
            "--new-session",
            "--cap-drop",
            "ALL",
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
            "--dev",
            "/dev",
            "--ro-bind",
            str(control),
            "/control.sock",
            "--ro-bind",
            str(root / "observe.sock"),
            "/observe.sock",
            "--remount-ro",
            "/",
            "--",
            "/usr/bin/python3",
            "-B",
            "-c",
            LAUNCHER,
        ]
        command = [
            "/usr/bin/prlimit",
            "--fsize=1048576:1048576",
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
            str(trace),
            "--",
            *command,
        ]
        with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
            process = subprocess.Popen(command, env=ENV, stdout=stdout, stderr=stderr)
            try:
                channel, _ = listener.accept()
                with channel:
                    channel.settimeout(5)
                    pid, uid, gid = struct.unpack(
                        "3i",
                        channel.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, 12),
                    )
                    assert (uid, gid) == (os.getuid(), os.getgid())
                    assert channel.recv(1) == b"P"
                    descriptor = os.open(
                        f"/proc/{pid}", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
                    )
                    try:
                        tracer = observe_exec_tracer(
                            pid,
                            trace,
                            expected_tracer_executable=Path("/usr/bin/strace"),
                        )
                        channel.sendall(str(count).encode())
                        assert channel.recv(1) == b"R"
                        yield pid, descriptor, tracer
                        channel.sendall(b"X")
                        assert channel.recv(1) == b"D"
                        channel.sendall(b"X")
                    finally:
                        os.close(descriptor)
                assert process.wait(timeout=5) == 0
                stderr.seek(0)
                assert stderr.read(65537) == b""
            finally:
                (group / "cgroup.freeze").write_text("0")
                if process.poll() is None:
                    (group / "cgroup.kill").write_text("1")
                    process.wait(timeout=5)
                await_field(group / "cgroup.events", "populated", "0")
                control.unlink()
                stderr.seek(0)
                (root / "launcher.stderr").write_bytes(stderr.read(65536))


sys.path.insert(0, str(REPO / "scripts"))
from scripted_native import support

ORIGINAL_LAUNCHER = LAUNCHER


def worker(unit, root):
    global LAUNCHER
    assert re.fullmatch(r"caplab-scripted-control-[0-9a-f]{32}\.service", unit)
    member = Path("/proc/self/cgroup").read_text().strip()
    owner = (CGROUP / member[3:].lstrip("/")).parent
    assert owner.name == unit
    (owner / "cgroup.subtree_control").write_text("+memory +pids")
    group = owner / "workload"
    group.mkdir()
    for key, value in [
        ("memory.max", str(256 * 1024**2)),
        ("memory.swap.max", "0"),
        ("pids.max", "32"),
    ]:
        (group / key).write_text(value)
    before = set(os.listdir("/proc/self/fd"))
    results = []
    try:
        for mode in [
            "success",
            "wrong_peer",
            "malformed",
            "wrong_hash",
            "seal_failure",
        ]:
            case = root / mode
            case.mkdir()
            sealed = []
            raw = b"bad" if mode == "malformed" else b"a" * 64
            # The authenticated launcher sends from its own thread, inside the frozen group.
            # Its main thread retains the existing helper's shutdown/reaping protocol.
            hook = """import threading
 errors=[]
 def request():
  try:
   with socket.socket(socket.AF_UNIX,socket.SOCK_SEQPACKET) as observer:
    observer.settimeout(5);observer.connect('/observe.sock');
    try:observer.sendall(RAW);ack=observer.recv(1)
    except (BrokenPipeError,ConnectionResetError):ack=b''
    assert ack==ACK
  except Exception as error:errors.append(repr(error))
 thread=threading.Thread(target=request);thread.start()
 channel.recv(1);thread.join(6);assert not thread.is_alive() and not errors,errors"""
            hook = hook.replace("RAW", repr(raw)).replace(
                "ack==ACK", "ack==" + repr(b"1" if mode == "success" else b"")
            )
            if mode == "wrong_peer":
                # Make rejection before the sender writes observable, not schedule-dependent.
                hook = hook.replace(
                    "observer.connect('/observe.sock');",
                    "observer.connect('/observe.sock');import select;"
                    "assert select.select([observer],[],[],2)[0];",
                )
            LAUNCHER = ORIGINAL_LAUNCHER.replace(
                "channel.recv(1)\n for child", hook + "\n for child", 1
            )
            assert "def request" in LAUNCHER
            compile(LAUNCHER, "fixed-launcher", "exec")
            with socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET) as listener:
                listener.bind(str(case / "observe.sock"))
                listener.listen(1)
                listener.settimeout(5)
                with launcher(group, case, 1) as (pid, descriptor, tracer):
                    evidence = FrozenNativeChildEvidence(
                        pid,
                        descriptor,
                        Path("/usr/bin/sleep"),
                        "0" * 64
                        if mode == "wrong_hash"
                        else hashlib.sha256(
                            Path("/usr/bin/sleep").read_bytes()
                        ).hexdigest(),
                        1024**2,
                        32,
                    )

                    def seal(record):
                        assert (group / "cgroup.freeze").read_text().strip() == "0"
                        assert (
                            dict(
                                line.split()
                                for line in (group / "cgroup.events")
                                .read_text()
                                .splitlines()
                            )["frozen"]
                            == "0"
                        )
                        if mode == "seal_failure":
                            raise RuntimeError("fixed seal failure")
                        sealed.append(record)

                    try:
                        result = support.receive_child_observation(
                            listener,
                            group=group,
                            expected_peer=pid + 1 if mode == "wrong_peer" else pid,
                            evidence=evidence,
                            seal_observation=seal,
                        )
                    except (ValueError, RuntimeError) as error:
                        expected = {
                            "wrong_peer": "peer differs",
                            "malformed": "invalid child observation packet",
                            "wrong_hash": "hash differs",
                            "seal_failure": "fixed seal failure",
                        }
                        assert mode in expected and expected[mode] in str(error), (
                            mode,
                            error,
                        )
                        result = {"refusal": str(error)}
                    else:
                        assert mode == "success" and len(sealed) == 1
                        clock = result["clock"]
                        assert list(clock.values()) == sorted(clock.values())
                        assert result["observation"]["child_status"]["PPid"] == pid
                    assert (group / "cgroup.freeze").read_text().strip() == "0"
                    os.fstat(descriptor)
                (case / "observe.sock").unlink()
                results.append(
                    {"mode": mode, "result": result, "sealed": sealed, "thawed": True}
                )
    finally:
        (group / "cgroup.freeze").write_text("0")
        (group / "cgroup.kill").write_text("1")
        await_field(group / "cgroup.events", "populated", "0")
        group.rmdir()
    assert set(os.listdir("/proc/self/fd")) == before
    return {
        "unit": unit,
        "cgroup": str(owner),
        "reports": results,
        "descriptor_restoration": True,
        "workload_removed": True,
    }


class ScriptedChildHandshakeTests(unittest.TestCase):
    @unittest.skipUnless(
        Path(f"/run/user/{os.getuid()}/systemd/private").exists(),
        "requires delegated user service",
    )
    def test_handshake_authentication_observation_and_failure_thaw(self):
        with tempfile.TemporaryDirectory(
            prefix="caplab-scripted-control-"
        ) as temporary:
            root = Path(temporary)
            unit = "caplab-scripted-control-" + uuid.uuid4().hex + ".service"
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
                "--property=TasksMax=64",
                "--property=RuntimeMaxSec=45",
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
                __file__,
                "--worker",
                unit,
                str(root),
            ]
            try:
                completed = subprocess.run(
                    command, env=environment, capture_output=True, timeout=55
                )
                diagnostics = completed.stderr.decode()
                if completed.returncode:
                    for case in (
                        "success",
                        "wrong_peer",
                        "malformed",
                        "wrong_hash",
                        "seal_failure",
                    ):
                        path = root / case / "launcher.stderr"
                        if path.is_file():
                            diagnostics += "\n" + case + ": " + path.read_text()[:65536]
                self.assertEqual(completed.returncode, 0, diagnostics)
                result = json.loads(completed.stdout)
                self.assertEqual(
                    [x["mode"] for x in result["reports"]],
                    [
                        "success",
                        "wrong_peer",
                        "malformed",
                        "wrong_hash",
                        "seal_failure",
                    ],
                )
                self.assertTrue(
                    result["descriptor_restoration"] and result["workload_removed"]
                )
            finally:
                subprocess.run(
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
                    check=True,
                    timeout=5,
                )
                self.assertEqual(state.stdout.strip(), b"not-found")
            self.assertFalse(Path(result["cgroup"]).exists())


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "--worker":
        print(json.dumps(worker(sys.argv[2], Path(sys.argv[3]))))
    else:
        unittest.main()
