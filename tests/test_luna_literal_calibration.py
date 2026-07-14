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

import run_luna_literal_calibration as runner  # noqa: E402


class LunaLiteralCalibrationTests(unittest.TestCase):
    def setUp(self):
        self.experiment = runner.load_experiment()
        self.treatment = runner.load_treatment()

    def test_order_is_exact_seeded_complete_blocks(self):
        generator = random.Random(0x4C554E414C495431)
        expected = []
        for block, task in (
            ("mutant-1", "checkout-retries-m1"),
            ("mutant-2", "checkout-retries-m1"),
            ("clean-1", "checkout-retries-v2"),
        ):
            arms = ["B", "V", "D", "VD"]
            generator.shuffle(arms)
            expected.extend((block, task, arm) for arm in arms)
        rows = runner.load_order()
        self.assertEqual(
            [(row["block"], row["task"], row["arm"]) for row in rows],
            expected,
        )
        self.assertEqual(
            runner.sha256_file(runner.ORDER_PATH),
            self.experiment["order_manifest_sha256"],
        )

    def test_active_components_are_byte_identical_to_stopped_experiment(self):
        old = NATIVE / "checkout-retries-luna-components-2x2" / "components"
        current = runner.EXPERIMENT_DIR / "components"
        self.assertEqual((old / "V1.md").read_bytes(), (current / "V.md").read_bytes())
        self.assertEqual((old / "D1.md").read_bytes(), (current / "D.md").read_bytes())

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
                    self.assertNotIn(b"condition", prompt.lower())
                    self.assertNotIn(b"##", prompt[len(base.rstrip(b"\r\n")) :])
                    self.assertTrue(prompt.endswith(b"\n"))

    def test_current_tasks_corpus_capture_cli_and_declaration_match_pins(self):
        runner.verify_frozen_inputs(
            self.experiment,
            self.treatment,
            runner.DEFAULT_DECLARATION,
            runner.DEFAULT_CORPUS,
            runner.DEFAULT_CAPTURE,
            Path(self.experiment["subject"]["cli_package_json"]),
        )

    def test_each_frozen_input_drift_is_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            capture = temporary / "capture"
            capture.write_bytes(runner.DEFAULT_CAPTURE.read_bytes())
            cli = temporary / "package.json"
            cli.write_bytes(Path(self.experiment["subject"]["cli_package_json"]).read_bytes())
            order = temporary / "order.csv"
            order.write_bytes(runner.ORDER_PATH.read_bytes())
            tasks = temporary / "tasks"
            for task_name in self.experiment["tasks"]:
                shutil.copytree(runner.TASKS / task_name, tasks / task_name)
            corpus = temporary / "corpus"
            shutil.copytree(runner.DEFAULT_CORPUS, corpus)

            cases = (
                ("capture", lambda: capture.write_bytes(capture.read_bytes() + b"x"), {}),
                (
                    "cli",
                    lambda: cli.write_text(json.dumps({"version": "0.144.2"}) + "\n"),
                    {},
                ),
                ("order", lambda: order.write_bytes(order.read_bytes() + b"\n"), {}),
                (
                    "task",
                    lambda: (tasks / "checkout-retries-m1" / "tests" / "test.sh").write_text(
                        (tasks / "checkout-retries-m1" / "tests" / "test.sh").read_text()
                        + "\n"
                    ),
                    {"tasks_root": tasks},
                ),
                (
                    "corpus",
                    lambda: (corpus / "projection-manifest.json").write_bytes(
                        (corpus / "projection-manifest.json").read_bytes() + b"\n"
                    ),
                    {},
                ),
            )
            for name, mutate, overrides in cases:
                with self.subTest(name=name):
                    capture.write_bytes(runner.DEFAULT_CAPTURE.read_bytes())
                    cli.write_bytes(
                        Path(self.experiment["subject"]["cli_package_json"]).read_bytes()
                    )
                    order.write_bytes(runner.ORDER_PATH.read_bytes())
                    shutil.rmtree(tasks)
                    for task_name in self.experiment["tasks"]:
                        shutil.copytree(runner.TASKS / task_name, tasks / task_name)
                    shutil.rmtree(corpus)
                    shutil.copytree(runner.DEFAULT_CORPUS, corpus)
                    mutate()
                    with self.assertRaises(SystemExit):
                        runner.verify_frozen_inputs(
                            self.experiment,
                            self.treatment,
                            runner.DEFAULT_DECLARATION,
                            corpus,
                            capture,
                            cli,
                            order_path=order,
                            **overrides,
                        )

    def test_dry_run_cannot_invoke_capture_runtime_or_model(self):
        output = io.StringIO()
        with mock.patch.object(sys, "argv", ["runner", "--dry-run"]), mock.patch.object(
            runner.subprocess,
            "run",
            side_effect=AssertionError("dry run invoked subprocess.run"),
        ), contextlib.redirect_stdout(output):
            self.assertEqual(runner.main(), 0)
        self.assertIn("no capture, runtime, Codex, or model invoked", output.getvalue())

    def test_fixture_mode_refuses_existing_trial_before_launch(self):
        with tempfile.TemporaryDirectory() as directory:
            output_root = Path(directory)
            (output_root / "s01-mutant-1-D-attempt1").mkdir()
            argv = ["runner", "--fixture-all", "--output-root", str(output_root)]
            with mock.patch.object(sys, "argv", argv), mock.patch.object(
                runner.subprocess,
                "run",
                side_effect=AssertionError("existing path reached subprocess.run"),
            ), self.assertRaisesRegex(SystemExit, "already exist"):
                runner.main()


if __name__ == "__main__":
    unittest.main()
