"""Paired comparison of two verified retrieval runs.

`compare_runs` first verifies both runs (every retained byte, every attempt, the
recomputed report), then aligns them by identical `(query_id, seed)` assignments
under identical corpus, label, seed, cutoff and timeout pins. A mismatch raises
`ArtifactError` with code `INCOMPATIBLE_RUNS`; nothing is dropped to force a
match. Assignments that are not scorable in both arms stay visible as unpaired
and are never treated as successes.

Seeds repeat a case, so uncertainty is case-level: seeds are averaged within a
query before deltas are aggregated across queries. Rational metrics keep exact
numerators and denominators; nDCG is a float mean. All deltas are right minus
left. No pass threshold or significance rule is applied; the sign test and the
t interval are descriptive and assume nothing about how cases were chosen.

Unscorable assignments are handled two ways, kept apart. Complete-pair
conditional estimates use only assignments scorable in both arms. The
all-roster sensitivity covers every planned answerable assignment: each arm's
mean recall is bounded by imputing 0 (lower) or 1 (upper) for its unscorable
assignments, and the delta is bounded by [right lower - left upper,
right upper - left lower]. The difference of the two zero-imputed means is only
one imputation scenario; it is not a bound on the delta.
"""
from __future__ import annotations

import math
import os
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable

from caplab.retrieval.artifacts import ArtifactError, verify_run
from caplab.retrieval.report import COMPARISON_SCHEMA

MAX_LISTED = 200
RATIONAL_METRICS = ("recall", "precision", "reciprocal_rank", "success")
# Two-sided 95% Student t critical values. Above df 30 the value for the largest tabulated df at or below
# the actual df is used, which is slightly conservative, so a stated t interval is never narrower than a true one.
_T_975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228, 11: 2.201,
          12: 2.179, 13: 2.160, 14: 2.145, 15: 2.131, 16: 2.120, 17: 2.110, 18: 2.101, 19: 2.093, 20: 2.086,
          21: 2.080, 22: 2.074, 23: 2.069, 24: 2.064, 25: 2.060, 26: 2.056, 27: 2.052, 28: 2.048, 29: 2.045,
          30: 2.042, 40: 2.021, 60: 2.000, 120: 1.980}
LIMITATIONS = (
    "Deltas are observational, paired by assignment, and computed right minus left. No pass threshold or "
    "significance rule is applied, and no qualification claim follows.",
    "Seeds repeat a case. Case-level figures average seeds within a query first; assignment-level discordant "
    "counts are listed for inspection and are not independent observations.",
    "The interval is a t interval over cases (conservative critical value above 30 degrees of freedom) and the "
    "sign test ignores ties; both are descriptive and need more cases than a small fixture provides.",
    "Conditional estimates pair only assignments scorable in both arms; unpaired assignments are listed and "
    "counted. The all-roster sensitivity bounds each arm's mean recall by imputing 0 or 1 for unscorable "
    "assignments and bounds the delta by [right lower - left upper, right upper - left lower]. Neither is "
    "observed quality, and the zero-imputed delta is one scenario, not a bound.",
    "Relevance and exposure are not task completion. A better ranking does not show that an agent was helped.",
)


def compare_runs(left: Path | str, right: Path | str, *, left_arm: str | None = None,
                 right_arm: str | None = None) -> dict:
    """Compare two finished runs, or two arms of one run, after verifying their evidence."""
    left_path, right_path = Path(os.path.realpath(os.fspath(left))), Path(os.path.realpath(os.fspath(right)))
    same_run = left_path == right_path
    left_run = verify_run(left_path)
    right_run = left_run if same_run else verify_run(right_path)
    pins = _pins(left_run, right_run)
    mismatched = [name for name, pin in pins.items() if pin["required"] and not pin["equal"]]
    if mismatched:
        raise ArtifactError("INCOMPATIBLE_RUNS", "the runs do not share " + ", ".join(mismatched),
                            mismatches=mismatched)
    selection, pairs = _select_arms(left_run, right_run, left_arm, right_arm, same_run)
    comparisons = [_compare_arm(left_run, right_run, a, b) for a, b in pairs]
    return {
        "schema_version": COMPARISON_SCHEMA,
        "reviewer_context": _context(left_run, right_run, pairs, selection),
        "compatibility": {"pins": pins, "arm_selection": selection},
        "runs": [_run_row("left", left_run), _run_row("right", right_run)],
        "comparisons": comparisons,
        "limitations": list(LIMITATIONS),
    }


