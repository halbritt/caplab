"""End-to-end retrieval command contracts, using actual subprocesses."""
from __future__ import annotations

import json
import hashlib
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "examples/retrieval/fixture.py"


class FixtureTests(unittest.TestCase):
    def test_good_retrieval_filters_access_and_supersession_without_gold_labels(self):
        request = {
            "schema_version": "caplab-retrieval-request/1", "query_id": "unknown-id",
            "query": "Cairn startup receipt", "seed": 0, "cutoff": 4,
            "corpus": [
                {"id": "live", "body": "Cairn startup receipt", "repo": "cairn"},
                {"id": "foreign", "body": "Cairn startup receipt", "repo": "surveyor"},
                {"id": "private", "body": "Cairn startup receipt", "shareable": False},
                {"id": "old", "body": "Cairn startup receipt", "supersede_with": "live"},
            ],
        }
        result = subprocess.run([sys.executable, str(FIXTURE), "good", "--project", "cairn"],
                                input=json.dumps(request), text=True, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        response = json.loads(result.stdout)
        self.assertEqual(response["ranked_ids"], ["live"])
        self.assertNotIn("delivered_ids", response)



class CliTests(unittest.TestCase):
    def cli(self, *args, outer=False):
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        env.setdefault("PYTHONPATH", str(ROOT / "src"))
        command = [sys.executable, "-m", "caplab" if outer else "caplab.retrieval"]
        if outer:
            command.append("retrieval")
        return subprocess.run([*command, *map(str, args)], text=True, capture_output=True,
                              cwd=ROOT, env=env, timeout=30)

    def test_validate_normalizes_frozen_example_through_both_entrypoints(self):
        for outer in (False, True):
            with self.subTest(outer=outer):
                result = self.cli("validate", "--spec", ROOT / "examples/retrieval/spec.json", outer=outer)
                self.assertEqual(result.returncode, 0, result.stderr)
                spec = json.loads(result.stdout)
                self.assertEqual(spec["experiment_id"], "retrieval-fixture-v1")
                self.assertTrue(all("kind" in note for note in spec["corpus"]))
                self.assertEqual(len(spec["queries"]), 7)



    def test_validation_errors_are_structured_and_never_create_a_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            spec = Path(tmp) / "invalid.json"
            for payload in ('{"schema_version":"wrong"}', '{"same":1,"same":2}', '{"n":NaN}'):
                with self.subTest(payload=payload):
                    spec.write_text(payload)
                    result = self.cli("validate", "--spec", spec)
                    self.assertEqual(result.returncode, 2)
                    self.assertEqual(result.stdout, "")
                    error = json.loads(result.stderr)
                    self.assertEqual(error["schema_version"], "caplab-retrieval-cli-error/1")
                    self.assertTrue(error["code"])
                    self.assertNotIn("Traceback", result.stderr)
            unicode_spec = json.loads((ROOT / "examples/retrieval/spec.json").read_text())
            unicode_spec["corpus"][0]["body"] = "SYNTHETIC café 🧭: preserve exact text"
            spec.write_text(json.dumps(unicode_spec, ensure_ascii=False), encoding="utf-8")
            preserved = self.cli("validate", "--spec", spec)
            self.assertEqual(preserved.returncode, 0, preserved.stderr)
            self.assertEqual(json.loads(preserved.stdout)["corpus"][0]["body"], unicode_spec["corpus"][0]["body"])
            missing = self.cli("run", "--spec", spec)
            self.assertEqual(missing.returncode, 2)
            self.assertEqual(json.loads(missing.stderr)["code"], "argument_error")



    def spec_for_fixture(self, root, modes=("good", "bad", "empty", "failing")):
        path = root / "spec.json"
        prepared = subprocess.run([sys.executable, str(ROOT / "examples/retrieval/prepare.py"),
                                   "--output", str(path)], text=True, capture_output=True, timeout=10)
        self.assertEqual(prepared.returncode, 0, prepared.stderr)
        spec = json.loads(path.read_text())
        spec["arms"] = [arm for arm in spec["arms"] if arm["id"] in modes]
        path.write_text(json.dumps(spec))
        return path

    def test_run_preserves_failed_assignments_and_report_checks_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = self.spec_for_fixture(root)
            output = root / "run"
            run = self.cli("run", "--spec", spec, "--output", output, outer=True)
            self.assertEqual(run.returncode, 1, run.stderr)
            report = json.loads(run.stdout)
            self.assertEqual(report["schema_version"], "caplab-retrieval-report/1")
            arms = report["summary"]["arms"]
            self.assertEqual(sum(a["coverage"]["planned"] for a in arms.values()), 28)
            self.assertEqual(arms["failing"]["coverage"]["failures"], 7)
            self.assertEqual(arms["failing"]["coverage"]["scorable"], 0)
            self.assertEqual(arms["empty"]["coverage"]["scorable"], 7)
            self.assertEqual(arms["good"]["cutoffs"]["1"]["answerable"]["conditional"]["recall"]["numerator"], 1)
            self.assertEqual(arms["empty"]["cutoffs"]["1"]["answerable"]["conditional"]["recall"]["numerator"], 0)
            self.assertEqual(arms["good"]["exposure"]["observed"]["numerator"], 0)
            for name in ("plan.json", "attempts.jsonl", "report.json", "manifest.json"):
                self.assertTrue((output / name).is_file(), name)
            observed = self.cli("report", "--run", output)
            self.assertEqual(observed.returncode, 1, observed.stderr)
            self.assertEqual(json.loads(observed.stdout), report)
            markdown = self.cli("report", "--run", output, "--format", "markdown")
            self.assertEqual(markdown.returncode, 1, markdown.stderr)
            self.assertIn("retrieval-fixture-v1", markdown.stdout)
            manifest_before = (output / "manifest.json").read_bytes()
            existing = self.cli("run", "--spec", spec, "--output", output)
            self.assertEqual(existing.returncode, 2)
            self.assertEqual(existing.stdout, "")
            self.assertEqual((output / "manifest.json").read_bytes(), manifest_before)
            plan = output / "plan.json"
            plan.chmod(0o600)
            plan.write_bytes(plan.read_bytes() + b" ")
            broken = self.cli("report", "--run", output)
            self.assertEqual(broken.returncode, 2)
            self.assertEqual(broken.stdout, "")
            self.assertTrue(json.loads(broken.stderr)["code"])



    def test_report_shows_unfinished_plan_as_missing_instead_of_success(self):
        from caplab.retrieval.artifacts import RunArtifacts

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec_path = self.spec_for_fixture(root, ("good",))
            RunArtifacts(root / "unfinished", json.loads(spec_path.read_text()))
            result = self.cli("report", "--run", root / "unfinished")
            self.assertEqual(result.returncode, 1, result.stderr)
            report = json.loads(result.stdout)
            self.assertFalse(report["run"]["finished"])
            self.assertEqual(report["run"]["missing"], 7)
            self.assertEqual(report["run"]["ok"], 0)



    def test_compare_requires_unambiguous_arms_and_unchanged_case_pins(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec_path = self.spec_for_fixture(root, ("good", "empty"))
            left = root / "left"
            run = self.cli("run", "--spec", spec_path, "--output", left)
            self.assertEqual(run.returncode, 0, run.stderr)
            ambiguous = self.cli("compare", "--left", left, "--right", left)
            self.assertEqual(ambiguous.returncode, 2)
            self.assertEqual(json.loads(ambiguous.stderr)["code"], "AMBIGUOUS_ARM")
            paired = self.cli("compare", "--left", left, "--right", left,
                              "--left-arm", "good", "--right-arm", "empty", outer=True)
            self.assertEqual(paired.returncode, 0, paired.stderr)
            comparison = json.loads(paired.stdout)
            self.assertEqual(comparison["schema_version"], "caplab-retrieval-comparison/1")
            recall = comparison["comparisons"][0]["cutoffs"]["1"]["answerable"]["metrics"]["recall"]
            self.assertEqual(recall["delta"]["numerator"], -1)
            spec = json.loads(spec_path.read_text())
            spec["queries"][0]["text"] += " Changed case."
            spec_path.write_text(json.dumps(spec))
            right = root / "right"
            changed = self.cli("run", "--spec", spec_path, "--output", right)
            self.assertEqual(changed.returncode, 0, changed.stderr)
            mismatch = self.cli("compare", "--left", left, "--right", right)
            self.assertEqual(mismatch.returncode, 2)
            self.assertEqual(mismatch.stdout, "")
            self.assertEqual(json.loads(mismatch.stderr)["code"], "INCOMPATIBLE_RUNS")



    def test_unavailable_command_returns_a_classified_error_before_sealing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec_path = self.spec_for_fixture(root, ("good",))
            spec = json.loads(spec_path.read_text())
            spec["arms"][0]["configuration"]["argv"] = [str(root / "absent-command")]
            spec_path.write_text(json.dumps(spec))
            output = root / "run"
            result = self.cli("run", "--spec", spec_path, "--output", output)
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertEqual(json.loads(result.stderr)["code"], "command_unavailable")
            self.assertEqual(result.stdout, "")
            self.assertFalse(output.exists())



    @unittest.skipUnless((Path(os.environ.get("CAIRN_CHECKOUT", Path.home() / "git/cairn"))
                          / "scripts/trial_task_evidence.py").is_file(),
                         "set CAIRN_CHECKOUT to test the real selected Cairn evidence parser")
    def test_import_task_preserves_original_grades_and_report_verifies_evidence(self):
        checkout = Path(os.environ.get("CAIRN_CHECKOUT", Path.home() / "git/cairn"))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            corpus = root / "corpus.json"
            corpus.write_text(json.dumps({"notes": [{"id": "toy", "body": "SYNTHETIC CLI fixture only"}]}))
            frozen = {"corpus_sha256": hashlib.sha256(corpus.read_bytes()).hexdigest(),
                      "cases_sha256": "0" * 64, "labels_sha256": "1" * 64, "label_version": 1}
            identity = {"frozen": frozen, "arms": ["baseline"], "model": "synthetic-no-model-invocation",
                        "harness": "codex", "reasoning_effort": None}
            plan = root / "plan.json"
            plan.write_text(json.dumps({**identity, "runs": [["completion", "baseline", 0, 0],
                                                            ["control", "baseline", 0, 0]]}))
            source = {**identity, "schema": "cairn.task-eval.agent/1", "records": [
                {"run_id": "completion.baseline.s0", "case": "completion", "arm": "baseline", "seed": 0,
                 "outcome": "correct", "stratum": "completion", "seconds": 1.25,
                 "correct": ["synthetic-grade"], "mistake": []}],
                "admission": {"planned": 2, "admitted": 1, "not_started": [
                    {"case": "control", "arm": "baseline", "seed": 0, "order": 0}]}}
            report_path = root / "agent.json"
            report_path.write_text(json.dumps(source))
            output = root / "task-evidence"
            imported = self.cli("import-task", "--report", report_path, "--plan", plan,
                                "--corpus", corpus, "--cairn-checkout", checkout, "--output", output, outer=True)
            self.assertEqual(imported.returncode, 0, imported.stderr)
            evidence = json.loads(imported.stdout)
            self.assertEqual(evidence["schema_version"], "caplab-retrieval-task-evidence/1")
            self.assertEqual(evidence["counts"]["not_started"], 1)
            self.assertIsNone(evidence["identity"]["binding"])
            first = evidence["assignments"][0]
            self.assertEqual(first["original"]["outcome"], "correct")
            self.assertEqual(first["original"]["seconds"], 1.25)
            self.assertFalse(first["delivery"]["observed"])
            self.assertEqual(evidence["sources"]["report"]["sha256"], hashlib.sha256(report_path.read_bytes()).hexdigest())
            verified = self.cli("report-task", "--run", output)
            self.assertEqual(verified.returncode, 0, verified.stderr)
            self.assertEqual(json.loads(verified.stdout), evidence)
            original_files = {f: f.read_bytes() for f in (report_path, plan, corpus)}
            (output / "evidence.json").chmod(0o600)
            (output / "evidence.json").write_text("{}")
            tampered = self.cli("report-task", "--run", output)
            self.assertEqual(tampered.returncode, 2)
            self.assertEqual(tampered.stdout, "")
            self.assertEqual(json.loads(tampered.stderr)["code"], "INTEGRITY")
            self.assertEqual(original_files, {f: f.read_bytes() for f in original_files})



    def test_malformed_command_response_is_failure_not_empty_abstention(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec_path = self.spec_for_fixture(root, ("good",))
            spec = json.loads(spec_path.read_text())
            spec["arms"][0]["configuration"]["argv"][2] = "malformed"
            spec_path.write_text(json.dumps(spec))
            result = self.cli("run", "--spec", spec_path, "--output", root / "run")
            self.assertEqual(result.returncode, 1, result.stderr)
            coverage = json.loads(result.stdout)["summary"]["arms"]["good"]["coverage"]
            self.assertEqual(coverage["planned"], 7)
            self.assertEqual(coverage["failures"], 7)
            self.assertEqual(coverage["scorable"], 0)

    def test_preparation_keeps_labels_and_refuses_existing_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / "new-spec.json"
            command = [sys.executable, str(ROOT / "examples/retrieval/prepare.py"), "--output", str(output)]
            prepared = subprocess.run([*command, "--cairn-binary", str(root / "binary"),
                                       "--cairn-checkout", str(root / "checkout")],
                                      text=True, capture_output=True, timeout=10)
            self.assertEqual(prepared.returncode, 0, prepared.stderr)
            spec = json.loads(output.read_text())
            original = json.loads((ROOT / "examples/retrieval/spec.json").read_text())
            self.assertEqual(spec["corpus"], original["corpus"])
            self.assertEqual(spec["queries"], original["queries"])
            self.assertEqual(spec["arms"][0]["adapter"], "cairn")
            self.assertEqual(spec["arms"][0]["configuration"]["semantic_mode"], "off")
            before = output.read_bytes()
            existing = subprocess.run(command, text=True, capture_output=True, timeout=10)
            self.assertEqual(existing.returncode, 2)
            self.assertEqual(output.read_bytes(), before)
            self.assertEqual(existing.stdout, "")



    def test_deep_json_is_a_structured_failure_not_an_incomplete_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            spec = Path(tmp) / "deep.json"
            spec.write_text("[" * 100_000 + "]" * 100_000)
            result = self.cli("validate", "--spec", spec)
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertEqual(result.stdout, "")
            error = json.loads(result.stderr)
            self.assertEqual(error["schema_version"], "caplab-retrieval-cli-error/1")
            self.assertEqual(error["code"], "internal_error")
            self.assertEqual(error["error_type"], "RecursionError")
            self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
