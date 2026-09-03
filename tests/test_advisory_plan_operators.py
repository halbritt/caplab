import copy
import json
import os
import random
import shutil
import unittest

from caplab.advisory.instrument_defects import NotApplicable
from caplab.advisory.plan_operators import (BY_NAME, ORACLE_EXPECTATION,
                                            PLAN_OPERATORS, SIZE_DELTA,
                                            check_present, inject,
                                            oracle_flip)

# A five-packet graph in the plan-v2 skeleton: one root, two parallel
# children with disjoint scopes, a join, and a tail. Every operator has
# something to bite on.
GRAPH = {
    "schema_version": 2,
    "plan": {"identity": "produce/example/implementation-plan",
             "version_seq": 1, "content_hash": "0" * 64},
    "index": ["p1", "p2", "p3", "p4", "p5"],
    "packets": [
        {"id": "p1", "purpose": "Declare the catalog tuples.",
         "derived_from": "el:c1", "inputs": ["inputs/design"],
         "outputs": ["lanes/catalog/tuples.toml", "lanes/catalog/note.md"],
         "depends_on": [], "write_scope": ["lanes/catalog/"],
         "acceptance_checks": ["subject-default", "code"]},
        {"id": "p2", "purpose": "Add the admission coherence check.",
         "derived_from": "el:c4", "inputs": ["lanes/catalog/tuples.toml"],
         "outputs": ["lanes/admission/coherence.py"],
         "depends_on": ["p1"], "write_scope": ["lanes/admission/"],
         "acceptance_checks": ["withholding-guards", "code"]},
        {"id": "p3", "purpose": "Make the supervisor commit boundary strict.",
         "derived_from": "el:c5", "inputs": ["lanes/catalog/tuples.toml"],
         "outputs": ["lanes/supervisor/materialize.py",
                     "lanes/supervisor/closure.py"],
         "depends_on": ["p1"], "write_scope": ["lanes/supervisor/"],
         "acceptance_checks": ["semantic-and-durable-closure", "code"]},
        {"id": "p4", "purpose": "Cover both surfaces with tests.",
         "derived_from": "el:c6", "inputs": ["lanes/admission/coherence.py",
                                             "lanes/supervisor/closure.py"],
         "outputs": ["lanes/tests/test_lane.py"],
         "depends_on": ["p2", "p3"], "write_scope": ["lanes/tests/"],
         "acceptance_checks": ["code"]},
        {"id": "p5", "purpose": "Record the evidence.",
         "derived_from": "el:c7", "inputs": ["lanes/tests/test_lane.py"],
         "outputs": ["passes/evidence/report.md"],
         "depends_on": ["p4"], "write_scope": ["passes/evidence/"],
         "acceptance_checks": ["subject-default", "summaries-guards"]},
    ],
}
BODY = json.dumps(GRAPH, sort_keys=True)


