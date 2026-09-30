import copy
import unittest

from caplab.retrieval.contracts import (ContractError, assignment_id, assignments, canonical_json, spec_digest,
                                        validate_attempt, validate_spec)


def base_spec():
    return {
        "schema_version": "caplab-retrieval-spec/1",
        "experiment_id": "fixture-1",
        "corpus": [{"id": "a", "body": "alpha"}, {"id": "b", "body": "beta", "kind": "lesson", "shareable": False, "repo": "/x"},
                   {"id": "old", "body": "superseded", "supersede_with": "a"}],
        "queries": [{"id": "q1", "text": "find alpha", "relevant_ids": ["a"], "forbidden_ids": ["old"]},
                    {"id": "q0", "text": "nothing", "relevant_ids": [], "stratum": "no_answer"}],
        "arms": [{"id": "cmd", "adapter": "command", "configuration": {"argv": ["python3", "fixture.py"]}},
                 {"id": "cairn", "adapter": "cairn", "configuration": {"binary": "/b/cairn", "checkout": "/c"}}],
        "cutoffs": [5, 1],
        "seeds": [1, 0],
        "timeout_seconds": 30,
    }


def ok_attempt(arm="cmd", query="q1", seed=0, ranked=("a",), **extra):
    return dict({"assignment_id": assignment_id(arm, query, seed), "arm": arm, "query_id": query, "seed": seed,
                 "status": "ok", "ranked_ids": list(ranked), "latency_ns": 10}, **extra)


class SpecValidation(unittest.TestCase):
    def assertCode(self, document, code, path=None):
        with self.assertRaises(ContractError) as caught:
            validate_spec(document)
        self.assertEqual(caught.exception.code, code, caught.exception)
        if path is not None:
            self.assertEqual(caught.exception.path, path)

    def test_normalizes_defaults_and_orders(self):
        spec = validate_spec(base_spec())
        self.assertEqual(spec["cutoffs"], [1, 5])
        self.assertEqual(spec["seeds"], [0, 1])
        self.assertEqual(spec["corpus"][0], {"id": "a", "body": "alpha", "kind": "note", "shareable": True})
        self.assertEqual(spec["queries"][0]["stratum"], "answerable")
        self.assertEqual(spec["queries"][1]["forbidden_ids"], [])
        self.assertEqual(spec["arms"][1]["configuration"]["semantic_mode"], "off")
        self.assertEqual(validate_spec(spec), spec)  # idempotent
        self.assertEqual(spec_digest(spec), spec_digest(validate_spec(base_spec())))
        self.assertTrue(canonical_json(spec).startswith(b'{"arms":'))

    def test_input_is_not_mutated(self):
        document = base_spec()
        before = copy.deepcopy(document)
        validate_spec(document)
        self.assertEqual(document, before)

    def test_rejects_schema_identity_and_shape_errors(self):
        cases = [
            (lambda d: d.update(schema_version="caplab-retrieval-spec/2"), "UNKNOWN_SCHEMA"),
            (lambda d: d.update(experiment_id="bad id"), "INVALID_ID"),
            (lambda d: d.update(extra=1), "UNKNOWN_FIELD"),
            (lambda d: d.pop("seeds"), "MISSING_FIELD"),
            (lambda d: d["corpus"].append({"id": "a", "body": "dup"}), "DUPLICATE_ID"),
            (lambda d: d["corpus"][0].update(id="a:b"), "INVALID_ID"),
            (lambda d: d["corpus"][0].update(body=""), "TYPE"),
            (lambda d: d["corpus"][0].update(shareable="yes"), "TYPE"),
            (lambda d: d["corpus"][2].update(supersede_with="missing"), "UNKNOWN_ID"),
            (lambda d: d["corpus"][2].update(supersede_with="old"), "UNKNOWN_ID"),
            (lambda d: d["queries"].append(dict(d["queries"][0])), "DUPLICATE_ID"),
            (lambda d: d["queries"][0].update(relevant_ids=["a", "a"]), "DUPLICATE_ID"),
            (lambda d: d["queries"][0].update(relevant_ids=["ghost"]), "UNKNOWN_ID"),
            (lambda d: d["queries"][0].update(forbidden_ids=["a"]), "INCONSISTENT_LABELS"),
            (lambda d: d["queries"][1].update(stratum="answerable"), "INCONSISTENT_LABELS"),
            (lambda d: d["queries"][1].pop("stratum"), "INCONSISTENT_LABELS"),
            (lambda d: d["arms"].append(dict(d["arms"][0])), "DUPLICATE_ID"),
            (lambda d: d["arms"][0].update(adapter="http"), "INVALID_VALUE"),
            (lambda d: d["arms"][0]["configuration"].update(argv=[]), "EMPTY"),
            (lambda d: d["arms"][0]["configuration"].update(extra=True), "UNKNOWN_FIELD"),
            (lambda d: d["arms"][1]["configuration"].pop("checkout"), "MISSING_FIELD"),
            (lambda d: d["arms"][1]["configuration"].update(semantic_mode="on"), "MISSING_FIELD"),
            (lambda d: d["arms"][1]["configuration"].update(semantic_mode="maybe"), "INVALID_VALUE"),
            (lambda d: d.update(cutoffs=[1, 1]), "DUPLICATE_ID"),
            (lambda d: d.update(cutoffs=[0]), "OUT_OF_RANGE"),
            (lambda d: d.update(cutoffs=[True]), "TYPE"),
            (lambda d: d.update(cutoffs=[2.0]), "TYPE"),
            (lambda d: d.update(cutoffs=[]), "EMPTY"),
            (lambda d: d.update(seeds=[-1]), "OUT_OF_RANGE"),
            (lambda d: d.update(seeds=[False]), "TYPE"),
            (lambda d: d.update(timeout_seconds=0), "OUT_OF_RANGE"),
            (lambda d: d.update(timeout_seconds=float("inf")), "TYPE"),
            (lambda d: d.update(corpus=[]), "EMPTY"),
            (lambda d: d["queries"][0].update(text="x" * (70 << 10)), "TOO_LARGE"),
        ]
        for mutate, code in cases:
            document = base_spec()
            mutate(document)
            with self.subTest(code=code):
                self.assertCode(document, code)
        self.assertCode([], "TYPE", "")

    def test_roster_is_every_arm_query_seed(self):
        spec = validate_spec(base_spec())
        roster = assignments(spec)
        self.assertEqual(len(roster), 2 * 2 * 2)
        self.assertEqual(len({r["assignment_id"] for r in roster}), 8)
        self.assertEqual(roster[0], {"assignment_id": "cmd:q1:0", "arm": "cmd", "query_id": "q1", "seed": 0})


