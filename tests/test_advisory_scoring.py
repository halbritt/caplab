import json
import os
import tempfile
import unittest

from caplab.advisory.claims import Ledger, build_claim
from caplab.advisory.export import export_document
from caplab.advisory.scoring import completed, eligible_run_dirs, score_backends
from caplab.advisory.seed import seed_claims
from caplab.advisory.wilson import wilson


def write_run(root, name, rows, complete=True, mutant_reviews=None,
              aborted=None):
    run_dir = os.path.join(root, name)
    os.makedirs(run_dir, exist_ok=True)
    with open(os.path.join(run_dir, "results.jsonl"), "w") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")
    if complete:
        with open(os.path.join(run_dir, "summary.json"), "w") as f:
            json.dump({"instrument": "matched-pair defect injection",
                       "pairs_usable": sum(1 for r in rows if r.get("usable")),
                       "aborted": aborted}, f)
    for dispatch_id, review in (mutant_reviews or {}).items():
        out = os.path.join(run_dir, "arms", dispatch_id[:12], "mutant-ws",
                           "work", "outputs")
        os.makedirs(out, exist_ok=True)
        with open(os.path.join(out, "review-ledger"), "w") as f:
            json.dump(review, f)
    return run_dir


def row(dispatch, backend="tuple-a", caught=True, alarm=False,
        anchor="#el:decision-clauses", usable=True, valid=True):
    return {
        "dispatch_id": dispatch, "backend_measured": backend, "usable": usable,
        "defect_class": "dangling_reference", "defect_anchor": anchor,
        "caught": caught, "false_alarm": alarm, "mutant_findings": 1,
        "control_json_valid": valid, "mutant_json_valid": valid,
    }


class ScoringTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def test_incomplete_run_excluded_whole(self):
        write_run(self.root, "cc-tuple-a", [row("a" * 64)], complete=True)
        write_run(self.root, "cc-killed", [row("b" * 64)], complete=False)
        eligible, skipped = eligible_run_dirs(self.root)
        self.assertEqual([os.path.basename(d) for d in eligible], ["cc-tuple-a"])
        self.assertEqual([os.path.basename(d) for d in skipped], ["cc-killed"])

    def test_aborted_run_is_not_complete(self):
        # The instrument writes summary.json and THEN raises its abort, so a
        # vendor session limit leaves a complete-looking directory holding a
        # truncated sample. It must be excluded whole.
        write_run(self.root, "cc-aborted", [row("a" * 64), row("b" * 64)],
                  complete=True,
                  aborted='9 consecutive empty lanes; last body: '
                          '"You\'ve hit your session limit"')
        self.assertFalse(completed(os.path.join(self.root, "cc-aborted")))
        eligible, skipped = eligible_run_dirs(self.root)
        self.assertEqual(eligible, [])
        self.assertEqual([os.path.basename(d) for d in skipped], ["cc-aborted"])

    def test_aborted_run_yields_no_claims(self):
        write_run(self.root, "cc-aborted", [row("a" * 64)], complete=True,
                  aborted="session limit")
        from caplab.advisory.seed import seed_claims
        self.assertEqual(seed_claims(self.root, None)["claims"], [])

    def test_metrics_and_merge_across_runs(self):
        write_run(self.root, "cc-tuple-a",
                  [row("a" * 64, caught=True), row("b" * 64, caught=False)])
        write_run(self.root, "confirm-tuple-a",
                  [row("c" * 64, caught=True, alarm=True),
                   row("a" * 64, caught=True)])  # repeated case
        eligible, _ = eligible_run_dirs(self.root)
        scored = score_backends(eligible)["tuple-a"]
        metrics = scored["metrics"]
        self.assertEqual(metrics["n_pairs"]["value"], 4)
        self.assertEqual(metrics["n_distinct_cases"]["value"], 3)
        self.assertEqual(scored["repeated_case_trials"], 1)
        self.assertAlmostEqual(metrics["catch_rate"]["value"], 0.75)
        self.assertAlmostEqual(metrics["false_alarm_rate"]["value"], 0.25)
        self.assertAlmostEqual(metrics["discrimination"]["value"], 0.5)
        self.assertNotIn("anchored_detection", metrics)  # no retained arms

    def test_unusable_and_unparseable_rows_do_not_count(self):
        write_run(self.root, "cc-tuple-a", [
            row("a" * 64),
            row("b" * 64, usable=False),
            row("c" * 64, valid=False),
        ])
        eligible, _ = eligible_run_dirs(self.root)
        scored = score_backends(eligible)["tuple-a"]
        self.assertEqual(scored["metrics"]["n_pairs"]["value"], 1)

    def test_anchor_rescore_reads_free_text_anchor(self):
        # The corrected path must find an anchor written inside free text,
        # codex-style, with no element_anchor field.
        dispatch = "d" * 64
        review = {"verdict": "needs_revision", "findings": [
            {"text": "F1 | element anchor: #el:decision-clauses | broken ref"}]}
        write_run(self.root, "cc-tuple-a", [row(dispatch)],
                  mutant_reviews={dispatch: review})
        eligible, _ = eligible_run_dirs(self.root)
        anchored = score_backends(eligible)["tuple-a"]["metrics"]["anchored_detection"]
        self.assertEqual(anchored["value"], 1.0)
        self.assertEqual(anchored["denominator"], 1)

    def test_anchor_rescore_miss_counts_denominator(self):
        dispatch = "e" * 64
        review = {"verdict": "needs_revision", "findings": [
            {"element_anchor": "#el:some-other-element"}]}
        write_run(self.root, "cc-tuple-a", [row(dispatch)],
                  mutant_reviews={dispatch: review})
        eligible, _ = eligible_run_dirs(self.root)
        anchored = score_backends(eligible)["tuple-a"]["metrics"]["anchored_detection"]
        self.assertEqual(anchored["value"], 0.0)
        self.assertEqual(anchored["denominator"], 1)


