"""Model-free qualification of the CAPLAB preference-study instrument."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from caplab.preference import (
    PreferenceContractError,
    assess_study_state,
    build_blinded_packet,
    load_instrument,
    render_task,
    run_canned_attempt,
)


ROOT = Path(__file__).parents[1]
INSTRUMENT = ROOT / "docs" / "product" / "studies" / "preference-001" / "instrument.json"


class PreferenceInstrumentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.instrument = load_instrument(INSTRUMENT)

    def test_frozen_subjects_share_one_harness_surface(self) -> None:
        self.assertEqual(self.instrument["status"], "model-free-qualified")
        self.assertEqual(self.instrument["harness"], {"name": "terminus-2", "version": "2.0.0"})
        self.assertEqual(
            {subject["model_id"] for subject in self.instrument["subjects"].values()},
            {"claude-fable-5", "gpt-5.6-terra"},
        )
        surfaces = {json.dumps(subject["surface"], sort_keys=True) for subject in self.instrument["subjects"].values()}
        self.assertEqual(len(surfaces), 1)
        self.assertEqual(self.instrument["call_budget"]["authorized_calls"], 0)
        self.assertEqual(self.instrument["call_budget"]["authorized_usd"], 0)
        self.assertEqual(
            self.instrument["subject_instruction_sha256"],
            "6a0a7cbda7c6011bc48839436042bb933dd478dadad46d1d722dc4191cf982c6",
        )

    def test_fixed_order_and_all_six_task_contracts_are_qualified(self) -> None:
        self.assertEqual(len(self.instrument["execution_order"]), 12)
        self.assertEqual(len(set(self.instrument["execution_order"])), 12)
        self.assertEqual(set(self.instrument["tasks"]), {"P01", "P02", "P03", "P04", "P05", "P06"})
        for task in self.instrument["tasks"].values():
            self.assertGreaterEqual(len(task["constraints"]), 8)
            self.assertGreaterEqual(len({item["surface"] for item in task["constraints"]}), 4)
            self.assertTrue(all(item["oracle"]["kind"] in {"equals", "absent", "contains", "unchanged"} for item in task["constraints"]))

    def test_all_twelve_canned_subject_positions_produce_blindable_pairs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            for task_id, task in self.instrument["tasks"].items():
                final_files: dict[str, str] = {}
                handoff_parts: list[str] = []
                for constraint in task["constraints"]:
                    oracle = constraint["oracle"]
                    if oracle["path"] == "$handoff":
                        handoff_parts.append(oracle["value"])
                    elif oracle["kind"] == "equals":
                        final_files[oracle["path"]] = oracle["value"]
                    elif oracle["kind"] == "contains":
                        final_files[oracle["path"]] = final_files.get(oracle["path"], "") + oracle["value"] + "\n"
                captures = {
                    subject_id: run_canned_attempt(
                        self.instrument,
                        task_id=task_id,
                        subject_id=subject_id,
                        attempt={
                            "mode": "canned",
                            "status": "completed",
                            "final_files": final_files,
                            "handoff": "; ".join(handoff_parts),
                        },
                        destination=root / f"{task_id}-{subject_id}",
                    )
                    for subject_id in ("fable", "gpt")
                }
                self.assertEqual({capture["outcome"] for capture in captures.values()}, {"complete"})
                self.assertEqual(
                    {capture["instrument_design_sha256"] for capture in captures.values()},
                    {self.instrument["design_sha256"]},
                )
                self.assertEqual(len({capture["subject_seal"] for capture in captures.values()}), 2)
                packet = build_blinded_packet(self.instrument, task_id, captures)
                self.assertEqual(set(packet["candidates"]), {"A", "B"})

    def test_task_render_is_fresh_deterministic_and_refuses_reuse(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            destination = Path(temporary_directory) / "task"
            rendered = render_task(self.instrument, "P01", destination)
            self.assertEqual(rendered["task_id"], "P01")
            self.assertTrue((destination / "tracker.json").is_file())
            self.assertTrue((destination / ".caplab-task.json").is_file())
            with self.assertRaisesRegex(PreferenceContractError, "destination_exists"):
                render_task(self.instrument, "P01", destination)

    def test_canned_capture_separates_mechanical_and_human_judgment(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            capture = run_canned_attempt(
                self.instrument,
                task_id="P01",
                subject_id="fable",
                attempt={
                    "mode": "canned",
                    "status": "completed",
                    "final_files": {
                        "tracker.json": "{\"future_work\":\"ready\",\"v0\":\"narrow\"}\n",
                        "decision.md": "Scope and authorization are distinct. Future work remains ready.\n",
                    },
                    "handoff": "Narrowed v0 and preserved the future queue; checks passed.",
                },
                destination=Path(temporary_directory) / "run",
            )
        self.assertEqual(capture["outcome"], "complete")
        self.assertGreaterEqual(len(capture["mechanical"]["satisfied"]), 8)
        self.assertEqual(capture["human_disposition"], None)
        self.assertNotIn("provider", capture)
        self.assertEqual(capture["execution_mode"], "canned")

    def test_failure_classification_does_not_replace_subject_outcomes(self) -> None:
        cases = {
            "refused": ("declined", False),
            "partial": ("partial", False),
            "invalid": ("invalid", False),
            "provider_failure": ("infrastructure", True),
        }
        for status, expected in cases.items():
            with self.subTest(status=status), tempfile.TemporaryDirectory() as temporary_directory:
                capture = run_canned_attempt(
                    self.instrument,
                    task_id="P02",
                    subject_id="gpt",
                    attempt={"mode": "canned", "status": status, "final_files": {}, "handoff": ""},
                    destination=Path(temporary_directory) / "run",
                )
                self.assertEqual((capture["outcome"], capture["replacement_eligible"]), expected)

    def test_blinded_packet_contains_no_subject_identity_or_judgment(self) -> None:
        captures = {}
        with tempfile.TemporaryDirectory() as temporary_directory:
            for subject_id in ("fable", "gpt"):
                captures[subject_id] = run_canned_attempt(
                    self.instrument,
                    task_id="P03",
                    subject_id=subject_id,
                    attempt={"mode": "canned", "status": "completed", "final_files": {}, "handoff": "State checked; retry bounded."},
                    destination=Path(temporary_directory) / subject_id,
                )
            packet = build_blinded_packet(self.instrument, "P03", captures)
        encoded = json.dumps(packet, sort_keys=True).casefold()
        for forbidden in ("fable", "gpt", "anthropic", "openai", "claude", "gpt-5.6", "terminus"):
            self.assertNotIn(forbidden, encoded)
        self.assertEqual(set(packet["candidates"]), {"A", "B"})
        self.assertEqual(packet["adjudication"]["selection"], None)

    def test_blinding_refuses_identity_leak_in_subject_material(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            captures = {
                subject_id: run_canned_attempt(
                    self.instrument,
                    task_id="P04",
                    subject_id=subject_id,
                    attempt={"mode": "canned", "status": "partial", "final_files": {}, "handoff": "Completed."},
                    destination=Path(temporary_directory) / subject_id,
                )
                for subject_id in ("fable", "gpt")
            }
            captures["fable"]["handoff"] = "Claude Fable 5 completed this."
            with self.assertRaisesRegex(PreferenceContractError, "identity_leak"):
                build_blinded_packet(self.instrument, "P04", captures)

    def test_blinding_refuses_swapped_or_unsealed_capture(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            captures = {
                subject_id: run_canned_attempt(
                    self.instrument,
                    task_id="P06",
                    subject_id=subject_id,
                    attempt={"mode": "canned", "status": "partial", "final_files": {}, "handoff": "Completed."},
                    destination=Path(temporary_directory) / subject_id,
                )
                for subject_id in ("fable", "gpt")
            }
            captures["fable"], captures["gpt"] = captures["gpt"], captures["fable"]
            with self.assertRaisesRegex(PreferenceContractError, "capture_identity_mismatch"):
                build_blinded_packet(self.instrument, "P06", captures)

    def test_mutated_frozen_surface_is_refused(self) -> None:
        mutated = json.loads(INSTRUMENT.read_text(encoding="utf-8"))
        mutated["subjects"]["gpt"]["surface"]["output_tokens"] = 9000
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "instrument.json"
            path.write_text(json.dumps(mutated), encoding="utf-8")
            with self.assertRaisesRegex(PreferenceContractError, "unequal_subject_surface"):
                load_instrument(path)

    def test_any_other_frozen_design_mutation_is_refused(self) -> None:
        mutations = (
            lambda value: value["execution_order"].reverse(),
            lambda value: value["reveal_map"]["P01"].update({"A": "fable", "B": "gpt"}),
            lambda value: value["subjects"]["fable"].update({"model_id": "substitute"}),
            lambda value: value["tasks"]["P06"].update({"contract_sha256": "0" * 64}),
            lambda value: value["call_budget"].update({"authorized_calls": 1}),
        )
        for mutate in mutations:
            with self.subTest(mutate=mutate), tempfile.TemporaryDirectory() as temporary_directory:
                value = json.loads(INSTRUMENT.read_text(encoding="utf-8"))
                mutate(value)
                path = Path(temporary_directory) / "instrument.json"
                path.write_text(json.dumps(value), encoding="utf-8")
                with self.assertRaises(PreferenceContractError):
                    load_instrument(path)

    def test_replacement_and_adjudication_stop_rules_are_accounted(self) -> None:
        allowed = assess_study_state([
            {"task_id": "P01", "outcome": "infrastructure", "replacement": True},
            {"task_id": "P02", "outcome": "invalid", "replacement": False},
        ])
        self.assertTrue(allowed["preference_adjudication_allowed"])
        stopped = assess_study_state(
            [
                {"task_id": f"P0{index + 1}", "outcome": "infrastructure", "replacement": True}
                for index in range(5)
            ],
            blinding_breach=True,
        )
        self.assertFalse(stopped["preference_adjudication_allowed"])
        self.assertEqual(stopped["stop_reasons"], ["replacement_ceiling_exceeded", "blinding_breach"])
        with self.assertRaisesRegex(PreferenceContractError, "replacement_for_subject_outcome"):
            assess_study_state([{"task_id": "P01", "outcome": "declined", "replacement": True}])

    def test_live_mode_and_external_locator_are_refused(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            with self.assertRaisesRegex(PreferenceContractError, "model_calls_not_authorized"):
                run_canned_attempt(
                    self.instrument,
                    task_id="P05",
                    subject_id="gpt",
                    attempt={"mode": "live", "status": "completed", "final_files": {}, "handoff": ""},
                    destination=Path(temporary_directory) / "run",
                )


if __name__ == "__main__":
    unittest.main()
