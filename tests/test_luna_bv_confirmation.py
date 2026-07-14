import contextlib
import hashlib
import io
import json
import random
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT / "doctrine" / "evaluations" / "robustness" / "native"
sys.path.insert(0, str(NATIVE))

import run_luna_bv_confirmation as runner  # noqa: E402


class LunaBvConfirmationTests(unittest.TestCase):
    def setUp(self):
        self.experiment = runner.load_experiment()
        self.treatment = runner.load_treatment()

    def test_order_is_exact_seeded_complete_blocks(self):
        generator = random.Random(0x4C554E4142563230)
        expected = []
        for block, task in (
            ("m1", "checkout-retries-m1"),
            ("m2", "checkout-retries-m1"),
            ("m3", "checkout-retries-m1"),
            ("m4", "checkout-retries-m1"),
            ("c1", "checkout-retries-v2"),
            ("m5", "checkout-retries-m1"),
            ("m6", "checkout-retries-m1"),
            ("m7", "checkout-retries-m1"),
            ("m8", "checkout-retries-m1"),
            ("c2", "checkout-retries-v2"),
        ):
            arms = ["B", "V"]
            generator.shuffle(arms)
            expected.extend((block, task, arm) for arm in arms)

        rows = runner.load_order()

        self.assertEqual(
            [(row["block"], row["task"], row["arm"]) for row in rows],
            expected,
        )
        self.assertEqual(runner.generate_order(), runner.FROZEN_ORDER)
        self.assertEqual(
            runner.sha256_file(runner.ORDER_PATH),
            self.experiment["order_manifest_sha256"],
        )

    def test_v_component_and_fixtures_are_byte_identical_to_calibration(self):
        old = NATIVE / "checkout-retries-luna-literal-calibration"
        current = runner.EXPERIMENT_DIR
        for relative in (
            Path("components/V.md"),
            Path("fixtures/noop-backend.yaml"),
            Path("fixtures/noop.sh"),
        ):
            with self.subTest(path=relative):
                self.assertEqual((old / relative).read_bytes(), (current / relative).read_bytes())

    def test_rendered_arms_match_frozen_bytes_words_and_hashes(self):
        task = runner.TASKS / "checkout-retries-m1"
        base = (task / "instruction.md").read_bytes()
        for arm, expected in self.treatment["arms"].items():
            with self.subTest(arm=arm):
                prompt = runner.render_prompt(task, arm)
                self.assertEqual(len(prompt), expected["bytes"])
                self.assertEqual(len(prompt.decode().split()), expected["words"])
                self.assertEqual(hashlib.sha256(prompt).hexdigest(), expected["sha256"])
                if arm == "B":
                    self.assertEqual(prompt, base)
                else:
                    self.assertEqual(
                        prompt,
                        base.rstrip(b"\r\n")
                        + b"\n\n"
                        + (runner.EXPERIMENT_DIR / "components" / "V.md")
                        .read_bytes()
                        .rstrip(b"\r\n")
                        + b"\n",
                    )

    def test_exact_analysis_complete_separation_meets_criterion(self):
        analysis = runner.analyze_mutant_blocks([(True, False)] * 8)

        self.assertEqual(analysis["block_differences"], [1] * 8)
        self.assertEqual(analysis["risk_difference"], 1.0)
        self.assertEqual(analysis["t_observed"], 8)
        self.assertEqual(analysis["permutation_assignments"], 256)
        self.assertEqual(analysis["p_one_sided"], 1 / 256)
        self.assertEqual(analysis["p_two_sided"], 2 / 256)
        self.assertTrue(analysis["confirmatory_criterion_met"])

    def test_exact_analysis_seven_favorable_one_reversed(self):
        analysis = runner.analyze_mutant_blocks([(True, False)] * 7 + [(False, True)])

        self.assertEqual(analysis["risk_difference"], 0.75)
        self.assertEqual(analysis["t_observed"], 6)
        self.assertEqual(analysis["p_one_sided"], 9 / 256)
        self.assertTrue(analysis["confirmatory_criterion_met"])

    def test_exact_analysis_retains_all_assignments_when_ties_duplicate_statistics(self):
        analysis = runner.analyze_mutant_blocks(
            [(True, False), (True, False)] + [(False, False)] * 6
        )

        self.assertEqual(analysis["permutation_assignments"], 256)
        self.assertEqual(analysis["p_one_sided"], 0.25)
        self.assertEqual(analysis["p_two_sided"], 0.5)
        self.assertFalse(analysis["confirmatory_criterion_met"])

    def test_exact_analysis_is_undefined_if_any_mutant_outcome_is_undefined(self):
        analysis = runner.analyze_mutant_blocks([(True, False)] * 7 + [(None, False)])

        self.assertFalse(analysis["all_mutant_outcomes_defined"])
        self.assertIsNone(analysis["risk_difference"])
        self.assertIsNone(analysis["t_observed"])
        self.assertIsNone(analysis["p_one_sided"])
        self.assertIsNone(analysis["p_two_sided"])
        self.assertEqual(analysis["permutation_assignments"], 0)
        self.assertFalse(analysis["confirmatory_criterion_met"])

    def test_current_tasks_corpus_capture_cli_declaration_and_treatments_match_pins(self):
        runner.verify_frozen_inputs(
            self.experiment,
            self.treatment,
            runner.DEFAULT_DECLARATION,
            runner.DEFAULT_CORPUS,
            runner.DEFAULT_CAPTURE,
            Path(self.experiment["subject"]["cli_package_json"]),
        )

    def test_each_frozen_input_drift_is_refused(self):
        cases = {
            "declaration": lambda paths: paths["declaration"].write_bytes(
                paths["declaration"].read_bytes() + b"x"
            ),
            "capture": lambda paths: paths["capture"].write_bytes(
                paths["capture"].read_bytes() + b"x"
            ),
            "cli": lambda paths: paths["cli"].write_text(json.dumps({"version": "0.144.2"}) + "\n"),
            "order": lambda paths: paths["order"].write_bytes(paths["order"].read_bytes() + b"\n"),
            "treatment": lambda paths: paths["treatment"].write_bytes(
                paths["treatment"].read_bytes() + b"\n"
            ),
            "task": lambda paths: (
                paths["tasks"] / "checkout-retries-m1" / "tests" / "test.sh"
            ).write_text(
                (paths["tasks"] / "checkout-retries-m1" / "tests" / "test.sh").read_text() + "\n"
            ),
            "corpus": lambda paths: (paths["corpus"] / "projection-manifest.json").write_bytes(
                (paths["corpus"] / "projection-manifest.json").read_bytes() + b"\n"
            ),
            "component": lambda paths: (
                paths["experiment_dir"] / "components" / "V.md"
            ).write_bytes((paths["experiment_dir"] / "components" / "V.md").read_bytes() + b"x"),
            "fixture": lambda paths: (paths["experiment_dir"] / "fixtures" / "noop.sh").write_bytes(
                (paths["experiment_dir"] / "fixtures" / "noop.sh").read_bytes() + b"x"
            ),
            "calibration_component": lambda paths: (
                paths["calibration_dir"] / "components" / "V.md"
            ).write_bytes((paths["calibration_dir"] / "components" / "V.md").read_bytes() + b"x"),
        }

        for name, mutate in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                temporary = Path(directory)
                paths = {
                    "declaration": temporary / "backend.yaml",
                    "capture": temporary / "capture",
                    "cli": temporary / "package.json",
                    "order": temporary / "order.csv",
                    "treatment": temporary / "treatment.json",
                    "tasks": temporary / "tasks",
                    "corpus": temporary / "corpus",
                    "experiment_dir": temporary / "experiment",
                    "calibration_dir": temporary / "calibration",
                }
                paths["declaration"].write_bytes(runner.DEFAULT_DECLARATION.read_bytes())
                paths["capture"].write_bytes(runner.DEFAULT_CAPTURE.read_bytes())
                paths["cli"].write_bytes(
                    Path(self.experiment["subject"]["cli_package_json"]).read_bytes()
                )
                paths["order"].write_bytes(runner.ORDER_PATH.read_bytes())
                paths["treatment"].write_bytes(runner.TREATMENT_PATH.read_bytes())
                for task_name in self.experiment["tasks"]:
                    shutil.copytree(runner.TASKS / task_name, paths["tasks"] / task_name)
                shutil.copytree(runner.DEFAULT_CORPUS, paths["corpus"])
                shutil.copytree(runner.EXPERIMENT_DIR, paths["experiment_dir"])
                shutil.copytree(
                    NATIVE / "checkout-retries-luna-literal-calibration",
                    paths["calibration_dir"],
                )
                mutate(paths)

                with self.assertRaises(SystemExit):
                    runner.verify_frozen_inputs(
                        self.experiment,
                        self.treatment,
                        paths["declaration"],
                        paths["corpus"],
                        paths["capture"],
                        paths["cli"],
                        order_path=paths["order"],
                        treatment_path=paths["treatment"],
                        tasks_root=paths["tasks"],
                        experiment_dir=paths["experiment_dir"],
                        calibration_dir=paths["calibration_dir"],
                    )

    def test_dry_run_cannot_invoke_capture_runtime_or_model(self):
        output = io.StringIO()
        with (
            mock.patch.object(sys, "argv", ["runner", "--dry-run"]),
            mock.patch.object(
                runner,
                "run_native_driver",
                side_effect=AssertionError("dry run invoked subprocess.run"),
            ),
            contextlib.redirect_stdout(output),
        ):
            self.assertEqual(runner.main(), 0)
        self.assertIn("validated 20 rows", output.getvalue())
        self.assertIn("no capture, runtime, Codex, or model invoked", output.getvalue())

    def test_fixture_mode_refuses_any_existing_trial_before_launch(self):
        with tempfile.TemporaryDirectory() as directory:
            output_root = Path(directory)
            (output_root / "s20-c2-V-attempt1").mkdir()
            argv = ["runner", "--fixture-all", "--output-root", str(output_root)]
            with (
                mock.patch.object(sys, "argv", argv),
                mock.patch.object(
                    runner,
                    "run_native_driver",
                    side_effect=AssertionError("existing path reached subprocess.run"),
                ),
                self.assertRaisesRegex(SystemExit, "already exist"),
            ):
                runner.main()

    def test_live_layout_refuses_preservation_data_and_out_of_order_runs(self):
        rows = runner.load_order()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            live = root / "live"
            preserved = root / "preserved"
            preserved.mkdir()
            (preserved / "manifest.sha256").write_text("occupied\n")
            with self.assertRaisesRegex(SystemExit, "preservation root"):
                runner.validate_live_layout(rows, 1, 1, live, preserved)

            shutil.rmtree(preserved)
            live.mkdir()
            (live / "s02-m1-V-attempt1").mkdir()
            with self.assertRaisesRegex(SystemExit, "out-of-order"):
                runner.validate_live_layout(rows, 1, 1, live, preserved)


if __name__ == "__main__":
    unittest.main()
