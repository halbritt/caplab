"""Native-agent-system contract for the corrected preference instrument."""

from __future__ import annotations

import unittest
import hashlib
import json
import tempfile
from pathlib import Path

from caplab.preference.native import (
    NativePreferenceContractError,
    build_native_invocation,
    load_native_instrument,
    render_native_task,
)


ROOT = Path(__file__).parents[1]
INSTRUMENT = (
    ROOT
    / "docs"
    / "product"
    / "studies"
    / "preference-001"
    / "native-instrument.json"
)


class NativePreferenceInstrumentTests(unittest.TestCase):
    def test_instrument_loads_striatum_compatible_native_agent_systems(self) -> None:
        instrument = load_native_instrument(INSTRUMENT)

        self.assertEqual(instrument["status"], "model-free-qualified")
        self.assertEqual(
            {
                subject["tuple_id"]
                for subject in instrument["agent_systems"].values()
            },
            {"claude-fable-5-max", "codex-terra-max"},
        )
        self.assertEqual(set(instrument["_task_bank"]["tasks"]), {
            "P01", "P02", "P03", "P04", "P05", "P06"
        })
        self.assertNotIn("harness", instrument["_task_bank"])
        self.assertNotIn("subjects", instrument["_task_bank"])
        self.assertEqual(len(instrument["execution_order"]), 12)
        self.assertEqual(
            sorted(instrument["execution_order"]),
            sorted(
                f"{task_id}:{subject_id}"
                for task_id in instrument["reveal_map"]
                for subject_id in ("fable", "gpt")
            ),
        )

    def test_render_seals_task_to_native_instrument_not_proxy_task_bank(self) -> None:
        instrument = load_native_instrument(INSTRUMENT)
        with tempfile.TemporaryDirectory() as temporary_directory:
            destination = Path(temporary_directory) / "task"
            render_native_task(instrument, "P01", destination)

            seal = json.loads(
                (destination / ".caplab-task.json").read_text(encoding="utf-8")
            )
            self.assertEqual(seal["instrument_design_sha256"], instrument["design_sha256"])
            self.assertEqual(seal["study_id"], "caplab-preference-001-native-r1")
            self.assertTrue((destination / "AGENTS.md").is_file())

    def test_invocations_preserve_each_native_harness_tuple(self) -> None:
        instrument = load_native_instrument(INSTRUMENT)
        task_root = Path("/tmp/caplab-native-task")
        fable = build_native_invocation(instrument, "fable", "P01", task_root)
        gpt = build_native_invocation(instrument, "gpt", "P01", task_root)

        self.assertIn("claude", fable["command"])
        self.assertIn("claude-fable-5", fable["command"])
        self.assertIn("--effort", fable["command"])
        self.assertIn("max", fable["command"])
        self.assertNotIn("codex", fable["command"])
        self.assertIn("codex", gpt["command"])
        self.assertIn("gpt-5.6-terra", gpt["command"])
        self.assertIn("model_reasoning_effort=max", gpt["command"])
        self.assertNotIn("claude", gpt["command"])
        self.assertEqual(fable["cwd"], task_root)
        self.assertEqual(gpt["cwd"], task_root)

    def test_proxy_substitution_is_refused_even_with_a_resealed_instrument(self) -> None:
        document = json.loads(INSTRUMENT.read_text(encoding="utf-8"))
        document["agent_systems"]["fable"]["native_harness_id"] = "terminus-2"
        sealed = dict(document)
        sealed.pop("design_sha256")
        document["design_sha256"] = hashlib.sha256(
            json.dumps(
                sealed, ensure_ascii=False, sort_keys=True, separators=(",", ":")
            ).encode("utf-8")
        ).hexdigest()
        with tempfile.TemporaryDirectory(dir=INSTRUMENT.parent) as temporary_directory:
            changed = Path(temporary_directory) / "instrument.json"
            changed.write_text(json.dumps(document), encoding="utf-8")
            with self.assertRaisesRegex(
                NativePreferenceContractError, "native_agent_tuple_mismatch"
            ):
                load_native_instrument(changed)


if __name__ == "__main__":
    unittest.main()
