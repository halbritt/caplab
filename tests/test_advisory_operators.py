import json
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
        # Operators target different artifact shapes: prose operators bite on
        # markdown, delivery operators on change sets. Each must apply to at
        # least one, and must gate correctly on whichever it applies to.
        for operator in CAPLAB_OPERATORS:
            applicable = False
            for control in (DOC, CHANGE_SET):
                for seed in range(6):
                    try:
                        injection = operator(control, random.Random(seed))
                    except NotApplicable:
                        continue
                    applicable = True
                    self.assertTrue(injection.checkable, operator.__name__)
                    self.assertTrue(
                        check_present(injection, injection.body),
                        f"{operator.__name__}: mutant fails its own check")
                    self.assertFalse(
                        check_present(injection, control),
                        f"{operator.__name__}: control already 'broken'")
                    self.assertNotEqual(injection.body, control,
                                        operator.__name__)
                    self.assertTrue(injection.element_anchor, operator.__name__)
            self.assertTrue(applicable,
                            f"{operator.__name__} applied to no fixture")

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


GATED_VENDORED = ("dropped_section", "contradicted_clause", "scope_violation",
                  "refuted_conclusion", "overclaimed_level")

CLAIMY_DOC = DOC + """
## Status {#el:status}

The delivery is Asserted at this stage and binds nothing further.
"""

CHANGE_SET = json.dumps({
    "schema_version": "1",
    "base": {"content_hash": "a" * 64},
    "files": {
        "docs/thing/README.md": "# Thing\n\n- `thing_test.go`: Exercises the "
                                "aggregation path.\n",
        "tests/thing/thing_test.go": "package thing_test\n\nimport (\n"
                                     "\t\"encoding/json\"\n\t\"testing\"\n)\n\n"
                                     "func TestRoundTrip(t *testing.T) {\n"
                                     "\tdata, _ := json.Marshal(struct{}{})\n"
                                     "\t_ = data\n}\n",
    },
}, indent=2)


class GatedVendoredOperatorTest(unittest.TestCase):
    """The five operators that shipped without a checker are now gated."""

    def test_each_gates_mutant_true_control_false(self):
        for name in GATED_VENDORED:
            body = CLAIMY_DOC
            injection = None
            for seed in range(10):
                try:
                    injection = BY_NAME[name](body, random.Random(seed))
                    break
                except NotApplicable:
                    continue
            self.assertIsNotNone(injection, f"{name} never applied")
            self.assertTrue(injection.checkable, name)
            self.assertTrue(check_present(injection, injection.body),
                            f"{name}: mutant fails its own gate")
            self.assertFalse(check_present(injection, body),
                             f"{name}: control passes as already broken")

    def test_gating_does_not_change_the_mutation(self):
        # The wrapper must not alter what the vendored operator produced.
        from caplab.advisory import instrument_defects as vendored
        for name in GATED_VENDORED:
            try:
                plain = getattr(vendored, name)(CLAIMY_DOC, random.Random(4))
                gated = BY_NAME[name](CLAIMY_DOC, random.Random(4))
            except NotApplicable:
                continue
            self.assertEqual(plain.body, gated.body, name)
            self.assertEqual(plain.element_anchor, gated.element_anchor, name)


class ClaimVsBehaviorTest(unittest.TestCase):
    def test_claims_a_verification_the_test_does_not_perform(self):
        injection = BY_NAME["unearned_verification_claim"](
            CHANGE_SET, random.Random(0))
        self.assertEqual(injection.defect_class, "unearned_verification_claim")
        self.assertTrue(check_present(injection, injection.body))
        self.assertFalse(check_present(injection, CHANGE_SET))

    def test_skips_tests_that_really_validate(self):
        honest = json.loads(CHANGE_SET)
        honest["files"]["tests/thing/thing_test.go"] += (
            '\n// loads schemas/thing.schema.json via jsonschema\n')
        with self.assertRaises(NotApplicable):
            BY_NAME["unearned_verification_claim"](
                json.dumps(honest), random.Random(0))

    def test_not_applicable_to_plain_markdown(self):
        with self.assertRaises(NotApplicable):
            BY_NAME["unearned_verification_claim"](DOC, random.Random(0))


class BaseHashExclusionTest(unittest.TestCase):
    """hash_mismatch must not plant defects on hashes of absent content.

    A flipped base.content_hash can only be verified by locating the base
    blob, which the v2 change-set contract declares unavailable and the
    2026-08-21 OOM postmortem shows was answered by grepping the whole
    store. An operator may only plant what the contract lets a subject
    honestly find.
    """

    def test_base_only_hash_is_not_applicable(self):
        import json as _json
        import random as _random

        from caplab.advisory.instrument_defects import (NotApplicable,
                                                        hash_mismatch)
        body = _json.dumps({"schema_version": "1",
                            "base": {"content_hash": "a" * 64},
                            "files": {"docs/x.md": "content"}})
        with self.assertRaises(NotApplicable):
            hash_mismatch(body, _random.Random(1))

    def test_non_base_hash_is_still_planted(self):
        import json as _json
        import random as _random

        from caplab.advisory.instrument_defects import hash_mismatch
        body = _json.dumps({"schema_version": "1",
                            "base": {"content_hash": "a" * 64},
                            "packet": {"artifact_hash": "b" * 64},
                            "files": {"docs/x.md": "content"}})
        for seed in range(5):
            injection = hash_mismatch(body, _random.Random(seed))
            self.assertEqual(injection.detail["was"], "b" * 64,
                             "must never select the base hash")
        mutated = _json.loads(injection.body)
        self.assertEqual(mutated["base"]["content_hash"], "a" * 64)
