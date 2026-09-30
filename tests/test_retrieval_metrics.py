import json
import math
import unittest

from caplab.retrieval.contracts import ContractError, assignment_id, assignments, validate_attempt, validate_spec
from caplab.retrieval.metrics import score_attempt, summarize


def spec(seeds=(0,), arms=("good",)):
    return validate_spec({
        "schema_version": "caplab-retrieval-spec/1", "experiment_id": "metrics", "timeout_seconds": 10,
        "corpus": [{"id": n, "body": n} for n in ("r1", "r2", "r3", "x1", "x2", "x3", "old")],
        "queries": [
            {"id": "two", "text": "t", "relevant_ids": ["r1", "r2"], "forbidden_ids": ["old"]},
            {"id": "one", "text": "t", "relevant_ids": ["r3"]},
            {"id": "none", "text": "t", "relevant_ids": [], "stratum": "no_answer"},
            {"id": "trap", "text": "t", "relevant_ids": [], "forbidden_ids": ["old"], "stratum": "forbidden_control"},
        ],
        "arms": [{"id": a, "adapter": "command", "configuration": {"argv": ["x"]}} for a in arms],
        "cutoffs": [1, 3, 10], "seeds": list(seeds),
    })


def attempt(s, arm, query, seed=0, ranked=(), status="ok", delivered=None):
    a = {"assignment_id": assignment_id(arm, query, seed), "arm": arm, "query_id": query, "seed": seed,
         "status": status, "ranked_ids": list(ranked) if status == "ok" else [], "latency_ns": 100 * (seed + 1)}
    if status != "ok":
        a["error"] = {"code": status.upper()}
    if delivered is not None:
        a["delivered_ids"] = list(delivered)
    return validate_attempt(a, s)


def q(s, qid):
    return next(x for x in s["queries"] if x["id"] == qid)


def frac(r):
    return (r["numerator"], r["denominator"])


class ScoreAttempt(unittest.TestCase):
    def setUp(self):
        self.s = spec()

    def test_cutoff_arithmetic_and_short_lists(self):
        scored = score_attempt(q(self.s, "two"), attempt(self.s, "good", "two", ranked=["x1", "r2", "old"]), [1, 3, 10])
        c1, c3, c10 = (scored["cutoffs"][k] for k in ("1", "3", "10"))
        self.assertEqual(frac(c1["precision"]), (0, 1))
        self.assertEqual(frac(c3["precision"]), (1, 3))
        self.assertEqual(frac(c10["precision"]), (1, 10))  # k denominator even for a 3-item list
        self.assertEqual(frac(c3["recall"]), (1, 2))
        self.assertEqual(frac(c1["reciprocal_rank"]), (0, 1))  # first hit at rank 2 is outside k=1
        self.assertEqual(frac(c3["reciprocal_rank"]), (1, 2))
        self.assertAlmostEqual(c3["ndcg"], (1 / math.log2(3)) / (1 + 1 / math.log2(3)))
        self.assertEqual((c1["forbidden_hits"], c3["forbidden_hits"]), (0, 1))
        self.assertTrue(c3["forbidden_hit"])
        self.assertEqual(c10["returned"], 3)
        perfect = score_attempt(q(self.s, "two"), attempt(self.s, "good", "two", ranked=["r1", "r2"]), [3])
        self.assertEqual(perfect["cutoffs"]["3"]["ndcg"], 1.0)
        self.assertEqual(frac(perfect["cutoffs"]["3"]["recall"]), (2, 2))

    def test_ndcg_ideal_is_cut_at_k_when_gold_exceeds_k(self):
        # 'two' has 2 relevant notes; at k=1 a relevant first hit is a perfect ranking.
        scored = score_attempt(q(self.s, "two"), attempt(self.s, "good", "two", ranked=["r1", "x1"]), [1, 3])
        self.assertEqual(scored["cutoffs"]["1"]["ndcg"], 1.0)
        self.assertEqual(frac(scored["cutoffs"]["1"]["recall"]), (1, 2))
        self.assertAlmostEqual(scored["cutoffs"]["3"]["ndcg"], 1 / (1 + 1 / math.log2(3)))

    def test_empty_gold_controls_get_false_positive_not_precision(self):
        clean = score_attempt(q(self.s, "none"), attempt(self.s, "good", "none", ranked=[]), [1, 3])
        dirty = score_attempt(q(self.s, "none"), attempt(self.s, "good", "none", ranked=["x1"]), [1, 3])
        self.assertFalse(clean["answerable"])
        self.assertNotIn("precision", clean["cutoffs"]["1"])
        self.assertFalse(clean["cutoffs"]["3"]["false_positive"])
        self.assertTrue(dirty["cutoffs"]["1"]["false_positive"])

    def test_failure_is_not_an_abstention(self):
        for status in ("error", "timeout", "interrupted", "not_started"):
            scored = score_attempt(q(self.s, "none"), attempt(self.s, "good", "none", status=status), [1])
            self.assertFalse(scored["scorable"])
            self.assertEqual(scored["cutoffs"], {})

    def test_exposure_only_when_observed(self):
        unobserved = score_attempt(q(self.s, "two"), attempt(self.s, "good", "two", ranked=["r1"]), [1])
        self.assertIsNone(unobserved["exposure"])
        observed = score_attempt(q(self.s, "two"), attempt(self.s, "good", "two", ranked=["r1"], delivered=["r2", "old"]), [1])
        self.assertEqual(frac(observed["exposure"]["recall"]), (1, 2))
        self.assertEqual(observed["exposure"]["forbidden_delivered"], 1)

    def test_wrong_query_is_refused(self):
        with self.assertRaises(ContractError):
            score_attempt(q(self.s, "one"), attempt(self.s, "good", "two", ranked=["r1"]), [1])


