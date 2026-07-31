"""Tests for advisory-selection artifact-rater recovery tooling."""

import json
import tempfile
import unittest
from pathlib import Path

from caplab.artifact_rater import (
    CalibrationError,
    build_artifact_prompt,
    build_calibration_manifest,
    build_judgment_schema,
    evaluate_calibration,
    extract_thread_id,
    read_rollout_attestation,
    validate_judgment,
)


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


class ArtifactRaterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.campaign = self.root / "campaign"
        self.scenarios = self.root / "scenarios"

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def _scenario(self, name: str) -> None:
        _write_json(
            self.scenarios / name / "codes.json",
            {
                "scenario": name,
                "codes": [
                    {"id": "C1", "positive": "one", "negative_space": "not one"},
                    {"id": "C2", "positive": "two", "negative_space": "not two"},
                    {"id": "C3", "positive": "three", "negative_space": "not three"},
                    {"id": "SCOPE", "positive": "scope", "negative_space": "not scope"},
                ],
            },
        )

    def _attempt(
        self,
        scenario: str,
        number: int,
        judgment: dict[str, bool],
        *,
        disposition: str = "behavioural-attempt",
        diff: str = "diff --git a/a.py b/a.py\n+changed\n",
    ) -> str:
        slot = f"{scenario}--none--luna-low--t{number}"
        attempt = self.campaign / "attempts" / slot
        _write_json(
            attempt / "episode.json",
            {
                "slot": slot,
                "scenario": scenario,
                "disposition": disposition,
            },
        )
        _write_json(attempt / "codes.json", judgment)
        (attempt / "diff.patch").write_text(diff, encoding="utf-8")
        return slot

    def test_manifest_selection_is_deterministic_balanced_and_fail_closed(self) -> None:
        scenario = "02-example"
        self._scenario(scenario)
        judgments = [
            {"C1": False, "C2": False, "C3": False, "SCOPE": True},
            {"C1": True, "C2": False, "C3": False, "SCOPE": True},
            {"C1": True, "C2": True, "C3": False, "SCOPE": True},
            {"C1": True, "C2": True, "C3": True, "SCOPE": True},
        ]
        for number in range(1, 13):
            self._attempt(scenario, number, judgments[(number - 1) % 4])
        self._attempt(
            scenario,
            50,
            judgments[0],
            disposition="infrastructure",
        )
        self._attempt(scenario, 51, {}, diff="")

        first = build_calibration_manifest(
            self.campaign, self.scenarios, seed=20260731, per_scenario=6
        )
        second = build_calibration_manifest(
            self.campaign, self.scenarios, seed=20260731, per_scenario=6
        )

        self.assertEqual(first, second)
        self.assertEqual(len(first["entries"]), 6)
        self.assertEqual(
            {entry["old_score"] for entry in first["entries"]},
            {0.0, 1 / 3, 2 / 3, 1.0},
        )
        self.assertTrue(
            all(entry["disposition"] == "behavioural-attempt" for entry in first["entries"])
        )
        self.assertTrue(all(entry["diff_sha256"] for entry in first["entries"]))

    def test_manifest_refuses_a_scenario_without_six_eligible_attempts(self) -> None:
        scenario = "02-example"
        self._scenario(scenario)
        for number in range(1, 6):
            self._attempt(
                scenario,
                number,
                {"C1": False, "C2": False, "C3": False, "SCOPE": True},
            )

        with self.assertRaisesRegex(CalibrationError, "eligible attempts"):
            build_calibration_manifest(
                self.campaign, self.scenarios, seed=20260731, per_scenario=6
            )

    def test_judgment_requires_exact_boolean_keys(self) -> None:
        expected = ("C1", "C2", "C3", "SCOPE")
        valid = {"C1": True, "C2": False, "C3": True, "SCOPE": False}
        self.assertEqual(validate_judgment(valid, expected), valid)

        invalid = (
            {},
            {"C1": True, "C2": False, "C3": True},
            {**valid, "explanation": "plausible"},
            {**valid, "C1": 1},
        )
        for value in invalid:
            with self.subTest(value=value):
                with self.assertRaises(CalibrationError):
                    validate_judgment(value, expected)

    def test_prompt_is_blinded_and_schema_is_exact(self) -> None:
        scenario = "02-example"
        self._scenario(scenario)
        prompt = build_artifact_prompt(
            self.scenarios / scenario / "codes.json",
            "diff --git a/a.py b/a.py\n+changed\n",
        )
        for hidden in ("02-example", "luna", "injection", "--none--", "old_judgment"):
            self.assertNotIn(hidden, prompt)
        self.assertIn('"C1"', prompt)
        self.assertIn("diff --git", prompt)

        schema = build_judgment_schema(("C1", "C2", "C3", "SCOPE"))
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(schema["required"], ["C1", "C2", "C3", "SCOPE"])
        self.assertEqual(schema["properties"]["C1"], {"type": "boolean"})

    def test_thread_and_rollout_attestation_are_required(self) -> None:
        events = (
            '{"type":"thread.started","thread_id":"thread-123"}\n'
            '{"type":"turn.completed","usage":{"input_tokens":1}}\n'
        )
        self.assertEqual(extract_thread_id(events), "thread-123")
        with self.assertRaises(CalibrationError):
            extract_thread_id('{"type":"turn.completed"}\n')

        rollout = self.root / "rollout.jsonl"
        rollout.write_text(
            "\n".join(
                [
                    json.dumps(
                        {
                            "type": "session_meta",
                            "payload": {"id": "thread-123", "cli_version": "0.146.0"},
                        }
                    ),
                    json.dumps(
                        {
                            "type": "event_msg",
                            "payload": {
                                "type": "thread_settings_applied",
                                "thread_settings": {
                                    "model": "gpt-5.6-luna",
                                    "reasoning_effort": "high",
                                },
                            },
                        }
                    ),
                ]
            ),
            encoding="utf-8",
        )
        attestation = read_rollout_attestation(rollout, "thread-123")
        self.assertEqual(attestation["model"], "gpt-5.6-luna")
        self.assertEqual(attestation["effort"], "high")
        self.assertEqual(attestation["cli_version"], "0.146.0")

    def test_calibration_evaluation_enforces_every_gate(self) -> None:
        entries = []
        scores: dict[str, dict[str, bool]] = {}
        for scenario_number in range(7):
            scenario = f"{scenario_number:02d}-example"
            for trial in range(6):
                slot = f"{scenario}--none--luna-low--t{trial}"
                old = {
                    "C1": trial % 2 == 0,
                    "C2": trial % 3 == 0,
                    "C3": trial % 4 == 0,
                    "SCOPE": True,
                }
                entries.append(
                    {
                        "slot": slot,
                        "scenario": scenario,
                        "code_ids": ["C1", "C2", "C3", "SCOPE"],
                        "old_judgment": old,
                    }
                )
                scores[slot] = dict(old)

        manifest = {"entries": entries}
        passed = evaluate_calibration(manifest, scores)
        self.assertTrue(passed["passed"])
        self.assertEqual(passed["overall_primary_agreement"], 1.0)

        scores[entries[0]["slot"]]["C1"] = not scores[entries[0]["slot"]]["C1"]
        scores[entries[1]["slot"]]["C1"] = not scores[entries[1]["slot"]]["C1"]
        scores[entries[2]["slot"]]["C1"] = not scores[entries[2]["slot"]]["C1"]
        scores[entries[3]["slot"]]["C1"] = not scores[entries[3]["slot"]]["C1"]
        failed = evaluate_calibration(manifest, scores)
        self.assertFalse(failed["passed"])
        self.assertLess(failed["scenario_primary_agreement"]["00-example"], 0.80)


if __name__ == "__main__":
    unittest.main()
