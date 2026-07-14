import hashlib
import random
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT / "doctrine" / "evaluations" / "robustness" / "native"
sys.path.insert(0, str(NATIVE))

from run_luna_components_2x2 import (  # noqa: E402
    EXPERIMENT_DIR,
    EXPERIMENT_PATH,
    ORDER_PATH,
    TASKS,
    build_metadata,
    load_experiment,
    load_order,
    render_prompt,
    sha256_file,
)


class LunaComponentsTests(unittest.TestCase):
    def setUp(self):
        self.experiment = load_experiment()
        self.rows = load_order()

    def test_order_is_exact_seeded_block_randomization(self):
        generator = random.Random(0x4C554E41325832)
        conditions = ["V0D0", "V1D0", "V0D1", "V1D1"]
        expected = []
        for block in ["m1", "m2", "c1", "m3", "m4", "c2", "m5", "m6"]:
            shuffled = conditions.copy()
            generator.shuffle(shuffled)
            expected.extend((block, condition) for condition in shuffled)
        self.assertEqual(
            [(row["block"], row["condition"]) for row in self.rows],
            expected,
        )
        self.assertEqual(sha256_file(ORDER_PATH), self.experiment["order_manifest_sha256"])

    def test_components_match_frozen_lengths_hashes_and_language_constraints(self):
        texts = {}
        for level, expected in self.experiment["components"].items():
            path = EXPERIMENT_DIR / "components" / f"{level}.md"
            data = path.read_bytes()
            texts[level] = data.decode().lower()
            self.assertEqual(hashlib.sha256(data).hexdigest(), expected["sha256"])
            self.assertEqual(len(data), expected["bytes"])
            self.assertEqual(len(data.decode().split()), expected["words"])

        self.assertLessEqual(
            max(self.experiment["components"][level]["bytes"] for level in ("V0", "V1"))
            / min(self.experiment["components"][level]["bytes"] for level in ("V0", "V1")),
            1.10,
        )
        self.assertLessEqual(
            max(self.experiment["components"][level]["bytes"] for level in ("D0", "D1"))
            / min(self.experiment["components"][level]["bytes"] for level in ("D0", "D1")),
            1.10,
        )

        for forbidden in ("replay", "ledger", "durable", "contradict", "does not ship", "decision artifact"):
            self.assertNotIn(forbidden, texts["V0"])
        for forbidden in ("does not ship", "decline", "stop", "decision.md", "decision artifact"):
            self.assertNotIn(forbidden, texts["V1"])
        for forbidden in ("replay", "ledger", "charge id", "curl", "command"):
            self.assertNotIn(forbidden, texts["D1"])
        for forbidden in ("does not ship", "decline", "refuse", "ledger", "decision artifact", "decision.md"):
            self.assertNotIn(forbidden, texts["D0"])
        for text in texts.values():
            for forbidden in ("mutant", "v0d0", "v1d0", "v0d1", "v1d1", "expected reward"):
                self.assertNotIn(forbidden, text)

    def test_every_combined_prompt_matches_frozen_hash_and_size(self):
        task = TASKS / self.experiment["tasks"]["m1"]["name"]
        for condition, expected in self.experiment["combined_prompts"].items():
            prompt = render_prompt(task, condition[:2], condition[2:])
            self.assertEqual(hashlib.sha256(prompt).hexdigest(), expected["sha256"])
            self.assertEqual(len(prompt), expected["bytes"])
            self.assertEqual(len(prompt.decode().split()), expected["words"])
            self.assertEqual(prompt.count(b"## Pre-edit evidence slot"), 1)
            self.assertEqual(prompt.count(b"## Decision slot"), 1)
            self.assertLess(prompt.index(b"## Pre-edit evidence slot"), prompt.index(b"## Decision slot"))

    def test_sealed_metadata_contains_every_frozen_identity(self):
        row = self.rows[0]
        metadata = build_metadata(self.experiment, row, 1, "a" * 40)
        for field in (
            "sequence", "block", "task", "condition", "V", "D",
            "V_component_sha256", "D_component_sha256", "combined_prompt_sha256",
            "order_manifest_sha256", "preregistration_commit", "declaration_sha256",
            "task_content_hash", "surface_hash", "capture_binary_sha256", "observer_version",
        ):
            self.assertIn(field, metadata)
        self.assertEqual(metadata["experiment_manifest_sha256"], sha256_file(EXPERIMENT_PATH))


if __name__ == "__main__":
    unittest.main()
