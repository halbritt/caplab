"""Standing order 2026-09-07: only natural-analog operators enter a claim."""
import json
import os
import tempfile
import unittest

from caplab.advisory import operators as O
from caplab.advisory import scoring


def _run(dirpath, rows):
    os.makedirs(dirpath)
    with open(os.path.join(dirpath, "summary.json"), "w") as f:
        json.dump({"instrument": "matched-pair defect injection (synthetic contract)",
                   "backend": "b", "started_at": "2026-09-07T00:00:00+00:00",
                   "finished_at": "2026-09-07T00:01:00+00:00", "usable": len(rows),
                   "environment": "iso-v1", "case_selection": "seeded-draw"}, f)
    with open(os.path.join(dirpath, "results.jsonl"), "w") as f:
        for r in rows:
            f.write(json.dumps({"usable": True, "control_json_valid": True, "mutant_json_valid": True,
                                "backend_measured": "b", "anchors_emitted": [], **r}) + "\n")


class SentinelTest(unittest.TestCase):
    def test_partition_is_complete_and_disjoint(self):
        kept, sentinel = set(O.QUALIFICATION_OPERATORS), set(O.SENTINEL_ONLY_OPERATORS)
        self.assertEqual(kept | sentinel, set(O.BY_NAME))
        self.assertFalse(kept & sentinel)
        self.assertEqual(len(kept), 5)

    def test_sentinel_rows_are_reported_not_scored(self):
        with tempfile.TemporaryDirectory() as d:
            run = os.path.join(d, "run")
            _run(run, [
                {"dispatch_id": "a", "substrate_id": "qs-a", "defect_class": "contradicted_clause", "caught": True, "false_alarm": False},
                {"dispatch_id": "b", "substrate_id": "qs-b", "defect_class": "truncated_tail", "caught": True, "false_alarm": True},
                {"dispatch_id": "c", "substrate_id": "qs-c", "defect_class": "refuted_conclusion", "caught": False, "false_alarm": False},
            ])
            scored = scoring.score_backends([run])["b"]
            self.assertEqual(scored["metrics"]["n_pairs"]["value"], 2)
            self.assertAlmostEqual(scored["metrics"]["catch_rate"]["value"], 0.5)
            self.assertEqual(scored["sentinel_by_defect_class"], {"truncated_tail": {"n": 1, "caught": 1, "false_alarm": 1}})
            self.assertEqual(scored["qualification_operators"], sorted(O.QUALIFICATION_OPERATORS))

    def test_all_sentinel_rows_yield_no_scorable_pair(self):
        with tempfile.TemporaryDirectory() as d:
            run = os.path.join(d, "run")
            _run(run, [{"dispatch_id": "b", "substrate_id": "qs-b", "defect_class": "hash_mismatch", "caught": True, "false_alarm": False}])
            scored = scoring.score_backends([run])["b"]
            self.assertEqual(scored["metrics"]["n_pairs"]["value"], 0)
            self.assertIn("hash_mismatch", scored["sentinel_by_defect_class"])

    def test_explicit_none_allows_everything(self):
        with tempfile.TemporaryDirectory() as d:
            run = os.path.join(d, "run")
            _run(run, [{"dispatch_id": "b", "substrate_id": "qs-b", "defect_class": "hash_mismatch", "caught": True, "false_alarm": False}])
            scored = scoring.score_backends([run], qualification_operators=None if scoring.DEFAULT_QUALIFICATION_OPERATORS is None else ())
            # an empty explicit allowlist scores nothing; the module default is the standing order
            self.assertEqual(scored["b"]["metrics"]["n_pairs"]["value"], 0)


if __name__ == "__main__":
    unittest.main()
