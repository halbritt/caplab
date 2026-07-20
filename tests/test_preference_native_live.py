"""Containment contract for native preference-study invocations."""

from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from caplab.preference.native import load_native_instrument
from caplab.preference.native_live import (
    NativePreferenceLiveContractError,
    build_contained_invocation,
    build_contained_version_probe,
    load_native_live_manifest,
    prepare_native_trial,
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

    def test_prepared_manifest_cannot_create_attempt_custody(self) -> None:
        instrument = load_native_instrument(INSTRUMENT)
        with tempfile.TemporaryDirectory() as temporary_directory:
            manifest = {
                "status": "prepared-not-authorized",
                "authority": "pending-adr-0041",
                "_instrument": instrument,
                "storage": {"raw_custody_root": temporary_directory},
            }
            with self.assertRaisesRegex(
                NativePreferenceLiveContractError, "native_live_not_authorized"
            ):
                prepare_native_trial(manifest, slot_index=0, attempt_kind="primary")
            self.assertEqual(list(Path(temporary_directory).iterdir()), [])

    def test_authorized_manifest_seals_one_native_slot_before_launch(self) -> None:
        document = json.loads(MANIFEST.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as custody_directory, tempfile.TemporaryDirectory(
            dir=MANIFEST.parent
        ) as manifest_directory:
            document["status"] = "active"
            document["authority"] = "adr-0041"
            document["storage"]["raw_custody_root"] = custody_directory
            sealed = dict(document)
            sealed.pop("manifest_sha256")
            document["manifest_sha256"] = hashlib.sha256(
                json.dumps(
                    sealed, ensure_ascii=False, sort_keys=True, separators=(",", ":")
                ).encode("utf-8")
            ).hexdigest()
            active_path = Path(manifest_directory) / "manifest.json"
            active_path.write_text(json.dumps(document), encoding="utf-8")
            manifest = load_native_live_manifest(active_path, INSTRUMENT)
            attempt_root, command = prepare_native_trial(
                manifest, slot_index=0, attempt_kind="primary"
            )

            launch = json.loads((attempt_root / "launch.json").read_text(encoding="utf-8"))
            self.assertEqual(launch["task_id"], "P02")
            self.assertEqual(launch["subject_id"], "fable")
            self.assertEqual(launch["command"], command)
            self.assertTrue((attempt_root / "input/P02/.caplab-task.json").is_file())

    def test_authorized_manifest_refuses_changed_containment_source(self) -> None:
        document = json.loads(MANIFEST.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory(dir=MANIFEST.parent) as manifest_directory:
            document["status"] = "active"
            document["authority"] = "adr-0041"
            document["containment"]["source_sha256"] = "0" * 64
            sealed = dict(document)
            sealed.pop("manifest_sha256")
            document["manifest_sha256"] = hashlib.sha256(
                json.dumps(
                    sealed, ensure_ascii=False, sort_keys=True, separators=(",", ":")
                ).encode("utf-8")
            ).hexdigest()
            active_path = Path(manifest_directory) / "manifest.json"
            active_path.write_text(json.dumps(document), encoding="utf-8")

            with self.assertRaisesRegex(
                NativePreferenceLiveContractError,
                "native_live_containment_source_mismatch",
            ):
                load_native_live_manifest(active_path, INSTRUMENT)

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
