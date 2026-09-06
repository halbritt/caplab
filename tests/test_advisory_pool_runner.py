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
    def test_oversize_arg_prompt_is_refused_not_silently_rerouted(self):
        # An arg-mode CLI never reads stdin, so the old stdin fallback asked
        # nothing and recorded the silence as the subject's answer. The
        # transport must refuse instead, without invoking anything.
        adapter = {"command": ["python3", "-c",
                               "import sys;print('{\"verdict\":\"accept\"}');"
                               "sys.stdin.read()"],
                   "prompt_mode": "arg"}
        result = invoke(adapter, "x" * (MAX_ARG_BYTES + 10), timeout=60)
        self.assertIsNone(result["doc"])
        self.assertEqual(result["error"], "prompt exceeds transport capacity")
        self.assertEqual(result["transport"], "none")
        self.assertIsNone(result["exit_code"])

    def test_timeout_is_recorded_as_timeout_not_empty_answer(self):
        # "timed out" and "returned empty" could not be told apart in sweep
        # 20260817; the row must say which happened.
        adapter = {"command": ["python3", "-c", "import time;time.sleep(30)"],
                   "prompt_mode": "arg"}
        result = invoke(adapter, "hi", timeout=1)
        self.assertIsNone(result["doc"])
        self.assertTrue(result["timed_out"])
        self.assertIsNone(result["exit_code"])

    def test_declared_arg_transport_is_used_when_it_fits(self):
        adapter = {"command": ["python3", "-c",
                               "import sys;print('{\"verdict\":\"accept\"}')"],
                   "prompt_mode": "arg"}
        result = invoke(adapter, "small", timeout=60)
        self.assertEqual(result["transport"], "arg")


class SpillTransportTest(unittest.TestCase):
    """An arg-mode subject with an oversize body gets the body by file path,
    as striatum's own renderer spills argv-mode inputs in production."""

    READS_SPILLED_FILE = (
        "import sys, json;"
        "prompt = sys.argv[1];"
        "path = prompt.rstrip().split()[-1];"
        "body = open(path).read();"
        "bad = 'may freely' in body or 'may clear a gate' in body;"
        "print(json.dumps({'verdict': 'needs_revision' if bad else 'accept',"
        " 'findings': [{'element_anchor': '#el:motivation'}] if bad else []}))"
    )

    def test_oversize_body_is_spilled_to_a_file_the_subject_can_read(self):
        big = DOC + "\n## Appendix {#el:appendix}\n\n" + ("filler text " * 12000)
        adapter = {"command": ["python3", "-c", self.READS_SPILLED_FILE],
                   "prompt_mode": "arg"}
        with tempfile.TemporaryDirectory() as workspace:
            row = measure_case(case(), big, adapter, timeout=60,
                               workspace=workspace)
            self.assertTrue(row["usable"], row.get("error"))
        self.assertTrue(row["caught"])
        self.assertFalse(row["false_alarm"])
        self.assertEqual(row["control_transport"], "arg-spill")
        self.assertEqual(row["mutant_transport"], "arg-spill")


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

        def spy(adapter, prompt, timeout, **kwargs):
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

        def record_order(adapter, prompt, timeout, **kwargs):
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


class PairValidityTest(unittest.TestCase):
    """A pair with an unmeasured arm is not a measurement of the subject.

    Sweep 20260817 scored four such pairs: dead mutant arms as misses and a
    dead control arm as a clean clearance. Both readings invent an answer
    the subject never gave.
    """

    def _one_dead_arm(self, dead_arm):
        def fake_invoke(adapter, prompt, timeout, **kwargs):
            arm = "mutant" if ("may freely" in prompt or "may clear" in prompt) \
                else "control"
            if arm == dead_arm:
                return {"doc": None, "exit_code": None, "timed_out": True,
                        "seconds": 900.0, "transport": "arg",
                        "prompt_bytes": len(prompt), "raw_head": "",
                        "error": None}
            return {"doc": {"verdict": "accept", "findings": []},
                    "exit_code": 0, "timed_out": False, "seconds": 1.0,
                    "transport": "arg", "prompt_bytes": len(prompt),
                    "raw_head": "{}", "error": None}
        return fake_invoke

    def _run(self, dead_arm):
        original = pool_runner.invoke
        pool_runner.invoke = self._one_dead_arm(dead_arm)
        try:
            return measure_case(case(), DOC, echo_adapter(), timeout=60,
                                replicates=3, mutant_replicates=1)
        finally:
            pool_runner.invoke = original

    def test_dead_mutant_arm_discards_the_pair_and_says_why(self):
        row = self._run("mutant")
        self.assertFalse(row["usable"])
        self.assertIn("mutant arm", row["error"])
        self.assertTrue(row["mutant_timed_out"])
        self.assertIsNone(row["mutant_exit_code"])
        # The live arm's evidence is preserved for later audit.
        self.assertEqual(row["control_verdicts"], ["accept"] * 3)

    def test_dead_control_arm_discards_the_pair_and_says_why(self):
        row = self._run("control")
        self.assertFalse(row["usable"])
        self.assertIn("control arm", row["error"])
        self.assertTrue(row["control_timed_out"])
        self.assertNotIn("false_alarm", row)


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