class ClaimsTest(unittest.TestCase):
    def test_seed_claims_and_ledger_idempotent(self):
        with tempfile.TemporaryDirectory() as root:
            write_run(root, "cc-tuple-a", [row("a" * 64)])
            result = seed_claims(root, backends_root=None)
            self.assertEqual(len(result["claims"]), 1)
            claim = result["claims"][0]
            self.assertEqual(claim["custody"], "historical-seed")
            self.assertEqual(claim["subject"]["source_id"], "tuple-a")
            self.assertFalse(claim["subject"]["matched_current_declaration"])

            ledger_path = os.path.join(root, "claims.jsonl")
            ledger = Ledger(ledger_path)
            self.assertEqual(ledger.append(result["claims"])["added"], 1)
            again = ledger.append(seed_claims(root, backends_root=None)["claims"])
            self.assertEqual(again["added"], 0)
            self.assertEqual(again["skipped_duplicates"], 1)

    def test_custody_is_closed(self):
        with self.assertRaises(ValueError):
            build_claim(subject_source_id="x", subject_matched=False,
                        construct="c/1", metrics={}, custody="vendor-table",
                        as_of="2026-08-09T00:00:00+00:00", evidence=[])

    def test_export_document_shape(self):
        with tempfile.TemporaryDirectory() as root:
            write_run(root, "cc-tuple-a", [row("a" * 64)])
            ledger = Ledger(os.path.join(root, "claims.jsonl"))
            ledger.append(seed_claims(root, backends_root=None)["claims"])
            doc = export_document(ledger)
            self.assertEqual(doc["document"], "caplab-advisory-export/1")
            self.assertEqual(len(doc["claims"]), 1)
            self.assertNotIn("_content_hash", doc["claims"][0])


class WilsonTest(unittest.TestCase):
    def test_extremes_stay_bounded(self):
        low, high = wilson(0, 13)
        self.assertEqual(low, 0.0)
        self.assertGreater(high, 0.0)
        low, high = wilson(13, 13)
        self.assertLess(low, 1.0)
        self.assertAlmostEqual(high, 1.0, places=9)

    def test_known_value(self):
        low, high = wilson(12, 21)  # fable-5-high catch 57%
        self.assertAlmostEqual(low, 0.364, places=2)
        self.assertAlmostEqual(high, 0.755, places=2)


if __name__ == "__main__":
    unittest.main()


class SweepSeedVerificationTest(unittest.TestCase):
    """A recorded seed must be verified against the draws, never assumed."""

    def _fixture(self, root, drawn):
        analysis = os.path.join(root, "analysis.json")
        exchange = os.path.join(root, "exchange")
        ids = [f"{i:064x}" for i in range(40)]
        with open(analysis, "w") as f:
            json.dump({"reviews": [{"dispatch_id": i, "fate": "final"}
                                   for i in ids]}, f)
        for i in ids:
            d = os.path.join(exchange, "dispatch", i)
            os.makedirs(d, exist_ok=True)
            with open(os.path.join(d, "manifest.json"), "w") as f:
                json.dump({}, f)
        run_dir = os.path.join(root, "run")
        os.makedirs(run_dir, exist_ok=True)
        with open(os.path.join(run_dir, "results.jsonl"), "w") as f:
            for i in drawn:
                f.write(json.dumps({"dispatch_id": i}) + "\n")
        return run_dir, exchange, analysis, ids

    def test_correct_seed_verifies_and_wrong_seed_does_not(self):
        from caplab.advisory.seed import candidate_pool, verify_sweep_seed
        with tempfile.TemporaryDirectory() as root:
            run_dir, exchange, analysis, ids = self._fixture(root, [])
            drawn = candidate_pool(exchange, analysis, 20260807)[:6]
            with open(os.path.join(run_dir, "results.jsonl"), "w") as f:
                for i in drawn:
                    f.write(json.dumps({"dispatch_id": i}) + "\n")
            self.assertTrue(verify_sweep_seed(run_dir, 20260807, exchange,
                                              analysis))
            self.assertFalse(verify_sweep_seed(run_dir, 20260815, exchange,
                                               analysis))

    def test_empty_run_does_not_verify(self):
        from caplab.advisory.seed import verify_sweep_seed
        with tempfile.TemporaryDirectory() as root:
            run_dir, exchange, analysis, _ = self._fixture(root, [])
            self.assertFalse(verify_sweep_seed(run_dir, 20260807, exchange,
                                               analysis))


