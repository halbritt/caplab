import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from caplab.native_tool_pairs import inspect_captured_tool_pairs
from caplab.task_capture import TaskCaptureLimits, capture_task_attempt
from caplab.task_capture_verify import CaptureVerificationError


def encoded(events):
    return b"".join((json.dumps(e) + "\n").encode() for e in events)


def events(format):
    if format == "codex-exec-jsonl":
        return [{"type": "thread.started", "thread_id": "root"},
            {"type": "item.started", "item": {"id": "call", "type": "command_execution"}},
            {"type": "item.completed", "item": {"id": "call", "type": "command_execution", "exit_code": 7}}]
    return [{"type": "system", "subtype": "init", "session_id": "root"},
        {"type": "assistant", "session_id": "root", "message": {"content": [
            {"type": "tool_use", "id": "call", "name": "Bash", "input": {"command": "synthetic-check"}}]}},
        {"type": "user", "session_id": "root", "message": {"content": [
            {"type": "tool_result", "tool_use_id": "call", "is_error": True, "content": "synthetic failure"}]}}]


def fixture(root, content, *, limit=65536, timeout=3, sleep=0, exit_code=7, stderr=b""):
    root.mkdir()
    task = root / "task"; task.mkdir()
    (task / "before.txt").write_bytes(b"before")
    custody = root / "custody"
    code = ("import os,time\nfrom pathlib import Path\nPath('after.txt').write_bytes(b'after')\n"
            f"os.write(1,{content!r})\nos.write(2,{stderr!r})\ntime.sleep({sleep!r})\nraise SystemExit({exit_code!r})")
    capture_task_attempt([sys.executable, "-B", "-c", code], task_root=task,
        environment={"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8"}, output_dir=custody,
        limits=TaskCaptureLimits(limit, 1024, 20, timeout))
    anchor = hashlib.sha256((custody / "attempt.json").read_bytes()).hexdigest()
    return custody, anchor


def inspect(custody, anchor, format="codex-exec-jsonl", **kwargs):
    return inspect_captured_tool_pairs(custody, expected_attempt_sha256=anchor, format=format,
        expected_root_id=kwargs.pop("expected_root_id", "root"), max_receipt_bytes=100000,
        max_event_bytes=kwargs.pop("max_event_bytes", 65536), **kwargs)


class CapturedToolPairTests(unittest.TestCase):
    def test_failed_process_is_inspected_after_task_removal_without_native_success_claim(self):
        with tempfile.TemporaryDirectory() as d:
            for format in ("codex-exec-jsonl", "claude-stream-jsonl"):
                with self.subTest(format=format):
                    content = encoded(events(format))
                    root = Path(d, format)
                    custody, anchor = fixture(root, content, stderr=b"\xffopaque")
                    shutil.rmtree(root / "task")
                    before = {str(p): p.read_bytes() for p in custody.rglob("*") if p.is_file()}
                    report = inspect(custody, anchor, format)
                    self.assertTrue(report["task_capture"]["integrity_verified"])
                    self.assertTrue(report["task_capture"]["capture_complete"])
                    self.assertEqual(report["task_capture"]["return_code"], 7)
                    self.assertTrue(report["tool_pairs_available"])
                    self.assertEqual(report["tool_pair_report"]["status_counts"], {"paired": 1})
                    self.assertEqual(report["stdout"]["sha256"], hashlib.sha256(content).hexdigest())
                    self.assertEqual(report["tool_pair_report"]["source_sha256"], report["stdout"]["sha256"])
                    self.assertFalse(report["native_execution_linked"])
                    self.assertIsNone(report["native_capture_complete"])
                    self.assertEqual({str(p): p.read_bytes() for p in custody.rglob("*") if p.is_file()}, before)

    def test_parseable_incomplete_capture_retains_pending_calls_and_termination(self):
        stream = events("codex-exec-jsonl")
        prefix = encoded(stream[:2])
        with tempfile.TemporaryDirectory() as d:
            for mode in ("timeout", "byte-limit"):
                with self.subTest(mode=mode):
                    options = {"timeout": .3, "sleep": 2} if mode == "timeout" else {"limit": len(prefix)}
                    content = prefix if mode == "timeout" else encoded(stream)
                    custody, anchor = fixture(Path(d, mode), content, **options)
                    report = inspect(custody, anchor)
                    self.assertEqual(report["task_capture"]["termination"], mode)
                    self.assertFalse(report["task_capture"]["capture_complete"])
                    self.assertTrue(report["tool_pairs_available"])
                    self.assertEqual(report["tool_pair_report"]["status_counts"], {"request_without_result": 1})

    def test_unavailable_pairs_do_not_become_zero_activity(self):
        good = encoded(events("codex-exec-jsonl"))
        scenarios = [("malformed", b"not JSON\n", {}, {}, "native_event_contract"),
            ("truncated", good, {"limit": len(good) - 3}, {}, "native_event_contract"),
            ("parse-budget", good, {}, {"max_event_bytes": len(good) - 1}, "event_byte_allowance"),
            ("wrong-root", good, {}, {"expected_root_id": "other"}, "native_event_contract")]
        with tempfile.TemporaryDirectory() as d:
            for name, content, capture_options, read_options, reason in scenarios:
                with self.subTest(name=name):
                    custody, anchor = fixture(Path(d, name), content, **capture_options)
                    report = inspect(custody, anchor, **read_options)
                    self.assertTrue(report["task_capture"]["integrity_verified"])
                    self.assertFalse(report["tool_pairs_available"])
                    self.assertIsNone(report["tool_pair_report"])
                    self.assertEqual(report["unavailable_reason"]["code"], reason)
            custody, anchor = fixture(Path(d, "observed-empty"), encoded(events("codex-exec-jsonl")[:1]))
            empty = inspect(custody, anchor)
            self.assertTrue(empty["tool_pairs_available"])
            self.assertEqual(empty["tool_pair_report"]["status_counts"], {})
            self.assertIsNone(empty["native_capture_complete"])

    def test_wrong_anchor_and_tampered_stderr_raise_before_pairing(self):
        with tempfile.TemporaryDirectory() as d:
            custody, anchor = fixture(Path(d, "capture"), encoded(events("codex-exec-jsonl")), stderr=b"original")
            with self.assertRaises(CaptureVerificationError):
                inspect(custody, "0" * 64)
            (custody / "process/native.stderr").write_bytes(b"tampered")
            with self.assertRaises(CaptureVerificationError):
                inspect(custody, anchor)

    def test_cli_distinguishes_unavailable_analysis_from_failed_integrity(self):
        with tempfile.TemporaryDirectory() as d:
            custody, anchor = fixture(Path(d, "capture"), b"unparseable\n")
            command = [sys.executable, "scripts/captured_tool_pairs.py", str(custody),
                "--format", "codex-exec-jsonl", "--expected-root-id", "root", "--max-receipt-bytes", "100000",
                "--max-event-bytes", "65536", "--expected-attempt-sha256"]
            done = subprocess.run(command + [anchor], capture_output=True, check=True)
            self.assertFalse(json.loads(done.stdout)["tool_pairs_available"])
            bad = subprocess.run(command + ["0" * 64], capture_output=True)
            self.assertEqual(bad.returncode, 2)
            self.assertEqual(bad.stdout, b"")