CHANGE_SET = json.dumps({
    "schema_version": "1",
    "base": {"content_hash": "a" * 64},
    "files": {"docs/x.md": "# X\n\nBody text.\n",
              "src/x.py": "def x():\n    return 1\n",
              "src/y.py": "def y():\n    return 2\n",
              "src/z.py": "def z():\n    return 3\n"},
}, indent=2)


class ProfileRoutingTest(unittest.TestCase):
    """A contract written for prose asks a delivery questions it cannot answer."""

    def test_document_case_uses_the_document_contract(self):
        row = measure_case(case(), DOC, echo_adapter(), timeout=60)
        self.assertEqual(row["calibration_profile"], "v1")

    def test_change_set_case_uses_the_delivery_contract(self):
        seen = {}

        def spy(adapter, prompt, timeout, **kwargs):
            seen["prompt"] = prompt
            return {"doc": {"verdict": "accept", "findings": []},
                    "exit_code": 0, "seconds": 0, "transport": "stdin",
                    "prompt_bytes": len(prompt), "raw_head": ""}

        original = pool_runner.invoke
        pool_runner.invoke = spy
        try:
            row = measure_case(case("hollow_delivery", seed=5), CHANGE_SET,
                               echo_adapter(), timeout=60)
        finally:
            pool_runner.invoke = original
        self.assertTrue(row["usable"], row.get("error"))
        self.assertEqual(row["calibration_profile"], "v2-changeset")
        self.assertIn("CHANGE SET:", seen["prompt"])
        self.assertNotIn("carry the sections its stage requires", seen["prompt"])
        # The v2 contract must close the store-grep escape hatch the
        # 2026-08-21 OOM postmortem documented.
        self.assertIn("base tree is NOT available", seen["prompt"])
        self.assertIn("Do not search", seen["prompt"])

    def test_unusable_row_still_records_a_profile(self):
        row = measure_case(case("no_such_operator"), DOC, echo_adapter(),
                           timeout=60)
        self.assertIn("calibration_profile", row)
if __name__ == "__main__":
    unittest.main()


