import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import review_canary
import review_criterion_ledger_pass as criterion


class ReviewCanaryTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.events = []
        self.event("graph_genesis", {})

    def event(self, kind, payload):
        seq = len(self.events)
        self.events.append({"seq": seq, "type": kind, "written_at": f"2026-09-07T00:00:{seq:02d}Z",
                            "payload": payload})
        return seq

    def review(self, backend="reviewer-a", verdict="pass", version=1, identity="repo/passes/a/change-set", close=True):
        run = self.event("pass_run_opened", {
            "pass_id": "review", "request_ref": 99, "contract_version": 2,
            "manifest": {"input_pins": [{"role": "materialized_base", "content_hash": "base"}],
                         "subject_pin": {"identity": identity, "version_seq": version, "content_hash": f"hash-{version}"}}})
        self.event("lane_binding", {"run_ref": run, "backend_id": backend})
        if verdict:
            self.event("gate_result", {"gate_class": "review", "outcome": verdict,
                                       "evidence": [{"producing_run": {"run_ref": run}}]})
        if close:
            self.event("pass_run_closed", {"run_ref": run, "outcome": "submitted" if verdict else "error"})
        return run

    def read(self):
        ledger = self.root / "ledger.jsonl"
        ledger.write_text("".join(json.dumps(e) + "\n" for e in self.events))
        return ledger, criterion.read_reviews(str(ledger))

    def test_retains_unknown_and_open_runs_and_reports_only_linked_observations(self):
        cleared = self.review()
        refused = self.review(backend="reviewer-b", verdict="fail")
        self.review(verdict=None)
        self.review(verdict=None, close=False)
        cancellation = self.event("cancellation_record", {
            "issuer": {"kind": "principal"}, "request_ref": 99, "reason": "incorrect lowering process"})
        self.event("application_record", {"change_set": {"content_hash": "hash-1"}})
        self.event("head_movement", {"identity": "repo/passes/a/change-set", "to_version": len(self.events)})
        # A downstream acceptance is not a review-specific re-ruling.
        self.event("gate_result", {"gate_class": "acceptance", "authority": {"kind": "principal"},
                                   "outcome": "fail", "applicability": {"materialization": {
                                       "identity": "repo/passes/a/change-set", "content_hash": "hash-1"}}})
        _, (snapshot, _, runs, _) = self.read()
        report = review_canary.summarize(snapshot, runs, 0)
        self.assertEqual(report["population"], 4)
        a, b = report["reviewers"]
        self.assertEqual(a["decisions"], {"cleared": 1, "unknown": 2})
        self.assertEqual(a["verdict_sources"], {"gate-only": 1, "missing": 2})
        self.assertEqual(a["closed_wall_n"], 2)
        self.assertEqual(a["run_outcomes"]["open"], 1)
        self.assertEqual(a["distinct_cancellation_records"], [cancellation])
        self.assertEqual(a["clearances_with_application"], 1)
        self.assertEqual(b["refusals_with_later_version"], 1)
        self.assertTrue(report["gold_outcomes"].startswith("unavailable:"))
        self.assertEqual(report["placement"], "frozen")
        self.assertEqual([r["run"] for r in report["reviews"][:2]], [cleared, refused])

    def test_cancellation_multiplicity_and_fixed_cutoff_do_not_become_defect_counts(self):
        old_run = self.review()
        self.review(version=2)
        self.event("cancellation_record", {"issuer": {"kind": "principal"}, "request_ref": 99,
                                           "reason": "defect in the request lowering"})
        _, (snapshot, _, runs, _) = self.read()
        all_rows = review_canary.summarize(snapshot, runs, 0)
        row = all_rows["reviewers"][0]
        self.assertEqual(row["clearances_with_request_cancellation"], 2)
        self.assertEqual(len(row["distinct_cancellation_records"]), 1)
        later = review_canary.summarize(snapshot, runs, old_run)
        self.assertEqual(later["population"], 1)
        self.assertEqual(later["reviewers"][0]["clearances_with_request_cancellation"], 1)
        empty = review_canary.summarize(snapshot, runs, snapshot["last_seq"])
        self.assertEqual(empty["population"], 0)
        self.assertIn("does not establish", review_canary.render(empty))
        with self.assertRaisesRegex(ValueError, "last sequence"):
            review_canary.summarize(snapshot, runs, snapshot["last_seq"] + 1)

    def test_events_before_close_do_not_count_as_later_outcomes(self):
        run = self.review(close=False)
        self.event("application_record", {"change_set": {"content_hash": "hash-1"}})
        self.event("pass_run_closed", {"run_ref": run, "outcome": "submitted"})
        _, (snapshot, _, runs, _) = self.read()
        row = review_canary.summarize(snapshot, runs, 0)["reviewers"][0]
        self.assertEqual(row["clearances_with_application"], 0)

    def test_body_verdict_precedes_gate_and_prose_is_excluded(self):
        run = self.review()
        self.event("artifact_admitted", {"kind": "review-ledger", "produced_by_run": run,
                                         "identity": "review", "body": {"content_hash": "body-hash"}})
        self.review(identity="repo/passes/a/design")
        with patch.object(criterion.M, "store_object", return_value=b'{"verdict":"reject","findings":[]}'):
            _, (snapshot, _, runs, _) = self.read()
        report = review_canary.summarize(snapshot, runs, 0)
        self.assertEqual(report["population"], 1)
        self.assertEqual(report["reviews"][0]["decision"], "refused")
        self.assertEqual(report["reviews"][0]["verdict_source"], "body")
        with patch.object(criterion.M, "store_object", return_value=b'{"verdict":"unknown-schema","findings":[]}'):
            _, (snapshot, _, runs, _) = self.read()
        report = review_canary.summarize(snapshot, runs, 0)
        self.assertEqual(report["reviews"][0]["decision"], "cleared")
        self.assertEqual(report["reviews"][0]["verdict_source"], "gate-only")

    def test_cli_retains_source_fingerprint_and_refuses_overwrite(self):
        self.review(backend="<reviewer>|a")
        ledger, _ = self.read()
        out = self.root / "report"
        command = [sys.executable, str(SCRIPTS / "review_canary.py"), "--ledger", str(ledger), "--out", str(out)]
        completed = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        report = json.loads((out / "report.json").read_text())
        self.assertEqual(report["snapshot"]["sha256"], hashlib.sha256(ledger.read_bytes()).hexdigest())
        self.assertIn("&lt;reviewer&gt;&#124;a", (out / "report.md").read_text())
        repeated = subprocess.run(command, capture_output=True, text=True)
        self.assertNotEqual(repeated.returncode, 0)
        self.assertIn("already exists", repeated.stderr)
        self.assertEqual(json.loads((out / "report.json").read_text()), report)

    def test_bad_exports_fail_without_emitting_a_report(self):
        gap = {**self.events[0], "seq": 2}
        for raw in ("", "{broken", json.dumps(self.events[0]) + "\n" + json.dumps(self.events[0]),
                    json.dumps(gap), json.dumps(self.events[0]) + "\n" + json.dumps(gap)):
            with self.subTest(raw=raw):
                ledger = self.root / "invalid.jsonl"
                ledger.write_text(raw)
                with self.assertRaises(ValueError):
                    criterion.read_reviews(str(ledger))


if __name__ == "__main__":
    unittest.main()
