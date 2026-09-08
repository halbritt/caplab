"""Rollout leaf-file and sync failures must withhold attestation."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from caplab.artifact_rater import (
    CalibrationError, preserve_rollout_attestation, read_rollout_attestation,
)


def rollout():
    return (json.dumps({"type": "session_meta", "payload": {"id": "thread-1", "cli_version": "fixture"}})
            + "\n" + json.dumps({"type": "turn_context", "payload": {"model": "fixture", "effort": "low"}})
            + "\n").encode()


class RolloutFileBoundaryTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.source = self.root / "source.jsonl"
        self.source.write_bytes(rollout())
        self.custody = self.root / "custody.jsonl"

    def test_linked_source_is_rejected_without_copying_target(self):
        link = self.root / "link.jsonl"
        link.symlink_to(self.source)
        with self.assertRaises(CalibrationError):
            preserve_rollout_attestation(link, self.custody, "thread-1")
        self.assertFalse(self.custody.exists())
        self.assertEqual(self.source.read_bytes(), rollout())

    def test_direct_attestation_refuses_a_linked_leaf(self):
        self.custody.symlink_to(self.source)
        with self.assertRaises(CalibrationError):
            read_rollout_attestation(self.custody, "thread-1")
        self.assertTrue(self.custody.is_symlink())

    def test_fifo_source_custody_and_direct_reads_fail_without_waiting_for_a_writer(self):
        fifo = self.root / "fifo"
        os.mkfifo(fifo)
        calls = [
            f"preserve_rollout_attestation(Path({str(fifo)!r}),Path({str(self.custody)!r}),'thread-1')",
            f"preserve_rollout_attestation(Path({str(self.source)!r}),Path({str(fifo)!r}),'thread-1')",
            f"read_rollout_attestation(Path({str(fifo)!r}),'thread-1')",
        ]
        for call in calls:
            code = ("from pathlib import Path\nfrom caplab.artifact_rater import *\n"
                    "try:\n " + call + "\nexcept CalibrationError:\n print('rejected')\n"
                    "else:\n raise AssertionError('special file accepted')\n")
            with self.subTest(call=call):
                result = subprocess.run([sys.executable, "-c", code], capture_output=True, timeout=2)
                self.assertEqual(result.returncode, 0, result.stderr.decode())
                self.assertEqual(result.stdout, b"rejected\n")

    def test_file_sync_failure_withholds_attestation_and_retains_bytes(self):
        with patch("caplab.artifact_rater.os.fsync", side_effect=OSError("file sync failed")):
            with self.assertRaisesRegex(CalibrationError, "file sync failed"):
                preserve_rollout_attestation(self.source, self.custody, "thread-1")
        self.assertEqual(self.custody.read_bytes(), rollout())

    def test_directory_sync_failure_withholds_attestation_and_retry_syncs_again(self):
        real_sync = os.fsync
        calls = []
        def fail_directory(fd):
            calls.append(Path(os.readlink(f"/proc/self/fd/{fd}")))
            if calls[-1].is_dir():
                raise OSError("directory sync failed")
            real_sync(fd)
        with patch("caplab.artifact_rater.os.fsync", side_effect=fail_directory):
            with self.assertRaisesRegex(CalibrationError, "directory sync failed"):
                preserve_rollout_attestation(self.source, self.custody, "thread-1")
        self.assertEqual(calls, [self.custody, self.root])
        self.assertEqual(self.custody.read_bytes(), rollout())
        before = self.custody.stat()
        with patch("caplab.artifact_rater.os.fsync", wraps=real_sync) as sync:
            attestation = preserve_rollout_attestation(self.source, self.custody, "thread-1")
        self.assertEqual(sync.call_count, 2)
        self.assertEqual(self.custody.stat().st_mtime_ns, before.st_mtime_ns)
        self.assertEqual(attestation["model"], "fixture")

    def test_identical_reuse_does_not_bypass_a_failed_sync(self):
        self.custody.write_bytes(rollout())
        with patch("caplab.artifact_rater.os.fsync", side_effect=OSError("reuse sync failed")):
            with self.assertRaisesRegex(CalibrationError, "reuse sync failed"):
                preserve_rollout_attestation(self.source, self.custody, "thread-1")
        self.assertEqual(self.custody.read_bytes(), rollout())

    def test_reuse_refuses_a_leaf_replaced_after_the_symlink_check(self):
        self.custody.write_bytes(rollout())
        is_symlink = Path.is_symlink
        def replace_after_check(path):
            observed = is_symlink(path)
            if path == self.custody:
                path.unlink()
                path.symlink_to(self.source)
            return observed
        with patch.object(Path, "is_symlink", replace_after_check):
            with self.assertRaises(CalibrationError):
                preserve_rollout_attestation(self.source, self.custody, "thread-1")
        self.assertTrue(self.custody.is_symlink())
        self.assertEqual(self.source.read_bytes(), rollout())

    def test_opened_descriptor_is_closed_if_stream_setup_fails(self):
        real_open = os.open
        descriptors = []
        def retain_fd(*args, **kwargs):
            fd = real_open(*args, **kwargs)
            descriptors.append(fd)
            return fd
        with patch("caplab.artifact_rater.os.open", side_effect=retain_fd), patch(
                "caplab.artifact_rater.open", create=True, side_effect=OSError("stream setup failed")):
            with self.assertRaisesRegex(CalibrationError, "stream setup failed"):
                read_rollout_attestation(self.source, "thread-1")
        self.assertEqual(len(descriptors), 1)
        with self.assertRaises(OSError):
            os.fstat(descriptors[0])


if __name__ == "__main__":
    unittest.main()