class ReplicationTest(unittest.TestCase):
    """The control arm reproduces at ~53%; a single trial cannot score it."""

    def _flaky(self, control_pattern, mutant_pattern="rrr"):
        state = {"control": list(control_pattern), "mutant": list(mutant_pattern)}

        def invoke(adapter, prompt, timeout, **kwargs):
            arm = "mutant" if ("may freely" in prompt or "may clear" in prompt) \
                else "control"
            token = state[arm].pop(0)
            verdict = "needs_revision" if token == "r" else "accept"
            return {"doc": {"verdict": verdict, "findings": []},
                    "exit_code": 0, "seconds": 0, "transport": "stdin",
                    "prompt_bytes": len(prompt), "raw_head": ""}

        return invoke

    def _run(self, control_pattern, replicates=3):
        original = pool_runner.invoke
        pool_runner.invoke = self._flaky(control_pattern)
        try:
            return measure_case(case(), DOC, echo_adapter(), timeout=60,
                                replicates=replicates)
        finally:
            pool_runner.invoke = original

    def test_majority_decides_and_the_split_is_kept(self):
        row = self._run("raa")          # one refusal, two clearances
        self.assertFalse(row["false_alarm"])
        self.assertEqual(row["control_verdicts"],
                         ["needs_revision", "accept", "accept"])
        self.assertAlmostEqual(row["control_refusing_share"], 1 / 3)
        self.assertFalse(row["control_unanimous"])

    def test_majority_refusal_is_a_false_alarm(self):
        row = self._run("rra")
        self.assertTrue(row["false_alarm"])
        self.assertAlmostEqual(row["control_refusing_share"], 2 / 3)

    def test_unanimous_is_distinguishable_from_split(self):
        row = self._run("rrr")
        self.assertTrue(row["false_alarm"])
        self.assertTrue(row["control_unanimous"])

    def test_tie_resolves_to_refusing_and_is_recorded(self):
        row = self._run("ra", replicates=2)
        self.assertTrue(row["false_alarm"])
        self.assertAlmostEqual(row["control_refusing_share"], 0.5)
        self.assertFalse(row["control_unanimous"])

    def test_findings_follow_the_majority_verdict(self):
        # qs-9f2748c49dd3313e's refusal reasons were unauditable because the
        # row kept the first parseable replicate — an accept with no
        # findings — while the majority refused. The retained capture must
        # agree with the verdict the row reports.
        state = {"control": ["a", "r", "r"], "mutant": ["r"]}

        def fake(adapter, prompt, timeout, **kwargs):
            arm = "mutant" if ("may freely" in prompt or "may clear" in prompt) \
                else "control"
            refusing = state[arm].pop(0) == "r"
            findings = ([{"element_anchor": "#el:x", "text": "broken"}]
                        if refusing else [])
            return {"doc": {"verdict": ("needs_revision" if refusing
                                        else "accept"),
                            "findings": findings},
                    "exit_code": 0, "timed_out": False, "seconds": 0,
                    "transport": "stdin", "prompt_bytes": len(prompt),
                    "raw_head": "", "error": None}

        original = pool_runner.invoke
        pool_runner.invoke = fake
        try:
            row = measure_case(case(), DOC, echo_adapter(), timeout=60,
                               replicates=3, mutant_replicates=1)
        finally:
            pool_runner.invoke = original
        self.assertTrue(row["false_alarm"])
        self.assertTrue(row["control_findings_detail"],
                        "refusal reasons must survive when the row refuses")

    def test_single_replicate_keeps_prior_behaviour(self):
        row = self._run("a", replicates=1)
        self.assertEqual(row["replicates"], 1)
        self.assertFalse(row["false_alarm"])
        self.assertTrue(row["control_unanimous"])
if __name__ == "__main__":
    unittest.main()


