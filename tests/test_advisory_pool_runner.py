import json
import os
import random
import tempfile
import unittest

from caplab.advisory import pool_runner
from caplab.advisory.pool_runner import (MAX_ARG_BYTES,
                                         SYNTHETIC_CONTRACT_INSTRUMENT,
                                         invoke, measure_case)
from caplab.advisory.scoring import is_matched_pair_run

DOC = """# Design {#el:design}

## Motivation {#el:motivation}

The pipeline must not admit an unverified claim, and reviewers never clear a
gate without evidence. This paragraph is long enough that structural
operators have real material to act upon in a test fixture.

## Decision (Clauses) {#el:decision-clauses}

- **C1 — Evidence first**: every claim cites registered evidence.
- **C2 — Fail closed**: a missing record refuses rather than defaults open.

The clauses above bind the implementation, and this trailing paragraph gives
the section enough bulk that duplication reads as a defect.

## Consequences {#el:consequences}

Quality becomes expensive to claim and cheap to withdraw, which is intended,
and this sentence runs on so a truncation point exists comfortably here.
"""


def case(operator="requirement_inversion", seed=11):
    return {"substrate_id": "qs-test", "operator": operator, "seed": seed,
            "sha256": "d" * 64, "source": {"kind": "repo-doc", "repo": "caplab",
                                           "path": "docs/x.md"}}


def echo_adapter(verdict_for_mutant="needs_revision",
                 verdict_for_control="accept"):
    """An adapter that refuses only when the body shows the inverted rule."""
    script = (
        "import sys, json;"
        "body = sys.stdin.read();"
        "bad = 'may freely' in body or 'may clear a gate' in body;"
        "print(json.dumps({'verdict': "
        f"{verdict_for_mutant!r} if bad else {verdict_for_control!r},"
        "'findings': [{'element_anchor': '#el:motivation'}] if bad else []}))"
    )
    return {"command": ["python3", "-c", script], "prompt_mode": "stdin"}


class InvokeTest(unittest.TestCase):
    def test_oversize_arg_falls_back_to_stdin_and_records_it(self):
        adapter = {"command": ["python3", "-c",
                               "import sys;print('{\"verdict\":\"accept\"}');"
                               "sys.stdin.read()"],
                   "prompt_mode": "arg"}
        result = invoke(adapter, "x" * (MAX_ARG_BYTES + 10), timeout=60)
        self.assertEqual(result["transport"], "stdin-oversize-fallback")
        self.assertEqual(result["doc"]["verdict"], "accept")

    def test_declared_arg_transport_is_used_when_it_fits(self):
        adapter = {"command": ["python3", "-c",
                               "import sys;print('{\"verdict\":\"accept\"}')"],
                   "prompt_mode": "arg"}
        result = invoke(adapter, "small", timeout=60)
        self.assertEqual(result["transport"], "arg")


class MeasureCaseTest(unittest.TestCase):
    def test_scores_a_matched_pair(self):
        row = measure_case(case(), DOC, echo_adapter(), timeout=60)
        self.assertTrue(row["usable"], row.get("error"))
        self.assertTrue(row["caught"])
        self.assertFalse(row["false_alarm"])
        self.assertTrue(row["defect_checkable"])
        self.assertEqual(row["calibration_profile"], "v1")

    def test_mechanical_gate_precedes_any_call(self):
        calls = []

        def spy(adapter, prompt, timeout):
            calls.append(prompt)
            return {"doc": None, "exit_code": 0, "seconds": 0,
                    "transport": "stdin", "prompt_bytes": 0, "raw_head": ""}

        original = pool_runner.invoke
        pool_runner.invoke = spy
        try:
            # An operator that cannot bite this body must not reach a model.
            row = measure_case(case("hollow_delivery"), DOC, echo_adapter(),
                               timeout=60)
        finally:
            pool_runner.invoke = original
        self.assertFalse(row["usable"])
        self.assertEqual(calls, [])

    def test_arm_order_is_case_derived_not_fixed(self):
        orders = set()

        def record_order(adapter, prompt, timeout):
            orders.add(("may freely" in prompt or "may clear" in prompt))
            return {"doc": {"verdict": "accept", "findings": []},
                    "exit_code": 0, "seconds": 0, "transport": "stdin",
                    "prompt_bytes": len(prompt), "raw_head": ""}

        original = pool_runner.invoke
        pool_runner.invoke = record_order
        try:
            measure_case(case(seed=11), DOC, echo_adapter(), timeout=60)
        finally:
            pool_runner.invoke = original
        # both arms were sent
        self.assertEqual(orders, {True, False})

    def test_unknown_operator_is_refused(self):
        row = measure_case(case("no_such_operator"), DOC, echo_adapter(),
                           timeout=60)
        self.assertFalse(row["usable"])
        self.assertIn("unknown operator", row["error"])


class SummaryShapeTest(unittest.TestCase):
    def test_summary_is_recognised_as_a_scoreable_run(self):
        with tempfile.TemporaryDirectory() as root:
            with open(os.path.join(root, "results.jsonl"), "w") as f:
                f.write(json.dumps({"dispatch_id": "x", "usable": True}) + "\n")
            with open(os.path.join(root, "summary.json"), "w") as f:
                json.dump({"instrument": SYNTHETIC_CONTRACT_INSTRUMENT,
                           "aborted": None}, f)
            self.assertTrue(is_matched_pair_run(root))

    def test_aborted_pool_run_is_not_scoreable(self):
        with tempfile.TemporaryDirectory() as root:
            with open(os.path.join(root, "results.jsonl"), "w") as f:
                f.write(json.dumps({"dispatch_id": "x", "usable": True}) + "\n")
            with open(os.path.join(root, "summary.json"), "w") as f:
                json.dump({"instrument": SYNTHETIC_CONTRACT_INSTRUMENT,
                           "aborted": "8 consecutive empty lanes"}, f)
            self.assertFalse(is_matched_pair_run(root))


if __name__ == "__main__":
    unittest.main()
