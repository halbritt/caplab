import copy
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from verify_reviewer_timeout_witness import assess

CRITERIA = json.loads((ROOT / "docs/product/studies/reviewer-ranking-001/development-witnesses/council-provider-lifetime/criteria.json").read_text())


class TimeoutWitnessTest(unittest.TestCase):
    def observation(self):
        return {"schema": "caplab.council-provider-lifetime-observation/v1", "condition": "delayed-body",
                "requests": 1, "events": [{"event": event, "ms": ms} for event, ms in
                    [("turn-invoked", 0), ("headers-flushed", 20), ("body-prefix-sent", 21), ("turn-returned", 320)]],
                "result": {"status": "failure", "code": "provider_timeout", "phase": "provider", "dispatched": True, "reply": None}}

    def test_timeout_code_does_not_hide_a_late_return(self):
        observation = self.observation()
        self.assertTrue(assess(observation, "delayed-body", CRITERIA)["property_satisfied"])
        observation["events"][-1]["ms"] = 2100
        result = assess(observation, "delayed-body", CRITERIA)
        self.assertFalse(result["property_satisfied"])
        self.assertIn("maximum_ms_from_headers_to_return", result["mismatches"])

    def test_success_after_delayed_body_is_a_real_property_failure(self):
        observation = self.observation()
        observation["events"][-1:] = [{"event": "body-ended", "ms": 2020}, {"event": "turn-returned", "ms": 2025}]
        observation["result"] = {"status": "success", "code": None, "phase": None, "dispatched": True, "reply": "ordinary reply"}
        result = assess(observation, "delayed-body", CRITERIA)
        self.assertFalse(result["property_satisfied"])
        self.assertIn("body-ended-before-return", result["mismatches"])

    def test_missing_or_contradictory_capture_is_unavailable_not_defect_credit(self):
        original = self.observation()
        variants = []
        observation = copy.deepcopy(original)
        observation["events"].pop(1)
        variants.append(observation)
        observation = copy.deepcopy(original)
        observation["events"][-1]["ms"] = float("nan")
        variants.append(observation)
        observation = copy.deepcopy(original)
        observation["events"][-1]["ms"] = -1
        variants.append(observation)
        observation = copy.deepcopy(original)
        observation["requests"] = True
        variants.append(observation)
        observation = copy.deepcopy(original)
        observation["condition"] = "ordinary"
        variants.append(observation)
        for observation in variants:
            with self.subTest(observation=observation), self.assertRaises(ValueError):
                assess(observation, "delayed-body", CRITERIA)

    def test_preaborted_request_dispatch_is_not_hidden_by_cancellation_code(self):
        observation = self.observation()
        observation.update(condition="pre-aborted", events=[{"event": e, "ms": t} for e,t in
            [("service-aborted",0), ("turn-invoked",1), ("turn-returned",2)]])
        observation["result"] = {"status":"failure", "code":"provider_cancelled", "phase":"pre_dispatch", "dispatched":False}
        result = assess(observation, "pre-aborted", CRITERIA)
        self.assertFalse(result["property_satisfied"])
        self.assertEqual(result["mismatches"], ["requests"])


if __name__ == "__main__":
    unittest.main()
