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
    def test_both_sources_are_measurable_under_the_contract_profile(self):
        pool = [substrate("a" * 64), substrate("b" * 64, kind="repo-doc")]
        cases = sample_cases(pool, sweep_seed=1, per_operator=5)
        self.assertEqual({c["source"]["kind"] for c in cases},
                         {"striatum-exchange", "repo-doc"})

    def test_an_unknown_source_is_still_withheld(self):
        odd = substrate("c" * 64)
        odd["source"] = {"kind": "scraped-from-the-web"}
        self.assertEqual(sample_cases([odd], sweep_seed=1, per_operator=5), [])

    def test_sealed_partition_never_sampled_for_open_sweeps(self):
        pool = [substrate("c" * 64, partition="sealed")]
        self.assertEqual(sample_cases(pool, sweep_seed=1, per_operator=5), [])

    def test_measurement_ready_is_source_derived(self):
        self.assertIn("striatum-exchange", MEASUREMENT_READY_SOURCES)
        self.assertIn("repo-doc", MEASUREMENT_READY_SOURCES)
        self.assertTrue(measurement_ready(substrate("a" * 64)))
        self.assertTrue(measurement_ready(substrate("a" * 64, kind="repo-doc")))

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


class SamplingConstraintTest(unittest.TestCase):
    """A claim must not rest on one artifact twice, nor on an accidental mix."""

    def _pool(self, n_exchange=12, n_doc=12, operators=("a_op", "b_op")):
        out = []
        for i in range(n_exchange):
            # Distinct ids: a zero-padded hex prefix is identical for every
            # small i, which silently collapsed this fixture to one substrate.
            sha = f"{i:064x}"
            out.append({"substrate_id": f"qs-e{i:012x}", "sha256": sha,
                        "partition": "open",
                        "source": {"kind": "striatum-exchange",
                                   "dispatch_id": sha},
                        "applicable_operators": sorted(operators)})
        for i in range(n_doc):
            sha = f"{i + 500:064x}"
            out.append({"substrate_id": f"qs-d{i:012x}", "sha256": sha,
                        "partition": "open",
                        "source": {"kind": "repo-doc", "repo": "caplab",
                                   "path": f"docs/{i}.md"},
                        "applicable_operators": sorted(operators)})
        return out

    def test_no_substrate_carries_two_cases(self):
        cases = sample_cases(self._pool(), sweep_seed=3, per_operator=6)
        ids = [c["substrate_id"] for c in cases]
        self.assertEqual(len(ids), len(set(ids)))

    def test_sources_are_balanced_within_an_operator(self):
        cases = sample_cases(self._pool(), sweep_seed=3, per_operator=6)
        for operator in {c["operator"] for c in cases}:
            kinds = [c["source"]["kind"] for c in cases
                     if c["operator"] == operator]
            exchange = kinds.count("striatum-exchange")
            docs = kinds.count("repo-doc")
            self.assertLessEqual(abs(exchange - docs), 1,
                                 f"{operator} drew {exchange}/{docs}")

    def test_a_single_source_pool_still_fills(self):
        cases = sample_cases(self._pool(n_doc=0), sweep_seed=3, per_operator=4)
        self.assertEqual(len(cases), 8)
        self.assertEqual({c["source"]["kind"] for c in cases},
                         {"striatum-exchange"})

    def test_allocation_is_capped_by_availability(self):
        cases = sample_cases(self._pool(n_exchange=2, n_doc=1), sweep_seed=3,
                             per_operator=5)
        # 3 substrates, 2 operators, disjointness caps the draw at 3
        self.assertEqual(len(cases), 3)
