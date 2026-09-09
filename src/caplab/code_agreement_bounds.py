"""Conservative simultaneous agreement bounds, conditional on IID complete pairs."""

from fractions import Fraction
import math

from caplab.code_agreement import build_code_agreement_report


def _endpoints(lower: Fraction, upper: Fraction) -> list[float]:
    """Round exact rational endpoints outward when encoding JSON numbers."""
    lo, hi = float(lower), float(upper)
    if Fraction(lo) > lower:
        lo = math.nextafter(lo, -math.inf)
    if Fraction(hi) < upper:
        hi = math.nextafter(hi, math.inf)
    return [lo, hi]


def _row_bounds(row: dict, confidence: float, family_size: int) -> dict:
    count = row["complete_pairs"]
    result = {"world": row["world"], "code_id": row["code_id"],
              "complete_pairs": count, "epsilon": None,
              "observed_agreement": None, "coder_positive_rates": None,
              "chance_agreement": None, "kappa": None,
              "undefined_population_kappa_not_excluded": True,
              "bounds_unavailable_reason": "no-complete-pairs"}
    if not count:
        return result
    # Three two-sided bounds per declared row; no independence across rows needed.
    epsilon = math.nextafter(math.sqrt(
        (math.log(6 * family_size) - math.log1p(-confidence)) / (2 * count)), math.inf)
    radius = Fraction(epsilon)
    joint = row["joint_counts"]
    rates = [Fraction(joint["00"] + joint["11"], count),
             Fraction(joint["10"] + joint["11"], count),
             Fraction(joint["01"] + joint["11"], count)]
    observed, a, b = [(max(Fraction(0), p - radius), min(Fraction(1), p + radius)) for p in rates]
    corners = [x * y + (1 - x) * (1 - y) for x in a for y in b]
    chance_low, chance_high = min(corners), max(corners)
    lower = (Fraction(-1) if chance_high == 1 else
             max(Fraction(-1), (observed[0] - chance_high) / (1 - chance_high)))
    upper = min(Fraction(1), (observed[1] - chance_low) / (1 - chance_low))
    result.update(epsilon=epsilon, observed_agreement=_endpoints(*observed),
                  coder_positive_rates=[_endpoints(*a), _endpoints(*b)],
                  chance_agreement=_endpoints(chance_low, chance_high),
                  kappa=_endpoints(lower, upper),
                  undefined_population_kappa_not_excluded=chance_high == 1,
                  bounds_unavailable_reason=None)
    return result


def build_iid_agreement_bounds(document: object, *, confidence: float) -> dict:
    """Report conditional bounds; the caller must establish sampling assumptions.

    Complete pairs must be IID within each world/code, with outcome-independent
    sample size/selection. Bounds target that complete-pair population, not missing
    episodes. Repeated actions within an episode are not independent slots.
    """
    if type(confidence) not in (int, float) or not 0 < confidence < 1:
        raise ValueError("confidence must be a finite number strictly between zero and one")
    agreement = build_code_agreement_report(document)
    size = len(agreement["codes"])
    return {
        "schema_version": "caplab-code-agreement-bounds-report/1",
        "method": "hoeffding-three-proportions-union-bound/1",
        "confidence": confidence, "family_size": size,
        "agreement": agreement,
        "bounds": [_row_bounds(row, confidence, size) for row in agreement["codes"]],
        "interpretation": (
            "simultaneous conservative bounds for defined population kappa, conditional on "
            "IID complete episode pairs within each world/code and outcome-independent sampling; "
            "all declared rows count in the family; no independence across rows is required; "
            "does not cover missing episodes, clustered or adaptively selected data, repeated "
            "looks, or multiple separately generated reports; assumptions are not verified; "
            "does not establish accuracy, blinding, qualification or study readiness; "
            "undefined point estimates remain undefined; no threshold is applied"),
    }
