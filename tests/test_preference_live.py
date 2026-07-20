"""Live-runner contract for the authorized CAPLAB preference campaign."""

from __future__ import annotations

import json
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from caplab.preference.live import (
    LivePreferenceContractError,
    assess_attempts,
    custody_tree_manifest,
    freeze_dispositions,
    harbor_command,
    load_live_manifest,
    load_custody_attempts,
    prepare_trial,
    reveal_dispositions,
)


ROOT = Path(__file__).parents[1]
INSTRUMENT = ROOT / "docs" / "product" / "studies" / "preference-001" / "instrument.json"
MANIFEST = ROOT / "docs" / "product" / "studies" / "preference-001" / "live-manifest.json"


class PreferenceLiveRunnerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = load_live_manifest(MANIFEST, INSTRUMENT)

    def test_manifest_binds_exact_authority_instrument_subjects_and_limits(self) -> None:
        self.assertEqual(self.manifest["authority"], "adr-0037")
        self.assertEqual(self.manifest["instrument"]["design_sha256"], "b61f109be67031614b0830d49922280be594d015aa405bdd741a795f08dabe45")
        self.assertEqual(
            {subject["provider_route"] for subject in self.manifest["subjects"].values()},
            {"openrouter/anthropic/claude-fable-5", "openrouter/openai/gpt-5.6-terra"},
        )
        self.assertEqual(self.manifest["limits"]["primary_trials"], 12)
        self.assertEqual(self.manifest["limits"]["maximum_trials"], 16)
        self.assertEqual(self.manifest["limits"]["maximum_completion_tokens"], 131072)
        self.assertEqual(self.manifest["limits"]["maximum_usd"], "50.00")

    def test_harbor_commands_are_equal_except_frozen_slot_and_provider_route(self) -> None:
        fable = harbor_command(
            self.manifest,
            slot_index=1,
            task_path=Path("/tmp/task"),
            jobs_path=Path("/tmp/jobs"),
        )
        gpt = harbor_command(
            self.manifest,
            slot_index=0,
            task_path=Path("/tmp/task"),
            jobs_path=Path("/tmp/jobs"),
        )
        self.assertIn("openrouter/anthropic/claude-fable-5", fable)
        self.assertIn("openrouter/openai/gpt-5.6-terra", gpt)
        self.assertIn("max_turns=8", fable)
        self.assertIn('llm_kwargs={"max_tokens":1024}', fable)
        self.assertIn("reasoning_effort=default", fable)
        self.assertIn("enable_summarize=false", fable)
        self.assertIn("--max-retries", fable)
        self.assertEqual(fable[fable.index("--max-retries") + 1], "0")
        self.assertNotIn("--upload", fable)
        normalized_fable = ["MODEL" if value == "openrouter/anthropic/claude-fable-5" else value for value in fable]
        normalized_gpt = ["MODEL" if value == "openrouter/openai/gpt-5.6-terra" else value for value in gpt]
        normalized_fable[normalized_fable.index("--instruction") + 1] = "INSTRUCTION"
        normalized_gpt[normalized_gpt.index("--instruction") + 1] = "INSTRUCTION"
        normalized_fable[normalized_fable.index("caplab-preference-001-s02")] = "JOB"
        normalized_gpt[normalized_gpt.index("caplab-preference-001-s01")] = "JOB"
        self.assertEqual(normalized_fable, normalized_gpt)

    def test_attempt_accounting_allows_only_frozen_order_and_bounded_replacement(self) -> None:
        attempts = [
            {"slot_index": 0, "attempt_kind": "primary", "status": "provider_failure", "completion_tokens": 0, "cost_usd": "0"},
            {"slot_index": 0, "attempt_kind": "replacement", "status": "completed", "completion_tokens": 700, "cost_usd": "0.25"},
            {"slot_index": 1, "attempt_kind": "primary", "status": "partial", "completion_tokens": 800, "cost_usd": "0.40"},
        ]
        state = assess_attempts(self.manifest, attempts)
        self.assertEqual(state["next_slot_index"], 2)
        self.assertEqual(state["replacement_count"], 1)
        self.assertEqual(state["total_completion_tokens"], 1500)
        self.assertEqual(state["total_cost_usd"], Decimal("0.65"))
        self.assertIsNone(state["stop_reason"])

        attempts[0]["status"] = "refused"
        with self.assertRaisesRegex(LivePreferenceContractError, "replacement_without_infrastructure_failure"):
            assess_attempts(self.manifest, attempts)

    def test_attempt_accounting_stops_on_trial_token_cost_and_sequence_breaches(self) -> None:
        cases = [
            ([{"slot_index": 0, "attempt_kind": "primary", "status": "completed", "completion_tokens": 8193, "cost_usd": "0"}], "trial_completion_token_limit"),
            ([{"slot_index": 0, "attempt_kind": "primary", "status": "completed", "completion_tokens": 1, "cost_usd": "50.00"}], "campaign_cost_limit"),
            ([{"slot_index": 1, "attempt_kind": "primary", "status": "completed", "completion_tokens": 1, "cost_usd": "0"}], "primary_order_mismatch"),
        ]
        for attempts, message in cases:
            with self.subTest(message=message), self.assertRaisesRegex(LivePreferenceContractError, message):
                assess_attempts(self.manifest, attempts)

    def test_custody_manifest_is_deterministic_and_refuses_symlinks(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "b.txt").write_text("b\n", encoding="utf-8")
            (root / "a.txt").write_text("a\n", encoding="utf-8")
            first = custody_tree_manifest(root)
            second = custody_tree_manifest(root)
            self.assertEqual(first, second)
            self.assertEqual([entry["path"] for entry in first["files"]], ["a.txt", "b.txt"])
            (root / "link").symlink_to(root / "a.txt")
            with self.assertRaisesRegex(LivePreferenceContractError, "custody_symlink"):
                custody_tree_manifest(root)

    def test_prepare_trial_renders_only_the_next_slot_and_writes_launch_before_call(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            manifest = dict(self.manifest)
            manifest["storage"] = dict(self.manifest["storage"])
            manifest["storage"]["raw_custody_root"] = temporary_directory
            attempt_root, command = prepare_trial(
                manifest,
                slot_index=0,
                attempt_kind="primary",
                prior_attempts=[],
            )
            launch = json.loads((attempt_root / "launch.json").read_text(encoding="utf-8"))
            self.assertEqual(launch["task_id"], "P04")
            self.assertEqual(launch["subject_id"], "gpt")
            self.assertEqual(launch["command"], command)
            self.assertTrue((attempt_root / "input" / "P04" / ".caplab-task.json").is_file())
            with self.assertRaisesRegex(LivePreferenceContractError, "unclassified_attempt"):
                load_custody_attempts(manifest)
            with self.assertRaisesRegex(LivePreferenceContractError, "attempt_custody_exists"):
                prepare_trial(
                    manifest,
                    slot_index=0,
                    attempt_kind="primary",
                    prior_attempts=[],
                )

    def test_dispositions_freeze_blind_packet_hashes_before_reveal(self) -> None:
        packets = {f"P0{index}": {"schema": "caplab.preference.blind-packet/v1", "pair_alias": f"Pair-{index}"} for index in range(1, 7)}
        decisions = {
            task_id: {
                "preferred_alias": "A",
                "criteria": {"completion": "A", "constraints": "A", "safety": "tie", "evidence": "A", "presentation": "tie"},
                "rationale": "Alias A satisfies more frozen constraints.",
                "uncertainty": "low",
            }
            for task_id in packets
        }
        frozen = freeze_dispositions(self.manifest, packets, decisions)
        encoded = json.dumps(frozen, sort_keys=True).casefold()
        for marker in ("fable", "gpt", "openrouter", "anthropic", "openai", "terminus"):
            self.assertNotIn(marker, encoded)
        revealed = reveal_dispositions(self.manifest, frozen)
        self.assertEqual(len(revealed["pairs"]), 6)
        self.assertEqual(revealed["pairs"]["P01"]["preferred_subject"], "gpt")

        incomplete = dict(decisions)
        incomplete.pop("P06")
        with self.assertRaisesRegex(LivePreferenceContractError, "incomplete_dispositions"):
            freeze_dispositions(self.manifest, packets, incomplete)


if __name__ == "__main__":
    unittest.main()
