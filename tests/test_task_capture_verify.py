"""Synthetic real captures and re-anchored inconsistent receipts exercise the reader."""

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from caplab.task_capture import TaskCaptureLimits, capture_task_attempt
from caplab.task_capture_verify import CaptureVerificationError, verify_task_capture
import caplab.task_capture_verify as verifier


class TaskCaptureVerificationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.task = self.root / "task"
        self.task.mkdir()
        (self.task / "binary").write_bytes(b"\0\xffraw")
        (self.task / "empty").mkdir()
        os.symlink(b"missing-\xff", os.fsencode(self.task / "link"))
        (self.task / os.fsdecode(b"name-\xff")).write_bytes(b"opaque")
        self.out = self.root / "capture"
        self.capture("from pathlib import Path; import os; Path('binary').write_bytes(b'changed'); os.write(2,b'failure\\xff'); raise SystemExit(7)")

    def capture(self, code, *, stream_bytes=10000, timeout=3):
        self.receipt = capture_task_attempt([sys.executable, "-c", code], task_root=self.task,
            environment={"LANG": "C.UTF-8", "SYNTHETIC_CAPTURE_SECRET": "do-not-print"}, output_dir=self.out,
            limits=TaskCaptureLimits(stream_bytes, 10000, 100, timeout))
        self.anchor = hashlib.sha256((self.out / "attempt.json").read_bytes()).hexdigest()

    def verify(self, **kwargs):
        return verify_task_capture(self.out, expected_attempt_sha256=self.anchor,
                                   max_receipt_bytes=kwargs.get("budget", 1000000))

    def read(self, path):
        return json.loads((self.out / path).read_bytes())

    def rewrite(self, path, document):
        raw = (json.dumps(document, sort_keys=True) + "\n").encode()
        (self.out / path).write_bytes(raw)
        return hashlib.sha256(raw).hexdigest()

    def reanchor(self, path, document):
        digest = self.rewrite(path, document)
        if path != "attempt.json":
            attempt = self.read("attempt.json")
            field = {"intent.json": "intent_sha256", "before/inventory.json": "before_inventory_sha256",
                     "after/inventory.json": "after_inventory_sha256", "process/capture.json": "process_capture_sha256"}[path]
            attempt[field] = digest
            if path == "process/capture.json":
                attempt["process"] = document
            digest = self.rewrite("attempt.json", attempt)
        self.anchor = digest

    def files(self):
        return {str(p.relative_to(self.out)): (p.read_bytes(), p.stat().st_mtime_ns, p.stat().st_mode)
                for p in self.out.rglob("*") if p.is_file()}

    def test_real_capture_report_is_read_only_and_does_not_open_original_tree(self):
        before = self.files()
        shutil.rmtree(self.task)
        report = self.verify()
        self.assertTrue(report["integrity_verified"])
        self.assertTrue(report["capture_complete"])
        self.assertEqual(report["return_code"], 7)
        self.assertEqual(report["changes"], [{"path": "binary", "change": "modified", "fields": ["bytes", "sha256"]}])
        self.assertEqual(report["retained_task_bytes"], self.receipt["retained_task_bytes"])
        self.assertEqual(before, self.files())
        self.assertNotIn("do-not-print", json.dumps(report))
        self.assertNotIn("command", report)
        self.assertNotIn("environment", report)

    def test_timeout_and_truncation_can_have_verified_integrity(self):
        for termination, code, options in (
                ("timeout", "import time; time.sleep(30)", {"timeout": .15}),
                ("byte-limit", "import os; os.write(1,b'x'*100)", {"stream_bytes": 7})):
            with self.subTest(termination=termination):
                self.out = self.root / termination
                self.capture(code, **options)
                report = self.verify()
                self.assertTrue(report["integrity_verified"])
                self.assertFalse(report["capture_complete"])
                self.assertEqual(report["termination"], termination)

    def test_each_linked_receipt_and_payload_is_checked(self):
        paths = ["attempt.json", "intent.json", "before/inventory.json", "after/inventory.json",
                 "process/capture.json", "process/native.stdout", "process/native.stderr"]
        paths += [str(p.relative_to(self.out)) for phase in ("before", "after")
                  for p in (self.out / phase).glob("object-*")]
        for path in paths:
            with self.subTest(path=path):
                original = (self.out / path).read_bytes()
                (self.out / path).write_bytes(original + b" ")
                with self.assertRaises(CaptureVerificationError):
                    self.verify()
                (self.out / path).write_bytes(original)
        self.assertTrue(self.verify()["integrity_verified"])

    def test_same_length_payload_corruption_and_missing_payload_fail(self):
        path = next((self.out / "before").glob("object-*"))
        original = path.read_bytes()
        path.write_bytes(bytes([original[0] ^ 1]) + original[1:])
        with self.assertRaisesRegex(CaptureVerificationError, "hash mismatch"):
            self.verify()
        path.unlink()
        with self.assertRaises(FileNotFoundError):
            self.verify()

    def test_root_component_receipt_and_payload_symlinks_are_rejected(self):
        object_path = str(next((self.out / "before").glob("object-*")).relative_to(self.out))
        for relative in ("", "before", "after", "process", "intent.json", "process/native.stderr", object_path):
            with self.subTest(relative=relative):
                target = self.out / relative if relative else self.out
                parked = self.root / "parked"
                target.rename(parked)
                target.symlink_to(parked)
                try:
                    with self.assertRaises(OSError):
                        self.verify()
                finally:
                    target.unlink()
                    parked.rename(target)

    def test_fifo_rejection_is_nonblocking_in_bounded_child(self):
        target = self.out / "process/native.stdout"
        target.unlink()
        os.mkfifo(target)
        result = subprocess.run([sys.executable, "scripts/verify_task_capture.py", str(self.out),
            "--expected-attempt-sha256", self.anchor, "--max-receipt-bytes", "1000000"],
            env={"PATH": os.defpath, "PYTHONPATH": "src"}, capture_output=True, timeout=3)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, b"")
        self.assertIn(b"unsupported type", result.stderr)

    def test_receipt_budget_exact_boundary_and_invalid_input(self):
        size = sum((self.out / p).stat().st_size for p in
                   ("attempt.json", "intent.json", "before/inventory.json", "after/inventory.json", "process/capture.json"))
        self.assertEqual(self.verify(budget=size)["verified_receipt_bytes"], size)
        for budget in (size - 1, 0, True, -1, 3.5):
            with self.subTest(budget=budget), self.assertRaises(CaptureVerificationError):
                self.verify(budget=budget)
        for digest in (None, "", "A" * 64, "0" * 64):
            with self.subTest(digest=digest), self.assertRaises(CaptureVerificationError):
                verify_task_capture(self.out, expected_attempt_sha256=digest, max_receipt_bytes=1000000)

    def test_reanchored_ambiguous_or_invalid_json_never_produces_report(self):
        path = self.out / "attempt.json"
        original = path.read_bytes()
        for raw in (b'{"schema":"caplab.task-attempt-capture/v1","schema":"x"}',
                    b'{"schema":NaN}', b'{"schema":Infinity}', b'\xff', b'null', b'[]'):
            with self.subTest(raw=raw):
                path.write_bytes(raw)
                self.anchor = hashlib.sha256(raw).hexdigest()
                with self.assertRaises(CaptureVerificationError):
                    self.verify()
        path.write_bytes(original)

    def test_reanchored_summaries_and_process_claims_must_match_evidence(self):
        original_files = self.files()
        original_anchor = self.anchor
        cases = [("attempt.json", key, value) for key, value in (
            ("changes", []), ("capture_complete", False), ("capture_complete", 1),
            ("retained_task_entries", True), ("retained_task_bytes", 0), ("process", {}))]
        cases += [("process/capture.json", key, value) for key, value in (
            ("return_code", True), ("streams_complete", False), ("max_stream_bytes", 1),
            ("timeout_seconds", True), ("retained_stream_bytes", 0), ("termination", "byte-limit"))]
        for path, key, value in cases:
            with self.subTest(path=path, key=key, value=value):
                document = self.read(path)
                document[key] = value
                self.reanchor(path, document)
                with self.assertRaises(CaptureVerificationError):
                    self.verify()
                for name, (raw, _, _) in original_files.items():
                    (self.out / name).write_bytes(raw)
                self.anchor = original_anchor

    def test_reanchored_inventory_rejects_unsafe_and_inconsistent_structure(self):
        original_files, original_anchor = self.files(), self.anchor
        def file_entry(doc):
            return next(e for e in doc["entries"] if e["kind"] == "file")
        mutations = [lambda d: file_entry(d).update(object="../intent.json"),
                     lambda d: file_entry(d).update(object="/etc/passwd"),
                     lambda d: file_entry(d).update(path="../outside"),
                     lambda d: file_entry(d).update(path="absent/file"),
                     lambda d: file_entry(d).update(bytes=True),
                     lambda d: file_entry(d).update(bytes=10001),
                     lambda d: d["entries"].append(d["entries"][0]),
                     lambda d: d["entries"].reverse(),
                     lambda d: d.update(retained_bytes=0),
                     lambda d: d.update(source_root="/different"),
                     lambda d: next(e for e in d["entries"] if e["kind"] == "symlink").update(target_base64="!"),
                     lambda d: d["entries"][0].update(kind="file")]
        for index, mutate in enumerate(mutations):
            with self.subTest(index=index):
                doc = self.read("before/inventory.json")
                mutate(doc)
                self.reanchor("before/inventory.json", doc)
                with self.assertRaises(CaptureVerificationError):
                    self.verify()
                for name, (raw, _, _) in original_files.items():
                    (self.out / name).write_bytes(raw)
                self.anchor = original_anchor

    def test_combined_capture_limits_and_stream_locator_are_checked(self):
        intent = self.read("intent.json")
        intent["limits"]["max_task_entries"] = self.receipt["retained_task_entries"] - 1
        self.reanchor("intent.json", intent)
        with self.assertRaisesRegex(CaptureVerificationError, "entry count"):
            self.verify()
        intent["limits"]["max_task_entries"] = 100
        intent["limits"]["max_task_bytes"] = self.receipt["retained_task_bytes"] - 1
        self.reanchor("intent.json", intent)
        with self.assertRaisesRegex(CaptureVerificationError, "task byte limit"):
            self.verify()
        intent["limits"]["max_task_bytes"] = 10000
        self.reanchor("intent.json", intent)
        process = self.read("process/capture.json")
        process["streams"]["stderr"]["path"] = "../../outside"
        self.reanchor("process/capture.json", process)
        with self.assertRaisesRegex(CaptureVerificationError, "stream locator"):
            self.verify()

    def test_payload_change_during_read_closes_all_descriptors(self):
        target = next((self.out / "before").glob("object-*"))
        read, opened, closed, changed = os.read, [], [], False
        open_fd, close_fd = os.open, os.close
        def observe_open(*args, **kwargs):
            fd = open_fd(*args, **kwargs)
            opened.append(fd)
            return fd
        def observe_close(fd):
            closed.append(fd)
            close_fd(fd)
        def mutate(fd, count):
            nonlocal changed
            result = read(fd, count)
            if not changed and Path(os.readlink(f"/proc/self/fd/{fd}")) == target:
                changed = True
                target.write_bytes(b"x" * target.stat().st_size)
            return result
        with patch.object(verifier.os, "open", side_effect=observe_open), \
                patch.object(verifier.os, "close", side_effect=observe_close), \
                patch.object(verifier.os, "read", side_effect=mutate):
            with self.assertRaisesRegex(CaptureVerificationError, "changed during read"):
                self.verify()
        self.assertTrue(changed)
        self.assertCountEqual(opened, closed)

    def test_large_binary_payload_reads_are_bounded(self):
        self.out = self.root / "large-capture"
        (self.task / "large").write_bytes(b"\xff" * 200000)
        capture_task_attempt([sys.executable, "-c", "pass"], task_root=self.task,
            environment={}, output_dir=self.out, limits=TaskCaptureLimits(100, 500000, 100, 3))
        self.anchor = hashlib.sha256((self.out / "attempt.json").read_bytes()).hexdigest()
        sizes, read = [], os.read
        def bounded(fd, count):
            sizes.append(count)
            return read(fd, count)
        with patch.object(verifier.os, "read", side_effect=bounded):
            self.assertTrue(self.verify()["integrity_verified"])
        self.assertEqual(max(sizes), 65536)
        self.assertGreaterEqual(sizes.count(65536), 6)

    def test_cli_reports_integrity_without_private_intent_and_fails_without_stdout(self):
        command = [sys.executable, "scripts/verify_task_capture.py", str(self.out),
                   "--expected-attempt-sha256", self.anchor, "--max-receipt-bytes", "1000000"]
        result = subprocess.run(command, env={"PATH": os.defpath, "PYTHONPATH": "src"},
                                capture_output=True, timeout=3)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report, self.verify())
        self.assertNotIn(b"do-not-print", result.stdout + result.stderr)
        (self.out / "attempt.json").unlink()
        result = subprocess.run(command, env={"PATH": os.defpath, "PYTHONPATH": "src"},
                                capture_output=True, timeout=3)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, b"")


if __name__ == "__main__":
    unittest.main()
