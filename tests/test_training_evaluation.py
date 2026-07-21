import json
import subprocess
import tempfile
import unittest
from hashlib import sha256
from pathlib import Path

from caplab.review_dissent.training_evaluation import (
    TrainingEvaluationError,
    heldout_order,
    run_evaluation,
    validate_adapter_seal,
)


ROOT = Path(__file__).resolve().parents[1]
STUDY = ROOT / "docs/product/studies/review-dissent-001"
CONTROLS = (
    ROOT
    / "docs/product/training/caplab-review-dissent-local-qwen-r1/general-coding-controls.json"
)


class TrainingEvaluationTests(unittest.TestCase):
    def _training_root(self, root: Path) -> Path:
        training = root / "training-output"
        adapter = training / "final-adapter" / "adapter_model.safetensors"
        adapter.parent.mkdir(parents=True)
        adapter.write_bytes(b"sealed-adapter")
        result = {
            "experiment_id": "caplab-review-dissent-qwen27b-qlora-r2",
            "global_steps": 12,
            "files": {
                "final-adapter/adapter_model.safetensors": sha256(
                    adapter.read_bytes()
                ).hexdigest()
            },
        }
        result["result_sha256"] = sha256(
            json.dumps(
                result, ensure_ascii=False, sort_keys=True, separators=(",", ":")
            ).encode("utf-8")
        ).hexdigest()
        (training / "result.json").write_text(json.dumps(result), encoding="utf-8")
        return training

    def test_adapter_seal_refuses_changed_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            training = self._training_root(Path(temporary))
            validate_adapter_seal(training)
            (training / "final-adapter/adapter_model.safetensors").write_bytes(b"changed")
            with self.assertRaisesRegex(TrainingEvaluationError, "final_adapter_not_sealed"):
                validate_adapter_seal(training)

    def test_heldout_order_keeps_pairs_and_is_deterministic(self) -> None:
        first = heldout_order()
        self.assertEqual(first, heldout_order())
        self.assertEqual(len(first), 16)
        for index in range(0, len(first), 2):
            pair = first[index : index + 2]
            self.assertEqual(pair[0][0], pair[1][0])
            self.assertEqual({pair[0][1], pair[1][1]}, {"base", "tuned"})

    def test_evaluation_uses_native_lane_for_all_frozen_slots(self) -> None:
        calls: list[list[str]] = []
        defect = {
            "review-10": ("AC-1", "src/lease.py"),
            "review-11": ("AC-1", "src/lease.py"),
            "review-14": ("AC-2", "src/policy.py"),
            "review-15": ("AC-2", "src/policy.py"),
        }
        control_answers = {
            "stable_unique": "['a', 'b', 'c']",
            "chunks([1, 2, 3, 4, 5]": "[[1, 2], [3, 4], [5]]",
            "move_false_after_loop": "move_false_after_loop",
            "all_pairs": "O(n^2)",
        }

        def fake_run(command, *, input, **_kwargs):
            calls.append(command)
            prompt = input.decode("utf-8")
            if "TASK FILES:" in prompt:
                public_id = next(
                    item for item in [f"review-{number:02d}" for number in range(9, 17)]
                    if item in prompt
                )
                if public_id in defect:
                    criterion, path = defect[public_id]
                    value = {
                        "verdict": "needs_revision",
                        "findings": [{
                            "severity": "critical",
                            "criterion": criterion,
                            "path": path,
                            "summary": "The implementation violates the named criterion.",
                        }],
                        "summary": "Revision is required.",
                    }
                else:
                    value = {"verdict": "clear", "findings": [], "summary": "Clear."}
            else:
                answer = next(value for marker, value in control_answers.items() if marker in prompt)
                value = {"answer": answer}
            return subprocess.CompletedProcess(command, 0, json.dumps(value).encode(), b"")

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            training = self._training_root(root)
            result = run_evaluation(
                endpoint="http://peecee:18081/v1",
                training_root=training,
                study_root=STUDY,
                controls_path=CONTROLS,
                output=root / "evaluation",
                run=fake_run,
            )

        self.assertEqual(len(calls), 24)
        self.assertEqual(result["subjects"]["base"]["schema_valid"], 8)
        self.assertEqual(result["subjects"]["tuned"]["schema_valid"], 8)
        self.assertEqual(result["general_control_summary"]["base"]["correct"], 4)
        self.assertFalse(result["success"])
        for command in calls:
            self.assertEqual(command[0], "striatum-openai-lane")
            self.assertNotIn("openrouter", " ".join(command).lower())


if __name__ == "__main__":
    unittest.main()
