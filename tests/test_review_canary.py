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
from test_review_gate_attribution import gate_for_review


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
            gate_for_review(self.event, self.events, run, verdict)
        if close:
            self.event("pass_run_closed", {"run_ref": run, "outcome": "submitted" if verdict else "error"})
        return run

    def read(self):
        ledger = self.root / "ledger.jsonl"
        ledger.write_text("".join(json.dumps(e) + "\n" for e in self.events))
        return ledger, criterion.read_reviews(str(ledger))

    def admit(self, identity="repo/passes/a/change-set", content_hash="new-hash"):
        return self.event("artifact_admitted", {"identity": identity, "kind": "change-set",
                                                "content_hash": content_hash})

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
        report.pop("downstream_ordering")
        for version in range(1, 7):
            with self.subTest(version=version):
                report["record"] = f"caplab-review-canary/{version}"
                path.write_text(json.dumps(report))
                before = path.read_bytes()
                reference, _, cutoff = review_canary.load_baseline(path)
                self.assertEqual(cutoff, report["snapshot"]["last_seq"])
                self.assertEqual(reference["record"], report["record"])
                self.assertEqual(path.read_bytes(), before)

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
        admitted = self.admit()
        self.event("head_movement", {"identity": "repo/passes/a/change-set", "to_version": admitted})
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
        revised = self.admit()
        self.event("head_movement", {"identity": "repo/passes/a/change-set", "to_version": revised})
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

    def test_version_mentions_do_not_establish_a_later_admission(self):
        run = self.review(verdict="fail")
        other = self.admit(identity="another/change-set")
        for version in (other, 999):
            self.event("head_movement", {"identity": "repo/passes/a/change-set", "to_version": version})
        self.review(version=999)
        with patch.object(criterion.M, "store_object") as store:
            _, (snapshot, _, runs, strata) = self.read()
            store.assert_not_called()
        row = next(r for r in review_canary.summarize(snapshot, runs, 0)["reviews"] if r["run"] == run)
        self.assertEqual(row["later_versions"], [])
        self.assertEqual(runs[run]["later"]["later_versions"], [])
        self.assertNotIn(run, [r["run"] for r in strata["excluded-refused-then-revised"]])

    def test_admissions_need_no_head_movement_or_later_review_and_keep_source_events(self):
        refused = self.review(verdict="fail")
        unknown = self.review(verdict=None)
        opened = self.review(verdict=None, close=False)
        admissions = [self.admit(content_hash="hash-1"), self.admit(content_hash="hash-1")]
        for seq in admissions:
            self.events[seq]["written_at"] = "2026-09-07T00:00:00Z"
        with patch.object(criterion.M, "store_object") as store:
            _, (snapshot, summary, runs, strata) = self.read()
            store.assert_not_called()
        report = review_canary.summarize(snapshot, runs, 0)
        rows = {r["run"]: r for r in report["reviews"]}
        expected = [{"seq": seq, "at": "2026-09-07T00:00:00Z",
                     "identity": "repo/passes/a/change-set", "content_hash": "hash-1"} for seq in admissions]
        for run in (refused, unknown):
            self.assertEqual(rows[run]["later_versions"], admissions)
            self.assertEqual(rows[run]["later_version_observations"], expected)
        self.assertEqual(rows[opened]["later_versions"], [])
        self.assertEqual(rows[opened]["later_version_observations"], [])
        self.assertEqual(report["reviewers"][0]["refusals_with_later_version"], 1)
        self.assertEqual([r["run"] for r in strata["excluded-refused-then-revised"]], [refused])
        self.assertEqual(summary["revision_evidence"], "artifact-admission-after-review-closure/1")
        self.assertIn("Refusals with later admission", review_canary.render(report))

    def test_admission_before_closure_is_not_a_post_refusal_revision(self):
        run = self.review(verdict="fail", close=False)
        admitted = self.admit()
        self.event("pass_run_closed", {"run_ref": run, "outcome": "submitted"})
        self.event("head_movement", {"identity": "repo/passes/a/change-set", "to_version": admitted})
        _, (snapshot, _, runs, strata) = self.read()
        row = review_canary.summarize(snapshot, runs, 0)["reviews"][0]
        self.assertEqual(row["later_versions"], [])
        self.assertEqual(runs[run]["later"]["later_versions"], [])
        self.assertNotIn(run, [r["run"] for r in strata["excluded-refused-then-revised"]])

    def test_later_admission_requires_exact_identity_and_a_known_reviewed_version(self):
        self.review(verdict="fail", identity="répo/change-set")
        self.review(verdict="fail", identity="unknown/change-set", version=None)
        self.admit(identity="re\u0301po/change-set")
        self.admit(identity="unknown/change-set")
        _, (snapshot, _, runs, _) = self.read()
        report = review_canary.summarize(snapshot, runs, 0)
        self.assertTrue(all(r["later_versions"] == [] for r in report["reviews"]))
        self.assertEqual(report["reviewers"][0]["refusals_with_later_version"], 0)

    def test_ledger_order_handles_ties_and_clock_reversal(self):
        for written_at in ("2026-09-07T00:00:00Z", "2026-09-07T00:00:04Z"):
            with self.subTest(written_at=written_at):
                self.events = self.events[:1]
                self.review()
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
        self.assertEqual([x["seq"] for x in observations], [run + 2, first, last])
        self.assertEqual(observations[0]["status"], "missing-reference")
        self.assertEqual(observations[-2]["verdict"], "reject")
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
                observation = row["review_body_observations"][-1]
                self.assertEqual(observation["seq"], seq)
                self.assertEqual(observation["status"], status)
                self.assertIsNotNone(observation["response_error"])

    def test_ambiguous_latest_body_cannot_supply_or_inherit_a_verdict(self):
        bodies = [
            b'{"verdict":"reject","verdict":"accept","findings":[]}',
            b'{"verdict":"accept","verdict":"reject","findings":[]}',
            b'{"verdict":"accept","verdict":"accept","findings":[]}',
            b'{"verdict":"reject","ver\\u0064ict":"accept","findings":[]}',
            b'{"verdict":"accept","findings":[{"text":"a","text":"b"}]}',
            b'{"verdict":"accept","findings":[],"extra":NaN}',
            b'{"verdict":"accept","findings":[],"extra":Infinity}',
            b'{"verdict":"accept","findings":[],"extra":-Infinity}',
            '{"verdict":"accept","findings":[]}'.encode("utf-16"),
            b'{"verdict":"accept","summary":"\xff","findings":[]}',
        ]
        for raw in bodies:
            for gate in (None, "pass"):
                with self.subTest(raw=raw, gate=gate):
                    self.events = self.events[:1]
                    run = self.review(verdict=gate)
                    for ref in ("earlier", "latest"):
                        self.event("artifact_admitted", {"kind": "review-ledger",
                            "produced_by_run": run, "identity": ref, "body": {"content_hash": ref}})
                    with patch.object(criterion.M, "store_object", side_effect=[
                            b'{"verdict":"reject","findings":[]}', raw]):
                        _, (snapshot, _, runs, _) = self.read()
                    row = review_canary.summarize(snapshot, runs, 0)["reviews"][0]
                    self.assertIsNone(row["verdict"])
                    self.assertEqual(row["review_body_hash"], "latest")
                    self.assertEqual(row["latest_body_status"], "invalid-json")
                    self.assertEqual(row["review_body_observations"][-2]["verdict"], "reject")
                    self.assertIsNone(row["review_body_observations"][-1]["verdict"])
                    self.assertEqual(row["verdict_source"], "gate-only" if gate else "missing")
                    self.assertEqual(row["decision"], "cleared" if gate else "unknown")

    def test_strict_body_reader_preserves_unicode_without_normalization(self):
        text = "café / cafe\u0301 / 改修 / 🙂"
        doc = {"verdict": "reject", "findings": [], "summary": text}
        event = {"seq": 7, "payload": {"identity": "review", "body": {"content_hash": "body"}}}
        with patch.object(criterion.M, "store_object", return_value=json.dumps(doc, ensure_ascii=False).encode("utf-8")):
            observation, parsed = criterion.review_body_observation(event)
        self.assertEqual(parsed, doc)
        self.assertEqual(observation["status"], "parsed-object")
        self.assertEqual(observation["verdict"], "reject")

    def test_ambiguous_ledger_json_fails_before_store_reads_or_report_output(self):
        valid = json.dumps(self.events[0])
        variants = [
            valid.replace('"seq": 0', '"seq": 9, "seq": 0'),
            valid.replace('"payload": {}', '"payload": {"key": 1, "key": 2}'),
            valid.replace('"payload": {}', '"payload": {"key": NaN}'),
        ]
        for number, raw in enumerate(variants):
            with self.subTest(raw=raw):
                ledger = self.root / "ambiguous-ledger.jsonl"
                ledger.write_text(raw + "\n", encoding="utf-8")
                with patch.object(criterion.M, "store_object") as store:
                    with self.assertRaises(ValueError):
                        criterion.read_reviews(str(ledger))
                    store.assert_not_called()
                out = self.root / f"bad-json-{number}"
                completed = subprocess.run([sys.executable, str(SCRIPTS / "review_canary.py"),
                    "--ledger", str(ledger), "--out", str(out)], capture_output=True, text=True)
                self.assertEqual(completed.returncode, 2, completed.stderr)
                self.assertFalse(out.exists())

    def test_ambiguous_baseline_cannot_select_a_follow_up_window(self):
        self.review()
        path, report = self.baseline()
        valid = json.dumps(report)
        variants = [
            valid.replace('"after_run": 0', '"after_run": 1, "after_run": 0').encode(),
            valid.replace('"last_seq":', '"last_seq": 0, "last_seq":').encode(),
            valid.replace('"after_run": 0', '"extra": NaN, "after_run": 0').encode(),
            valid.encode("utf-16"),
        ]
        for number, raw in enumerate(variants):
            with self.subTest(raw=raw):
                path.write_bytes(raw)
                with self.assertRaises(ValueError):
                    review_canary.load_baseline(path)
                out = self.root / f"bad-baseline-{number}"
                completed = subprocess.run([sys.executable, str(SCRIPTS / "review_canary.py"),
                    "--ledger", report["snapshot"]["path"], "--baseline-report", str(path),
                    "--out", str(out)], capture_output=True, text=True)
                self.assertEqual(completed.returncode, 2, completed.stderr)
                self.assertFalse(out.exists())

    def test_baseline_terminal_record_requires_unambiguous_json_even_with_matching_hash(self):
        path, report = self.baseline()
        source = Path(report["snapshot"]["path"])
        raw = source.read_bytes().replace(b'"seq": 0', b'"seq": 7, "seq": 0')
        source.write_bytes(raw)
        report["snapshot"]["sha256"] = hashlib.sha256(raw).hexdigest()
        path.write_text(json.dumps(report))
        with self.assertRaises(ValueError):
            review_canary.load_baseline(path)

    def test_body_reference_cannot_alias_an_integer_review_run(self):
        for ref in (True, 1.0, -1, "1", [], {}):
            with self.subTest(ref=ref):
                self.events = self.events[:1]
                self.assertEqual(self.review(verdict=None), 1)
                self.event("artifact_admitted", {"kind": "review-ledger", "produced_by_run": ref,
                    "identity": "aliased", "body": {"content_hash": "synthetic-body"}})
                with patch.object(criterion.M, "store_object", return_value=b'{"verdict":"accept","findings":[]}') as store:
                    with self.assertRaisesRegex(ValueError, "produced_by_run"):
                        self.read()
                    store.assert_not_called()

    def test_numeric_join_paths_are_checked_before_any_body_read(self):
        events = [
            ("pass_run_closed", {"run_ref": True, "outcome": "submitted"}),
            ("lane_binding", {"run_ref": True, "backend_id": "wrong-reviewer"}),
            ("scheduling_decision", {"run_ref": True, "backend_id": "wrong-reviewer"}),
            ("submission_received", {"run_ref": True}),
            ("admission_decision", {"run_ref": True, "decision": "refused"}),
            ("submission_refused", {"run_ref": True}),
            ("dispatch_lapse", {"run_ref": True}),
            ("gate_result", {"gate_class": "review", "outcome": "pass",
                             "evidence": [{"producing_run": {"run_ref": True}}]}),
            ("pass_run_opened", {"pass_id": "review", "request_ref": True}),
            ("pass_run_opened", {"pass_id": "review", "manifest": {"subject_pin": {"version_seq": 1.0}}}),
            ("cancellation_record", {"issuer": {"kind": "principal"}, "request_ref": True, "reason": "defect"}),
            ("head_movement", {"identity": "repo/passes/a/change-set", "to_version": 9.0}),
        ]
        for kind, payload in events:
            with self.subTest(kind=kind, payload=payload):
                self.events = self.events[:1]
                run = self.review(verdict=None)
                self.event("artifact_admitted", {"kind": "review-ledger", "produced_by_run": run,
                    "identity": "earlier-valid", "body": {"content_hash": "synthetic-body"}})
                self.event(kind, payload)
                with patch.object(criterion.M, "store_object", return_value=b'{"verdict":"accept","findings":[]}') as store:
                    with self.assertRaisesRegex(ValueError, "nonnegative integer"):
                        self.read()
                    store.assert_not_called()

    def test_sequence_requires_integer_type_including_genesis(self):
        for seq in (False, 0.0, "0", -1, None):
            with self.subTest(seq=seq):
                self.events[0]["seq"] = seq
                with self.assertRaisesRegex(ValueError, "sequence"):
                    self.read()

    def test_reference_containers_cannot_hide_invalid_join_fields(self):
        cases = [
            ("pass_run_opened", None),
            ("pass_run_opened", {"manifest": False}),
            ("pass_run_opened", {"manifest": {"subject_pin": []}}),
            ("gate_result", {"gate_class": "review", "evidence": {}}),
            ("gate_result", {"gate_class": "review", "evidence": [None]}),
            ("gate_result", {"gate_class": "review", "evidence": [{"producing_run": 0}]}),
        ]
        for kind, payload in cases:
            with self.subTest(kind=kind, payload=payload):
                self.events = self.events[:1]
                self.event(kind, payload)
                with self.assertRaisesRegex(ValueError, "event 1 payload"):
                    self.read()

    def test_null_missing_zero_and_large_integer_references_remain_distinct(self):
        run = self.review(verdict=None, version=2**53 + 1, close=False)
        for ref in (None, 0):
            self.event("lane_binding", {"run_ref": ref, "backend_id": "must-not-join"})
            self.event("gate_result", {"gate_class": "review", "outcome": "pass",
                "evidence": [{"producing_run": {"run_ref": ref}}, {}]})
        self.event("lane_binding", {"backend_id": "also-must-not-join"})
        self.event("head_movement", {"identity": "repo/passes/a/change-set", "to_version": None})
        _, (snapshot, _, runs, _) = self.read()
        row = review_canary.summarize(snapshot, runs, 0)["reviews"][0]
        self.assertEqual(row["run"], run)
        self.assertEqual(row["backend"], "reviewer-a")
        self.assertEqual(row["version_seq"], 2**53 + 1)
        self.assertIs(type(row["version_seq"]), int)
        self.assertEqual(row["decision"], "unknown")
        self.assertEqual(row["review_gate_observations"], [])
        self.assertIsNone(row["closed_seq"])

    def test_bad_reference_cli_fails_without_report_and_preserves_source(self):
        run = self.review(verdict=None)
        self.event("gate_result", {"gate_class": "review", "outcome": "pass",
            "evidence": [{"producing_run": {"run_ref": float(run)}}]})
        ledger = self.root / "bad-reference.jsonl"
        raw = "".join(json.dumps(e) + "\n" for e in self.events).encode()
        ledger.write_bytes(raw)
        out = self.root / "bad-reference-report"
        completed = subprocess.run([sys.executable, str(SCRIPTS / "review_canary.py"),
            "--ledger", str(ledger), "--out", str(out)], capture_output=True, text=True)
        self.assertEqual(completed.returncode, 2, completed.stderr)
        self.assertIn("producing_run.run_ref", completed.stderr)
        self.assertFalse(out.exists())
        self.assertEqual(ledger.read_bytes(), raw)

    def test_baseline_terminal_sequence_cannot_alias_its_integer_metadata(self):
        path, report = self.baseline()
        source = Path(report["snapshot"]["path"])
        for seq in (False, 0.0):
            with self.subTest(seq=seq):
                raw = (json.dumps({**self.events[0], "seq": seq}) + "\n").encode()
                source.write_bytes(raw)
                report["snapshot"]["sha256"] = hashlib.sha256(raw).hexdigest()
                path.write_text(json.dumps(report))
                with self.assertRaisesRegex(ValueError, "baseline"):
                    review_canary.load_baseline(path)

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
        self.assertEqual([x["seq"] for x in row["review_body_observations"]], [run + 2, *seqs])
        self.assertTrue(row["multiple_body_verdicts"])
        self.assertFalse(row["body_gate_disagreement"])
        self.assertFalse(row["body_gate_comparable"])
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
        self.assertEqual([g["seq"] for g in row["review_gate_observations"]], [run + 3, fail, invalid])
        self.assertTrue(row["multiple_gate_outcomes"])
        self.assertIn("Latest review gate: unsupported outcome", review_canary.render(report))

    def test_missing_verdict_lifecycle_preserves_recorded_causes_and_diagnostic_refs(self):
        self.review(verdict=None)
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
        self.assertEqual(report["record"], "caplab-review-canary/7")
        self.assertEqual(report["json_interpretation"], "utf8-unique-object-keys-no-non-json-constants/1")
        self.assertEqual(report["reference_validation"], "nonnegative-integer-sequence-paths/1")
        self.assertEqual(report["revision_evidence"], "artifact-admission-after-review-closure/1")
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
