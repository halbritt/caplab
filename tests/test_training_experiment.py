import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from caplab.review_dissent.training_experiment import (
    TrainingExperimentContractError,
    load_training_experiment,
)


ROOT = Path(__file__).resolve().parents[1]
TRAINING_ROOT = ROOT / "docs/product/training/caplab-review-dissent-local-qwen-r1"
MANIFEST = TRAINING_ROOT / "training-experiment.json"


class TrainingExperimentTests(unittest.TestCase):
    def test_committed_experiment_is_zero_authority_and_native_harness_bound(self) -> None:
        experiment = load_training_experiment(MANIFEST, ROOT)
        self.assertEqual(experiment["base_checkpoint"]["repository"], "Qwen/Qwen3.6-27B")
        self.assertEqual(experiment["method"]["name"], "qlora-sft")
        self.assertEqual(experiment["method"]["optimizer_steps_max"], 12)
        self.assertEqual(experiment["evaluation"]["heldout_cells"], 8)
        self.assertEqual(experiment["authorization"]["training_attempts"], 0)

    def test_loader_does_not_open_heldout_content(self) -> None:
        original_open = Path.open

        def guarded_open(path: Path, *args, **kwargs):
            if path.name == "heldout.json":
                raise AssertionError("preregistration loader opened heldout content")
            return original_open(path, *args, **kwargs)

        with patch.object(Path, "open", guarded_open):
            load_training_experiment(MANIFEST, ROOT)

    def test_drift_and_execution_authority_fail_closed(self) -> None:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            relative_manifest = root / "manifest.json"
            for binding in (
                manifest["training_data"],
                manifest["evaluation"],
            ):
                path_key = "path" if "path" in binding else "general_controls_path"
                source = ROOT / binding[path_key]
                target = root / binding[path_key]
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(source.read_bytes())

            manifest["authorization"]["training_attempts"] = 1
            relative_manifest.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(
                TrainingExperimentContractError, "execution_authority_not_zero"
            ):
                load_training_experiment(relative_manifest, root)

            manifest["authorization"]["training_attempts"] = 0
            manifest["training_data"]["file_sha256"] = "0" * 64
            relative_manifest.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(
                TrainingExperimentContractError, "training_data_sha256_mismatch"
            ):
                load_training_experiment(relative_manifest, root)


if __name__ == "__main__":
    unittest.main()