class PlanOperatorContractTest(unittest.TestCase):
    def test_registry_covers_the_card_and_the_size_probes(self):
        names = set(BY_NAME)
        for name in ("dangling_dependency", "circular_depends_on",
                     "unresolvable_acceptance_check", "write_scope_outside_tree",
                     "atomicity_split", "dropped_deliverable",
                     "purpose_scope_contradiction", "overclaimed_verification",
                     "merge_independent_packets"):
            self.assertIn(name, names)
        self.assertEqual(set(ORACLE_EXPECTATION), names)
        self.assertEqual(SIZE_DELTA, {"atomicity_split": 1,
                                      "merge_independent_packets": -1})

    def test_every_operator_applies_and_only_the_mutant_checks(self):
        for op in PLAN_OPERATORS:
            with self.subTest(op=op.__name__):
                inj = op(BODY, random.Random(7))
                self.assertEqual(inj.defect_class, op.__name__)
                self.assertTrue(inj.checkable)
                self.assertTrue(check_present(inj, inj.body),
                                f"{op.__name__}: defect absent from mutant")
                self.assertFalse(check_present(inj, BODY),
                                 f"{op.__name__}: checker fires on control")
                mutant = json.loads(inj.body)          # still a JSON graph
                self.assertEqual(mutant["schema_version"], 2)
                self.assertIn(inj.element_anchor, [p["id"] for p in GRAPH["packets"]])

    def test_deterministic_given_seed(self):
        for op in PLAN_OPERATORS:
            with self.subTest(op=op.__name__):
                a = op(BODY, random.Random(11)).body
                b = op(BODY, random.Random(11)).body
                self.assertEqual(a, b)

    def test_exactly_one_defect_per_mutant(self):
        # No operator may change the packet set except the two size probes,
        # and those by exactly their declared delta.
        for op in PLAN_OPERATORS:
            with self.subTest(op=op.__name__):
                mutant = json.loads(op(BODY, random.Random(3)).body)
                delta = len(mutant["packets"]) - len(GRAPH["packets"])
                self.assertEqual(delta, SIZE_DELTA.get(op.__name__, 0))
                self.assertEqual(len(mutant["index"]), len(mutant["packets"]))
                self.assertEqual(set(mutant["index"]),
                                 {p["id"] for p in mutant["packets"]})

    def test_index_stays_topological_where_the_class_does_not_break_it(self):
        for op in PLAN_OPERATORS:
            if op.__name__ in ("circular_depends_on", "dangling_dependency"):
                continue
            with self.subTest(op=op.__name__):
                mutant = json.loads(op(BODY, random.Random(5)).body)
                position = {pid: i for i, pid in enumerate(mutant["index"])}
                for p in mutant["packets"]:
                    for d in p["depends_on"]:
                        self.assertLess(position[d], position[p["id"]],
                                        f"{p['id']} listed before its dependency {d}")

    def test_inject_is_seed_driven_and_restrictable(self):
        inj = inject(BODY, seed=20260902, only=["dropped_deliverable"])
        self.assertEqual(inj.defect_class, "dropped_deliverable")
        self.assertEqual(inject(BODY, 1).body, inject(BODY, 1).body)

    def test_not_applicable_on_degenerate_graphs(self):
        single = copy.deepcopy(GRAPH)
        single["packets"] = [single["packets"][0]]
        single["index"] = ["p1"]
        body = json.dumps(single)
        for name in ("circular_depends_on", "purpose_scope_contradiction",
                     "merge_independent_packets"):
            with self.subTest(op=name):
                with self.assertRaises(NotApplicable):
                    BY_NAME[name](body, random.Random(1))
        with self.assertRaises(NotApplicable):
            inject("not json", 1)

    def test_dropped_deliverable_also_removes_downstream_reference(self):
        inj = BY_NAME["dropped_deliverable"](BODY, random.Random(2))
        mutant = json.loads(inj.body)
        victim = inj.detail["deliverable"]
        for p in mutant["packets"]:
            self.assertNotIn(victim, p["inputs"])
            self.assertNotIn(victim, p["outputs"])

    def test_merge_rewires_dependents_onto_the_survivor(self):
        inj = BY_NAME["merge_independent_packets"](BODY, random.Random(4))
        mutant = json.loads(inj.body)
        ids = {p["id"] for p in mutant["packets"]}
        self.assertNotIn(inj.detail["absorbed"], ids)
        for p in mutant["packets"]:
            for d in p["depends_on"]:
                self.assertIn(d, ids)
                self.assertNotEqual(d, p["id"])

    def test_oracle_flip_reads_the_owed_field(self):
        control = {"legality": {"ok": True}, "application_index": {"ok": True},
                   "resolvability": {"status": "checked", "unresolvable": []}}
        mutant = {"legality": {"ok": False}, "application_index": {"ok": True},
                  "resolvability": {"status": "checked",
                                    "unresolvable": [{"check": "x"}]}}
        self.assertTrue(oracle_flip(control, mutant, "dangling_dependency"))
        self.assertFalse(oracle_flip(control, mutant, "circular_depends_on"))
        self.assertTrue(oracle_flip(control, mutant, "unresolvable_acceptance_check"))
        self.assertIsNone(oracle_flip(control, mutant, "dropped_deliverable"))


@unittest.skipUnless(shutil.which("striatum-plan-oracle"),
                     "striatum-plan-oracle not on PATH")
class PlanOperatorOracleTest(unittest.TestCase):
    """The three oracle-visible classes flip the verdict they owe; the
    oracle-silent classes leave every mechanical verdict as the control's."""

    REGISTRY = os.path.expanduser(
        "~/.local/lib/caplab-instruments/plan-p2b-20260827/checks-repository-v37.json")

    def setUp(self):
        from caplab.advisory.planning_corpus import score_graph
        self.score = lambda g: score_graph(
            g, registry_path=self.REGISTRY if os.path.isfile(self.REGISTRY) else None)
        self.control = self.score(GRAPH)
        if not (self.control.get("parse") or {}).get("ok"):
            self.skipTest("fixture does not parse under the installed oracle")

    def test_oracle_visible_classes_flip_and_silent_ones_do_not(self):
        for op in PLAN_OPERATORS:
            with self.subTest(op=op.__name__):
                inj = op(BODY, random.Random(9))
                verdict = self.score(json.loads(inj.body))
                flip = oracle_flip(self.control, verdict, op.__name__)
                if ORACLE_EXPECTATION[op.__name__] is None:
                    self.assertIsNone(flip)
                    self.assertTrue((verdict.get("parse") or {}).get("ok"))
                    self.assertTrue((verdict.get("application_index") or {}).get("ok"))
                    self.assertTrue((verdict.get("legality") or {}).get("ok"),
                                    (verdict.get("legality") or {}).get("failures"))
                else:
                    self.assertTrue(flip, f"{op.__name__} did not flip "
                                    f"{ORACLE_EXPECTATION[op.__name__]}")


if __name__ == "__main__":
    unittest.main()