class AnchorSetTest(unittest.TestCase):
    """The invariant replay set is an instrument control, not more evidence."""

    def _substrates(self, n=30):
        from caplab.advisory.operators import ALL_OPERATORS
        names = [op.__name__ for op in ALL_OPERATORS]
        out = []
        for i in range(n):
            sha = f"{i:064x}"
            out.append({"substrate_id": "qs-" + sha[:16], "sha256": sha,
                        "partition": "open",
                        "source": {"kind": "striatum-exchange",
                                   "dispatch_id": sha,
                                   "input_path": "inputs/a"},
                        "applicable_operators": sorted(names)})
        return out

    def test_set_is_invariant_and_substrate_disjoint(self):
        from caplab.advisory.anchor import build_anchor_set
        subs = self._substrates()
        first = build_anchor_set(subs, size=12)
        second = build_anchor_set(list(reversed(subs)), size=12)
        self.assertEqual(first["cases"], second["cases"])
        ids = [c["substrate_id"] for c in first["cases"]]
        self.assertEqual(len(ids), len(set(ids)))
        # one case per operator: the set spans the defect space first
        ops = [c["operator"] for c in first["cases"]]
        self.assertEqual(len(ops), len(set(ops)))

    def test_defective_control_substrate_cannot_anchor(self):
        from caplab.advisory.adjudication import (Adjudications,
                                                  build_adjudication)
        from caplab.advisory.anchor import build_anchor_set
        subs = self._substrates()
        banned = subs[0]["source"]["dispatch_id"]
        adj = Adjudications([build_adjudication(
            dispatch_id=banned, disposition="defective", basis="audited",
            adjudicated_by="principal:test",
            as_of="2026-08-16T00:00:00+00:00")])
        chosen = build_anchor_set(subs, size=12, adjudications=adj)
        used = {c["source"]["dispatch_id"] for c in chosen["cases"]}
        self.assertNotIn(banned, used)

    def test_anchor_substrates_are_withheld_from_breadth(self):
        from caplab.advisory.anchor import anchor_substrate_ids
        from caplab.advisory.corpus import sample_cases
        subs = self._substrates()
        from caplab.advisory.anchor import build_anchor_set
        anchor = build_anchor_set(subs, size=12)
        withheld = anchor_substrate_ids(anchor)
        breadth_pool = [s for s in subs if s["substrate_id"] not in withheld]
        drawn = {c["substrate_id"] for c in
                 sample_cases(breadth_pool, sweep_seed=1, per_operator=3)}
        self.assertFalse(drawn & withheld)

    def test_reliability_reports_per_arm_unanimity(self):
        from caplab.advisory.anchor import reliability
        rows = [
            {"anchor": True, "usable": True, "caught": True, "false_alarm": False,
             "control_unanimous": True, "mutant_unanimous": True},
            {"anchor": True, "usable": True, "caught": True, "false_alarm": True,
             "control_unanimous": False, "mutant_unanimous": True},
            {"anchor": False, "usable": True, "caught": False, "false_alarm": False,
             "control_unanimous": False, "mutant_unanimous": False},
        ]
        result = reliability(rows)
        self.assertEqual(result["anchor_cases"], 2)      # breadth row ignored
        self.assertEqual(result["control_unanimous_share"], 0.5)
        self.assertEqual(result["mutant_unanimous_share"], 1.0)

    def test_reliability_reports_pairwise_agreement_and_kappa(self):
        # Unanimity and pairwise agreement are different statistics, and the
        # 2026-08-17 report conflated them with a third (cross-sweep
        # agreement). The reliability block must state the statistic it
        # reports and say how null replicates were handled.
        from caplab.advisory.anchor import reliability
        rows = [
            {"anchor": True, "usable": True, "caught": True,
             "false_alarm": False,
             "control_verdicts": ["accept", "accept", "accept"],
             "mutant_verdicts": ["needs_revision"] * 3},
            {"anchor": True, "usable": True, "caught": False,
             "false_alarm": True,
             "control_verdicts": ["needs_revision", "accept", None],
             "mutant_verdicts": ["needs_revision", "accept", "accept"]},
        ]
        result = reliability(rows)
        control = result["control_pairwise"]
        # Case 1: three agreeing pairs. Case 2: the null replicate excludes
        # two pairs; the one valid pair disagrees.
        self.assertEqual(control["agreeing_pairs"], 3)
        self.assertEqual(control["valid_pairs"], 4)
        self.assertEqual(control["null_replicates"], 1)
        self.assertAlmostEqual(control["agreement"], 0.75)
        self.assertAlmostEqual(control["kappa"], 0.21875)
        self.assertIn("null replicates excluded", control["handling"])
        self.assertAlmostEqual(result["mutant_pairwise"]["agreement"], 4 / 6)

    def test_drift_names_the_ambiguity_it_cannot_resolve(self):
        from caplab.advisory.anchor import drift
        before = [{"dispatch_id": "a", "anchor": True, "usable": True,
                   "caught": True, "false_alarm": False}]
        after = [{"dispatch_id": "a", "anchor": True, "usable": True,
                  "caught": False, "false_alarm": False}]
        result = drift(after, before)
        self.assertEqual(result["shared_anchor_cases"], 1)
        self.assertEqual(result["caught_agreement"], 0.0)
        self.assertIn("does not say which", result["reading"])

    def test_asymmetric_replication_is_honoured(self):
        counts = {"control": 0, "mutant": 0}

        def counting(adapter, prompt, timeout, **kwargs):
            arm = "mutant" if ("may freely" in prompt or "may clear" in prompt) \
                else "control"
            counts[arm] += 1
            return {"doc": {"verdict": "accept", "findings": []},
                    "exit_code": 0, "seconds": 0, "transport": "stdin",
                    "prompt_bytes": len(prompt), "raw_head": ""}

        original = pool_runner.invoke
        pool_runner.invoke = counting
        try:
            row = measure_case(case(), DOC, echo_adapter(), timeout=60,
                               replicates=3, mutant_replicates=1)
        finally:
            pool_runner.invoke = original
        self.assertEqual(counts, {"control": 3, "mutant": 1})
        self.assertEqual(row["replicates"], 3)
        self.assertEqual(row["mutant_replicates"], 1)
if __name__ == "__main__":
    unittest.main()


class ConcurrencyTest(unittest.TestCase):
    def test_lanes_never_exceed_the_declaration(self):
        from caplab.advisory.pool_runner import declared_lanes
        self.assertEqual(declared_lanes(
            {"capabilities": {"concurrency": {"max_lanes": 2}}}), 2)
        # A declaration that states nothing gets one lane, not unlimited.
        self.assertEqual(declared_lanes({"capabilities": {}}), 1)
        self.assertEqual(declared_lanes({}), 1)
        self.assertEqual(declared_lanes(
            {"capabilities": {"concurrency": {"max_lanes": "bad"}}}), 1)
