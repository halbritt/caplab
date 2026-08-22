import unittest

from caplab.advisory.build_corpus import (BUILD_CONSTRUCT, build_claims,
                                          harvest_build_corpus)


def ledger(*events):
    return list(events)


def opened(seq, pass_id="build"):
    return {"seq": seq, "type": "pass_run_opened",
            "payload": {"pass_id": pass_id}}


def bound(seq, run, backend):
    return {"seq": seq, "type": "lane_binding",
            "payload": {"run_ref": run, "backend_id": backend}}


def submitted(seq, run):
    return {"seq": seq, "type": "submission_received", "causes": [run],
            "payload": {"run_ref": run}}


def gate(seq, cause, outcome, gate_id="packet-checks", detail=""):
    payload = {"gate_id": gate_id, "outcome": outcome}
    if detail:
        payload["detail"] = detail
    return {"seq": seq, "type": "gate_result", "causes": [cause],
            "payload": payload}


def closed(seq, run, outcome="submitted", source="submission_admission_v2"):
    return {"seq": seq, "type": "pass_run_closed",
            "payload": {"run_ref": run, "outcome": outcome,
                        "closure_source": source}}


class HarvestTest(unittest.TestCase):
    def test_gate_results_attribute_to_the_bound_backend(self):
        events = ledger(opened(1), bound(2, 1, "tuple-a"), submitted(3, 1),
                        gate(4, 3, "pass"), closed(5, 1))
        corpus = harvest_build_corpus(events)
        self.assertEqual(corpus["tuple-a"]["packet_checks"],
                         {"pass": 1, "fail": 0, "excluded_tree_moved": 0})

    def test_non_build_passes_are_ignored(self):
        events = ledger(opened(1, pass_id="review"), bound(2, 1, "tuple-a"),
                        submitted(3, 1), gate(4, 3, "pass"), closed(5, 1))
        self.assertEqual(harvest_build_corpus(events), {})

    def test_tree_moved_failures_are_excluded_not_scored(self):
        # An operator commit moved the anchored base under the build; the
        # failure describes the churn, not the builder.
        events = ledger(
            opened(1), bound(2, 1, "tuple-a"), submitted(3, 1),
            gate(4, 3, "fail",
                 detail="change set pins base X, actual base is Y "
                        "(tree moved: rebase-style revision required)"),
            closed(5, 1, outcome="error"))
        corpus = harvest_build_corpus(events)
        self.assertEqual(corpus["tuple-a"]["packet_checks"],
                         {"pass": 0, "fail": 0, "excluded_tree_moved": 1})

    def test_capacity_deferrals_leave_the_delivery_denominator(self):
        events = ledger(
            opened(1), bound(2, 1, "tuple-a"),
            closed(3, 1, outcome="canceled", source="scheduling_deferral"),
            opened(10), bound(11, 10, "tuple-a"), submitted(12, 10),
            gate(13, 12, "pass"), closed(14, 10, outcome="submitted"))
        corpus = harvest_build_corpus(events)
        d = corpus["tuple-a"]["deliveries"]
        self.assertEqual(d["submitted"], 1)
        self.assertEqual(d["excluded_deferrals"], 1)
        self.assertNotIn("canceled", d)

    def test_other_gates_do_not_count(self):
        events = ledger(opened(1), bound(2, 1, "tuple-a"), submitted(3, 1),
                        gate(4, 3, "pass", gate_id="capture-checks"),
                        closed(5, 1))
        corpus = harvest_build_corpus(events)
        self.assertEqual(corpus["tuple-a"]["packet_checks"]["pass"], 0)

    def test_multiple_submissions_score_each_gate_result(self):
        events = ledger(opened(1), bound(2, 1, "tuple-a"),
                        submitted(3, 1), gate(4, 3, "fail"),
                        submitted(5, 1), gate(6, 5, "pass"),
                        closed(7, 1))
        pc = harvest_build_corpus(events)["tuple-a"]["packet_checks"]
        self.assertEqual((pc["pass"], pc["fail"]), (1, 1))


class ClaimTest(unittest.TestCase):
    def test_claim_carries_construct_custody_and_wilson_ci(self):
        events = ledger(opened(1), bound(2, 1, "tuple-a"), submitted(3, 1),
                        gate(4, 3, "pass"), submitted(5, 1),
                        gate(6, 5, "fail"), closed(7, 1))
        claims = build_claims(harvest_build_corpus(events),
                              as_of="2026-08-22T00:00:00+00:00",
                              ledger_lines=250000)
        self.assertEqual(len(claims), 1)
        c = claims[0]
        self.assertEqual(c["construct"], BUILD_CONSTRUCT)
        self.assertEqual(c["custody"], "striatum-production")
        m = c["metrics"]["packet_checks_pass_rate"]
        self.assertEqual(m["value"], 0.5)
        self.assertEqual(m["denominator"], 2)
        self.assertEqual(len(m["ci95"]), 2)
        self.assertTrue(any("tree moved" in n or "tree_moved" in n
                            for n in c["notes"]))

    def test_backend_below_floor_still_claims_with_denominator(self):
        # The floor is the consumer's to enforce; CAPLAB reports what it
        # measured with its n, never silently drops a subject.
        events = ledger(opened(1), bound(2, 1, "tuple-a"), submitted(3, 1),
                        gate(4, 3, "pass"), closed(5, 1))
        claims = build_claims(harvest_build_corpus(events),
                              as_of="2026-08-22T00:00:00+00:00",
                              ledger_lines=250000)
        self.assertEqual(claims[0]["metrics"]["packet_checks_pass_rate"]
                         ["denominator"], 1)