def _pins(left: dict, right: dict) -> dict:
    lp, rp = left["plan"], right["plan"]
    values = [
        ("schema_version", lp["spec"]["schema_version"], rp["spec"]["schema_version"], True),
        ("corpus_sha256", lp["pins"]["corpus_sha256"], rp["pins"]["corpus_sha256"], True),
        ("cases_sha256", lp["pins"]["cases_sha256"], rp["pins"]["cases_sha256"], True),
        ("seeds", lp["spec"]["seeds"], rp["spec"]["seeds"], True),
        ("cutoffs", lp["spec"]["cutoffs"], rp["spec"]["cutoffs"], True),
        ("timeout_seconds", lp["spec"]["timeout_seconds"], rp["spec"]["timeout_seconds"], True),
        ("experiment_id", lp["experiment_id"], rp["experiment_id"], False),
        ("spec_sha256", lp["pins"]["spec_sha256"], rp["pins"]["spec_sha256"], False),
    ]
    return {name: {"left": a, "right": b, "equal": a == b, "required": required} for name, a, b, required in values}


def _run_row(side: str, run: dict) -> dict:
    return {"side": side, "output": run["output"], "experiment_id": run["plan"]["experiment_id"],
            "manifest_sha256": run["manifest_sha256"], "status": run["report"]["run"]["status"],
            "spec_sha256": run["plan"]["pins"]["spec_sha256"]}


def _select_arms(left: dict, right: dict, left_arm: str | None, right_arm: str | None,
                 same_run: bool) -> tuple[dict, list[tuple[str, str]]]:
    left_arms = [arm["id"] for arm in left["spec"]["arms"]]
    right_arms = [arm["id"] for arm in right["spec"]["arms"]]
    if (left_arm is None) != (right_arm is None):
        raise ArtifactError("AMBIGUOUS_ARM", "give both left and right arm selectors, or neither")
    if left_arm is not None:
        for side, arm, available in (("left", left_arm, left_arms), ("right", right_arm, right_arms)):
            if arm not in available:
                raise ArtifactError("UNKNOWN_ARM", f"{side} run has no arm {arm!r}", available=available)
        if same_run and left_arm == right_arm:
            raise ArtifactError("SAME_ARM", "an arm cannot be compared with itself in the same run")
        return {"mode": "selected", "left": left_arm, "right": right_arm}, [(left_arm, right_arm)]
    if same_run:
        raise ArtifactError("AMBIGUOUS_ARM", "comparing a run with itself needs two different arm selectors",
                            available=left_arms)
    if len(left_arms) == 1 and len(right_arms) == 1:
        return {"mode": "single_arm_inputs", "left": left_arms[0], "right": right_arms[0]}, [(left_arms[0], right_arms[0])]
    if set(left_arms) == set(right_arms):
        common = sorted(left_arms)
        return {"mode": "matching_arms", "arms": common}, [(arm, arm) for arm in common]
    raise ArtifactError("AMBIGUOUS_ARM", "multi-arm runs need selectors or identical arm ids",
                        left_arms=left_arms, right_arms=right_arms)


def _context(left: dict, right: dict, pairs: list[tuple[str, str]], selection: dict) -> dict:
    spec = left["spec"]
    queries = len(spec["queries"])
    return {
        "mode": selection["mode"],
        "orientation": "delta = right minus left",
        "summary": (f"Paired comparison of {', '.join(f'{a} (left) against {b} (right)' for a, b in pairs)} over "
                    f"{queries} labelled queries and {len(spec['seeds'])} seed(s), at cutoffs "
                    f"{', '.join(str(k) for k in spec['cutoffs'])}. Both runs were verified byte for byte first, and "
                    "share the same corpus, labels, seeds, cutoffs and timeout."),
        "how_to_read": [
            "Check the pairing counts first: only assignments scorable in both arms contribute to deltas.",
            "Means are over cases (queries), with seeds averaged inside each case first.",
            "A positive delta favors the right arm for every metric, including success (a hit in the top k).",
        ],
    }


# ---- pairing and statistics ------------------------------------------------------------------


def _scores(run: dict, arm: str) -> dict:
    summary = run["report"].get("summary", {})
    if summary.get("schema_version") != "caplab-retrieval-summary/1":
        raise ArtifactError("SUMMARY_UNSUPPORTED", "the retained summary has an unsupported schema")
    return {(item["query_id"], item["seed"]): item for item in summary["arms"][arm]["attempts"]}


def _state(score: dict | None) -> str:
    return "missing" if score is None else score["status"]


def _fraction(value: dict) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def _mean(values: list[Fraction]) -> dict:
    if not values:
        return {"numerator": 0, "denominator": 0, "value": None, "count": 0}
    total = sum(values, Fraction(0)) / len(values)
    return {"numerator": total.numerator, "denominator": total.denominator, "value": float(total), "count": len(values)}


