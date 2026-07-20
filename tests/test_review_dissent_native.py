"""Native-agent contract for the review-dissent development calibration."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from caplab.review_dissent.native import (
    build_native_review_capture,
    build_native_review_invocation,
    load_native_review_instrument,
    observed_reads_from_native_jsonl,
    render_native_review_cell,
)


ROOT = Path(__file__).parents[1]
STUDY = ROOT / "docs/product/studies/review-dissent-001"
INSTRUMENT = STUDY / "native-instrument.json"


class NativeReviewDissentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.instrument = load_native_review_instrument(INSTRUMENT)

    def test_loader_uses_native_tuples_without_opening_heldout(self) -> None:
        original = Path.read_bytes

        def guarded(path: Path) -> bytes:
            if path.name == "heldout.json":
                raise AssertionError("native calibration opened heldout content")
            return original(path)

        with patch.object(Path, "read_bytes", guarded):
            instrument = load_native_review_instrument(INSTRUMENT)

        self.assertEqual(instrument["agent_systems"]["fable"]["tuple_id"], "claude-fable-5-max")
        self.assertEqual(instrument["agent_systems"]["gpt"]["tuple_id"], "codex-terra-max")
        self.assertEqual(len(instrument["execution_order"]), 16)
        self.assertEqual(instrument["heldout_seal"]["cell_count"], 8)
        self.assertNotIn("worlds", instrument["heldout_seal"])

    def test_invocations_preserve_native_harnesses_and_review_only_prompt(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            render_native_review_cell(self.instrument, "r03", root / "fable")
            fable = build_native_review_invocation(
                self.instrument, "fable", "r03", root / "fable"
            )
            render_native_review_cell(self.instrument, "r03", root / "gpt")
            gpt = build_native_review_invocation(
                self.instrument, "gpt", "r03", root / "gpt"
            )

        self.assertIn("claude-fable-5", fable["command"])
        self.assertIn("--effort", fable["command"])
        self.assertIn("gpt-5.6-terra", gpt["command"])
        self.assertIn("model_reasoning_effort=max", gpt["command"])
        self.assertIn("REVIEW.json", fable["command"][-1])
        self.assertIn("Do not edit any other task file", fable["command"][-1])

    def test_native_trace_reads_and_completed_capture_are_mechanically_graded(self) -> None:
        events = [
            {
                "type": "assistant",
                "message": {"content": [{"type": "tool_use", "name": "Read", "input": {"file_path": "/work/ACCEPTANCE.md"}}]},
            },
            {
                "type": "assistant",
                "message": {"content": [{"type": "tool_use", "name": "Read", "input": {"file_path": "/work/src/migration.py"}}]},
            },
            {
                "type": "assistant",
                "message": {"content": [{"type": "tool_use", "name": "Read", "input": {"file_path": "/work/tests/test_migration.py"}}]},
            },
        ]
        stream = "\n".join(json.dumps(event) for event in events).encode()
        available = ["ACCEPTANCE.md", "src/migration.py", "tests/test_migration.py"]
        self.assertEqual(
            observed_reads_from_native_jsonl("fable", stream, available), available
        )

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "task"
            render_native_review_cell(self.instrument, "r03", root)
            review = {
                "verdict": "needs_revision",
                "findings": [
                    {
                        "severity": "critical",
                        "criterion": "AC-2",
                        "path": "src/migration.py",
                        "summary": "The migration bypasses validate before mutation.",
                    }
                ],
                "summary": "One acceptance-blocking defect.",
            }
            (root / "REVIEW.json").write_text(json.dumps(review), encoding="utf-8")
            capture = build_native_review_capture(
                self.instrument,
                cell_id="r03",
                subject_id="fable",
                task_root=root,
                native_jsonl=stream,
                status="completed",
                observation_sha256="a" * 64,
                campaign_manifest_sha256="b" * 64,
            )

        self.assertEqual(capture["mechanical"]["score"], "1.0")
        self.assertTrue(capture["mechanical"]["required_evidence_observed"])
        self.assertTrue(capture["preservation"]["preserved"])
        self.assertEqual(capture["execution_mode"], "native-live")


if __name__ == "__main__":
    unittest.main()