if __name__ == "__main__":
    unittest.main()


class CaseSelectionTest(unittest.TestCase):
    """The runner draws by seed unless a targeted-cell document names cases.

    Targeted cells exist for the promotion gate: they re-measure exactly the
    (substrate, defect class) cells that separated a pair, under a fresh
    sweep seed. Cases selected on prior outcome are claim-poison, so the
    selection mode is stamped where scoring can refuse it.
    """

    def _substrate(self, sha, operators=("dropped_section", "hash_mismatch")):
        return {"substrate_id": "qs-" + sha[:16], "sha256": sha,
                "partition": "open",
                "source": {"kind": "striatum-exchange", "dispatch_id": sha,
                           "input_path": "inputs/a.md"},
                "applicable_operators": sorted(operators)}

    def test_seeded_draw_is_the_default(self):
        cases, selection = pool_runner.select_cases(
            [self._substrate("a" * 64)], sweep_seed=5, per_operator=1,
            partition="open", max_cases=40, withheld=set(), cases_doc=None)
        self.assertEqual(selection, "seeded-draw")
        self.assertTrue(cases)

    def test_targeted_doc_yields_exactly_its_cells(self):
        pool = [self._substrate("a" * 64), self._substrate("b" * 64)]
        doc = {"cells": [{"substrate_id": pool[0]["substrate_id"],
                          "operator": "hash_mismatch"}]}
        cases, selection = pool_runner.select_cases(
            pool, sweep_seed=5, per_operator=1, partition="open",
            max_cases=40, withheld=set(), cases_doc=doc)
        self.assertEqual(selection, "targeted-reproduction")
        self.assertEqual([(c["substrate_id"], c["operator"]) for c in cases],
                         [(pool[0]["substrate_id"], "hash_mismatch")])

    def test_empty_targeted_doc_refuses(self):
        with self.assertRaises(ValueError):
            pool_runner.select_cases(
                [self._substrate("a" * 64)], sweep_seed=5, per_operator=1,
                partition="open", max_cases=40, withheld=set(),
                cases_doc={"cells": []})

    def test_targeted_cell_on_an_anchor_substrate_refuses(self):
        # An anchor substrate is replayed every sweep as an instrument
        # control; letting a targeted cell double-run it would let one
        # constant subset serve two populations at once.
        pool = [self._substrate("a" * 64)]
        doc = {"cells": [{"substrate_id": pool[0]["substrate_id"],
                          "operator": "hash_mismatch"}]}
        with self.assertRaises(ValueError):
            pool_runner.select_cases(
                pool, sweep_seed=5, per_operator=1, partition="open",
                max_cases=40, withheld={pool[0]["substrate_id"]},
                cases_doc=doc)


class ProfileRemeasurementTest(unittest.TestCase):
    """Cells selected by CONTRACT VERSION are not outcome-selected.

    The v1-changeset quarantine removed ~35%% of early synthetic sweeps'
    cases. Re-measuring exactly those cells under the clean contract selects
    on profile — an exogenous property fixed before any result existed — so
    the run is claim-eligible, unlike targeted-reproduction runs whose cells
    are chosen for what they previously scored.
    """

    def _substrate(self, sha):
        return {"substrate_id": "qs-" + sha[:16], "sha256": sha,
                "partition": "open",
                "source": {"kind": "striatum-exchange", "dispatch_id": sha,
                           "input_path": "inputs/a.md"},
                "applicable_operators": ["dropped_section", "hash_mismatch"]}

    def test_profile_remeasurement_stamp(self):
        pool = [self._substrate("a" * 64)]
        doc = {"selection": "profile-remeasurement",
               "cells": [{"substrate_id": pool[0]["substrate_id"],
                          "operator": "hash_mismatch"}]}
        cases, selection = pool_runner.select_cases(
            pool, sweep_seed=5, per_operator=1, partition="open",
            max_cases=40, withheld=set(), cases_doc=doc)
        self.assertEqual(selection, "profile-remeasurement")
        self.assertEqual(len(cases), 1)

    def test_profile_remeasurement_is_claim_eligible(self):
        import json as _json
        import os as _os
        import tempfile as _tempfile

        from caplab.advisory.scoring import outcome_selected
        with _tempfile.TemporaryDirectory() as root:
            with open(_os.path.join(root, "summary.json"), "w") as f:
                _json.dump({"case_selection": "profile-remeasurement",
                            "aborted": None}, f)
            self.assertFalse(outcome_selected(root))

    def test_unknown_selection_refuses(self):
        pool = [self._substrate("a" * 64)]
        doc = {"selection": "vibes",
               "cells": [{"substrate_id": pool[0]["substrate_id"],
                          "operator": "hash_mismatch"}]}
        with self.assertRaises(ValueError):
            pool_runner.select_cases(
                pool, sweep_seed=5, per_operator=1, partition="open",
                max_cases=40, withheld=set(), cases_doc=doc)


