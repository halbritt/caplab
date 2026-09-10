"""Supervisor observation works without a provider or child readiness message."""

from contextlib import contextmanager
from dataclasses import replace
import hashlib
import json
import os
from pathlib import Path
import socket
import struct
import subprocess
import sys
import tempfile
import time
import unittest
import uuid

REPO = Path(__file__).resolve().parents[1]
ENV = {"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8"}
PARENT = """import os,socket,subprocess,sys,time
from pathlib import Path
Path(sys.argv[1], 'cgroup.procs').write_text(str(os.getpid()))
with socket.socket(socket.AF_UNIX,socket.SOCK_SEQPACKET) as channel:
 channel.connect(sys.argv[2]); channel.sendall(b'P'); mode=channel.recv(1)
 if mode==b'D':time.sleep(.1)
 count=1 if mode==b'D' else int(mode)
 children=[subprocess.Popen(['/usr/bin/sleep','10']) for _ in range(count)]
 channel.sendall(b'R');channel.recv(1)
 for child in children:child.terminate()
 for child in children:child.wait(timeout=2)
"""


def field(group, name):
    return dict(
        line.split() for line in (group / "cgroup.events").read_text().splitlines()
    )[name]


@contextmanager
def parent(group, root, mode):
    path = root / "control.sock"
    with socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET) as listener:
        listener.bind(str(path))
        listener.listen(1)
        listener.settimeout(3)
        process = subprocess.Popen(
            ["/usr/bin/python3", "-I", "-S", "-c", PARENT, str(group), str(path)],
            env=ENV,
        )
        try:
            channel, _ = listener.accept()
            with channel:
                channel.settimeout(3)
                pid, uid, gid = struct.unpack(
                    "3i", channel.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, 12)
                )
                assert (
                    pid == process.pid
                    and (uid, gid) == (os.getuid(), os.getgid())
                    and channel.recv(1) == b"P"
                )
                fd = os.open(
                    f"/proc/{pid}",
                    os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                )
                try:
                    channel.sendall(mode.encode())
                    # The successful case deliberately has no child-ready wait.
                    if mode != "D":
                        assert channel.recv(1) == b"R"
                    yield pid, fd
                    if mode == "D":
                        assert channel.recv(1) == b"R"
                    channel.sendall(b"X")
                finally:
                    os.close(fd)
            assert process.wait(timeout=3) == 0
        finally:
            (group / "cgroup.freeze").write_text("0")
            if process.poll() is None:
                (group / "cgroup.kill").write_text("1")
                process.wait(timeout=3)
            path.unlink()


def worker(unit, root):
    from caplab.native_child_observation import (
        wait_for_native_child,
        NativeChildObservationError,
    )
    from caplab.native_child_process import FrozenNativeChildEvidence

    membership = Path("/proc/self/cgroup").read_text().strip()
    owner = Path("/sys/fs/cgroup") / membership[3:].lstrip("/")
    assert owner.name == "supervisor" and owner.parent.name == unit
    group = owner.parent / "workload"
    group.mkdir()
    reports = []
    initial = set(os.listdir("/proc/self/fd"))
    try:
        for mode in ("D", "0", "2", "1"):
            with parent(group, root, mode) as (pid, fd):
                evidence = FrozenNativeChildEvidence(
                    pid,
                    fd,
                    Path("/usr/bin/sleep"),
                    hashlib.sha256(Path("/usr/bin/sleep").read_bytes()).hexdigest(),
                    1024**2,
                    8,
                )
                before = set(os.listdir("/proc/self/fd"))
                if mode == "D":
                    record = wait_for_native_child(
                        group, evidence=evidence, timeout_seconds=2
                    )
                    assert record["observation"]["child_status"]["PPid"] == pid
                    assert (
                        record["poll_count"] > 1
                        and record["profile"] == "supervisor-poll/v1"
                    )
                    assert (
                        record["clock"]["thawed_monotonic_ns"]
                        >= record["observation"]["finished_monotonic_ns"]
                    )
                else:
                    if mode == "1":
                        evidence = replace(
                            evidence, expected_executable_sha256="0" * 64
                        )
                    with unittest.TestCase().assertRaises(
                        NativeChildObservationError
                    ) as failure:
                        wait_for_native_child(
                            group, evidence=evidence, timeout_seconds=0.2
                        )
                    record = failure.exception.record
                    assert record["error_code"] == (
                        "native_child_wait_timed_out"
                        if mode == "0"
                        else "native_child_observation_failed"
                    )
                    if mode == "1":
                        assert (
                            record["clock"]["thawed_monotonic_ns"]
                            >= record["clock"]["freeze_requested_monotonic_ns"]
                        )
                assert field(group, "frozen") == "0"
                assert os.fstat(fd).st_ino == Path(f"/proc/{pid}").stat().st_ino
                assert set(os.listdir("/proc/self/fd")) == before
                reports.append(record)
    finally:
        (group / "cgroup.freeze").write_text("0")
        (group / "cgroup.kill").write_text("1")
        deadline = time.monotonic() + 2
        while field(group, "populated") != "0":
            assert time.monotonic() < deadline
            time.sleep(0.01)
        group.rmdir()
    assert set(os.listdir("/proc/self/fd")) == initial
    return {
        "unit": unit,
        "cgroup": str(owner.parent),
        "reports": reports,
        "workload_removed": not group.exists(),
    }