class AttemptValidation(unittest.TestCase):
    def setUp(self):
        self.spec = validate_spec(base_spec())

    def assertCode(self, attempt, code):
        with self.assertRaises(ContractError) as caught:
            validate_attempt(attempt, self.spec)
        self.assertEqual(caught.exception.code, code, caught.exception)

    def test_normalized_ok_attempt(self):
        a = validate_attempt(ok_attempt(), self.spec)
        self.assertIsNone(a["delivered_ids"])  # not observed: never inferred from rank
        self.assertEqual(a["observation"], {})
        self.assertEqual(validate_attempt(ok_attempt(ranked=[]), self.spec)["ranked_ids"], [])  # empty result is legal

    def test_failures_carry_no_results_and_need_error_codes(self):
        for status in ("error", "timeout", "interrupted"):
            failed = ok_attempt(ranked=[], status=status, error={"code": status.upper()})
            self.assertEqual(validate_attempt(failed, self.spec)["status"], status)
            self.assertCode(ok_attempt(ranked=[], status=status), "MISSING_FIELD")
            self.assertCode(ok_attempt(ranked=["a"], status=status, error={"code": "X"}), "INCONSISTENT_STATUS")
            self.assertCode(ok_attempt(ranked=[], delivered_ids=["a"], status=status, error={"code": "X"}), "INCONSISTENT_STATUS")
        not_started = ok_attempt(ranked=[], status="not_started", latency_ns=None)
        self.assertIsNone(validate_attempt(not_started, self.spec)["latency_ns"])
        self.assertCode(ok_attempt(error={"code": "X"}), "INCONSISTENT_STATUS")

    def test_rejects_bad_identity_ids_and_values(self):
        cases = [
            (ok_attempt(arm="ghost"), "UNKNOWN_ID"),
            (ok_attempt(query="ghost"), "UNKNOWN_ID"),
            (dict(ok_attempt(), seed=7, assignment_id="cmd:q1:7"), "UNKNOWN_ID"),
            (dict(ok_attempt(), seed=True), "UNKNOWN_ID"),
            (dict(ok_attempt(), assignment_id="cmd:q1:1"), "INCONSISTENT_ASSIGNMENT"),
            (ok_attempt(ranked=["a", "a"]), "DUPLICATE_ID"),
            (ok_attempt(ranked=["ghost"]), "UNKNOWN_ID"),
            (ok_attempt(delivered_ids=["b", "b"]), "DUPLICATE_ID"),
            (dict(ok_attempt(), status="done"), "INVALID_VALUE"),
            (dict(ok_attempt(), latency_ns=-1), "OUT_OF_RANGE"),
            (dict(ok_attempt(), latency_ns=1.5), "TYPE"),
            (ok_attempt(observation={"x": float("nan")}), "NOT_FINITE"),
            (ok_attempt(observation=[]), "TYPE"),
            (dict(ok_attempt(), gold=["a"]), "UNKNOWN_FIELD"),
        ]
        for attempt, code in cases:
            with self.subTest(code=code, attempt=attempt):
                self.assertCode(attempt, code)


if __name__ == "__main__":
    unittest.main()
