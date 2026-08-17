import unittest

from caplab.advisory.discrimination import promotion_candidates


def contrast(sweep_seed, discordant, a="tuple-a", b="tuple-b"):
    return {"a": a, "b": b, "sweep_seed": sweep_seed,
            "discordant_cases": discordant}


def case(substrate="qs-x", cls="hash_mismatch", caught_by="a"):
    return {"substrate_id": substrate, "defect_class": cls,
            "dispatch_id": f"{substrate}:{cls}:1", "caught_by": caught_by}


class SoundAdjudications:
    def disposition(self, dispatch_id):
        return "sound"


class UnexaminedAdjudications:
    def disposition(self, dispatch_id):
        return "unadjudicated"


class PromotionTest(unittest.TestCase):
    """A case enters the discrimination corpus only when its separation
    reproduces, its control is established sound, and it maps to a declared
    operator. One lucky disagreement is not evidence."""

    def test_reproduced_same_direction_separation_is_promoted(self):
        contrasts = [contrast(1, [case()]), contrast(2, [case()])]
        result = promotion_candidates(
            contrasts, adjudications=SoundAdjudications(),
            substrate_sources={"qs-x": "d" * 64})
        self.assertEqual(len(result["promoted"]), 1)
        candidate = result["promoted"][0]
        self.assertEqual(candidate["substrate_id"], "qs-x")
        self.assertEqual(candidate["defect_class"], "hash_mismatch")
        self.assertEqual(candidate["caught_by"], "tuple-a")
        self.assertEqual(candidate["sweeps"], [1, 2])

    def test_single_sweep_separation_is_withheld(self):
        result = promotion_candidates(
            [contrast(1, [case()])], adjudications=SoundAdjudications(),
            substrate_sources={"qs-x": "d" * 64})
        self.assertEqual(result["promoted"], [])
        self.assertIn("reproduction", result["withheld"][0]["reason"])

    def test_direction_flip_is_withheld_as_instability(self):
        contrasts = [contrast(1, [case(caught_by="a")]),
                     contrast(2, [case(caught_by="b")])]
        result = promotion_candidates(
            contrasts, adjudications=SoundAdjudications(),
            substrate_sources={"qs-x": "d" * 64})
        self.assertEqual(result["promoted"], [])
        self.assertIn("direction", result["withheld"][0]["reason"])

    def test_unadjudicated_control_is_withheld(self):
        contrasts = [contrast(1, [case()]), contrast(2, [case()])]
        result = promotion_candidates(
            contrasts, adjudications=UnexaminedAdjudications(),
            substrate_sources={"qs-x": "d" * 64})
        self.assertEqual(result["promoted"], [])
        self.assertIn("control", result["withheld"][0]["reason"])

    def test_unknown_operator_is_withheld(self):
        contrasts = [contrast(1, [case(cls="not_an_operator")]),
                     contrast(2, [case(cls="not_an_operator")])]
        result = promotion_candidates(
            contrasts, adjudications=SoundAdjudications(),
            substrate_sources={"qs-x": "d" * 64})
        self.assertEqual(result["promoted"], [])
        self.assertIn("operator", result["withheld"][0]["reason"])


if __name__ == "__main__":
    unittest.main()