class Summarize(unittest.TestCase):
    def run_arm(self, s, arm, ranking, statuses=None, seeds=(0,)):
        rows = []
        for query in s["queries"]:
            for seed in seeds:
                status = (statuses or {}).get((query["id"], seed), "ok")
                rows.append(attempt(s, arm, query["id"], seed, ranked=ranking(query), status=status))
        return rows

    def test_good_bad_and_empty_retrievers_are_discriminated(self):
        s = spec(arms=("good", "bad", "empty"))
        good = self.run_arm(s, "good", lambda q: q["relevant_ids"])
        bad = self.run_arm(s, "bad", lambda q: ["old", "x1", "x2"])
        empty = self.run_arm(s, "empty", lambda q: [])
        arms = summarize(s, good + bad + empty)["arms"]
        recall = {a: arms[a]["cutoffs"]["3"]["answerable"]["conditional"]["recall"]["value"] for a in arms}
        self.assertEqual(recall, {"good": 1.0, "bad": 0.0, "empty": 0.0})
        fp = {a: arms[a]["cutoffs"]["3"]["controls"]["false_positive_rate"]["value"] for a in arms}
        self.assertEqual(fp, {"good": 0.0, "bad": 1.0, "empty": 0.0})
        fhit = {a: arms[a]["cutoffs"]["3"]["forbidden"]["hit_rate"] for a in arms}
        self.assertEqual(frac(fhit["bad"]), (2, 2))
        self.assertEqual(frac(fhit["good"]), (0, 2))
        # The empty retriever is clean on controls but useless: controls cannot inflate quality.
        self.assertEqual(arms["empty"]["cutoffs"]["3"]["answerable"]["all_assignments"]["success_lower_bound"]["value"], 0.0)

    def test_failures_never_count_as_clean_or_successful(self):
        s = spec()
        statuses = {("none", 0): "timeout", ("trap", 0): "error", ("one", 0): "interrupted"}
        rows = self.run_arm(s, "good", lambda q: q["relevant_ids"], statuses)
        arm = summarize(s, rows)["arms"]["good"]
        cov = arm["coverage"]
        self.assertEqual((cov["planned"], cov["scorable"], cov["failures"], cov["missing"]), (4, 1, 3, 0))
        k = arm["cutoffs"]["3"]
        # Conditional metrics cover the one successful answerable run...
        self.assertEqual(frac(k["answerable"]["conditional"]["success"]), (1, 1))
        # ...but all-assignment accounting keeps the interrupted answerable query.
        bounds = k["answerable"]["all_assignments"]
        self.assertEqual(bounds["unscored"], 1)
        self.assertEqual(frac(bounds["success_lower_bound"]), (1, 2))
        self.assertEqual(frac(bounds["success_upper_bound"]), (2, 2))
        self.assertEqual(frac(bounds["recall_lower_bound_zero_imputed"]), (1, 2))
        self.assertEqual(frac(bounds["recall_upper_bound_one_imputed"]), (1, 1))
        # Failed controls are neither false positives nor clean abstentions.
        self.assertEqual(frac(k["controls"]["false_positive_rate"]), (0, 0))
        self.assertIsNone(k["controls"]["false_positive_rate"]["value"])
        self.assertEqual(frac(k["controls"]["clean_all_assignments"]), (0, 2))
        # 'two' succeeded without the forbidden note; the errored 'trap' is not clean.
        self.assertEqual(frac(k["forbidden"]["clean_all_assignments"]), (1, 2))
        self.assertEqual(frac(k["forbidden"]["hit_rate"]), (0, 1))

    def test_summarize_rejects_malformed_attempt_containers(self):
        s = spec()
        for bad in (None, 5, "attempts", {"a": 1}, [None], [5], [[]]):
            with self.subTest(bad=bad), self.assertRaises(ContractError):
                summarize(s, bad)

    def test_missing_attempts_are_counted_and_duplicates_fail_closed(self):
        s = spec()
        rows = self.run_arm(s, "good", lambda q: q["relevant_ids"])[:2]
        arm = summarize(s, rows)["arms"]["good"]
        self.assertEqual((arm["coverage"]["missing"], arm["coverage"]["scorable"]), (2, 2))
        self.assertEqual(frac(arm["cutoffs"]["1"]["controls"]["clean_all_assignments"]), (0, 2))
        with self.assertRaises(ContractError) as caught:
            summarize(s, rows + rows[:1])
        self.assertEqual(caught.exception.code, "DUPLICATE_ID")
        with self.assertRaises(ContractError) as caught:
            summarize(s, [dict(rows[0], ranked_ids=["ghost"])])
        self.assertEqual(caught.exception.path, "/attempts/0/ranked_ids/0")

    def test_seeds_are_repetitions_at_case_level(self):
        s = spec(seeds=(0, 1, 2))
        rows = []
        for query in s["queries"]:
            for seed in (0, 1, 2):
                # 'two' finds both relevant notes only on seed 0; 'one' always finds its note.
                ranked = query["relevant_ids"] if (query["id"] != "two" or seed == 0) else ["x1"]
                rows.append(attempt(s, "good", query["id"], seed, ranked=ranked))
        summary = summarize(s, rows)
        self.assertTrue(summary["seeds_are_repetitions"])
        k = summary["arms"]["good"]["cutoffs"]["3"]["answerable"]
        self.assertEqual(frac(k["conditional"]["recall"]), (2, 3))  # 4 of 6 attempt-level successes
        self.assertEqual(frac(k["case_level"]["recall"]), (2, 3))  # (1/3 + 1) / 2 queries
        self.assertEqual(k["case_level"]["recall"]["count"], 2)

    def test_latency_uses_scorable_attempts_and_summary_is_json(self):
        s = spec(seeds=(0, 1))
        rows = self.run_arm(s, "good", lambda q: q["relevant_ids"], {("one", 1): "timeout"}, seeds=(0, 1))
        summary = summarize(s, rows)
        latency = summary["arms"]["good"]["latency_ok"]
        self.assertEqual((latency["count"], latency["median_ns"], latency["max_ns"]), (7, 100, 200))
        json.dumps(summary, allow_nan=False)
        self.assertEqual(len(summary["arms"]["good"]["attempts"]), len(assignments(s)))


if __name__ == "__main__":
    unittest.main()
