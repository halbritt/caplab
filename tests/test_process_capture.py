"""Model-free qualification of bounded stream capture and owned process cleanup."""

import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

from caplab.process_capture import capture_process
import caplab.process_capture as capture


class ProcessCaptureTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.out = self.root / "capture"

    def run_child(self, code, *, limit=262144, timeout=3):
        return capture_process([sys.executable, "-c", code], cwd=self.root,
                               environment={"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8"},
                               output_dir=self.out, max_stream_bytes=limit,
                               timeout_seconds=timeout)

    def verify_receipt(self, receipt):
        self.assertEqual(json.loads((self.out / "capture.json").read_bytes()), receipt)
        self.assertEqual(self.out.stat().st_mode & 0o777, 0o700)
        total = 0
        for name in ("stdout", "stderr"):
            path = self.out / ("native." + name)
            raw = path.read_bytes()
            total += len(raw)
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            self.assertEqual(receipt["streams"][name]["bytes"], len(raw))
            self.assertEqual(receipt["streams"][name]["sha256"], hashlib.sha256(raw).hexdigest())
        self.assertEqual(receipt["retained_stream_bytes"], total)
        self.assertLessEqual(total, receipt["max_stream_bytes"])
        self.assertEqual((self.out / "capture.json").stat().st_mode & 0o777, 0o600)

    def test_binary_streams_preserved_without_decoding_or_pipe_deadlock(self):
        receipt = self.run_child("import os\nfor i in range(512):\n os.write(1,bytes(range(256)))\n os.write(2,bytes(reversed(range(256))))")
        self.assertEqual((self.out / "native.stdout").read_bytes(), bytes(range(256)) * 512)
        self.assertEqual((self.out / "native.stderr").read_bytes(), bytes(reversed(range(256))) * 512)
        self.assertEqual(receipt["termination"], "exited")
        self.assertTrue(receipt["streams_complete"])
        self.assertEqual(receipt["return_code"], 0)
        for stream in receipt["streams"].values():
            self.assertLessEqual(receipt["started_monotonic_ns"], stream["first_receipt_monotonic_ns"])
            self.assertLessEqual(stream["first_receipt_monotonic_ns"], stream["last_receipt_monotonic_ns"])
            self.assertLessEqual(stream["last_receipt_monotonic_ns"], receipt["finished_monotonic_ns"])
        self.verify_receipt(receipt)

    def test_shared_quota_retains_exact_prefix_and_marks_incomplete(self):
        for descriptor in (1, 2):
            with self.subTest(descriptor=descriptor):
                self.out = self.root / str(descriptor)
                first_path = str(self.out / ("native.stderr" if descriptor == 1 else "native.stdout"))
                code = (f"import os,time\nfrom pathlib import Path\nos.write({3-descriptor},b'abc')\n"
                        f"while Path({first_path!r}).stat().st_size < 3: time.sleep(.005)\n"
                        f"os.write({descriptor},b'x'*2000)\ntime.sleep(30)")
                receipt = self.run_child(code, limit=1000)
                self.assertEqual(receipt["termination"], "byte-limit")
                self.assertFalse(receipt["streams_complete"])
                self.assertEqual(receipt["retained_stream_bytes"], 1000)
                self.assertEqual(receipt["return_code"], -signal.SIGKILL)
                self.verify_receipt(receipt)
                name = "stdout" if descriptor == 1 else "stderr"
                other = "stderr" if descriptor == 1 else "stdout"
                self.assertEqual((self.out / ("native." + other)).read_bytes(), b"abc")
                self.assertEqual((self.out / ("native." + name)).read_bytes(), b"x"*997)

    def test_exact_limit_is_complete_when_no_extra_byte_arrives(self):
        receipt = self.run_child("import os; os.write(1,b'x'*17)", limit=17)
        self.assertEqual(receipt["termination"], "exited")
        self.assertTrue(receipt["streams_complete"])
        self.verify_receipt(receipt)

    def test_nonzero_exit_is_preserved_not_reclassified_as_success(self):
        receipt = self.run_child("import sys; sys.stderr.write('failure'); sys.exit(7)")
        self.assertEqual(receipt["return_code"], 7)
        self.assertTrue(receipt["streams_complete"])
        self.verify_receipt(receipt)

    def test_empty_streams_and_explicit_environment(self):
        with patch.dict(os.environ, {"CAPLAB_TEST_AMBIENT": "must-not-inherit"}):
            receipt = self.run_child("import os; assert 'CAPLAB_TEST_AMBIENT' not in os.environ")
        self.assertEqual(receipt["return_code"], 0)
        self.assertTrue(receipt["streams_complete"])
        self.assertTrue(all(s["first_receipt_monotonic_ns"] is None for s in receipt["streams"].values()))
        self.verify_receipt(receipt)

    def test_timeout_retains_prefix_and_kills_leader(self):
        receipt = self.run_child("import os,time; os.write(1,b'prefix'); time.sleep(30)", timeout=.2)
        self.assertEqual(receipt["termination"], "timeout")
        self.assertEqual(receipt["return_code"], -signal.SIGKILL)
        self.assertFalse(receipt["streams_complete"])
        self.assertEqual((self.out / "native.stdout").read_bytes(), b"prefix")
        self.verify_receipt(receipt)

    def test_exited_leader_with_inherited_pipes_cannot_hide_a_timeout(self):
        processes = []
        real_popen = subprocess.Popen
        def retain(*args, **kwargs):
            process = real_popen(*args, **kwargs)
            processes.append(process)
            return process
        def cleanup():
            for process in processes:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
        self.addCleanup(cleanup)
        with patch.object(capture.subprocess, "Popen", side_effect=retain):
            receipt = self.run_child("import os,time\npid=os.fork()\nif pid:\n os._exit(0)\nos.write(1,str(os.getpid()).encode()); time.sleep(30)", timeout=.3)
        self.assertEqual(receipt["termination"], "timeout")
        self.assertEqual(receipt["return_code"], 0)
        self.assertFalse(receipt["streams_complete"])
        child_pid = int((self.out / "native.stdout").read_bytes())
        deadline = time.monotonic() + 1
        while True:
            try:
                state = Path(f"/proc/{child_pid}/stat").read_text().split(") ", 1)[1].split()[0]
            except FileNotFoundError:
                break
            if state == "Z":
                break
            if time.monotonic() >= deadline:
                self.fail("same-group child still running after capture returned")
            time.sleep(.01)
        self.verify_receipt(receipt)

    def test_existing_custody_prevents_launch_and_preserves_contents(self):
        self.out.mkdir()
        sentinel = self.out / "native.stdout"
        sentinel.write_bytes(b"existing")
        with patch.object(capture.subprocess, "Popen") as launch:
            with self.assertRaises(FileExistsError):
                self.run_child("raise AssertionError('must not launch')")
            launch.assert_not_called()
        self.assertEqual(sentinel.read_bytes(), b"existing")

    def test_invalid_limits_fail_before_custody_or_launch(self):
        for limit, timeout in [(True,1),(0,1),(-1,1),(1.0,1),(1,True),(1,0),(1,float('inf')),(1,float('nan'))]:
            with self.subTest(limit=limit, timeout=timeout), patch.object(capture.subprocess,"Popen") as launch:
                with self.assertRaises(ValueError):
                    self.run_child("pass", limit=limit, timeout=timeout)
                launch.assert_not_called()
                self.assertFalse(self.out.exists())

    def test_launch_failure_leaves_no_completion_receipt(self):
        with self.assertRaises(FileNotFoundError):
            capture_process([str(self.root / 'missing-executable')], cwd=self.root, environment={},
                            output_dir=self.out, max_stream_bytes=10, timeout_seconds=1)
        self.assertFalse((self.out / "capture.json").exists())
        self.assertEqual((self.out / "native.stdout").read_bytes(), b"")

    def test_storage_failure_kills_and_reaps_child_and_never_seals_success(self):
        processes = []
        real_popen = subprocess.Popen
        def retain(*args, **kwargs):
            process = real_popen(*args, **kwargs)
            processes.append(process)
            return process
        with patch.object(capture.subprocess,"Popen",side_effect=retain), patch.object(capture,"_write_all",side_effect=OSError("disk failure")):
            with self.assertRaisesRegex(OSError,"disk failure"):
                self.run_child("import os,time; os.write(1,b'prefix'); time.sleep(30)")
        self.assertEqual(len(processes),1)
        self.assertEqual(processes[0].poll(),-signal.SIGKILL)
        self.assertFalse((self.out / "capture.json").exists())

    def test_receipt_sync_failure_leaves_only_unsealed_capture(self):
        real_fsync = os.fsync
        calls = 0
        def fail_receipt(fd):
            nonlocal calls
            calls += 1
            if calls == 3:
                raise OSError("receipt sync failed")
            real_fsync(fd)
        with patch.object(capture.os, "fsync", side_effect=fail_receipt):
            with self.assertRaisesRegex(OSError, "receipt sync failed"):
                self.run_child("import os; os.write(1,b'retained')")
        self.assertEqual((self.out / "native.stdout").read_bytes(), b"retained")
        self.assertFalse((self.out / "capture.json").exists())

    def test_directory_sync_failure_removes_published_receipt(self):
        real_fsync = os.fsync
        calls = 0
        def fail_directory(fd):
            nonlocal calls
            calls += 1
            if calls == 4:
                raise OSError("directory sync failed")
            real_fsync(fd)
        with patch.object(capture.os, "fsync", side_effect=fail_directory):
            with self.assertRaisesRegex(OSError, "directory sync failed"):
                self.run_child("import os; os.write(1,b'retained')")
        self.assertEqual((self.out / "native.stdout").read_bytes(), b"retained")
        self.assertFalse((self.out / "capture.json").exists())

    def test_cancellation_kills_and_reaps_child(self):
        processes = []
        real_popen = subprocess.Popen
        def retain(*args, **kwargs):
            process = real_popen(*args, **kwargs)
            processes.append(process)
            return process
        with patch.object(capture.subprocess, "Popen", side_effect=retain), patch.object(capture, "_write_all", side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                self.run_child("import os,time; os.write(1,b'prefix'); time.sleep(30)")
        self.assertEqual(processes[0].poll(), -signal.SIGKILL)
        self.assertFalse((self.out / "capture.json").exists())

    def test_closed_pipes_do_not_hide_a_running_process(self):
        receipt = self.run_child("import os,time; os.close(1); os.close(2); time.sleep(30)", timeout=.2)
        self.assertEqual(receipt["termination"], "timeout")
        self.assertEqual(receipt["return_code"], -signal.SIGKILL)
        self.assertFalse(receipt["streams_complete"])
        self.assertTrue(all(s["eof"] for s in receipt["streams"].values()))

    def test_short_disk_writes_preserve_all_bytes(self):
        real_write = os.write
        with patch.object(capture.os, "write", side_effect=lambda fd, data: real_write(fd, data[:7])):
            receipt = self.run_child("import os; os.write(1,bytes(range(256)))")
        self.assertEqual((self.out / "native.stdout").read_bytes(), bytes(range(256)))
        self.verify_receipt(receipt)


if __name__ == "__main__":
    unittest.main()
