import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from caplab.capture_accounting import build_capture_byte_report
from caplab.native_capture_invocation import NativeCaptureContext, build_native_capture_invocation
from caplab.native_collection import collect_native_outputs
from caplab.native_runtime import prepare_native_runtime
from caplab.task_capture import TaskCaptureLimits, capture_task_attempt
from caplab.task_capture_verify import CaptureVerificationError

REPO = Path(__file__).resolve().parents[1]
POLICY = REPO / "docs/product/contracts/native-agent-systems.json"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_fixture(root, harness="codex", *, stream_limit=100, missing_session=False):
    root.mkdir()
    task = root / "task"; task.mkdir()
    for name in ("a", "b"):
        (task / name).write_bytes(b"\xff\x00")
    (task / "empty").touch()
    (task / "link").symlink_to("a")
    plan = build_native_capture_invocation(POLICY,
        "codex-terra-max" if harness == "codex" else "claude-fable-5-max",
        context=NativeCaptureContext("/work", "/episode", b"synthetic task",
            None if harness == "codex" else "11111111-2222-4333-8444-555555555555"))
    prepared = root / "prepared"
    prep = prepare_native_runtime(POLICY, plan, expected_invocation_sha256=plan["invocation_sha256"],
                                  task_root=task, output_dir=prepared)
    paths = {k: Path(v) for k, v in prep["capture_paths"].items()}
    sessions = paths["session_search_root"]
    if missing_session:
        sessions.rmdir()
    else:
        for name in ("one", "two"):
            (sessions / name).write_bytes(b"\xff\x00")
        (sessions / "link").symlink_to("a")
    attempt = root / "attempt"
    command = [sys.executable, "-B", "-c",
        "import os,pathlib;pathlib.Path('added').write_bytes(b'12345');"
        "os.write(1,b'abc');os.write(2,b'xy');raise SystemExit(7)"]
    capture_task_attempt(command, task_root=task, environment={"PATH": "/usr/bin:/bin"},
        output_dir=attempt, limits=TaskCaptureLimits(stream_limit, 1000, 100, 5))
    collection = root / "collection"
    collect_native_outputs(POLICY, prepared, expected_preparation_sha256=digest(prepared / "preparation.json"),
        output_dir=collection, max_receipt_bytes=100000, max_artifact_bytes=1000, max_entries=100)
    return dict(task_custody=attempt, collection_custody=collection,
        expected_attempt_sha256=digest(attempt / "attempt.json"),
        expected_collection_sha256=digest(collection / "collection.json"), max_receipt_bytes=200000)


class CaptureAccountingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_binary_duplicates_symlinks_and_failed_task_after_source_removal(self):
        for harness in ("codex", "claude"):
            with self.subTest(harness=harness):
                root = self.root / harness
                options = build_fixture(root, harness)
                shutil.rmtree(root / "task"); shutil.rmtree(root / "prepared")
                before = {str(p): digest(p) for p in root.rglob("*") if p.is_file()}
                report = build_capture_byte_report(POLICY, **options)
                self.assertEqual(report["retained_file_bytes"], 22)
                self.assertEqual(report["retained_symlink_target_bytes"], 3)
                self.assertEqual(report["retained_logical_payload_bytes"], 25)
                rows = {r["surface"]: r for r in report["surfaces"]}
                self.assertEqual(rows["task/before"]["file_bytes"], 4)
                self.assertEqual(rows["task/after"]["file_bytes"], 9)
                self.assertEqual(rows["native/session_search_root"]["file_bytes"], 4)
                self.assertTrue(report["task_capture_complete"])
                self.assertEqual(report["return_code"], 7)
                self.assertFalse(report["executed_invocation_bound"])
                self.assertIsNone(report["native_capture_complete"])
                self.assertIsNone(report["capture_overhead_seconds"])
                receipts = [options["task_custody"] / n for n in
                    ("attempt.json", "intent.json", "before/inventory.json", "after/inventory.json", "process/capture.json")]
                receipts += [options["collection_custody"] / n for n in
                    ("collection.json", "intent.json", "preparation.json", "invocation.json")]
                self.assertEqual(report["verified_receipt_bytes"], sum(p.stat().st_size for p in receipts))
                self.assertEqual(before, {str(p): digest(p) for p in root.rglob("*") if p.is_file()})

    def test_missing_is_not_zero_and_truncated_capture_is_not_complete(self):
        options = build_fixture(self.root / "bounded", missing_session=True, stream_limit=2)
        report = build_capture_byte_report(POLICY, **options)
        rows = {r["surface"]: r for r in report["surfaces"]}
        self.assertIsNone(rows["native/session_search_root"]["logical_payload_bytes"])
        self.assertIsNone(rows["native/final_message"]["logical_payload_bytes"])
        self.assertEqual(rows["native/diagnostic_search_root"]["logical_payload_bytes"], 0)
        self.assertEqual(rows["native/diagnostic_search_root"]["status"], "retained")
        self.assertEqual(sum(rows[f"process/{s}"]["file_bytes"] for s in ("stdout", "stderr")), 2)
        self.assertFalse(report["task_capture_complete"])
        self.assertEqual(report["termination"], "byte-limit")

    def test_corruption_wrong_anchor_unrelated_bundle_and_receipt_bound_refuse(self):
        options = build_fixture(self.root / "first")
        other = build_fixture(self.root / "other")
        cases = [dict(expected_attempt_sha256="0" * 64), dict(max_receipt_bytes=1),
                 {k: other[k] for k in ("collection_custody", "expected_collection_sha256")}]
        for change in cases:
            with self.subTest(change=change), self.assertRaises(CaptureVerificationError):
                build_capture_byte_report(POLICY, **(options | change))
        payload = next((options["collection_custody"] / "objects").iterdir())
        raw = payload.read_bytes()
        payload.write_bytes(b"bad")
        with self.assertRaises(CaptureVerificationError):
            build_capture_byte_report(POLICY, **options)
        payload.write_bytes(raw)
        (options["task_custody"] / "process/native.stdout").write_bytes(b"BAD")
        with self.assertRaises(CaptureVerificationError):
            build_capture_byte_report(POLICY, **options)

    def test_cli_matches_api_and_emits_no_report_on_bad_anchor(self):
        options = build_fixture(self.root / "cli")
        command = [sys.executable, str(REPO / "scripts/capture_bytes.py"),
            str(options["task_custody"]), str(options["collection_custody"]), "--policy", str(POLICY),
            "--expected-attempt-sha256", options["expected_attempt_sha256"],
            "--max-receipt-bytes", "200000", "--expected-collection-sha256", options["expected_collection_sha256"]]
        env = {**os.environ, "PYTHONPATH": str(REPO / "src"), "PYTHONDONTWRITEBYTECODE": "1"}
        result = subprocess.run(command, capture_output=True, text=True, env=env, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), build_capture_byte_report(POLICY, **options))
        result = subprocess.run(command[:-1] + ["0" * 64], capture_output=True, text=True, env=env, timeout=10)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
