"""Review outputs are root-scoped exceptions, not reserved basenames."""

import copy
import json
from pathlib import Path
import tempfile
import unittest

from caplab.review_dissent.instrument import (
    ReviewDissentContractError,
    _snapshot,
    grade_canned_review,
)
from caplab.review_dissent.native import (
    NativeReviewContractError,
    _snapshot_task,
    build_native_review_capture,
    load_native_review_instrument,
    render_native_review_cell,
)


STUDY = Path(__file__).parents[1] / "docs/product/studies/review-dissent-001"
NAMES = ("REVIEW.json", ".caplab-review-task.json", ".caplab-native-review-task.json")


class ReviewTaskPreservationTests(unittest.TestCase):
    def setUp(self):
        self.instrument = load_native_review_instrument(STUDY / "native-instrument.json")
        self.oracle = self.instrument["cells"]["r03"]["oracle"]
        self.review = {
            "verdict": self.oracle["reference_verdict"],
            "findings": [{"severity": "critical", "criterion": self.oracle["criterion"],
                          "path": self.oracle["path"], "summary": "Synthetic reference finding."}],
            "summary": "Synthetic preservation check.",
        }
        events = [{"type": "system", "subtype": "init", "model": "claude-fable-5"}]
        for path in self.oracle["required_reads"]:
            events.append({"type": "assistant", "message": {
                "model": "claude-fable-5", "content": [
                    {"type": "tool_use", "name": "Read", "input": {"file_path": "/work/" + path}}]}})
        events.append({"type": "result", "subtype": "success", "is_error": False})
        self.stream = ("\n".join(json.dumps(e) for e in events) + "\n").encode()

    def native_capture(self, root, instrument=None):
        return build_native_review_capture(
            instrument or self.instrument, cell_id="r03", subject_id="fable",
            task_root=root, native_jsonl=self.stream, status="completed",
            observation_sha256="a" * 64, campaign_manifest_sha256="b" * 64,
        )

    def canned_capture(self, root, updates, instrument=None):
        return grade_canned_review(
            instrument or self.instrument, cell_id="r03", subject_id="synthetic",
            attempt={"mode": "canned", "status": "completed", "review": self.review,
                     "observed_reads": self.oracle["required_reads"], "target_updates": updates},
            destination=root,
        )

    def assert_preservation(self, capture, preserved):
        self.assertIs(capture["preservation"]["preserved"], preserved)
        self.assertIs(capture["mechanical"]["preserved"], preserved)
        self.assertEqual(capture["mechanical"]["score"], "1.0" if preserved else "0.0")
        self.assertEqual(capture["outcome"], "subject-outcome")

    def test_native_nested_additions_cannot_hide_behind_root_output_names(self):
        for directory in ("src", "nested/deeper"):
            for name in NAMES:
                with self.subTest(directory=directory, name=name), tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp) / "task"
                    render_native_review_cell(self.instrument, "r03", root)
                    (root / "REVIEW.json").write_text(json.dumps(self.review))
                    self.assert_preservation(self.native_capture(root), True)
                    extra = root / directory / name
                    extra.parent.mkdir(parents=True, exist_ok=True)
                    extra.write_bytes(b"untracked binary\x00\xff")
                    self.assert_preservation(self.native_capture(root), False)

    def test_canned_nested_additions_cannot_hide_behind_root_output_names(self):
        for name in NAMES:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                capture = self.canned_capture(Path(tmp) / "task", {"nested/" + name: "extra"})
                self.assert_preservation(capture, False)

    def test_legitimate_nested_native_inputs_are_preserved_then_detect_edit_or_deletion(self):
        for name in NAMES:
            for action in ("edit", "delete"):
                with self.subTest(name=name, action=action), tempfile.TemporaryDirectory() as tmp:
                    instrument = copy.deepcopy(self.instrument)
                    world = instrument["worlds"][instrument["cells"]["r03"]["world_id"]]
                    relative = "fixtures/" + name
                    world["common_files"][relative] = "résumé fixture\n"
                    root = Path(tmp) / "task"
                    render_native_review_cell(instrument, "r03", root)
                    (root / "REVIEW.json").write_text(json.dumps(self.review))
                    self.assert_preservation(self.native_capture(root, instrument), True)
                    target = root / relative
                    if action == "edit":
                        target.write_bytes(b"changed\x00\xff")
                    else:
                        target.unlink()
                    self.assert_preservation(self.native_capture(root, instrument), False)

    def test_legitimate_nested_canned_inputs_detect_edits(self):
        for name in NAMES:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                instrument = copy.deepcopy(self.instrument)
                world = instrument["worlds"][instrument["cells"]["r03"]["world_id"]]
                relative = "fixtures/" + name
                world["common_files"][relative] = "original\n"
                self.assert_preservation(self.canned_capture(Path(tmp) / "unchanged", {}, instrument), True)
                self.assert_preservation(
                    self.canned_capture(Path(tmp) / "changed", {relative: "edited\n"}, instrument), False)

    def test_root_exemptions_do_not_exempt_symlinks(self):
        for snapshot, error, names in (
            (_snapshot, ReviewDissentContractError, NAMES[:2]),
            (_snapshot_task, NativeReviewContractError, NAMES),
        ):
            for name in names:
                for directory in (".", "nested"):
                    with self.subTest(snapshot=snapshot.__name__, name=name, directory=directory):
                        with tempfile.TemporaryDirectory() as tmp:
                            root = Path(tmp) / "task"
                            parent = root / directory
                            parent.mkdir(parents=True)
                            target = Path(tmp) / "outside"
                            target.write_bytes(b"must not follow")
                            (parent / name).symlink_to(target)
                            with self.assertRaises(error):
                                snapshot(root)


if __name__ == "__main__":
    unittest.main()
