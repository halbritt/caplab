"""Individually valid retained copies must agree on shared source paths."""

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

from caplab.capture_overlap import compare_verified_capture_overlap
from caplab.native_collection_verify import verify_native_collection
from caplab.task_capture_verify import CaptureVerificationError
from test_supervised_task_capture import retained_fixture, POLICY

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import probe_cgroup_resource_limits as mounts


class CaptureOverlapTests(unittest.TestCase):
    def fixture(self, root, harness="codex"):
        result = retained_fixture(
            root,
            harness,
            7,
            mount_retainer=mounts.retain_mount,
            extra_files={"/episode/unselected/opaque": b"\x00\xffcaf\xc3\xa9"},
            extra_links={"/work/literal-link": b"../absent-\xff"},
        )
        mounts.verify_retention(root, {"reports": [result["full_retention"]]})
        read = lambda name: json.loads((root / name).read_bytes())
        inputs = dict(
            task_after=read("attempt/after/inventory.json"),
            native=read("collection/collection.json"),
            retained_task=read("fixture-retained/3/inventory.json"),
            retained_runtime=read("fixture-retained/4/inventory.json"),
        )
        return result, inputs

    def test_real_copies_agree_after_source_removal_for_both_native_layouts(self):
        with tempfile.TemporaryDirectory() as temporary:
            for harness in ("codex", "claude"):
                root = Path(temporary) / harness
                result, inputs = self.fixture(root, harness)
                before = deepcopy(inputs)
                compared = compare_verified_capture_overlap(**inputs)
                self.assertTrue(compared["overlapping_entries_agree"])
                self.assertEqual(
                    compared["task_entries"], len(inputs["task_after"]["entries"])
                )
                self.assertEqual(
                    len(compared["native_locations"]),
                    len(inputs["native"]["locations"]),
                )
                self.assertEqual(inputs, before)
                self.assertFalse(compared["study_eligible"])
                self.assertEqual(result["configured_process_return_code"], 7)

    def test_valid_collection_with_different_file_bytes_fails_overlap(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "capture"
            _, inputs = self.fixture(root)
            entry = next(
                e for e in inputs["native"]["entries"] if e["path"] == "final_message"
            )
            path = root / "collection/objects" / entry["object"]
            raw = path.read_bytes()
            path.write_bytes(bytes([raw[0] ^ 1]) + raw[1:])
            entry["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
            receipt = root / "collection/collection.json"
            receipt.write_text(json.dumps(inputs["native"]))
            checked = verify_native_collection(
                POLICY,
                root / "collection",
                expected_collection_sha256=hashlib.sha256(
                    receipt.read_bytes()
                ).hexdigest(),
                max_receipt_bytes=200000,
            )
            self.assertTrue(checked["integrity_verified"])
            with self.assertRaisesRegex(
                CaptureVerificationError, "overlapping entries differ"
            ):
                compare_verified_capture_overlap(**inputs)

    def test_metadata_links_and_entry_population_disagreements_are_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            _, original = self.fixture(Path(temporary) / "capture")
            cases = (
                "mode",
                "source metadata",
                "symlink",
                "omitted task",
                "omitted native",
                "added native",
            )
            for case in cases:
                with self.subTest(case=case):
                    inputs = deepcopy(original)
                    entries = inputs["retained_task"]["entries"]
                    entry = next(e for e in entries if e["path"] == "item")
                    if case == "mode":
                        entry["mode"] ^= 0o100
                    elif case == "source metadata":
                        entry["source_stat"]["mtime_ns"] += 1
                    elif case == "symlink":
                        entry = next(e for e in entries if e["kind"] == "symlink")
                        entry["target_base64"] = "ZGlmZmVyZW50"
                        entry["bytes"] = 9
                    elif case == "omitted task":
                        entries.remove(entry)
                    elif case == "omitted native":
                        entries = inputs["native"]["entries"]
                        entries.remove(
                            next(e for e in entries if e["path"] == "final_message")
                        )
                    else:
                        entry = next(
                            e
                            for e in inputs["retained_runtime"]["entries"]
                            if e["kind"] == "file"
                        )
                        inputs["retained_runtime"]["entries"].append(
                            entry | {"path": "codex/log/extra"}
                        )
                    with self.assertRaisesRegex(
                        CaptureVerificationError, "overlapping entries differ"
                    ):
                        compare_verified_capture_overlap(**inputs)

    def test_missing_location_requires_absence_and_empty_directory_remains_retained(
        self,
    ):
        with tempfile.TemporaryDirectory() as temporary:
            _, inputs = self.fixture(Path(temporary) / "capture")
            location = next(
                x
                for x in inputs["native"]["locations"]
                if x["name"] == "diagnostic_search_root"
            )
            inputs["native"]["entries"] = [
                e
                for e in inputs["native"]["entries"]
                if not e["path"].startswith("diagnostic_search_root/")
            ]
            inputs["retained_runtime"]["entries"] = [
                e
                for e in inputs["retained_runtime"]["entries"]
                if not e["path"].startswith("codex/log/")
            ]
            output = compare_verified_capture_overlap(**inputs)
            row = next(
                x for x in output["native_locations"] if x["name"] == location["name"]
            )
            self.assertEqual((row["status"], row["entries"]), ("retained", 1))
            location["status"] = "missing"
            inputs["native"]["entries"] = [
                e
                for e in inputs["native"]["entries"]
                if e["path"] != "diagnostic_search_root"
            ]
            with self.assertRaisesRegex(
                CaptureVerificationError, "missing native location exists"
            ):
                compare_verified_capture_overlap(**inputs)
            inputs["retained_runtime"]["entries"] = [
                e
                for e in inputs["retained_runtime"]["entries"]
                if e["path"] != "codex/log"
            ]
            output = compare_verified_capture_overlap(**inputs)
            row = next(
                x for x in output["native_locations"] if x["name"] == location["name"]
            )
            self.assertEqual((row["status"], row["entries"]), ("missing", 0))

    def test_namespace_boundaries_and_copy_object_names_are_distinct(self):
        with tempfile.TemporaryDirectory() as temporary:
            _, inputs = self.fixture(Path(temporary) / "capture")
            # Object names belong to each copy; source-relative paths govern overlap.
            for e in inputs["native"]["entries"]:
                if "object" in e:
                    e["object"] = "different-copy-" + e["object"]
            compare_verified_capture_overlap(**inputs)
            changed = deepcopy(inputs)
            changed["native"]["locations"][0]["source"] = "/episode-other/codex/log"
            with self.assertRaisesRegex(
                CaptureVerificationError, "outside retained runtime"
            ):
                compare_verified_capture_overlap(**changed)
            changed = deepcopy(inputs)
            changed["retained_task"]["source_root"] = "/different-work"
            with self.assertRaisesRegex(CaptureVerificationError, "task roots differ"):
                compare_verified_capture_overlap(**changed)