class ControlAdjudicationTest(unittest.TestCase):
    """A control established as defective cannot measure a false alarm."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def _score(self, adj=None):
        eligible, _ = eligible_run_dirs(self.root)
        return score_backends(eligible, adj)["tuple-a"]["metrics"]

    def test_unaudited_refusals_are_counted_but_flagged(self):
        write_run(self.root, "cc-tuple-a", [
            row("a" * 64, alarm=True), row("b" * 64), row("c" * 64),
            row("d" * 64)])
        fa = self._score()["false_alarm_rate"]
        self.assertAlmostEqual(fa["value"], 0.25)
        self.assertEqual(fa["denominator"], 4)
        self.assertEqual(fa["unaudited_refusals"], 1)
        self.assertEqual(fa["audit_status"], "contains-unaudited-refusals")

    def test_defective_control_leaves_the_denominator(self):
        from caplab.advisory.adjudication import (Adjudications,
                                                  build_adjudication)
        write_run(self.root, "cc-tuple-a", [
            row("a" * 64, alarm=True), row("b" * 64), row("c" * 64),
            row("d" * 64)])
        adj = Adjudications([build_adjudication(
            dispatch_id="a" * 64, disposition="defective",
            basis="audited: control carries an internal contradiction",
            adjudicated_by="principal:test", as_of="2026-08-16T00:00:00+00:00")])
        fa = self._score(adj)["false_alarm_rate"]
        # the refusal was correct: it is neither an error nor a measurement
        self.assertEqual(fa["value"], 0.0)
        self.assertEqual(fa["denominator"], 3)
        self.assertEqual(fa["excluded_defective_controls"], 1)
        self.assertEqual(fa["audit_status"], "established")

    def test_sound_adjudication_keeps_the_refusal_as_an_error(self):
        from caplab.advisory.adjudication import (Adjudications,
                                                  build_adjudication)
        write_run(self.root, "cc-tuple-a", [row("a" * 64, alarm=True),
                                            row("b" * 64)])
        adj = Adjudications([build_adjudication(
            dispatch_id="a" * 64, disposition="sound",
            basis="audited: no defect found", adjudicated_by="principal:test",
            as_of="2026-08-16T00:00:00+00:00")])
        fa = self._score(adj)["false_alarm_rate"]
        self.assertAlmostEqual(fa["value"], 0.5)
        self.assertEqual(fa["denominator"], 2)
        self.assertEqual(fa["unaudited_refusals"], 0)
        self.assertEqual(fa["audit_status"], "established")

    def test_defective_disposition_requires_an_authority(self):
        from caplab.advisory.adjudication import build_adjudication
        with self.assertRaises(ValueError):
            build_adjudication(dispatch_id="a" * 64, disposition="defective",
                               basis="a model said so", adjudicated_by="",
                               as_of="2026-08-16T00:00:00+00:00")


class AnchorExclusionTest(unittest.TestCase):
    """Replayed cases measure the instrument, never a claim's coverage."""

    def test_anchor_rows_leave_the_metrics_and_report_separately(self):
        with tempfile.TemporaryDirectory() as root:
            rows = [row("a" * 64, caught=True), row("b" * 64, caught=True)]
            anchor = row("c" * 64, caught=False, alarm=True)
            anchor["anchor"] = True
            anchor["control_unanimous"] = False
            anchor["mutant_unanimous"] = True
            write_run(root, "cc-tuple-a", rows + [anchor])
            eligible, _ = eligible_run_dirs(root)
            scored = score_backends(eligible)["tuple-a"]
            # the anchor case is not in the claim's numbers
            self.assertEqual(scored["metrics"]["n_pairs"]["value"], 2)
            self.assertEqual(scored["metrics"]["catch_rate"]["value"], 1.0)
            self.assertEqual(scored["metrics"]["false_alarm_rate"]["value"], 0.0)
            # but it is reported as instrument reliability
            rel = scored["instrument_reliability"]
            self.assertEqual(rel["anchor_cases"], 1)
            self.assertEqual(rel["control_unanimous_share"], 0.0)
            self.assertEqual(rel["mutant_unanimous_share"], 1.0)
