"""Contained native live boundary for CAPLAB-13."""

from __future__ import annotations

import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path
from unittest import mock

from caplab.review_dissent.native_live import (
    NativeReviewLiveContractError,
    assess_native_review_attempts,
    build_contained_review_invocation,
    load_native_review_live_manifest,
    prepare_native_review_trial,
)


ROOT = Path(__file__).parents[1]
STUDY = ROOT / "docs/product/studies/review-dissent-001"
MANIFEST = STUDY / "native-live-manifest.json"
INSTRUMENT = STUDY / "native-instrument.json"


class NativeReviewLiveTests(unittest.TestCase):
    def setUp(self) -> None:
        clock_patch = mock.patch(
            "caplab.review_dissent.native_live.datetime", wraps=datetime
        )
        clock = clock_patch.start()
        self.addCleanup(clock_patch.stop)
        clock.now.return_value = datetime(2026, 8, 3, 12, tzinfo=UTC)
        self.manifest = load_native_review_live_manifest(MANIFEST, INSTRUMENT)

    def test_manifest_binds_native_order_containment_and_limits(self) -> None:
        self.assertEqual(self.manifest["limits"]["primary_trials"], 16)
        self.assertEqual(self.manifest["limits"]["maximum_trials"], 20)
        self.assertEqual(self.manifest["authority"], "adr-0044")
        self.assertEqual(
            self.manifest["_instrument"]["execution_order"][0], "r03:gpt"
        )

    def test_both_subjects_use_the_same_external_task_namespace(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            for subject in ("fable", "gpt"):
                task = root / subject
                task.mkdir()
                invocation = build_contained_review_invocation(
                    self.manifest["_instrument"], subject, "r03", task
                )
                command = invocation["command"]
                self.assertEqual(command[0], "/usr/bin/bwrap")
                self.assertIn("--unshare-all", command)
                self.assertIn("--share-net", command)
                self.assertIn(str(task), command)
                self.assertIn("/work", command)

    def test_attempt_accounting_allows_only_ordered_infrastructure_replacement(self) -> None:
        attempts = [
            {
                "slot_index": 0,
                "attempt_kind": "primary",
                "status": "provider_failure",
                "duration_seconds": "1.0",
            },
            {
                "slot_index": 0,
                "attempt_kind": "replacement",
                "status": "completed",
                "duration_seconds": "2.0",
            },
        ]
        state = assess_native_review_attempts(self.manifest, attempts)
        self.assertEqual(state["next_slot_index"], 1)
        self.assertEqual(state["replacement_count"], 1)
        with self.assertRaises(NativeReviewLiveContractError):
            assess_native_review_attempts(
                self.manifest,
                [
                    {
                        "slot_index": 0,
                        "attempt_kind": "primary",
                        "status": "completed",
                        "duration_seconds": "1.0",
                    },
                    {
                        "slot_index": 0,
                        "attempt_kind": "replacement",
                        "status": "completed",
                        "duration_seconds": "1.0",
                    },
                ],
            )

    def test_unverified_manifest_cannot_create_attempt_custody(self) -> None:
        manifest = dict(self.manifest)
        manifest.pop("_verified_manifest_sha256")
        with self.assertRaises(NativeReviewLiveContractError):
            prepare_native_review_trial(
                manifest, slot_index=0, attempt_kind="primary", prior_attempts=[]
            )


if __name__ == "__main__":
    unittest.main()
