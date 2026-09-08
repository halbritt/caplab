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

    def baseline(self, after_run=0):
        ledger, (snapshot, _, runs, _) = self.read()
        retained = self.root / "baseline-ledger.jsonl"
        ledger.rename(retained)
        snapshot["path"] = str(retained)
        report = review_canary.summarize(snapshot, runs, after_run)
        path = self.root / "baseline-report.json"
        path.write_text(json.dumps(report))
        return path, report

    def test_baseline_binds_follow_up_to_unchanged_ledger_prefix(self):
        self.review()
        baseline_path, baseline = self.baseline()
        new_run = self.review(verdict="fail", version=2)
        ledger, _ = self.read()
        out = self.root / "follow-up"
        command = [sys.executable, str(SCRIPTS / "review_canary.py"), "--ledger", str(ledger),
                   "--baseline-report", str(baseline_path), "--out", str(out)]
        completed = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        report = json.loads((out / "report.json").read_text())
        self.assertEqual(report["after_run"], baseline["snapshot"]["last_seq"])
        self.assertEqual([r["run"] for r in report["reviews"]], [new_run])
        self.assertEqual(report["baseline"]["report_sha256"], hashlib.sha256(baseline_path.read_bytes()).hexdigest())
        self.assertEqual(report["baseline"]["ledger_sha256"], baseline["snapshot"]["sha256"])
        self.assertIn("Verified baseline", (out / "report.md").read_text())

    def test_follow_up_baseline_keeps_original_population_cutoff(self):
        cutoff = self.review()
        self.review(version=2)
        path, report = self.baseline(after_run=cutoff)
        reference, expected_prefix, after_run = review_canary.load_baseline(path)
        self.assertEqual(after_run, cutoff)
        self.assertLess(after_run, report["snapshot"]["last_seq"])
        self.assertEqual(expected_prefix["sha256"], report["snapshot"]["sha256"])

    def test_legacy_baseline_preserves_window_without_claiming_same_calculations(self):
        self.review()
        path, report = self.baseline()
        report["record"] = "caplab-review-canary/1"
        report.pop("downstream_ordering")
        path.write_text(json.dumps(report))
        reference, _, cutoff = review_canary.load_baseline(path)
        self.assertEqual(cutoff, report["snapshot"]["last_seq"])
        self.assertEqual(reference["record"], "caplab-review-canary/1")

    def test_follow_up_from_genesis_keeps_zero_cutoff_on_the_next_report(self):
        path, _ = self.baseline()
        self.review()
        ledger, _ = self.read()
        out = self.root / "since-genesis"
        completed = subprocess.run([sys.executable, str(SCRIPTS / "review_canary.py"),
                                    "--ledger", str(ledger), "--baseline-report", str(path),
                                    "--out", str(out)], capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        _, _, cutoff = review_canary.load_baseline(out / "report.json")
        self.assertEqual(cutoff, 0)

    def test_changed_or_truncated_source_cannot_be_a_follow_up(self):
        self.review()
        path, _ = self.baseline()
        self.review(version=2)
        ledger, _ = self.read()
        _, prefix, _ = review_canary.load_baseline(path)
        self.events[0]["payload"] = {"core_graph": "different-graph"}
        ledger.write_text("".join(json.dumps(e) + "\n" for e in self.events))
        with self.assertRaisesRegex(ValueError, "baseline"):
            criterion.read_reviews(str(ledger), expected_prefix=prefix)
        ledger.write_text(json.dumps(self.events[0]) + "\n")
        with self.assertRaisesRegex(ValueError, "baseline"):
            criterion.read_reviews(str(ledger), expected_prefix=prefix)

    def test_baseline_export_loss_or_mutation_is_an_explicit_error(self):
        self.review()
        path, report = self.baseline()
        source = Path(report["snapshot"]["path"])
        source.write_bytes(source.read_bytes() + b"\n")
        with self.assertRaisesRegex(ValueError, "baseline"):
            review_canary.load_baseline(path)
        source.unlink()
        with self.assertRaises(FileNotFoundError):
            review_canary.load_baseline(path)

    def test_baseline_metadata_must_match_its_retained_export(self):
        self.review()
        path, report = self.baseline()
        for key in ("last_seq", "events"):
            wrong = json.loads(json.dumps(report))
            wrong["snapshot"][key] += 1
            path.write_text(json.dumps(wrong))
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "baseline"):
                review_canary.load_baseline(path)

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
        self.assertEqual(len(report["reviews"][2]["request_cancellations"]), 1)
        self.assertEqual(report["reviews"][3]["request_cancellations"], [])
        self.assertEqual(report["reviews"][3]["applications"], [])
        self.assertEqual(report["reviews"][3]["later_versions"], [])

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
        self.events[-1]["written_at"] = "2026-09-08T00:00:00Z"
        self.event("pass_run_closed", {"run_ref": run, "outcome": "submitted"})
        _, (snapshot, _, runs, _) = self.read()
        row = review_canary.summarize(snapshot, runs, 0)["reviewers"][0]
        self.assertEqual(row["clearances_with_application"], 0)

    def test_unknown_verdict_keeps_downstream_inspection_evidence(self):
        run = self.review(verdict=None)
        applied = self.event("application_record", {"change_set": {"content_hash": "hash-1"}})
        cancelled = self.event("cancellation_record", {"issuer": {"kind": "principal"},
                               "request_ref": 99, "reason": "incorrect lowering process"})
        revised = self.event("head_movement", {"identity": "repo/passes/a/change-set",
                                             "to_version": len(self.events)})
        _, (snapshot, _, runs, _) = self.read()
        report = review_canary.summarize(snapshot, runs, 0)
        row = report["reviews"][0]
        self.assertEqual(row["run"], run)
        self.assertEqual(row["decision"], "unknown")
        self.assertEqual([e["seq"] for e in row["applications"]], [applied])
        self.assertEqual([e["seq"] for e in row["request_cancellations"]], [cancelled])
        self.assertEqual(row["later_versions"], [revised])
        self.assertIn(f"Event {cancelled}", review_canary.render(report))
        self.assertIn("unknown 1", review_canary.render(report))
        self.assertEqual(report["reviewers"][0]["clearances_with_application"], 0)

    def test_ledger_order_handles_ties_and_clock_reversal(self):
        for written_at in ("2026-09-07T00:00:00Z", "2026-09-07T00:00:04Z"):
            with self.subTest(written_at=written_at):
                self.events = self.events[:1]
                run = self.review()
                closed = self.events[-1]["seq"]
                application = self.event("application_record", {"change_set": {"content_hash": "hash-1"}})
                conflict = self.event("integration_conflict", {"losing_change_set_pin": {"content_hash": "hash-1"},
                                                             "detail": "declares a different tree"})
                cancellation = self.event("cancellation_record", {"issuer": {"kind": "principal"},
                    "request_ref": 99, "reason": "incorrect change"})
                for event in self.events[closed + 1:]:
                    event["written_at"] = written_at
                _, (snapshot, _, runs, _) = self.read()
                row = review_canary.summarize(snapshot, runs, 0)["reviews"][0]
                self.assertEqual(row["closed_seq"], closed)
                for field, seq in (("applications", application), ("conflicts", conflict),
                                   ("request_cancellations", cancellation)):
                    self.assertEqual([e["seq"] for e in row[field]], [seq])
                    self.assertEqual(row[field][0]["at"], written_at)

    def test_missing_join_identity_cannot_link_unrelated_events(self):
        run = self.review()
        self.events[run]["payload"].pop("request_ref")
        self.events[run]["payload"]["manifest"]["subject_pin"].pop("content_hash")
        self.event("application_record", {"change_set": {}})
        self.event("integration_conflict", {"losing_change_set_pin": {}, "detail": "incorrect tree"})
        self.event("cancellation_record", {"issuer": {"kind": "principal"}, "reason": "incorrect request"})
        _, (snapshot, _, runs, _) = self.read()
        row = review_canary.summarize(snapshot, runs, 0)["reviews"][0]
        for field in ("applications", "conflicts", "request_cancellations"):
            self.assertEqual(row[field], [])

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

    def test_unavailable_latest_body_cannot_inherit_an_earlier_verdict(self):
        run = self.review()
        first = self.event("artifact_admitted", {"kind": "review-ledger", "produced_by_run": run,
                           "identity": "review-a", "body": {"content_hash": "body-a"}})
        last = self.event("artifact_admitted", {"kind": "review-ledger", "produced_by_run": run,
                          "identity": "review-b", "body": {"content_hash": "body-b"}})
        with patch.object(criterion.M, "store_object", side_effect=[b'{"verdict":"reject","findings":[]}', None]):
            _, (snapshot, _, runs, _) = self.read()
        row = review_canary.summarize(snapshot, runs, 0)["reviews"][0]
        self.assertIsNone(row["verdict"])
        self.assertEqual(row["verdict_source"], "gate-only")
        self.assertEqual(row["review_body_hash"], "body-b")
        observations = row["review_body_observations"]
        self.assertEqual([x["seq"] for x in observations], [first, last])
        self.assertEqual(observations[0]["verdict"], "reject")
        self.assertEqual(observations[-1]["status"], "unavailable-or-unverified")

    def test_malformed_review_bodies_remain_explicit_inspection_evidence(self):
        for raw, status in ((b'[]', 'invalid-object'), (b'"reject"', 'invalid-object'),
                            (b'{broken', 'invalid-json'), (b'{"verdict":[]}', 'parsed-object'),
                            (b'{"verdict":"reject","findings":3,"summary":{}}', 'parsed-object')):
            with self.subTest(raw=raw):
                self.events = self.events[:1]
                run = self.review()
                seq = self.event("artifact_admitted", {"kind": "review-ledger", "produced_by_run": run,
                    "identity": "review", "body": {"content_hash": "body"}})
                with patch.object(criterion.M, "store_object", return_value=raw):
                    _, (snapshot, _, runs, _) = self.read()
                row = review_canary.summarize(snapshot, runs, 0)["reviews"][0]
                observation = row["review_body_observations"][0]
                self.assertEqual(observation["seq"], seq)
                self.assertEqual(observation["status"], status)
                self.assertIsNotNone(observation["response_error"])

    def test_conflicting_verdict_sources_are_retained_and_flagged(self):
        run = self.review()
        seqs = [self.event("artifact_admitted", {"kind": "review-ledger", "produced_by_run": run,
                "identity": f"review-{i}", "body": {"content_hash": f"body-{i}"}}) for i in range(2)]
        with patch.object(criterion.M, "store_object", side_effect=[
                b'{"verdict":"accept","findings":[]}', b'{"verdict":"reject","findings":[]}']):
            _, (snapshot, _, runs, _) = self.read()
        report = review_canary.summarize(snapshot, runs, 0)
        row = report["reviews"][0]
        self.assertEqual(row["verdict"], "reject")
        self.assertEqual([x["seq"] for x in row["review_body_observations"]], seqs)
        self.assertTrue(row["multiple_body_verdicts"])
        self.assertTrue(row["body_gate_disagreement"])
        self.assertEqual(row["review_gate_observations"][0]["outcome"], "pass")
        self.assertIn(f"Review {run}", review_canary.render(report))

    def test_missing_and_invalid_body_references_do_not_invent_a_verdict(self):
        for body, status in ((None, "missing-reference"), ({}, "missing-reference"),
                             ([], "invalid-reference"), ({"content_hash": []}, "invalid-reference")):
            with self.subTest(body=body):
                self.events = self.events[:1]
                run = self.review(verdict=None)
                self.event("artifact_admitted", {"kind": "review-ledger", "produced_by_run": run,
                                                "identity": "review", "body": body})
                with patch.object(criterion.M, "store_object") as store:
                    _, (snapshot, _, runs, _) = self.read()
                store.assert_not_called()
                row = review_canary.summarize(snapshot, runs, 0)["reviews"][0]
                self.assertEqual(row["decision"], "unknown")
                self.assertEqual(row["latest_body_status"], status)

    def test_gate_disagreement_retains_each_event_once_and_invalid_latest_is_unknown(self):
        run = self.review()
        fail = self.event("gate_result", {"gate_class": "review", "outcome": "fail",
                    "evidence": [{"producing_run": {"run_ref": run}}] * 2})
        invalid = self.event("gate_result", {"gate_class": "review", "outcome": [],
                    "evidence": [{"producing_run": {"run_ref": run}}]})
        _, (snapshot, _, runs, _) = self.read()
        report = review_canary.summarize(snapshot, runs, 0)
        row = report["reviews"][0]
        self.assertEqual(row["decision"], "unknown")
        self.assertEqual([g["seq"] for g in row["review_gate_observations"]], [run + 2, fail, invalid])
        self.assertTrue(row["multiple_gate_outcomes"])
        self.assertIn("Latest review gate: unsupported outcome", review_canary.render(report))

    def test_missing_verdict_lifecycle_preserves_recorded_causes_and_diagnostic_refs(self):
        deferred = self.review(verdict=None)
        self.events[-1]["payload"].update(outcome="canceled", closure_source="scheduling_deferral",
                                         deferral_reason="capacity_saturated", closure_reason="no free lane")
        partial = self.review(verdict=None, close=False)
        diagnostic = {"content_hash": "diagnostic-object", "label": "runerr-0"}
        submission = self.event("submission_received", {"run_ref": partial, "status": "failed",
                           "semantic_exhaust": [diagnostic], "operation_key": "submission-a"})
        admission = self.event("admission_decision", {"run_ref": partial, "decision": "refused",
                        "refusal_code": "schema_invalid", "submitted_state": "absent",
                        "detail": "required output missing", "output": {"output_id": "review-ledger"},
                        "submission_operation_key": "submission-a"})
        closure = self.event("pass_run_closed", {"run_ref": partial, "outcome": "submitted_partial",
                                                "closure_source": "submission_admission_v2"})
        _, (snapshot, _, runs, _) = self.read()
        report = review_canary.summarize(snapshot, runs, 0)
        summary = report["unknown_verdict_lifecycle"]
        self.assertEqual(summary["runs"], 2)
        self.assertEqual(summary["closure_sources"], {"scheduling_deferral": 1, "submission_admission_v2": 1})
        self.assertEqual(summary["deferral_reasons"], {"capacity_saturated": 1})
        self.assertEqual(summary["admission_refusals"], [{"code": "schema_invalid", "submitted_state": "absent",
                                                      "events": 1, "runs": 1}])
        observations = report["reviews"][1]["lifecycle_observations"]
        self.assertEqual([e["seq"] for e in observations], [submission, admission, closure])
        self.assertEqual(observations[0]["detail"]["semantic_exhaust"], [diagnostic])
        self.assertEqual(observations[1]["detail"]["detail"], "required output missing")
        self.assertIn("capacity_saturated", review_canary.render(report))
        self.assertEqual([x["decision"] for x in report["reviews"]], ["unknown", "unknown"])

    def test_lifecycle_summary_counts_events_and_runs_separately_and_keeps_unknowns(self):
        run = self.review(verdict=None)
        self.review(verdict=None, close=False)
        known = self.review()
        for ref in (run, run, known):
            self.event("admission_decision", {"run_ref": ref, "decision": "refused", "refusal_code": "schema_invalid"})
        _, (snapshot, _, runs, _) = self.read()
        report = review_canary.summarize(snapshot, runs, 0)
        summary = report["unknown_verdict_lifecycle"]
        self.assertEqual(summary["closure_sources"], {"not-recorded": 1, "open": 1})
        self.assertEqual(summary["admission_refusals"], [{"code": "schema_invalid", "submitted_state": "not-recorded",
                                                      "events": 2, "runs": 1}])
        self.assertEqual(report["population"], 3)

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