class SandboxTest(unittest.TestCase):
    """Replayed prompts name live repository paths, and an agentic harness
    will act on them: on 2026-08-23 an agy lane wrote a replay case's
    delivery into the live striatum-next checkout (postmortem
    scheduler-overwrite-postmortem-2026-08-23). Every adapter invocation is
    now contained: the user's git root is read-only inside the lane."""

    def test_sandbox_wraps_argv_with_git_root_masked(self):
        # Superseded ro-bind on 2026-08-23: read access was enough to
        # resolve references against the wrong repository, so the
        # checkouts are masked entirely.
        argv = pool_runner.sandbox_argv(["echo", "hi"], workspace="/tmp/ws")
        self.assertEqual(argv[0], "bwrap")
        joined = " ".join(argv)
        git_root = os.path.expanduser("~/git")
        # Stage B: the checkouts are gone with the rest of home (tmpfs over
        # home, nothing under ~/git re-bound).
        self.assertIn(f"--tmpfs {os.path.expanduser('~')} ", joined)
        self.assertNotIn(f"bind {git_root}", joined)
        self.assertIn("--bind /tmp/ws /tmp/ws", joined)
        self.assertTrue(joined.endswith("-- echo hi"))

    @unittest.skipUnless(pool_runner.sandbox_available()
                         and os.path.isdir(os.path.expanduser("~/git/caplab")),
                         "bwrap absent or no ~/git checkout to protect")
    def test_lane_cannot_write_into_git_root(self):
        import subprocess
        target = os.path.join(os.path.expanduser("~/git/caplab"),
                              ".caplab-sandbox-probe")
        argv = pool_runner.sandbox_argv(
            ["sh", "-c", f"touch {target} && echo WROTE || echo REFUSED"],
            workspace=tempfile.gettempdir())
        out = subprocess.run(argv, capture_output=True, text=True,
                             timeout=30).stdout
        self.assertIn("REFUSED", out)
        self.assertFalse(os.path.exists(target))

    def test_invoke_records_sandbox_and_preamble(self):
        adapter = {"command": ["python3", "-c",
                               "import sys;print('{\"verdict\":\"accept\"}')"],
                   "prompt_mode": "arg"}
        result = invoke(adapter, "small", timeout=60)
        self.assertIn(result["sandbox"], ("bwrap", "none"))

    def test_every_contract_forbids_side_effects(self):
        from caplab.advisory.calibrate import CALIBRATION_PROFILES
        for name, prompt in CALIBRATION_PROFILES.items():
            if name == "v0":
                continue
            self.assertIn("REVIEW ONLY", prompt, name)
            self.assertIn("Do not create, modify", prompt, name)


class WorkspaceIsolationTest(unittest.TestCase):
    """The filesystem is not the artifact. On 2026-08-23 two oc-deepseek-pro
    reviews demonstrably resolved a change set's file references against the
    caplab tree they were mounted in — a read-only cousin of the replay
    escape. The lane's visible universe is now the artifact: neutral cwd,
    every git checkout masked, only the case workspace visible."""

    def test_sandbox_masks_git_entirely(self):
        argv = pool_runner.sandbox_argv(["true"], workspace="/tmp/ws")
        joined = " ".join(argv)
        git_root = os.path.expanduser("~/git")
        self.assertIn(f"--tmpfs {os.path.expanduser('~')} ", joined)
        self.assertNotIn(f"bind {git_root}", joined)

    @unittest.skipUnless(pool_runner.sandbox_available()
                         and os.path.isdir(os.path.expanduser("~/git/caplab")),
                         "bwrap absent or no ~/git")
    def test_lane_cannot_even_read_the_checkouts(self):
        import subprocess
        argv = pool_runner.sandbox_argv(
            ["sh", "-c",
             "ls " + os.path.expanduser("~/git/caplab") + " 2>/dev/null "
             "| head -1; echo END"],
            workspace=tempfile.gettempdir())
        out = subprocess.run(argv, capture_output=True, text=True,
                             timeout=30).stdout
        self.assertEqual(out.strip(), "END")

    def test_invoke_runs_in_the_workspace_not_the_repo(self):
        with tempfile.TemporaryDirectory() as ws:
            adapter = {"command": ["python3", "-c",
                                   "import os;print(os.getcwd())"],
                       "prompt_mode": "arg"}
            result = invoke(adapter, "x", timeout=60, workspace=ws)
            self.assertIn(os.path.realpath(ws),
                          os.path.realpath(result["raw_head"].strip()))

    def test_preamble_v2_names_the_reference_universe(self):
        from caplab.advisory.calibrate import (REVIEW_PREAMBLE,
                                               REVIEW_PREAMBLE_VERSION)
        self.assertEqual(REVIEW_PREAMBLE_VERSION, 2)
        self.assertIn("filesystem is not the artifact", REVIEW_PREAMBLE)
        self.assertIn("only against the artifact's own content",
                      REVIEW_PREAMBLE)


