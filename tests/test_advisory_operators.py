import random
import unittest

from caplab.advisory.operators import (ALL_OPERATORS, CAPLAB_OPERATORS,
                                       BY_NAME, check_present, inject)
from caplab.advisory.instrument_defects import NotApplicable

DOC = """# Sample design {#el:sample-design}

## Motivation {#el:motivation}

The system must not accept an unverified claim, and reviewers never clear a
gate without evidence. See {#el:decision-clauses} for the binding rules, and
the runbook at `docs/runbooks/review.md` for operations. This paragraph
continues with enough prose to make the section body meaningfully large for
structural operators to act upon in tests.

## Decision (Clauses) {#el:decision-clauses}

- **C1 — Evidence first**: every claim cites registered evidence before use.
- **C2 — Fail closed**: a missing record refuses rather than defaults open.

The clauses above bind the implementation, and this trailing paragraph gives
the section sufficient bulk that duplication reads as a real defect rather
than a trivial echo of a heading line.

## Consequences {#el:consequences}

Adopting this design makes quality expensive to claim and cheap to withdraw,
which is the intended trade. Deterministic replay stays possible because all
effective state derives from pinned identities, and that sentence continues
long enough to allow a mid-sentence truncation point to exist comfortably.
"""


class OperatorContractTest(unittest.TestCase):
    def test_registry_merges_vendored_and_caplab(self):
        self.assertGreaterEqual(len(ALL_OPERATORS), 15)
        self.assertIn("dropped_section", BY_NAME)          # vendored
        self.assertIn("requirement_inversion", BY_NAME)    # caplab

    def test_each_caplab_operator_mutant_checks_and_control_passes(self):
        for operator in CAPLAB_OPERATORS:
            applicable = False
            for seed in range(6):
                try:
                    injection = operator(DOC, random.Random(seed))
                except NotApplicable:
                    continue
                applicable = True
                self.assertTrue(injection.checkable, operator.__name__)
                self.assertTrue(check_present(injection, injection.body),
                                f"{operator.__name__}: mutant fails its own check")
                self.assertFalse(check_present(injection, DOC),
                                 f"{operator.__name__}: control already 'broken'")
                self.assertNotEqual(injection.body, DOC, operator.__name__)
                self.assertTrue(injection.element_anchor, operator.__name__)
            self.assertTrue(applicable,
                            f"{operator.__name__} never applied to the fixture")

    def test_operators_deterministic(self):
        for operator in CAPLAB_OPERATORS:
            try:
                first = operator(DOC, random.Random(7))
                second = operator(DOC, random.Random(7))
            except NotApplicable:
                continue
            self.assertEqual(first.body, second.body, operator.__name__)
            self.assertEqual(first.description, second.description)

    def test_inject_restricted_to_caplab_class(self):
        injection = inject(DOC, seed=3, only=["requirement_inversion"])
        self.assertEqual(injection.defect_class, "requirement_inversion")
        self.assertNotIn("must not", injection.body.split("never")[0][:400])


if __name__ == "__main__":
    unittest.main()
