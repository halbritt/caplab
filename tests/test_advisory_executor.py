import json
import os
import stat
import subprocess
import tempfile
import unittest

from caplab.advisory.executor import (BudgetRefusal, claims_from_runs,
                                      run_advisory)

FAKE_INSTRUMENT = """#!/usr/bin/env python3
import argparse, json, os
ap = argparse.ArgumentParser()
for flag in ("--backend", "--out", "--seed", "--pairs", "--workers",
             "--timeout", "--abort-after-empty"):
    ap.add_argument(flag)
args = ap.parse_args()
os.makedirs(args.out, exist_ok=True)
row = {"dispatch_id": "f" * 64, "backend_measured": args.backend,
       "usable": True, "defect_class": "dangling_reference",
       "defect_anchor": "#el:x", "caught": True, "false_alarm": False,
       "mutant_findings": 1, "control_json_valid": True,
       "mutant_json_valid": True}
with open(os.path.join(args.out, "results.jsonl"), "w") as f:
    f.write(json.dumps(row) + "\\n")
with open(os.path.join(args.out, "summary.json"), "w") as f:
    json.dump({"instrument": "matched-pair defect injection",
               "pairs_usable": 1}, f)
"""


class ExecutorTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = self.tmp.name
        subprocess.run(["git", "init", "-q", self.repo], check=True)
        script = os.path.join(self.repo, "fake_instrument.py")
        with open(script, "w") as f:
            f.write(FAKE_INSTRUMENT)
        os.chmod(script, os.stat(script).st_mode | stat.S_IXUSR)
        subprocess.run(["git", "-C", self.repo, "add", "-A"], check=True)
        subprocess.run(
            ["git", "-C", self.repo, "-c", "user.email=t@t", "-c",
             "user.name=t", "commit", "-qm", "fixture"], check=True)

    def tearDown(self):
        self.tmp.cleanup()

    def test_budget_refusal_precedes_execution(self):
        with self.assertRaises(BudgetRefusal):
            run_advisory(backend="b", pairs=22, out_dir=self.tmp.name,
                         instrument_repo=self.repo,
                         instrument_script="fake_instrument.py",
                         max_pairs=21)

    def test_run_receipt_and_claims(self):
        out_dir = os.path.join(self.tmp.name, "runs", "adv-b")
        receipt = run_advisory(backend="tuple-b", pairs=1, out_dir=out_dir,
                               instrument_repo=self.repo,
                               instrument_script="fake_instrument.py")
        self.assertEqual(receipt["exit_code"], 0)
        self.assertTrue(receipt["completed"])
        self.assertTrue(os.path.isfile(
            os.path.join(out_dir, "caplab-receipt.json")))

        claims = claims_from_runs([out_dir], backends_root=None)
        self.assertEqual(len(claims), 1)
        claim = claims[0]
        self.assertEqual(claim["custody"], "caplab-advisory")
        self.assertEqual(claim["subject"]["source_id"], "tuple-b")
        self.assertEqual(claim["metrics"]["n_pairs"]["value"], 1)
        self.assertEqual(claim["evidence"][0]["instrument_commit"],
                         receipt["instrument_commit"])

    def test_incomplete_run_yields_no_claims(self):
        out_dir = os.path.join(self.tmp.name, "runs", "dead")
        os.makedirs(out_dir)
        with open(os.path.join(out_dir, "results.jsonl"), "w") as f:
            f.write(json.dumps({"dispatch_id": "a" * 64, "usable": True,
                                "backend_measured": "b",
                                "control_json_valid": True,
                                "mutant_json_valid": True}) + "\n")
        self.assertEqual(claims_from_runs([out_dir], backends_root=None), [])


if __name__ == "__main__":
    unittest.main()