class AdapterResourceTest(unittest.TestCase):
    """Masking the checkouts must not break declared adapters: files the
    declaration itself pins by absolute path (agy's --json-schema under
    striatum-next) are re-exposed read-only — files only, declaration only."""

    def test_declared_files_are_reexposed(self):
        with tempfile.NamedTemporaryFile(suffix=".json") as f:
            resources = pool_runner.adapter_resources(
                ["tool", "--schema", f.name, "--x", "/nonexistent/p", "-v"])
            self.assertEqual(resources, [f.name])
            argv = pool_runner.sandbox_argv(["tool"], workspace=None,
                                            extra_ro=resources)
            self.assertIn(f"--ro-bind {f.name} {f.name}", " ".join(argv))


class AbsoluteWorkspaceTest(unittest.TestCase):
    def test_relative_workspace_is_absolutized_in_binds(self):
        import shutil
        cwd = os.getcwd()
        scratch = tempfile.mkdtemp()
        os.chdir(scratch)
        try:
            os.makedirs("rel-ws-probe", exist_ok=True)
            argv = pool_runner.sandbox_argv(["true"], "rel-ws-probe")
            joined = " ".join(argv)
            self.assertNotIn(" rel-ws-probe ", joined)
            self.assertIn(os.path.abspath("rel-ws-probe"), joined)
        finally:
            os.chdir(cwd)
            shutil.rmtree(scratch, ignore_errors=True)


class EnvironmentStampTest(unittest.TestCase):
    def test_environment_version_is_declared(self):
        self.assertEqual(pool_runner.ENVIRONMENT_VERSION, "iso-v1")


