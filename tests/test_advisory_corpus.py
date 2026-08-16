import unittest

from caplab.advisory.corpus import (MEASUREMENT_READY_SOURCES,
                                    measurement_ready, sample_cases)


def substrate(sha, kind="striatum-exchange", partition="open",
              operators=("dropped_section", "hash_mismatch")):
    return {
        "record": "caplab-substrate/1",
        "substrate_id": "qs-" + sha[:16],
        "sha256": sha,
        "partition": partition,
        "source": ({"kind": "striatum-exchange", "dispatch_id": sha,
                    "input_path": "inputs/a.md"} if kind == "striatum-exchange"
                   else {"kind": "repo-doc", "repo": "caplab",
                         "commit": "c" * 40, "path": "docs/x.md"}),
        "applicable_operators": sorted(operators),
    }


class SamplingTest(unittest.TestCase):
    def test_repo_docs_withheld_from_scored_sampling(self):
        pool = [substrate("a" * 64), substrate("b" * 64, kind="repo-doc")]
        cases = sample_cases(pool, sweep_seed=1, per_operator=5)
        self.assertTrue(cases)
        self.assertEqual({c["source"]["kind"] for c in cases},
                         {"striatum-exchange"})

    def test_repo_docs_available_when_explicitly_allowed(self):
        pool = [substrate("b" * 64, kind="repo-doc")]
        self.assertEqual(sample_cases(pool, sweep_seed=1, per_operator=5), [])
        cases = sample_cases(pool, sweep_seed=1, per_operator=5,
                             require_measurement_ready=False)
        self.assertTrue(cases)

    def test_sealed_partition_never_sampled_for_open_sweeps(self):
        pool = [substrate("c" * 64, partition="sealed")]
        self.assertEqual(sample_cases(pool, sweep_seed=1, per_operator=5), [])

    def test_measurement_ready_is_source_derived(self):
        self.assertIn("striatum-exchange", MEASUREMENT_READY_SOURCES)
        self.assertTrue(measurement_ready(substrate("a" * 64)))
        self.assertFalse(measurement_ready(substrate("a" * 64, kind="repo-doc")))

    def test_sampling_is_deterministic_and_class_balanced(self):
        pool = [substrate(chr(97 + i) * 64) for i in range(6)]
        first = sample_cases(pool, sweep_seed=7, per_operator=2)
        second = sample_cases(pool, sweep_seed=7, per_operator=2)
        self.assertEqual(first, second)
        by_op = {}
        for case in first:
            by_op[case["operator"]] = by_op.get(case["operator"], 0) + 1
        self.assertEqual(set(by_op.values()), {2})

    def test_different_sweep_seeds_draw_different_injections(self):
        pool = [substrate(chr(97 + i) * 64) for i in range(6)]
        a = sample_cases(pool, sweep_seed=1, per_operator=2)
        b = sample_cases(pool, sweep_seed=2, per_operator=2)
        self.assertNotEqual([c["seed"] for c in a], [c["seed"] for c in b])


if __name__ == "__main__":
    unittest.main()
