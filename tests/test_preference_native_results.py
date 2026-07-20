"""Native preference normalization, freeze, and reveal contracts."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from caplab.preference.native import load_native_instrument
from caplab.preference.native_results import (
    NativePreferenceResultContractError,
    _digest,
    freeze_native_dispositions,
    reveal_native_dispositions,
)


ROOT = Path(__file__).parents[1]
INSTRUMENT = ROOT / "docs/product/studies/preference-001/native-instrument.json"


class NativePreferenceResultTests(unittest.TestCase):
    def _prepared_blind_fixture(
        self, root: Path
    ) -> tuple[dict[str, object], Path, Path, Path]:
        instrument = load_native_instrument(INSTRUMENT)
        packet_root = root / "packets-root"
        raw_root = root / "raw-normalization"
        decisions: dict[str, object] = {}
        hashes: dict[str, str] = {}
        capture_hashes: dict[str, str] = {}
        for task_id in sorted(instrument["reveal_map"]):
            packet = {"schema": "test-blind/v1", "pair_id": task_id}
            path = packet_root / "packets" / f"{task_id}.json"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(packet), encoding="utf-8")
            hashes[task_id] = _digest(packet)
            preferred_alias = next(
                alias
                for alias, subject_id in instrument["reveal_map"][task_id].items()
                if subject_id == "fable"
            )
            decisions[task_id] = {
                "preferred_alias": preferred_alias,
                "reasons": ["better mandatory-constraint coverage"],
                "rationale": "This candidate preserves more mandatory constraints.",
                "uncertainty": "low",
            }
            for subject_id, satisfied in (("fable", 8), ("gpt", 6)):
                capture_path = raw_root / "captures" / task_id / f"{subject_id}.json"
                capture_path.parent.mkdir(parents=True, exist_ok=True)
                capture = {
                    "outcome": "complete",
                    "mechanical": {
                        "satisfied": [f"C{index}" for index in range(satisfied)],
                        "missed": [],
                    },
                }
                capture_path.write_text(json.dumps(capture), encoding="utf-8")
                capture_hashes[
                    f"captures/{task_id}/{subject_id}.json"
                ] = _digest(capture)
        capture_manifest = {
            "schema": "caplab.preference.native-capture-manifest/v1",
            "campaign_id": "test-native-campaign",
            "manifest_sha256": "a" * 64,
            "normalization_source_sha256": "b" * 64,
            "captures": capture_hashes,
        }
        capture_manifest["capture_manifest_sha256"] = _digest(capture_manifest)
        (raw_root / "capture-manifest.json").write_text(
            json.dumps(capture_manifest), encoding="utf-8"
        )
        manifest = {
            "schema": "caplab.preference.native-packet-manifest/v1",
            "campaign_id": "test-native-campaign",
            "manifest_sha256": "a" * 64,
            "capture_manifest_sha256": capture_manifest[
                "capture_manifest_sha256"
            ],
            "packets": hashes,
        }
        manifest["packet_manifest_sha256"] = _digest(manifest)
        (packet_root / "packet-manifest.json").write_text(
            json.dumps(manifest), encoding="utf-8"
        )
        decisions_path = root / "decisions.json"
        decisions_path.write_text(json.dumps(decisions), encoding="utf-8")
        return instrument, packet_root, raw_root, decisions_path

    def test_freeze_precedes_reveal_and_recomputes_thresholds(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            instrument, packet_root, raw_root, decisions_path = (
                self._prepared_blind_fixture(Path(directory))
            )
            frozen = freeze_native_dispositions(packet_root, decisions_path)
            self.assertEqual(frozen["status"], "frozen-before-reveal")
            result = reveal_native_dispositions(
                instrument,
                packet_root=packet_root,
                raw_normalization_root=raw_root,
            )

            self.assertEqual(result["counts"]["valid_pairs"], 6)
            self.assertEqual(
                result["counts"]["fable_constraint_advantage_pairs"], 6
            )
            self.assertEqual(result["counts"]["fable_blinded_preference_pairs"], 6)
            self.assertEqual(result["conclusion"], "descriptive-thresholds-met")

    def test_identity_leak_is_refused_before_disposition_freeze(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            _, packet_root, _, decisions_path = self._prepared_blind_fixture(
                Path(directory)
            )
            decisions = json.loads(decisions_path.read_text(encoding="utf-8"))
            decisions["P01"]["rationale"] = "The Fable output is preferable."
            decisions_path.write_text(json.dumps(decisions), encoding="utf-8")

            with self.assertRaisesRegex(
                NativePreferenceResultContractError, "native_blind_identity_leak"
            ):
                freeze_native_dispositions(packet_root, decisions_path)


if __name__ == "__main__":
    unittest.main()
