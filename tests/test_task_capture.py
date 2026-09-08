"""Real local subprocesses and synthetic trees qualify task capture mechanics."""

import base64
import hashlib
import json
import os
from pathlib import Path
import signal
import sys
import tempfile
import unittest
from unittest.mock import patch

import caplab.task_capture as capture
from caplab.task_capture import TaskCaptureError, TaskCaptureLimits, capture_task_attempt


class TaskCaptureTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.task = self.root / "task"
        self.task.mkdir()
        self.out = self.root / "custody"

    def run_task(self, code, *, task_bytes=10000, entries=100, stream_bytes=10000, timeout=3):
        return capture_task_attempt([sys.executable, "-c", code], task_root=self.task,
                                    environment={"LANG": "C.UTF-8"}, output_dir=self.out,
                                    limits=TaskCaptureLimits(stream_bytes, task_bytes, entries, timeout))

    def inventory(self, phase):
        return json.loads((self.out / phase / "inventory.json").read_bytes())

    def verify_custody(self, receipt):
        self.assertEqual(json.loads((self.out / "attempt.json").read_bytes()), receipt)
        for name, field in (("intent.json", "intent_sha256"),
                            ("before/inventory.json", "before_inventory_sha256"),
                            ("after/inventory.json", "after_inventory_sha256"),
                            ("process/capture.json", "process_capture_sha256")):
            self.assertEqual(hashlib.sha256((self.out / name).read_bytes()).hexdigest(), receipt[field])
        for phase in ("before", "after"):
            inventory = self.inventory(phase)
            retained = 0
            for entry in inventory["entries"]:
                if entry["kind"] == "file":
                    raw = (self.out / phase / entry["object"]).read_bytes()
                    self.assertEqual(len(raw), entry["bytes"])
                    self.assertEqual(hashlib.sha256(raw).hexdigest(), entry["sha256"])
                    retained += len(raw)
                elif entry["kind"] == "symlink":
                    target = base64.b64decode(entry["target_base64"], validate=True)
                    self.assertEqual(len(target), entry["bytes"])
                    retained += len(target)
            self.assertEqual(retained, inventory["retained_bytes"])
        for path in (self.out, *self.out.rglob("*")):
            self.assertEqual(path.stat().st_mode & 0o777, 0o700 if path.is_dir() else 0o600)

    def test_before_after_raw_bytes_modes_directories_and_rename_effects(self):
        (self.task / "old.bin").write_bytes(b"\x00\xfforiginal")
        (self.task / "mode").write_bytes(b"unchanged")
        (self.task / "mode").chmod(0o640)
        (self.task / "deleted").write_bytes(b"gone")
        receipt = self.run_task("""from pathlib import Path
import os
assert Path('../custody/before/inventory.json').is_file()
Path('old.bin').rename('renamed.bin')
Path('mode').chmod(0o750)
Path('deleted').unlink()
Path('empty').mkdir()
Path('résumé').write_bytes(b'new\\x00\\xff')
os.write(1,b'verified effects\\n')
"""
        )
        self.assertTrue(receipt["capture_complete"])
        self.assertEqual(receipt["process"]["return_code"], 0)
        changes = {e["path"]: e for e in receipt["changes"]}
        self.assertEqual(changes["old.bin"]["change"], "deleted")
        self.assertEqual(changes["renamed.bin"]["change"], "added")
        self.assertEqual(changes["mode"], {"path": "mode", "change": "modified", "fields": ["mode"]})
        self.assertEqual(changes["deleted"]["change"], "deleted")
        self.assertEqual(changes["empty"]["change"], "added")
        self.assertEqual(changes["résumé"]["change"], "added")
        before = {e["path"]: e for e in self.inventory("before")["entries"]}
        after = {e["path"]: e for e in self.inventory("after")["entries"]}
        self.assertEqual(before["old.bin"]["sha256"], after["renamed.bin"]["sha256"])
        self.assertEqual((self.out / "before" / before["old.bin"]["object"]).read_bytes(), b"\x00\xfforiginal")
        self.verify_custody(receipt)

    def test_links_are_literal_evidence_and_external_targets_are_not_copied(self):
        outside = self.root / "outside"
        outside.write_bytes(b"not a task input")
        (self.task / "link").symlink_to(outside)
        (self.task / "dangling").symlink_to("missing")
        receipt = self.run_task("import os; os.unlink('link'); os.symlink('new-target', 'link')")
        before = {e["path"]: e for e in self.inventory("before")["entries"]}
        self.assertEqual(base64.b64decode(before["link"]["target_base64"]), os.fsencode(outside))
        self.assertFalse(list((self.out / "before").glob("object-*")))
        self.assertIn("target_base64", receipt["changes"][0]["fields"])
        self.assertEqual(outside.read_bytes(), b"not a task input")
        self.verify_custody(receipt)

    def test_unchanged_tree_and_nonzero_exit_are_separate_observations(self):
        (self.task / "file").write_bytes(b"content")
        receipt = self.run_task("import sys; sys.stderr.write('failed check'); sys.exit(7)")
        self.assertEqual(receipt["changes"], [])
        self.assertTrue(receipt["capture_complete"])
        self.assertEqual(receipt["process"]["return_code"], 7)
        self.verify_custody(receipt)

    def test_timeout_retains_final_effects_without_complete_capture(self):
        receipt = self.run_task("from pathlib import Path; import time; Path('written').write_bytes(b'kept'); time.sleep(30)", timeout=.3)
        self.assertFalse(receipt["capture_complete"])
        self.assertEqual(receipt["process"]["termination"], "timeout")
        self.assertEqual(receipt["process"]["return_code"], -signal.SIGKILL)
        self.assertEqual(receipt["changes"], [{"path": "written", "change": "added"}])
        self.verify_custody(receipt)

    def test_stream_overflow_retains_task_state_and_explicit_truncation(self):
        receipt = self.run_task("import os; os.write(1,b'x'*100)", stream_bytes=7)
        self.assertFalse(receipt["capture_complete"])
        self.assertEqual(receipt["process"]["termination"], "byte-limit")
        self.assertEqual((self.out / "process/native.stdout").read_bytes(), b"x"*7)
        self.verify_custody(receipt)

    def test_before_byte_limit_retains_prefix_and_prevents_launch(self):
        (self.task / "large").write_bytes(b"0123456789")
        with patch.object(capture, "capture_process") as launch:
            with self.assertRaisesRegex(TaskCaptureError, "task-byte-limit"):
                self.run_task("pass", task_bytes=4)
        launch.assert_not_called()
        self.assertEqual(next((self.out / "before").glob("object-*")).read_bytes(), b"0123")
        self.assertFalse((self.out / "before/inventory.json").exists())
        self.assertFalse((self.out / "attempt.json").exists())

    def test_inventory_quota_failure_records_phase_truncation_and_intent(self):
        (self.task / "file").write_bytes(b"abc")
        for phase, budget in (("before", 2), ("after", 4)):
            with self.subTest(phase=phase):
                self.out = self.root / phase
                with self.assertRaisesRegex(TaskCaptureError, "task-byte-limit"):
                    self.run_task("pass", task_bytes=budget)
                failure = json.loads((self.out / "failure.json").read_bytes())
                self.assertEqual(failure["phase"], phase)
                self.assertTrue(failure["truncated"])
                self.assertEqual(failure["reason"], "task-byte-limit:file")
                self.assertEqual(failure["intent_sha256"], hashlib.sha256((self.out / "intent.json").read_bytes()).hexdigest())
                self.assertFalse((self.out / "attempt.json").exists())

    def test_combined_task_limit_is_not_reused_for_after_snapshot(self):
        (self.task / "file").write_bytes(b"abc")
        with self.assertRaisesRegex(TaskCaptureError, "task-byte-limit"):
            self.run_task("from pathlib import Path; Path('file').write_bytes(b'12345')", task_bytes=7)
        self.assertEqual(next((self.out / "after").glob("object-*")).read_bytes(), b"1234")
        self.assertTrue((self.out / "before/inventory.json").exists())
        self.assertTrue((self.out / "process/capture.json").exists())
        self.assertFalse((self.out / "attempt.json").exists())

    def test_entry_limit_and_unsupported_fifo_prevent_launch(self):
        for kind in ("entries", "fifo"):
            with self.subTest(kind=kind):
                self.out = self.root / kind
                if kind == "fifo":
                    os.mkfifo(self.task / "pipe")
                else:
                    (self.task / "file").touch()
                with patch.object(capture, "capture_process") as launch:
                    with self.assertRaisesRegex(TaskCaptureError, "task-entry-limit|unsupported-task-object"):
                        self.run_task("pass", entries=1 if kind == "entries" else 100)
                launch.assert_not_called()
                self.assertFalse((self.out / "attempt.json").exists())

    def test_source_change_during_copy_prevents_sealing_and_launch(self):
        target = self.task / "file"
        target.write_bytes(b"original")
        read = os.read
        changed = False
        def mutate(fd, count):
            nonlocal changed
            chunk = read(fd, count)
            if chunk and not changed:
                changed = True
                target.write_bytes(b"modified")
            return chunk
        with patch.object(capture.os, "read", side_effect=mutate), patch.object(capture, "capture_process") as launch:
            with self.assertRaisesRegex(TaskCaptureError, "source-changed"):
                self.run_task("pass")
        launch.assert_not_called()
        self.assertFalse((self.out / "before/inventory.json").exists())

    def test_directory_growth_is_source_change_not_budget_exhaustion(self):
        (self.task / "file").write_bytes(b"original")
        original = capture._Inventory._retain_file
        def add_entry(inventory, *args):
            entry = original(inventory, *args)
            (self.task / "new").write_bytes(b"changed tree")
            return entry
        with patch.object(capture._Inventory, "_retain_file", add_entry), patch.object(capture, "capture_process") as launch:
            with self.assertRaisesRegex(TaskCaptureError, "source-entries-changed"):
                self.run_task("pass")
        launch.assert_not_called()
        failure = json.loads((self.out / "failure.json").read_bytes())
        self.assertFalse(failure["truncated"])

    def test_file_replaced_with_symlink_before_open_is_not_followed(self):
        (self.task / "file").write_bytes(b"initial")
        outside = self.root / "outside"
        outside.write_bytes(b"unrelated")
        original = capture._Inventory._retain_file
        def replace(inventory, parent, name, before, relative):
            (self.task / name).unlink()
            (self.task / name).symlink_to(outside)
            return original(inventory, parent, name, before, relative)
        with patch.object(capture._Inventory, "_retain_file", replace), patch.object(capture, "capture_process") as launch:
            with self.assertRaises(OSError):
                self.run_task("pass")
        launch.assert_not_called()
        self.assertFalse(list((self.out / "before").glob("object-*")))

    def test_storage_failure_propagates_without_attempt_receipt(self):
        (self.task / "file").write_bytes(b"preserve")
        fsync = os.fsync
        def fail_object(fd):
            if Path(os.readlink(f"/proc/self/fd/{fd}")).name.startswith("object-"):
                raise OSError("task disk failure")
            fsync(fd)
        with patch.object(capture.os, "fsync", side_effect=fail_object), patch.object(capture, "capture_process") as launch:
            with self.assertRaisesRegex(OSError, "task disk failure"):
                self.run_task("pass")
        launch.assert_not_called()
        self.assertFalse((self.out / "before/inventory.json").exists())
        self.assertFalse((self.out / "attempt.json").exists())

    def test_existing_or_inside_task_custody_never_launches(self):
        for destination in (self.task / "nested", self.root / "existing"):
            with self.subTest(destination=destination):
                self.out = destination
                if destination.name == "existing":
                    destination.mkdir()
                with patch.object(capture, "capture_process") as launch:
                    with self.assertRaises((ValueError, FileExistsError)):
                        self.run_task("pass")
                launch.assert_not_called()

    def test_limits_reject_boolean_nonfinite_and_nonpositive_values(self):
        for values in ((True, 1, 1, 1), (1, 0, 1, 1), (1, 1, -1, 1),
                       (1, 1, 1, True), (1, 1, 1, float("nan")), (1, 1, 1, float("inf"))):
            with self.subTest(values=values), self.assertRaises(ValueError):
                TaskCaptureLimits(*values)

    def test_exact_combined_limits_allow_complete_capture(self):
        (self.task / "file").write_bytes(b"abc")
        receipt = self.run_task("pass", task_bytes=6, entries=4)
        self.assertEqual(receipt["retained_task_bytes"], 6)
        self.assertEqual(receipt["retained_task_entries"], 4)
        self.assertTrue(receipt["capture_complete"])
        self.verify_custody(receipt)

    def test_non_utf8_names_and_link_targets_round_trip_without_decoding_contents(self):
        raw_name = b"name-\xff"
        raw_root = os.fsencode(self.task)
        fd = os.open(raw_root + b"/" + raw_name, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        os.close(fd)
        os.symlink(raw_name, raw_root + b"/link")
        receipt = self.run_task("pass")
        entries = {os.fsencode(e["path"]): e for e in self.inventory("before")["entries"]}
        self.assertIn(raw_name, entries)
        self.assertEqual(base64.b64decode(entries[b"link"]["target_base64"]), raw_name)
        self.assertEqual(receipt["changes"], [])
        self.verify_custody(receipt)

    def test_final_publication_failure_keeps_component_custody_without_attempt_receipt(self):
        seal = capture.seal_capture_json
        def fail_final(directory, name, receipt):
            if name == "attempt.json":
                raise OSError("attempt publication failed")
            return seal(directory, name, receipt)
        with patch.object(capture, "seal_capture_json", side_effect=fail_final):
            with self.assertRaisesRegex(OSError, "attempt publication failed"):
                self.run_task("from pathlib import Path; Path('effect').write_bytes(b'kept')")
        self.assertTrue((self.out / "before/inventory.json").exists())
        self.assertTrue((self.out / "process/capture.json").exists())
        self.assertTrue((self.out / "after/inventory.json").exists())
        self.assertFalse((self.out / "attempt.json").exists())

    def test_intent_matches_observed_command_working_directory_and_environment(self):
        receipt = self.run_task("import json,os,sys; print(json.dumps({'argv':sys.argv,'cwd':os.getcwd(),'LANG':os.environ['LANG']}))")
        intent = json.loads((self.out / "intent.json").read_bytes())
        observed = json.loads((self.out / "process/native.stdout").read_bytes())
        self.assertEqual(observed["cwd"], intent["cwd"])
        self.assertEqual(observed["LANG"], intent["environment"]["LANG"])
        self.assertEqual(observed["argv"], [intent["command"][1]])
        self.verify_custody(receipt)


if __name__ == "__main__":
    unittest.main()
