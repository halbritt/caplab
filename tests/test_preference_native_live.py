"""Containment contract for native preference-study invocations."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from caplab.preference.native import load_native_instrument
from caplab.preference.native_live import (
    NativePreferenceLiveContractError,
    build_contained_invocation,
    build_contained_version_probe,
    load_native_live_manifest,
)


ROOT = Path(__file__).parents[1]
INSTRUMENT = ROOT / "docs/product/studies/preference-001/native-instrument.json"
MANIFEST = ROOT / "docs/product/studies/preference-001/native-live-manifest.json"


class NativePreferenceLiveTests(unittest.TestCase):
    def test_prepared_manifest_cannot_cross_live_authorization_boundary(self) -> None:
        with self.assertRaisesRegex(
            NativePreferenceLiveContractError, "native_live_not_authorized"
        ):
            load_native_live_manifest(MANIFEST, INSTRUMENT)

    def test_both_native_harnesses_run_in_the_same_external_task_namespace(self) -> None:
        instrument = load_native_instrument(INSTRUMENT)
        with tempfile.TemporaryDirectory() as temporary_directory:
            task_root = Path(temporary_directory).resolve()
            fable = build_contained_invocation(instrument, "fable", "P01", task_root)
            gpt = build_contained_invocation(instrument, "gpt", "P01", task_root)

        for invocation in (fable, gpt):
            command = invocation["command"]
            self.assertEqual(command[0], "/usr/bin/bwrap")
            self.assertIn("--unshare-all", command)
            self.assertIn("--share-net", command)
            self.assertIn(str(task_root), command)
            self.assertIn("/work", command)
            self.assertNotIn(str(ROOT), command)
        self.assertIn("claude", fable["command"])
        self.assertIn("codex", gpt["command"])

    def test_version_probes_use_the_same_containment_without_a_model_prompt(self) -> None:
        instrument = load_native_instrument(INSTRUMENT)
        with tempfile.TemporaryDirectory() as temporary_directory:
            task_root = Path(temporary_directory).resolve()
            fable = build_contained_version_probe(instrument, "fable", task_root)
            gpt = build_contained_version_probe(instrument, "gpt", task_root)

        self.assertEqual(fable["command"][-2:], ["claude", "--version"])
        self.assertEqual(gpt["command"][-2:], ["codex", "--version"])


if __name__ == "__main__":
    unittest.main()