class NativeChildObservationTests(unittest.TestCase):
    @unittest.skipUnless(
        Path(f"/run/user/{os.getuid()}/systemd/private").exists(),
        "requires delegated systemd user service",
    )
    def test_wait_observe_timeout_ambiguity_and_thaw_after_failure(self):
        with tempfile.TemporaryDirectory(
            prefix="caplab-native-observation-test-"
        ) as temporary:
            root = Path(temporary)
            unit = "caplab-native-observation-" + uuid.uuid4().hex + ".service"
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
                "--property=MemoryMax=134217728",
                "--property=MemorySwapMax=0",
                "--property=TasksMax=32",
                "--property=RuntimeMaxSec=15",
                "--property=KillMode=control-group",
                "--property=LimitCORE=0",
                "--",
                "/usr/bin/env",
                "-i",
                "PATH=/usr/bin:/bin",
                "LANG=C.UTF-8",
                "PYTHONPATH=" + str(REPO / "src"),
                "/usr/bin/python3",
                "-B",
                str(Path(__file__).resolve()),
                "--worker",
                unit,
                str(root),
            ]
            try:
                completed = subprocess.run(
                    command, env=environment, capture_output=True, timeout=20
                )
                self.assertEqual(completed.returncode, 0, completed.stderr.decode())
                result = json.loads(completed.stdout)
                self.assertEqual(len(result["reports"]), 4)
                self.assertTrue(result["workload_removed"])
                from caplab.native_child_observation import (
                    inspect_supervisor_child_observation,
                )
                from copy import deepcopy

                record = result["reports"][0]
                arguments = dict(
                    expected_parent_pid=record["observation"]["parent_pid"],
                    expected_supervisor_pid=record["supervisor_pid"],
                    not_before_monotonic_ns=record["clock"]["started_monotonic_ns"],
                    not_after_monotonic_ns=record["clock"]["finished_monotonic_ns"],
                )
                timing = inspect_supervisor_child_observation(record, **arguments)
                self.assertFalse(timing["provider_signal_required"])
                self.assertGreater(timing["wait_nanoseconds"], 0)
                for defect in (
                    "wrong_parent",
                    "wrong_supervisor",
                    "clock",
                    "failed_capture",
                ):
                    changed = deepcopy(record)
                    if defect == "wrong_parent":
                        changed["observation"]["parent_pid"] += 1
                    elif defect == "wrong_supervisor":
                        changed["supervisor_pid"] += 1
                    elif defect == "clock":
                        changed["clock"]["thawed_monotonic_ns"] = 1
                    else:
                        changed = result["reports"][1]
                    with self.subTest(defect=defect), self.assertRaises(ValueError):
                        inspect_supervisor_child_observation(changed, **arguments)
            finally:
                subprocess.run(
                    ["/usr/bin/systemctl", "--user", "stop", unit],
                    env=environment,
                    capture_output=True,
                    timeout=3,
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
                    timeout=3,
                )
                self.assertEqual(state.stdout.strip(), b"not-found")
            self.assertFalse(Path(result["cgroup"]).exists())


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "--worker":
        print(json.dumps(worker(sys.argv[2], Path(sys.argv[3]))))
    else:
        unittest.main()