def _float_mean(values: list[float]) -> dict:
    return {"numerator": None, "denominator": None, "value": math.fsum(values) / len(values) if values else None,
            "count": len(values)}


def _sign_test_p(wins: int, losses: int) -> float | None:
    n = wins + losses
    if n == 0:
        return None
    tail = sum(math.comb(n, i) for i in range(min(wins, losses) + 1))
    return float(min(Fraction(1), Fraction(2 * tail, 2 ** n)))


def _interval(deltas: list[float]) -> tuple[list[float] | None, str]:
    n = len(deltas)
    if n < 3:
        return None, "fewer than 3 cases"
    mean = math.fsum(deltas) / n
    sd = math.sqrt(math.fsum((d - mean) ** 2 for d in deltas) / (n - 1))
    df = n - 1
    half = _T_975[max(known for known in _T_975 if known <= df)] * sd / math.sqrt(n)
    return [mean - half, mean + half], "t interval over cases; descriptive only"


def _case_stats(cases: list[tuple[Any, Any, Any]], exact: bool) -> dict:
    """cases: (case, left value, right value) with seeds already averaged inside the case."""
    lefts, rights = [c[1] for c in cases], [c[2] for c in cases]
    deltas = [r - l for l, r in zip(lefts, rights)]
    eps = 0 if exact else 1e-12  # float nDCG values that differ only by rounding are ties
    wins, losses = sum(1 for d in deltas if d > eps), sum(1 for d in deltas if d < -eps)
    mean = _mean if exact else _float_mean
    interval, note = _interval([float(d) for d in deltas])
    return {"cases": len(cases), "left_mean": mean(lefts), "right_mean": mean(rights), "delta": mean(deltas),
            "right_wins": wins, "left_wins": losses, "ties": len(deltas) - wins - losses,
            "sign_test_p": _sign_test_p(wins, losses), "interval": interval, "interval_note": note}


def _listed(items: list[dict]) -> dict:
    return {"count": len(items), "assignments": items[:MAX_LISTED], "truncated": len(items) > MAX_LISTED}


def _extract(name: str) -> Callable[[dict], Any]:
    if name == "ndcg":
        return lambda entry: entry["ndcg"]
    if name == "success":
        return lambda entry: Fraction(1 if entry["success"] else 0)
    return lambda entry: _fraction(entry[name])


def _compare_arm(left: dict, right: dict, left_arm: str, right_arm: str) -> dict:
    spec = left["spec"]
    queries = {q["id"]: q for q in spec["queries"]}
    lscores, rscores = _scores(left, left_arm), _scores(right, right_arm)
    roster = [(q["id"], seed) for q in spec["queries"] for seed in spec["seeds"]]
    paired, unpaired = [], []
    counts = {"planned_pairs": len(roster), "both_scorable": 0, "left_only_scorable": 0, "right_only_scorable": 0,
              "neither_scorable": 0}
    for key in roster:
        l, r = lscores.get(key), rscores.get(key)
        l_ok, r_ok = bool(l and l["scorable"]), bool(r and r["scorable"])
        if l_ok and r_ok:
            counts["both_scorable"] += 1
            paired.append((key, l, r))
            continue
        counts["left_only_scorable" if l_ok else "right_only_scorable" if r_ok else "neither_scorable"] += 1
        unpaired.append({"query_id": key[0], "seed": key[1], "left": _state(l), "right": _state(r)})
    counts["not_both_scorable"] = len(unpaired)
    cutoffs = {}
    for k in map(str, spec["cutoffs"]):
        cutoffs[k] = _compare_cutoff(k, queries, roster, lscores, rscores, paired)
    return {"arms": {"left": left_arm, "right": right_arm},
            "pairing": {"counts": counts, "unpaired": unpaired[:MAX_LISTED], "unpaired_truncated": len(unpaired) > MAX_LISTED},
            "cutoffs": cutoffs}