class StageBContainmentTest(unittest.TestCase):
    """Plan tree-v1 rev 2 §2.2, Stage B (2026-09-06): the allowlisted synthetic
    home. Home is a tmpfs; only the harness install roots (read-only), the
    harness's own state directory (from the declaration), declared files,
    /tmp and the case workspace exist inside a lane. Between 2026-08-23 and
    Stage A a lane could read and write the graph store, the exchange, the
    tuner's runs, the cache and the Plane tokens beneath the ~/git mask."""

    HOME = os.path.expanduser("~")

    def _joined(self, argv, **kw):
        return " ".join(pool_runner.sandbox_argv(argv, workspace="/tmp/ws", **kw))

    def test_home_is_a_tmpfs_and_nothing_masked_is_bound(self):
        joined = self._joined(["true"])
        self.assertIn(f"--ro-bind / / --tmpfs {self.HOME} ", joined)
        for masked in pool_runner.MASKED_HOME_PATHS:
            path = os.path.expanduser(masked)
            self.assertNotIn(f"bind {path} ", joined, path)
        # home is never re-bound after the tmpfs
        self.assertNotIn(f"--bind {self.HOME} {self.HOME}", joined)

    def test_toolchain_is_read_only_and_state_dir_writable(self):
        with tempfile.TemporaryDirectory(dir=self.HOME) as d:
            joined = self._joined(["/usr/bin/env", f"CLAUDE_CONFIG_DIR={d}", "claude", "-p"])
            self.assertIn(f"--bind {d} {d}", joined)
            for p in pool_runner.TOOLCHAIN_RO_PATHS:
                path = os.path.expanduser(p)
                if os.path.isdir(path):
                    self.assertIn(f"--ro-bind {path} {path}", joined)
                    self.assertNotIn(f"--bind {path} {path}", joined)
            # tmpfs first, then the binds on top of it
            self.assertLess(joined.index(f"--tmpfs {self.HOME}"), joined.index(f"--bind {d} {d}"))

    def test_opencode_state_is_bound_by_program_name_only(self):
        present = [os.path.expanduser(p) for p in pool_runner.OPENCODE_STATE_PATHS
                   if os.path.isdir(os.path.expanduser(p))]
        with_oc = self._joined(["/usr/bin/env", "X=1", "opencode", "run"])
        without = self._joined(["/usr/bin/env", "X=1", "claude", "-p"])
        for path in present:
            self.assertIn(f"--bind {path} {path}", with_oc)
            self.assertNotIn(path, without)
        self.assertEqual(pool_runner.adapter_program(["/usr/bin/env", "A=b", "codex", "exec"]), "codex")
        self.assertEqual(pool_runner.adapter_program(["striatum-openai-lane", "-model", "x"]),
                         "striatum-openai-lane")

    def test_declared_env_files_are_exposed_read_only(self):
        with tempfile.NamedTemporaryFile(dir=self.HOME) as f:
            joined = self._joined(["/usr/bin/env", f"RIPGREP_CONFIG_PATH={f.name}", "opencode", "run"])
            self.assertIn(f"--ro-bind {f.name} {f.name}", joined)

    def test_state_dir_under_a_masked_path_is_refused(self):
        plane = os.path.expanduser("~/.config/plane")
        if not os.path.isdir(plane):
            self.skipTest("no ~/.config/plane on this host")
        with self.assertRaises(ValueError):
            pool_runner.sandbox_argv(["/usr/bin/env", f"CODEX_HOME={plane}", "codex"], workspace="/tmp/ws")
        # A workspace under ~/git is fine: only the case directory exists there inside the lane.
        joined = " ".join(pool_runner.sandbox_argv(["true"], workspace="/tmp/ws/case"))
        self.assertIn("--tmpfs /tmp --bind /tmp/ws/case /tmp/ws/case", joined)

    def test_no_declared_env_means_no_rebind_and_never_home_itself(self):
        self.assertEqual(pool_runner.harness_rebinds(["tool", f"HOME={self.HOME}"]), [])
        self.assertEqual(pool_runner.harness_rebinds(["tool", "CODEX_HOME=/nonexistent/x"]), [])

    def test_readonly_subtrees_are_rebound_after_the_workspace(self):
        with tempfile.TemporaryDirectory() as ws:
            base = os.path.join(ws, "base")
            os.mkdir(base)
            joined = " ".join(pool_runner.sandbox_argv(["true"], workspace=ws, readonly=[base]))
            self.assertLess(joined.index(f"--bind {ws} {ws}"), joined.index(f"--ro-bind {base} {base}"))
            with self.assertRaises(ValueError):
                pool_runner.sandbox_argv(["true"], workspace=ws, readonly=["/tmp"])

    @unittest.skipUnless(pool_runner.sandbox_available(), "bwrap absent")
    def test_lane_sees_a_synthetic_home_and_writes_do_not_reach_it(self):
        import subprocess
        store = os.path.expanduser("~/.local/share/striatum")
        probe = os.path.join(self.HOME, ".caplab-stage-b-probe")
        with tempfile.TemporaryDirectory() as ws:
            base = os.path.join(ws, "base")
            os.mkdir(base)
            with open(os.path.join(base, "nonce.txt"), "w") as f:
                f.write("n\n")
            script = (f"ls -A {self.HOME} | grep -c . ; ls {store} {self.HOME}/git 2>/dev/null | wc -l; "
                      f"touch {probe} && echo HOME_WROTE; "
                      f"touch {base}/x 2>/dev/null && echo BASE_WROTE || echo BASE_REFUSED; "
                      f"rm {base}/nonce.txt 2>/dev/null && echo BASE_RM || echo RM_REFUSED; "
                      f"touch {ws}/ok && echo WS_OK")
            argv = pool_runner.sandbox_argv(["sh", "-c", script], workspace=ws, readonly=[base])
            out = subprocess.run(argv, capture_output=True, text=True, timeout=30).stdout.split()
            self.assertLessEqual(int(out[0]), 3, "home must hold only the install roots")
            self.assertEqual(out[1], "0", "store and checkouts must not exist inside the lane")
            self.assertIn("HOME_WROTE", out)       # the tmpfs accepts the write ...
            self.assertFalse(os.path.exists(probe))  # ... and it never reaches the real home
            self.assertIn("BASE_REFUSED", out)
            self.assertIn("RM_REFUSED", out)
            self.assertIn("WS_OK", out)
            self.assertTrue(os.path.exists(os.path.join(base, "nonce.txt")))
