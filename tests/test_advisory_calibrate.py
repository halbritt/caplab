import json
import os
import tempfile
import unittest

from caplab.advisory.calibrate import (adapter_review, materialize_case,
                                       validate_pending)

DOC = """# Sample {#el:sample}

## Rules {#el:rules}

Reviewers must not clear a gate without evidence, and the pipeline never
promotes an unverified claim. See `docs/runbooks/review.md` for operations;
this sentence pads the section so structural operators have material.

## Consequences {#el:consequences}

Quality becomes expensive to claim and cheap to withdraw, which is intended.
This trailing sentence exists so a mid-sentence truncation point is present.
"""


def pending_row(operator="requirement_inversion", seed=11):
    return {
        "difficulty_flag": "pending-strong-reference",
        "case": {"operator": operator, "seed": seed, "sha256": "x" * 64,
                 "substrate_id": "qs-test", "source": {"kind": "test"}},
    }


class CalibrateTest(unittest.TestCase):
    def test_materialize_case_gates_mechanically(self):
        case = {"operator": "requirement_inversion", "seed": 11}
        materialized = materialize_case(case, DOC)
        self.assertIsNotNone(materialized)
        control, mutant, injection = materialized
        self.assertEqual(control, DOC)
        self.assertNotEqual(mutant, DOC)
        self.assertEqual(injection.defect_class, "requirement_inversion")

    def test_validate_pending_flags(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "cal.jsonl")
            with open(path, "w") as f:
                f.write(json.dumps(pending_row()) + "\n")
                f.write(json.dumps(
                    {"difficulty_flag": "at-or-below-easy-floor",
                     "case": {"operator": "x", "seed": 0}}) + "\n")

            def catching_reviewer(body):
                defect = "may" in body.split("Reviewers ")[1][:60] or \
                    "may freely" in body
                return {"verdict": "needs_revision" if defect else "accept",
                        "findings": [{"element_anchor": "#el:rules"}]}

            rows = validate_pending(path, catching_reviewer, lambda c: DOC)
            self.assertEqual(len(rows), 1)  # easy-floor row not re-run
            self.assertEqual(rows[0]["difficulty_flag"], "validated-hard")
            self.assertTrue(rows[0]["strong_reference_anchored"])

            def blind_reviewer(body):
                return {"verdict": "accept", "findings": []}

            rows = validate_pending(path, blind_reviewer, lambda c: DOC)
            self.assertEqual(rows[0]["difficulty_flag"],
                             "strong-miss-quarantine-candidate")

    def test_adapter_review_parses_json_from_stdout(self):
        doc = adapter_review(
            ["python3", "-c",
             "import sys;print('{\"verdict\": \"accept\", \"findings\": []}')"],
            "arg", "body")
        self.assertEqual(doc["verdict"], "accept")

    def test_adapter_review_resolves_envelope_pointer(self):
        # The agy family wraps the completion; reading raw stdout finds no
        # verdict and would score every case a strong miss.
        envelope = ('{"type":"result","structured_output":'
                    '{"verdict":"needs_revision","findings":[]}}')
        argv = ["python3", "-c", f"print({envelope!r})"]
        self.assertIsNone(adapter_review(argv, "arg", "body").get("verdict"))
        doc = adapter_review(argv, "arg", "body",
                             stdout_json_pointer="/structured_output")
        self.assertEqual(doc["verdict"], "needs_revision")

    def test_unresolvable_pointer_yields_no_review(self):
        argv = ["python3", "-c", "print('{\"type\":\"result\"}')"]
        self.assertIsNone(adapter_review(argv, "arg", "body",
                                         stdout_json_pointer="/structured_output"))



class StreamingTest(unittest.TestCase):
    def test_rows_are_emitted_as_they_complete(self):
        import json as _json
        import tempfile as _tf
        with _tf.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "cal.jsonl")
            with open(path, "w") as f:
                for seed in (11, 12, 13):
                    f.write(_json.dumps(pending_row(seed=seed)) + "\n")
            seen = []

            def boom(body):
                # fail on the third case, after two have been answered
                if len(seen) >= 2:
                    raise RuntimeError("reference died")
                return {"verdict": "needs_revision",
                        "findings": [{"element_anchor": "#el:rules"}]}

            with self.assertRaises(RuntimeError):
                validate_pending(path, boom, lambda c: DOC,
                                 on_row=seen.append)
            # the answered cases survived the failure
            self.assertEqual(len(seen), 2)


if __name__ == "__main__":
    unittest.main()


class ChangesetV2ContractTest(unittest.TestCase):
    """The v2 change-set contract scopes the absent base out of the review.

    v1 demanded anchoring and hash verification while materializing no base
    and providing no lookup primitive; diligent subjects grepped the whole
    361 GB store (infra postmortem 2026-08-21-oom-rg-store-grep.md), which
    both exhausted host memory and confounded the measurement with
    store-forensics affordance. v2 states what is reviewable and forbids
    the hunt.
    """

    def test_v2_is_the_routed_changeset_profile(self):
        import json as _json

        from caplab.advisory.calibrate import profile_for_artifact
        body = _json.dumps({"base": {"content_hash": "a" * 64},
                            "files": {"x": "y"}})
        self.assertEqual(profile_for_artifact(body), "v2-changeset")

    def test_v2_contract_scopes_out_the_base(self):
        from caplab.advisory.calibrate import CALIBRATION_PROFILES
        prompt = CALIBRATION_PROFILES["v2-changeset"]
        self.assertIn("base tree is NOT available", prompt)
        self.assertIn("Do not search", prompt)
        self.assertIn("present in the change set", prompt)
        # The declaration of the base must still be reviewable: its absence
        # is a plantable defect (base_dropped).
        self.assertIn("stated base", prompt)

    def test_v1_changeset_remains_loadable_for_historical_reads(self):
        from caplab.advisory.calibrate import CALIBRATION_PROFILES
        self.assertIn("v1-changeset", CALIBRATION_PROFILES)
