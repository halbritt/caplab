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


def receipt(seq, cause, outcome):
    return {"seq": seq, "type": "gate_result", "causes": [cause],
            "payload": {"gate_id": "receipt-checks", "outcome": outcome}}


class TierAHarvestTest(unittest.TestCase):
    """Tier A: every producer pass has delivery outcomes; receipts have a
    mechanical compliance label; some passes carry their own gates."""

    def test_deliveries_harvest_per_pass_type(self):
        from caplab.advisory.build_corpus import harvest_deliveries
        events = ledger(
            opened(1, pass_id="implementation-planning"),
            bound(2, 1, "tuple-a"), closed(3, 1, outcome="submitted"),
            opened(10, pass_id="design-convergence"),
            bound(11, 10, "tuple-a"), closed(12, 10, outcome="abandoned"),
            opened(20, pass_id="implementation-planning"),
            bound(21, 20, "tuple-a"),
            closed(22, 20, outcome="canceled", source="scheduling_deferral"))
        d = harvest_deliveries(events)
        plan = d["implementation-planning"]["tuple-a"]
        self.assertEqual(plan["submitted"], 1)
        self.assertEqual(plan["excluded_deferrals"], 1)
        self.assertEqual(d["design-convergence"]["tuple-a"]["abandoned"], 1)

    def test_receipt_compliance_attributes_to_backend(self):
        from caplab.advisory.build_corpus import harvest_receipt_compliance
        events = ledger(
            opened(1, pass_id="review"), bound(2, 1, "tuple-a"),
            submitted(3, 1), receipt(4, 3, "pass"), receipt(5, 3, "fail"),
            closed(6, 1))
        rc = harvest_receipt_compliance(events)
        self.assertEqual(rc["tuple-a"], {"pass": 1, "fail": 1})

    def test_generic_gate_harvest(self):
        from caplab.advisory.build_corpus import harvest_gate
        events = ledger(
            opened(1, pass_id="packetization"), bound(2, 1, "tuple-a"),
            submitted(3, 1),
            gate(4, 3, "pass", gate_id="work-graph-legality"),
            closed(5, 1))
        g = harvest_gate(events, pass_id="packetization",
                         gate_id="work-graph-legality")
        self.assertEqual(g["tuple-a"], {"pass": 1, "fail": 0})

    def test_tier_a_claims_carry_constructs_and_n(self):
        from caplab.advisory.build_corpus import tier_a_claims
        events = ledger(
            opened(1, pass_id="implementation-planning"),
            bound(2, 1, "tuple-a"), closed(3, 1, outcome="submitted"),
            opened(4, pass_id="implementation-planning"),
            bound(5, 4, "tuple-a"), closed(6, 4, outcome="error"),
            opened(10, pass_id="review"), bound(11, 10, "tuple-a"),
            submitted(12, 10), receipt(13, 12, "pass"), closed(14, 10))
        claims = tier_a_claims(events, as_of="2026-08-23T00:00:00+00:00",
                               ledger_lines=250000)
        constructs = {c["construct"] for c in claims}
        self.assertIn("planning.delivery/1", constructs)
        self.assertIn("harness.receipt_compliance/1", constructs)
        plan = next(c for c in claims
                    if c["construct"] == "planning.delivery/1")
        self.assertEqual(plan["metrics"]["delivery_rate"]["value"], 0.5)
        self.assertEqual(plan["metrics"]["n_pairs"]["value"], 2)
        self.assertEqual(plan["custody"], "striatum-production")


def admitted(seq, chash, backend):
    return {"seq": seq, "type": "artifact_admitted",
            "payload": {"content_hash": chash,
                        "attribution": {"backend_id": backend}}}


def judged(seq, chash, gate_id, outcome):
    return {"seq": seq, "type": "gate_result",
            "payload": {"gate_id": gate_id, "outcome": outcome,
                        "subject": {"content_hash": chash,
                                    "identity": "x", "version_seq": seq}}}


class TierBHarvestTest(unittest.TestCase):
    """Tier B: judgment gates attributed to the PRODUCER of the judged
    artifact. The label is acceptance by independent-family review (aliasing
    exclusion at placement) — model-relative, never gold."""

    def test_judgment_gate_attributes_to_producer(self):
        from caplab.advisory.build_corpus import harvest_judgment_gates
        events = ledger(
            admitted(1, "a" * 64, "tuple-a"),
            judged(2, "a" * 64, "implementation-plan-review", "pass"),
            judged(3, "a" * 64, "implementation-plan-acceptance", "fail"))
        out = harvest_judgment_gates(events)
        self.assertEqual(
            out["implementation-plan-review"]["tuple-a"], {"pass": 1, "fail": 0})
        self.assertEqual(
            out["implementation-plan-acceptance"]["tuple-a"],
            {"pass": 0, "fail": 1})

    def test_unattributed_subjects_are_counted_not_scored(self):
        from caplab.advisory.build_corpus import harvest_judgment_gates
        events = ledger(judged(2, "b" * 64, "design-review", "pass"))
        out = harvest_judgment_gates(events)
        self.assertEqual(out["design-review"].get("(unattributed)"),
                         {"pass": 1, "fail": 0})

    def test_tier_b_claims_carry_label_class(self):
        from caplab.advisory.build_corpus import tier_b_claims
        events = ledger(
            admitted(1, "a" * 64, "tuple-a"),
            judged(2, "a" * 64, "design-review", "pass"),
            judged(3, "a" * 64, "design-review", "fail"),
            judged(4, "a" * 64, "design-acceptance", "pass"))
        claims = tier_b_claims(events, as_of="2026-08-23T00:00:00+00:00",
                               ledger_lines=250000)
        c = next(c for c in claims
                 if c["construct"] == "design.independent_acceptance/1"
                 and c["subject"]["source_id"] == "tuple-a")
        self.assertEqual(c["metrics"]["review_pass_rate"]["value"], 0.5)
        self.assertEqual(c["metrics"]["acceptance_pass_rate"]["value"], 1.0)
        self.assertTrue(any("independent-family" in n for n in c["notes"]))
        self.assertTrue(any("not gold" in n or "model-relative" in n
                            for n in c["notes"]))
