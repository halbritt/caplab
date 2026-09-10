"""Prepared bytes cross the real authenticated mount handoff before release."""

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import json
import os
from pathlib import Path
import shutil
import socket
import tempfile
import unittest

from caplab.process_capture import capture_process
from caplab.revbench.codex import ExactSecretStreamQuarantine
from caplab.supervised_task_capture import SupervisedTaskCapture
from caplab.task_capture import TaskCaptureLimits
from caplab.task_input import prepare_task_input
from caplab.task_capture_verify import verify_task_capture
from caplab.prepared_task_capture import verify_prepared_before
from test_mount_capture_quarantine import probe


PRODUCER = """import array,os,socket,sys
from pathlib import Path
with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as channel:
    channel.settimeout(3);channel.connect('/control.sock')
    fds=[os.open(p,os.O_RDONLY|os.O_DIRECTORY) for p in ('/scratch','/tmp','/dev/shm','/work','/episode')]
    channel.sendmsg([b'R'],[(socket.SOL_SOCKET,socket.SCM_RIGHTS,array.array('i',fds))])
    for fd in fds:os.close(fd)
    if channel.recv(1)!=b'1':sys.exit(7)
assert Path('/work/input/data.bin').read_bytes()==bytes.fromhex('00ff636166c3a9')
assert os.readlink('/work/link')=='input/data.bin'
Path('/work/capture-witness.txt').write_text('observed prepared task')
print('released with prepared task')
"""


def handoff_fixture(root, *, corrupt=False, quarantine=False):
    source = root / "source"
    source.mkdir()
    (source / "input").mkdir()
    (source / "input/data.bin").write_bytes(bytes.fromhex("00ff636166c3a9"))
    os.symlink("input/data.bin", source / "link")
    bundle = root / "input"
    anchor = prepare_task_input(
        source, output_dir=bundle, max_task_bytes=1000, max_task_entries=20
    )
    shutil.rmtree(source)
    selection = {
        "custody": str(bundle),
        "input_sha256": "0" * 64 if corrupt else anchor,
        "max_receipt_bytes": 100000,
    }
    task = root / "task"
    task.mkdir()
    attempt = root / "attempt"
    socket_path = root / "control.sock"
    member = Path("/proc/self/cgroup").read_text().strip()
    assert member.startswith("0::/")
    child = Path("/sys/fs/cgroup") / member[3:].lstrip("/")
    receipt_name = child.name.removeprefix("fixture-") + "-handoff.json"
    factory = (
        (lambda: ExactSecretStreamQuarantine((bytes.fromhex("00ff636166c3a9"),)))
        if quarantine
        else None
    )
    command = [
        "/usr/bin/bwrap",
        "--unshare-all",
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
    ]
    for mount in probe.MOUNTS:
        command += ["--size", str(64 * probe.MIB), "--tmpfs", mount]
    command += [
        "--ro-bind",
        str(socket_path),
        "/control.sock",
        "--chdir",
        "/work",
        "--remount-ro",
        "/proc",
        "--remount-ro",
        "/",
        "--",
        "/usr/bin/python3",
        "-B",
        "-c",
        PRODUCER,
    ]
    try:
        with SupervisedTaskCapture(
            command,
            task_root=task,
            namespace_root="/work",
            environment={},
            output_dir=attempt,
            limits=TaskCaptureLimits(10000, 2000, 40, 5),
            max_process_receipt_bytes=10000,
            quarantine_factory=factory,
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
                        timeout_seconds=5,
                        quarantine_factory=factory,
                    )
                    descriptors, handoff = probe.receive_mount(
                        listener,
                        child,
                        recorder,
                        usable_devices=True,
                        quarantine_factory=factory,
                        task_input=selection,
                    )
                    try:
                        assert json.loads((root / receipt_name).read_bytes()) == handoff
                    finally:
                        for descriptor in descriptors:
                            os.close(descriptor)
                    future.result(timeout=7)
            recorder.finish(
                expected_process_sha256=probe.digest(attempt / "process/capture.json")
            )
    finally:
        socket_path.unlink(missing_ok=True)
    verified = verify_task_capture(
        attempt,
        expected_attempt_sha256=probe.digest(attempt / "attempt.json"),
        max_receipt_bytes=100000,
    )
    return selection, handoff, verified


