import json
import os
import tempfile
import unittest
from unittest import mock

from caplab.advisory import plan_judges as pj

GRAPH_A = {"schema_version": 2, "index": ["p1"], "packets": [
    {"id": "p1", "purpose": "x", "derived_from": "el:a", "inputs": [],
     "outputs": ["a.md"], "depends_on": [], "write_scope": ["docs/"],
     "acceptance_checks": ["code"]}]}
GRAPH_B = json.loads(json.dumps(GRAPH_A))
GRAPH_B["packets"][0]["outputs"] = ["a.md", "b.md"]


class JudgePromptTest(unittest.TestCase):
    def test_prompt_carries_rubric_context_and_both_graphs_in_order(self):
        with mock.patch.object(pj, "task_context", return_value="DESIGN BODY"):
            prompt = pj.render_judge_prompt({"inputs": []}, GRAPH_A, GRAPH_B)
        self.assertTrue(prompt.startswith("JUDGE ONLY."))
        self.assertIn("DESIGN BODY", prompt)
        self.assertLess(prompt.index("WORK GRAPH A"), prompt.index("WORK GRAPH B"))
        self.assertLess(prompt.index('"a.md"'), prompt.index('"b.md"'))
        self.assertIn("Packet COUNT by itself is evidence of", prompt)

    def test_prompt_refuses_when_context_refuses(self):
        with mock.patch.object(pj, "task_context", return_value=None):
            self.assertIsNone(pj.render_judge_prompt({"inputs": []}, GRAPH_A, GRAPH_B))


class JudgeAdapterTest(unittest.TestCase):
    def _root(self, adapter_cmd, aliasing="google-gemini"):
        root = tempfile.mkdtemp()
        os.makedirs(os.path.join(root, "j1"))
        with open(os.path.join(root, "j1", "backend.yaml"), "w") as f:
            json.dump({"id": "j1", "aliasing": {"aliasing_class": aliasing},
                       "adapter": {"command": adapter_cmd, "prompt_mode": "arg",
                                   "stdout_json_pointer": "/structured_output"}}, f)
        return root

    def test_swaps_only_the_json_schema_argument(self):
        root = self._root(["agy", "--json-schema", "/x/review-ledger.schema.json",
                           "--print"])
        adapter = pj.judge_adapter(root, "j1", schema_path="/y/pairwise.json")
        self.assertEqual(adapter["command"],
                         ["agy", "--json-schema", "/y/pairwise.json", "--print"])
        self.assertEqual(adapter["stdout_json_pointer"], "/structured_output")
        self.assertEqual(adapter["aliasing_class"], "google-gemini")
        self.assertEqual(len(adapter["command_sha256"]), 64)

    def test_leaves_a_text_adapter_untouched(self):
        root = self._root(["codex", "exec", "-m", "sol"], aliasing="openai-gpt")
        adapter = pj.judge_adapter(root, "j1")
        self.assertEqual(adapter["command"], ["codex", "exec", "-m", "sol"])


class IndependenceTest(unittest.TestCase):
    JURY = [{"judge_id": "g", "aliasing_class": "google-gemini"},
            {"judge_id": "o", "aliasing_class": "openai-gpt"},
            {"judge_id": "z", "aliasing_class": "zhipu-glm"},
            {"judge_id": "?", "aliasing_class": None}]

    def test_excludes_the_planner_family_and_undeclared_judges(self):
        ids = [j["judge_id"] for j in pj.eligible_judges(self.JURY, "openai-gpt")]
        self.assertEqual(ids, ["g", "z"])
        ids = [j["judge_id"] for j in pj.eligible_judges(self.JURY, "anthropic-claude")]
        self.assertEqual(ids, ["g", "o"])
        ids = [j["judge_id"] for j in pj.eligible_judges(
            self.JURY, "openai-gpt", "google-gemini", want=3)]
        self.assertEqual(ids, ["z"])


class VerdictTest(unittest.TestCase):
    def test_parse(self):
        self.assertEqual(pj.parse_verdict({"preferred": "a"}), "A")
        self.assertEqual(pj.parse_verdict({"preferred": " Tie "}), "tie")
        self.assertIsNone(pj.parse_verdict({"preferred": "C"}))
        self.assertIsNone(pj.parse_verdict("A"))

    def test_resolve_orders_treats_order_dependence_as_tie(self):
        # control shown as A first, then as B
        self.assertEqual(pj.resolve_orders("A", "B"), "control")
        self.assertEqual(pj.resolve_orders("B", "A"), "mutant")
        self.assertEqual(pj.resolve_orders("A", "A"), "tie")      # always picks A
        self.assertEqual(pj.resolve_orders("tie", "B"), "tie")
        self.assertIsNone(pj.resolve_orders("A", None))
        self.assertTrue(pj.position_flipped("A", "A"))
        self.assertFalse(pj.position_flipped("A", "B"))
        self.assertIsNone(pj.position_flipped("tie", "B"))


class SamplingTest(unittest.TestCase):
    def test_balanced_across_planners_and_seeded(self):
        rows = []
        for planner in ("x", "y", "z"):
            for i in range(10):
                rows.append({"identity": f"{planner}/pt-{i}", "operator": "dropped_deliverable",
                             "applied": True, "admissible": True})
                rows.append({"identity": f"{planner}/pt-{i}", "operator": "atomicity_split",
                             "applied": True, "admissible": i % 2 == 0})
        pairs = pj.sample_pairs(rows, per_class=6, seed=1)
        drop = [p for p in pairs if p["operator"] == "dropped_deliverable"]
        self.assertEqual(len(drop), 6)
        self.assertEqual(sorted({p["planner"] for p in drop}), ["x", "y", "z"])
        self.assertTrue(all(p["size_probe"] for p in pairs if p["operator"] == "atomicity_split"))
        self.assertEqual(pairs, pj.sample_pairs(rows, per_class=6, seed=1))
        self.assertNotEqual([p["pair_id"] for p in pairs],
                            [p["pair_id"] for p in pj.sample_pairs(rows, per_class=6, seed=2)])


class SummaryTest(unittest.TestCase):
    def test_size_probes_are_read_apart_and_as_direction(self):
        rows = [
            {"judge": "g", "operator": "dropped_deliverable", "size_probe": False,
             "first": "A", "second": "B", "resolved": "control"},
            {"judge": "g", "operator": "dropped_deliverable", "size_probe": False,
             "first": "B", "second": "A", "resolved": "mutant"},
            {"judge": "g", "operator": "atomicity_split", "size_probe": True,
             "first": "B", "second": "A", "resolved": "mutant"},     # prefers larger
            {"judge": "g", "operator": "merge_independent_packets", "size_probe": True,
             "first": "A", "second": "B", "resolved": "control"},    # prefers larger
            {"judge": "g", "operator": "dangling_dependency", "size_probe": False,
             "first": "A", "second": "A", "resolved": "tie"},
        ]
        s = pj.summarize(rows)["g"]
        self.assertEqual(s["by_class"]["dropped_deliverable"]["catch"], 0.5)
        self.assertNotIn("atomicity_split", s["by_class"])
        self.assertEqual(s["size_probes"]["atomicity_split"]["mutant_is"], "larger")
        self.assertEqual(s["size_preference"], {"n": 2, "prefers_larger_share": 1.0})
        self.assertEqual(s["defect_classes_pooled"]["n"], 3)
        self.assertAlmostEqual(s["position_flip_rate"], 0.2)    # 1 of 5 decided


if __name__ == "__main__":
    unittest.main()
