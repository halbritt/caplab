"""Synthetic runtime custody and an actual local namespace persistence probe."""

import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import unittest
from unittest.mock import patch
import tempfile

from caplab.native_capture_invocation import NativeCaptureContext, _digest, build_native_capture_invocation
from caplab.native_runtime import NativeRuntimeError, prepare_native_runtime
import caplab.native_runtime as runtime
from caplab.task_capture import TaskCaptureLimits, capture_task_attempt
from caplab.task_capture_verify import verify_task_capture

POLICY = Path(__file__).parents[1] / "docs/product/contracts/native-agent-systems.json"


class NativeRuntimeTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.task = self.root / "task"
        self.task.mkdir()
        self.out = self.root / "custody"
        self.plan = self.invocation("codex")

    def invocation(self, harness):
        return build_native_capture_invocation(POLICY,
            "codex-terra-max" if harness == "codex" else "claude-fable-5-max",
            context=NativeCaptureContext("/work", "/episode", "Read résumé\u2028and verify.\n".encode(),
                None if harness == "codex" else "d82c1f85-f336-41d9-bd85-13953846867b"))

    def prepare(self, expected=None):
        return prepare_native_runtime(POLICY, self.plan,
            expected_invocation_sha256=self.plan["invocation_sha256"] if expected is None else expected,
            task_root=self.task, output_dir=self.out)

    def test_both_layouts_are_private_with_exact_separate_inputs_and_mappings(self):
        for harness in ("codex", "claude"):
            with self.subTest(harness=harness):
                self.out = self.root / harness
                self.plan = self.invocation(harness)
                original = copy.deepcopy(self.plan)
                result = self.prepare()
                self.assertEqual(self.plan, original)
                self.assertEqual(json.loads((self.out / "preparation.json").read_bytes()), result)
                self.assertEqual(json.loads((self.out / "invocation.json").read_bytes()), self.plan)
                self.assertEqual(hashlib.sha256((self.out / "invocation.json").read_bytes()).hexdigest(), result["invocation_file_sha256"])
                self.assertEqual((self.out / "prompt.bin").read_bytes(), self.plan["command"][-1].encode())
                self.assertEqual(result["prompt_sha256"], self.plan["prompt_sha256"])
                self.assertFalse(result["execution_authorized"])
                self.assertFalse(result["binding_complete"])
                self.assertEqual(result["mounts"]["runtime"], {"source": str(self.out / "runtime"), "destination": "/episode", "access": "rw"})
                self.assertEqual(result["mounts"]["task"]["source"], str(self.task))
                for path in (self.out, *self.out.rglob("*")):
                    self.assertEqual(path.stat().st_mode & 0o777, 0o700 if path.is_dir() else 0o600)
                self.assertFalse(any(p.is_file() for p in (self.out / "runtime").rglob("*")))
                for path in result["capture_paths"].values():
                    self.assertTrue(Path(path).is_relative_to(self.out / "runtime"))

    def test_reuse_or_task_overlap_never_overwrites_or_copies_inputs(self):
        result = self.prepare()
        before = {str(p): p.read_bytes() for p in self.out.rglob("*") if p.is_file()}
        with self.assertRaises(FileExistsError):
            self.prepare()
        self.assertEqual(before, {str(p): p.read_bytes() for p in self.out.rglob("*") if p.is_file()})
        self.out = self.task / "inside"
        with self.assertRaisesRegex(NativeRuntimeError, "outside_task"):
            self.prepare()
        self.assertFalse(self.out.exists())
        self.assertEqual(result["mounts"]["task"]["source"], str(self.task))

    def test_invocation_tampering_and_resealed_extra_behavior_fail_before_creation(self):
        original = copy.deepcopy(self.plan)
        for key, value in (("execution_authorized", True), ("command", ["sh", "-c", "touch bad"]),
                           ("capture_locations", {"outside": "/etc/passwd"}), ("environment", {"HOME": "/home/owner"})):
            for reseal in (False, True):
                with self.subTest(key=key, reseal=reseal):
                    self.plan = copy.deepcopy(original)
                    self.plan[key] = value
                    if reseal:
                        self.plan["invocation_sha256"] = _digest({k: v for k, v in self.plan.items() if k != "invocation_sha256"})
                    with self.assertRaises(NativeRuntimeError):
                        self.prepare()
                    self.assertFalse(self.out.exists())
        self.plan = original
        with self.assertRaises(NativeRuntimeError):
            self.prepare(expected="0" * 64)
        self.assertFalse(self.out.exists())

    def test_linked_task_parent_and_existing_output_link_are_rejected(self):
        linked = self.root / "linked"
        linked.symlink_to(self.task)
        self.task = linked
        with self.assertRaises(NativeRuntimeError):
            self.prepare()
        self.task = self.root / "task"
        self.out.symlink_to(self.task)
        with self.assertRaises(FileExistsError):
            self.prepare()
        self.assertEqual(list(self.task.iterdir()), [])
        self.out.unlink()
        parent = self.root / "parent"
        parent.symlink_to(self.root)
        self.out = parent / "new"
        with self.assertRaises(NativeRuntimeError):
            self.prepare()

    def test_runtime_sync_failure_retains_partial_state_without_preparation_receipt(self):
        with patch.object(runtime, "_sync_directory", side_effect=OSError("runtime sync failed")):
            with self.assertRaisesRegex(OSError, "runtime sync failed"):
                self.prepare()
        self.assertTrue((self.out / "invocation.json").exists())
        self.assertTrue((self.out / "prompt.bin").exists())
        self.assertFalse((self.out / "preparation.json").exists())
        with self.assertRaises(FileExistsError):
            self.prepare()

    def test_prompt_write_failure_closes_descriptor_and_withholds_preparation(self):
        captured = []
        def fail(fd, content):
            captured.append(fd)
            os.write(fd, content[:2])
            raise OSError("prompt storage failed")
        with patch.object(runtime, "_write_all", side_effect=fail):
            with self.assertRaisesRegex(OSError, "prompt storage failed"):
                self.prepare()
        self.assertEqual(len(captured), 1)
        with self.assertRaises(OSError):
            os.fstat(captured[0])
        self.assertEqual((self.out / "prompt.bin").read_bytes(), self.plan["command"][-1].encode()[:2])
        self.assertFalse((self.out / "preparation.json").exists())

    @unittest.skipUnless(shutil.which("bwrap"), "requires Linux bubblewrap")
    def test_namespace_writes_persist_without_exposing_outer_custody(self):
        prepared = self.prepare()
        probe = """import os
from pathlib import Path
assert not Path('/episode/invocation.json').exists()
assert not Path('/episode/prompt.bin').exists()
assert not Path('/episode/preparation.json').exists()
assert not Path('/home/halbritt').exists()
assert not Path('/episode/../prompt.bin').exists()
assert os.environ.get('UNRELATED_SECRET') is None
Path('/episode/codex/sessions/synthetic.jsonl').write_bytes(b'local probe only\\n')
Path('/episode/codex/log/diagnostic').write_bytes(b'local diagnostic')
Path('/work/observed').write_bytes(b'task effect')
print('persistent runtime and task writes completed')
"""
        command = [shutil.which("bwrap"), "--unshare-all", "--die-with-parent", "--new-session", "--clearenv",
                   "--ro-bind", "/usr", "/usr", "--symlink", "usr/bin", "/bin", "--symlink", "usr/lib", "/lib",
                   "--symlink", "usr/lib64", "/lib64", "--proc", "/proc", "--dev", "/dev", "--tmpfs", "/tmp"]
        for mount in prepared["mounts"].values():
            command += ["--bind", mount["source"], mount["destination"]]
        command += ["--chdir", "/work", "--setenv", "LANG", "C.UTF-8", "--", "/usr/bin/python3", "-c", probe]
        capture = self.root / "capture"
        result = capture_task_attempt(command, task_root=self.task, environment={"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8", "UNRELATED_SECRET": "synthetic-only"},
            output_dir=capture, limits=TaskCaptureLimits(10000, 10000, 100, 5))
        self.assertEqual(result["process"]["return_code"], 0, (capture / "process/native.stderr").read_bytes())
        self.assertEqual((self.out / "runtime/codex/sessions/synthetic.jsonl").read_bytes(), b"local probe only\n")
        self.assertEqual((self.out / "runtime/codex/log/diagnostic").read_bytes(), b"local diagnostic")
        self.assertEqual(result["changes"], [{"path": "observed", "change": "added"}])
        anchor = hashlib.sha256((capture / "attempt.json").read_bytes()).hexdigest()
        report = verify_task_capture(capture, expected_attempt_sha256=anchor, max_receipt_bytes=100000)
        self.assertTrue(report["integrity_verified"])
        self.assertTrue(report["capture_complete"])


if __name__ == "__main__":
    unittest.main()