def _compare_cutoff(k: str, queries: dict, roster: list, lscores: dict, rscores: dict, paired: list) -> dict:
    answerable = [(key, l, r) for key, l, r in paired if queries[key[0]]["relevant_ids"]]
    controls = [(key, l, r) for key, l, r in paired if not queries[key[0]]["relevant_ids"]]
    metrics: dict[str, dict] = {}
    for name in RATIONAL_METRICS + ("ndcg",):
        pick = _extract(name)
        by_case: dict[str, list[tuple[Any, Any]]] = {}
        for (query_id, _), l, r in answerable:
            by_case.setdefault(query_id, []).append((pick(l["cutoffs"][k]), pick(r["cutoffs"][k])))
        exact = name != "ndcg"
        cases = []
        for query_id, pairs in by_case.items():
            size = len(pairs)
            zero = Fraction(0) if exact else 0.0
            cases.append((query_id, sum((p[0] for p in pairs), zero) / size, sum((p[1] for p in pairs), zero) / size))
        metrics[name] = _case_stats(cases, exact)
    hits = {"right_hit_left_miss": [], "left_hit_right_miss": []}
    both_hit = both_miss = 0
    for (query_id, seed), l, r in answerable:
        lh, rh = l["cutoffs"][k]["success"], r["cutoffs"][k]["success"]
        if lh and rh:
            both_hit += 1
        elif not lh and not rh:
            both_miss += 1
        else:
            hits["right_hit_left_miss" if rh else "left_hit_right_miss"].append({"query_id": query_id, "seed": seed})
    exposure = [(key, _fraction(l["exposure"]["recall"]), _fraction(r["exposure"]["recall"]))
                for key, l, r in answerable if l.get("exposure") and r.get("exposure")]
    exposure_cases: dict[str, list[tuple[Fraction, Fraction]]] = {}
    for (query_id, _), a, b in exposure:
        exposure_cases.setdefault(query_id, []).append((a, b))
    exposure_stats = _case_stats([(q, sum((x for x, _ in v), Fraction(0)) / len(v), sum((y for _, y in v), Fraction(0)) / len(v))
                                  for q, v in exposure_cases.items()], True) if exposure_cases else None
    planned_answerable = [key for key in roster if queries[key[0]]["relevant_ids"]]
    return {
        "answerable": {
            "metrics": metrics,
            "discordant_hits": {**{name: _listed(items) for name, items in hits.items()}, "both_hit": both_hit,
                                "both_miss": both_miss},
            "exposure_recall": {"paired_observed_assignments": len(exposure), "stats": exposure_stats},
            "all_roster_sensitivity": _roster_sensitivity(planned_answerable, lscores, rscores, k),
        },
        "controls": {
            "false_positive": _flag_counts([(l["cutoffs"][k]["false_positive"], r["cutoffs"][k]["false_positive"])
                                            for _, l, r in controls], "fp"),
            "forbidden_hit": _flag_counts([(l["cutoffs"][k]["forbidden_hit"], r["cutoffs"][k]["forbidden_hit"])
                                           for key, l, r in paired if queries[key[0]]["forbidden_ids"]], "hit"),
        },
    }


def _exact(value: Fraction) -> dict:
    return {"numerator": value.numerator, "denominator": value.denominator, "value": float(value)}


def _roster_sensitivity(planned: list, lscores: dict, rscores: dict, k: str) -> dict:
    """Bound mean recall over every planned answerable assignment; see the module docstring."""
    def bounds(scores: dict) -> tuple[Fraction, Fraction, int]:
        observed, unscorable = Fraction(0), 0
        for key in planned:
            score = scores.get(key)
            if score and score["scorable"]:
                observed += _fraction(score["cutoffs"][k]["recall"])
            else:
                unscorable += 1
        return observed / len(planned), (observed + unscorable) / len(planned), unscorable

    note = ("Unscorable assignments are imputed 0 (lower) or 1 (upper). delta_bounds is [right lower - left upper, "
            "right upper - left lower]; the zero-imputed scenario delta is not a bound on the delta.")
    if not planned:
        return {"planned_assignments": 0, "note": note, "unscorable": {"left": 0, "right": 0}}
    (l_low, l_up, l_n), (r_low, r_up, r_n) = bounds(lscores), bounds(rscores)
    return {"planned_assignments": len(planned), "unscorable": {"left": l_n, "right": r_n},
            "left": {"lower": _exact(l_low), "upper": _exact(l_up)},
            "right": {"lower": _exact(r_low), "upper": _exact(r_up)},
            "delta_bounds": {"lower": _exact(r_low - l_up), "upper": _exact(r_up - l_low),
                             "formula": "[right_lower - left_upper, right_upper - left_lower]"},
            "zero_imputed_scenario_delta": _exact(r_low - l_low), "note": note}


def _flag_counts(flags: list[tuple[bool, bool]], word: str) -> dict:
    return {"both_clean": sum(1 for l, r in flags if not l and not r),
            f"left_{word}_only": sum(1 for l, r in flags if l and not r),
            f"right_{word}_only": sum(1 for l, r in flags if r and not l),
            f"both_{word}": sum(1 for l, r in flags if l and r), "assignments": len(flags)}
