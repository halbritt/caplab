"""Native-agent contract for the review-dissent development calibration."""

from __future__ import annotations

import copy
import json
from hashlib import sha256
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from caplab.review_dissent.native import (
    NativeReviewContractError,
    build_native_review_capture,
    build_native_review_invocation,
    load_native_review_instrument,
    observed_reads_from_native_jsonl,
    render_native_review_cell,
)
from caplab.review_dissent.native_live import load_native_review_attempts
from caplab.review_dissent.native_results import (
    NativeReviewResultContractError,
    summarize_native_review_rows,
    normalize_native_review_campaign,
    _digest,
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
        for event in events:
            event["message"]["model"] = "claude-fable-5"
        events.insert(0, {"type": "system", "subtype": "init", "model": "claude-fable-5"})
        events.append({"type": "result", "subtype": "success", "is_error": False})
        stream = ("\n".join(json.dumps(event) for event in events) + "\n").encode()
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


    def model_stream(self) -> list[dict]:
        return [
            {"type": "system", "subtype": "init", "model": "claude-fable-5"},
            {"type": "assistant", "message": {"model": "claude-fable-5", "content": [{"type": "text", "text": "Review résumé\u2028continued."}]}},
            {"type": "result", "subtype": "success", "is_error": False,
             "modelUsage": {"claude-fable-5": {}, "auxiliary-model": {}}},
        ]

    def capture_stream(self, events, *, subject="fable", status="completed"):
        stream = events if isinstance(events, bytes) else (
            "\n".join(json.dumps(event, ensure_ascii=False) for event in events) + "\n"
        ).encode()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "task"
            render_native_review_cell(self.instrument, "r03", root)
            (root / "REVIEW.json").write_text(json.dumps({
                "verdict": "needs_revision", "findings": [], "summary": "Review résumé."
            }))
            return build_native_review_capture(
                self.instrument, cell_id="r03", subject_id=subject, task_root=root,
                native_jsonl=stream, status=status, observation_sha256="a" * 64,
                campaign_manifest_sha256="b" * 64,
            ), stream

    def test_model_mismatch_and_fallback_withhold_score_without_reassignment(self):
        baseline, _ = self.capture_stream(self.model_stream())
        cases = []
        for position in (0, 1):
            events = self.model_stream()
            target = events[position] if position == 0 else events[position]["message"]
            target["model"] = "another-model"
            cases.append(events)
        events = self.model_stream()
        events.insert(1, {"type": "system", "subtype": "model_refusal_fallback",
                          "original_model": "claude-fable-5", "fallback_model": "another-model"})
        cases.append(events)
        events = self.model_stream()
        events.insert(1, {"type": "assistant", "message": {"model": "another-model", "content": []}})
        cases.append(events)
        for events in cases:
            with self.subTest(events=events):
                capture, stream = self.capture_stream(events)
                self.assertIsNone(capture["mechanical"]["score"])
                self.assertEqual(capture["outcome"], "identity-unavailable")
                self.assertEqual(capture["status"], "completed")
                self.assertEqual(capture["subject_seal"], baseline["subject_seal"])
                identity = capture["model_identity"]
                self.assertEqual(identity["status"], "model-mismatch")
                self.assertEqual(identity["native_stdout_sha256"], sha256(stream).hexdigest())

    def test_missing_model_or_unbounded_stream_withholds_score(self):
        base = self.model_stream()
        cases = [base[1:], base[:-1], [base[0], base[-1]], base + [base[-1]],
                 [base[0], base[0], *base[1:]], [base[1], base[0], base[-1]]]
        for position in (0, 1):
            events = copy.deepcopy(base)
            target = events[position] if position == 0 else events[position]["message"]
            del target["model"]
            cases.append(events)
        events = copy.deepcopy(base)
        events[-1]["is_error"] = True
        cases.append(events)
        cases.append(b'')
        for events in cases:
            with self.subTest(events=events):
                capture, _ = self.capture_stream(events)
                self.assertIsNone(capture["mechanical"]["score"])
                self.assertEqual(capture["model_identity"]["status"], "model-unverified")
        _, stream = self.capture_stream(base)
        capture, _ = self.capture_stream(stream.rstrip(b"\n"))
        self.assertIsNone(capture["mechanical"]["score"])

    def test_auxiliary_usage_is_not_primary_model_identity(self):
        events = self.model_stream()
        before = copy.deepcopy(events)
        capture, stream = self.capture_stream(events)
        self.assertIsNotNone(capture["mechanical"]["score"])
        self.assertEqual(capture["model_identity"]["status"], "native-model-match")
        self.assertEqual(capture["model_identity"]["usage_models"][0]["models"],
                         ["auxiliary-model", "claude-fable-5"])
        self.assertEqual(capture["model_identity"]["response_models"],
                         [{"line": 2, "model": "claude-fable-5"}])
        self.assertEqual(capture["model_identity"]["native_stdout_sha256"], sha256(stream).hexdigest())
        self.assertEqual(events, before)
        self.assertEqual(capture["schema"], "caplab.review-dissent.native-capture/v2")

    def test_codex_stdout_and_claude_shaped_fields_do_not_attest_codex(self):
        for events in ([{"type": "thread.started", "thread_id": "new-local-fixture"}], self.model_stream()):
            capture, _ = self.capture_stream(events, subject="gpt")
            self.assertIsNone(capture["mechanical"]["score"])
            self.assertEqual(capture["model_identity"]["status"], "model-unverified")

    def test_identity_exclusion_blocks_refusal_credit_preserves_infrastructure(self):
        for status in ("refused", "invalid", "provider_failure"):
            capture, _ = self.capture_stream(b"", status=status)
            self.assertIsNone(capture["mechanical"]["score"])
            self.assertEqual(capture["status"], status)
            self.assertEqual(capture["outcome"], "infrastructure" if status == "provider_failure" else "identity-unavailable")

    def test_ambiguous_native_json_cannot_receive_score(self):
        for stream in (b'{"type":"assistant","type":"system"}\n',
                       b'{"type":"assistant","value":NaN}\n', b'[]\n', b'\xff\n'):
            with self.subTest(stream=stream), self.assertRaises(NativeReviewContractError):
                self.capture_stream(stream)

    def test_summary_rejects_unattested_credit_and_retains_excluded_slots(self):
        row = {"subject_id": "fable", "truth": "defect", "cue": "favorable", "world_id": "RD-D01",
               "status": "completed", "outcome": "identity-unavailable", "score": "1.0",
               "review_schema_valid": True}
        for identity in (None, "model-unverified", "model-mismatch"):
            with self.subTest(identity=identity), self.assertRaises(NativeReviewResultContractError):
                summarize_native_review_rows([{**row, "model_identity_status": identity}])
        rows = [{**row, "outcome": "subject-outcome", "model_identity_status": "native-model-match"} for _ in range(15)]
        rows.append({**row, "score": None, "model_identity_status": "model-mismatch"})
        summary = summarize_native_review_rows(rows)
        self.assertEqual(summary["counts"]["primary_slots"], 16)
        self.assertEqual(summary["counts"]["score_eligible"], 15)
        self.assertEqual(summary["counts"]["model_identity"], {"native-model-match": 15, "model-mismatch": 1})
        self.assertEqual(summary["groups"]["subject_id"]["subject_id=fable"]["model_identity"], summary["counts"]["model_identity"])
        self.assertEqual(summary["comparison_status"], "not-estimable")


    def test_normalizer_preserves_slots_and_writes_identity_bound_results(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            instrument = {**self.instrument, "_project_root": str(root)}
            manifest = {
                "campaign_id": "new-local-model-evidence-fixture", "manifest_sha256": "b" * 64,
                "_instrument": instrument,
                "storage": {"raw_custody_root": str(root / "custody"), "normalized_repository_root": "results"},
                "limits": {"maximum_trials": 20, "maximum_replacements": 4, "maximum_wall_clock_hours": 1},
            }
            original_hashes = {}
            for number, assignment in enumerate(instrument["execution_order"], 1):
                cell_id, subject_id = assignment.split(":")
                task_id = instrument["cells"][cell_id]["public_task_id"]
                attempt = root / "custody" / "attempts" / f"a{number:02d}"
                task = attempt / "input" / task_id
                render_native_review_cell(instrument, cell_id, task)
                review_bytes = json.dumps({"verdict": "needs_revision", "findings": [], "summary": "New local fixture."}).encode()
                (task / "REVIEW.json").write_bytes(review_bytes)
                events = self.model_stream() if subject_id == "fable" else [{"type": "thread.started", "thread_id": f"fixture-{number}"}]
                if number == 2:
                    events.insert(1, {"type": "system", "subtype": "model_refusal_fallback", "original_model": "claude-fable-5", "fallback_model": "another-model"})
                stream = ("\n".join(json.dumps(event) for event in events) + "\n").encode()
                (attempt / "native.stdout").write_bytes(stream)
                common = {"attempt_number": number, "attempt_kind": "primary", "slot_index": number - 1,
                          "cell_id": cell_id, "subject_id": subject_id, "public_task_id": task_id,
                          "tuple_id": instrument["agent_systems"][subject_id]["tuple_id"],
                          "manifest_sha256": manifest["manifest_sha256"]}
                launch = dict(common)
                launch["launch_sha256"] = _digest(launch)
                completion = {"launch_sha256": launch["launch_sha256"], "stdout_sha256": sha256(stream).hexdigest()}
                completion["completion_sha256"] = _digest(completion)
                observation = {**common, "launch_sha256": launch["launch_sha256"], "completion_sha256": completion["completion_sha256"],
                               "status": "completed", "duration_seconds": "1.0", "review_sha256": sha256(review_bytes).hexdigest(),
                               "output_path": (attempt / "native.stdout").relative_to(root / "custody").as_posix(),
                               "output_sha256": sha256(stream).hexdigest()}
                observation["observation_sha256"] = _digest(observation)
                for name, value in (("launch", launch), ("completion", completion), ("observation", observation)):
                    (attempt / f"{name}.json").write_text(json.dumps(value))
                for path in attempt.rglob("*"):
                    if path.is_file():
                        original_hashes[path] = sha256(path.read_bytes()).hexdigest()
            first_stdout = root / "custody" / "attempts" / "a01" / "native.stdout"
            original_stdout = first_stdout.read_bytes()

            def change_after_validation(value):
                attempts = load_native_review_attempts(value)
                first_stdout.write_bytes(original_stdout + b'{"type":"changed"}\n')
                return attempts

            with patch("caplab.review_dissent.native_results.load_native_review_attempts", side_effect=change_after_validation):
                with self.assertRaisesRegex(NativeReviewResultContractError, "output_changed_before_capture"):
                    normalize_native_review_campaign(manifest)
            self.assertFalse((root / "custody" / "normalization").exists())
            first_stdout.write_bytes(original_stdout)
            result = normalize_native_review_campaign(manifest)
            self.assertEqual(result["schema"], "caplab.review-dissent.native-development-result/v2")
            self.assertEqual(result["summary"]["counts"]["primary_slots"], 16)
            self.assertEqual(result["summary"]["counts"]["score_eligible"], 7)
            self.assertEqual(result["summary"]["counts"]["model_identity"],
                             {"native-model-match": 7, "model-mismatch": 1, "model-unverified": 8})
            self.assertEqual(result["summary"]["comparison_status"], "not-estimable")
            self.assertEqual(result["attempt_accounting"]["replacement_count"], 0)
            self.assertTrue(result["attempt_accounting"]["complete"])
            self.assertIsNone(result["failure_explanation"])
            self.assertEqual(json.loads((root / "results" / "result.json").read_text()), result)
            for row in result["rows"]:
                capture_path = root / "custody" / "normalization" / "captures" / row["cell_id"] / f"{row['subject_id']}.json"
                capture = json.loads(capture_path.read_text())
                self.assertEqual(row["capture_sha256"], capture["capture_sha256"])
                self.assertEqual(row["model_identity_status"], capture["model_identity"]["status"])
                self.assertEqual(row["native_stdout_sha256"], capture["model_identity"]["native_stdout_sha256"])
                self.assertEqual(row["score"], capture["mechanical"]["score"])
            self.assertEqual(original_hashes, {path: sha256(path.read_bytes()).hexdigest() for path in original_hashes})
            with self.assertRaisesRegex(NativeReviewResultContractError, "normalization_exists"):
                normalize_native_review_campaign(manifest)

    def test_zero_schema_valid_reviews_fails_calibration_without_model_comparison(self) -> None:
        rows = [
            {
                "subject_id": "fable" if index % 2 else "gpt",
                "truth": "clean" if index % 4 < 2 else "defect",
                "cue": "favorable" if index % 2 else "cautious",
                "world_id": "RD-D01" if index < 8 else "RD-D02",
                "status": "invalid",
                "outcome": "subject-invalid",
                "score": None,
                "review_schema_valid": False,
            }
            for index in range(16)
        ]
        summary = summarize_native_review_rows(rows)
        self.assertEqual(summary["counts"]["primary_slots"], 16)
        self.assertEqual(summary["counts"]["score_eligible"], 0)
        self.assertEqual(summary["conclusion"], "instrument-not-calibrated")
        self.assertEqual(summary["comparison_status"], "not-estimable")


if __name__ == "__main__":
    unittest.main()