@unittest.skipUnless(
    Path("/usr/bin/bwrap").is_file(), "Bubblewrap required for descriptor fixture"
)
class PreparedTaskHandoffTests(unittest.TestCase):
    def test_bad_input_and_quarantine_refuse_without_releasing_child(self):
        descriptors = set(os.listdir("/proc/self/fd"))
        for mode in ("corrupt", "quarantine"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                with self.assertRaises(
                    ValueError if mode == "corrupt" else RuntimeError
                ):
                    handoff_fixture(root, **{mode: True})
                process = json.loads(
                    (root / "attempt/process/capture.json").read_bytes()
                )
                self.assertEqual(process["return_code"], 7)
                self.assertEqual(
                    (root / "attempt/process/native.stdout").read_bytes(), b""
                )
                self.assertEqual(list(root.glob("*-handoff.json")), [])
                self.assertFalse((root / "attempt/attempt.json").exists())
        self.assertEqual(set(os.listdir("/proc/self/fd")), descriptors)

    def test_link_tampering_and_a_different_valid_input_cannot_match_before(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            selection, handoff, _ = handoff_fixture(root)
            before = json.loads((root / "attempt/before/inventory.json").read_bytes())
            link = handoff["prepared_task"]
            sha = handoff["before_inventory_sha256"]
            self.assertTrue(
                verify_prepared_before(
                    selection, before, link, expected_before_sha256=sha
                )["prepared_content_agrees"]
            )
            changes = (
                "input",
                "before",
                "destination",
                "count",
                "boolean count",
                "verified",
            )
            for mode in changes:
                with (
                    self.subTest(mode=mode),
                    self.assertRaisesRegex(ValueError, "prepared task link differs"),
                ):
                    changed = deepcopy(link)
                    if mode == "input":
                        changed["input_sha256"] = "0" * 64
                    elif mode == "before":
                        changed["before_inventory_sha256"] = "0" * 64
                    elif mode == "destination":
                        changed["materialization"]["destination_identity"]["inode"] += 1
                    elif mode == "count":
                        changed["materialization"]["materialized_entries"] += 1
                    elif mode == "boolean count":
                        changed["materialization"]["materialized_bytes"] = True
                    else:
                        changed["materialization"]["tree_verified"] = 1
                    verify_prepared_before(
                        selection, before, changed, expected_before_sha256=sha
                    )
            source = root / "other-source"
            source.mkdir()
            (source / "input").mkdir()
            (source / "input/data.bin").write_bytes(b"different content")
            os.symlink("input/data.bin", source / "link")
            bundle = root / "other-input"
            other_sha = prepare_task_input(
                source, output_dir=bundle, max_task_bytes=1000, max_task_entries=20
            )
            other = selection | {"custody": str(bundle), "input_sha256": other_sha}
            receipt = json.loads((bundle / "input.json").read_bytes())
            changed = deepcopy(link)
            changed["input_sha256"] = other_sha
            changed["materialization"].update(
                input_sha256=other_sha,
                task_content_sha256=receipt["task_content_sha256"],
                materialized_bytes=receipt["retained_task_bytes"],
            )
            with self.assertRaisesRegex(
                ValueError, "prepared task differs from before capture"
            ):
                verify_prepared_before(
                    other, before, changed, expected_before_sha256=sha
                )

    def test_child_reads_prepared_bytes_only_after_linked_before_capture(self):
        descriptors = set(os.listdir("/proc/self/fd"))
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            selection, handoff, checked = handoff_fixture(root)
            link = handoff["prepared_task"]
            self.assertEqual(link["input_sha256"], selection["input_sha256"])
            self.assertEqual(
                link["before_inventory_sha256"], handoff["before_inventory_sha256"]
            )
            self.assertEqual(link["materialization"]["materialized_entries"], 4)
            self.assertEqual(
                checked["changes"], [{"path": "capture-witness.txt", "change": "added"}]
            )
            self.assertEqual(
                (root / "attempt/process/native.stdout").read_bytes(),
                b"released with prepared task\n",
            )
            self.assertFalse((root / "source").exists())
        self.assertEqual(set(os.listdir("/proc/self/fd")), descriptors)
