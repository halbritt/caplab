"""Pure retrieval metrics for the Cairn retrieval evaluation harness.

Contract (see docs/retrieval/metrics-contract.md):

- Every rate is a Rate object {"numerator", "denominator", "value"} with exact
  integers; "value" is a display float, or None when the denominator is 0.
  Averages of per-attempt rates are exact Fractions in the same shape plus
  "count". nDCG is irrational, so it is reported as a float mean only and never
  used for identity.
- precision@k always divides by k, even when fewer than k items were returned.
- Only `ok` attempts are scorable. A failed, timed-out, interrupted or
  not-started attempt is never a successful abstention: it is excluded from
  conditional metrics and counts against every all-assignment measure.
- Empty-gold controls get false-positive and forbidden-hit rates, never
  precision or recall.
- Exposure metrics use `delivered_ids` only when the adapter observed delivery.
- Seeds are repeated runs of the same case, not new cases: case-level figures
  average seeds within a query first.
"""
from __future__ import annotations

from fractions import Fraction
import math
from typing import Iterable

from caplab.retrieval.contracts import (ANSWERABLE, FAILURE_STATUSES, ContractError, assignments,
                                        validate_attempt)

SUMMARY_SCHEMA = "caplab-retrieval-summary/1"


def rate(numerator: int, denominator: int) -> dict:
    return {"numerator": numerator, "denominator": denominator,
            "value": None if denominator == 0 else numerator / denominator}


def mean(values: Iterable[Fraction]) -> dict:
    values = list(values)
    if not values:
        return {"numerator": 0, "denominator": 0, "value": None, "count": 0}
    total = sum(values, Fraction(0)) / len(values)
    return {"numerator": total.numerator, "denominator": total.denominator, "value": float(total), "count": len(values)}


def float_mean(values: Iterable[float]) -> dict:
    values = list(values)
    return {"value": math.fsum(values) / len(values) if values else None, "count": len(values)}


def _dcg(flags: list[bool]) -> float:
    return math.fsum(1 / math.log2(i + 2) for i, hit in enumerate(flags) if hit)


def score_attempt(query: dict, attempt: dict, cutoffs: list[int]) -> dict:
    """Score one normalized attempt for one normalized query at each cutoff.

    Returns scorable False (and no metric values) for any non-ok attempt.
    """
    if attempt["query_id"] != query["id"]:
        raise ContractError("INCONSISTENT_ASSIGNMENT", "/query_id", "attempt does not belong to this query")
    relevant, forbidden = set(query["relevant_ids"]), set(query["forbidden_ids"])
    answerable = bool(relevant)
    out = {"assignment_id": attempt["assignment_id"], "arm": attempt["arm"], "query_id": query["id"],
           "seed": attempt["seed"], "stratum": query["stratum"], "answerable": answerable,
           "status": attempt["status"], "scorable": attempt["status"] == "ok", "cutoffs": {}, "exposure": None}
    if not out["scorable"]:
        out["failure"] = (attempt.get("error") or {}).get("code") if attempt["status"] in FAILURE_STATUSES else None
        return out
    ranked = attempt["ranked_ids"]
    first = next((i + 1 for i, rid in enumerate(ranked) if rid in relevant), None)
    for k in cutoffs:
        top = ranked[:k]
        hits = sum(1 for rid in top if rid in relevant)
        forbidden_hits = sum(1 for rid in top if rid in forbidden)
        entry = {"returned": len(top), "forbidden_hits": forbidden_hits, "forbidden_hit": forbidden_hits > 0}
        if answerable:
            ideal = _dcg([True] * min(len(relevant), k))
            entry.update(hits=hits, precision=rate(hits, k), recall=rate(hits, len(relevant)), success=hits > 0,
                         reciprocal_rank=rate(1, first) if first is not None and first <= k else rate(0, 1),
                         ndcg=_dcg([rid in relevant for rid in top]) / ideal)
        else:
            entry["false_positive"] = len(top) > 0
        out["cutoffs"][str(k)] = entry
    delivered = attempt.get("delivered_ids")
    if delivered is not None:
        exposed = set(delivered)
        out["exposure"] = {"delivered": len(exposed), "forbidden_delivered": len(exposed & forbidden)}
        if answerable:
            out["exposure"]["recall"] = rate(len(exposed & relevant), len(relevant))
        else:
            out["exposure"]["false_positive"] = len(exposed) > 0
    return out


def _nearest_rank(values: list[int], p: float):
    if not values:
        return None
    ordered = sorted(values)
    return ordered[max(0, math.ceil(p * len(ordered)) - 1)]


def _arm_summary(spec, arm, attempts_by_id, queries):
    roster = [r for r in assignments(spec) if r["arm"] == arm]
    status_counts = {s: 0 for s in ("ok", *FAILURE_STATUSES, "not_started", "missing")}
    scored = []
    for row in roster:
        attempt = attempts_by_id.get(row["assignment_id"])
        if attempt is None:
            status_counts["missing"] += 1
            continue
        status_counts[attempt["status"]] += 1
        scored.append(score_attempt(queries[row["query_id"]], attempt, spec["cutoffs"]))
    planned = len(roster)
    ok = [s for s in scored if s["scorable"]]
    coverage = {"planned": planned, "attempted": planned - status_counts["missing"] - status_counts["not_started"],
                "scorable": len(ok), "failures": sum(status_counts[s] for s in FAILURE_STATUSES),
                "not_started": status_counts["not_started"], "missing": status_counts["missing"],
                "by_status": status_counts, "scorable_rate": rate(len(ok), planned)}

    answer_planned = sum(1 for r in roster if queries[r["query_id"]]["relevant_ids"])
    control_planned = planned - answer_planned
    forbidden_planned = sum(1 for r in roster if queries[r["query_id"]]["forbidden_ids"])
    answer_ok = [s for s in ok if s["answerable"]]
    control_ok = [s for s in ok if not s["answerable"]]
    forbidden_ok = [s for s in ok if queries[s["query_id"]]["forbidden_ids"]]

    per_cutoff = {}
    for k in map(str, spec["cutoffs"]):
        def frac(field, rows):
            return [Fraction(r["cutoffs"][k][field]["numerator"], r["cutoffs"][k][field]["denominator"]) for r in rows]
        success = sum(1 for s in answer_ok if s["cutoffs"][k]["success"])
        fp = sum(1 for s in control_ok if s["cutoffs"][k]["false_positive"])
        fhit = sum(1 for s in forbidden_ok if s["cutoffs"][k]["forbidden_hit"])
        # Case level: average seeds within each answerable query, then across queries.
        by_query = {}
        for s in answer_ok:
            by_query.setdefault(s["query_id"], []).append(s)
        answer_queries = [q for q in spec["queries"] if q["relevant_ids"]]
        per_cutoff[k] = {
            "answerable": {
                "conditional": {"precision": mean(frac("precision", answer_ok)), "recall": mean(frac("recall", answer_ok)),
                                "mrr": mean(frac("reciprocal_rank", answer_ok)),
                                "ndcg": float_mean(s["cutoffs"][k]["ndcg"] for s in answer_ok),
                                "success": rate(success, len(answer_ok))},
                # Unscorable assignments have no observed recall. Report the
                # zero-imputed lower bound and one-imputed upper bound with the
                # unscored count; neither bound is observed recall.
                "all_assignments": {
                    "unscored": answer_planned - len(answer_ok),
                    "recall_lower_bound_zero_imputed": mean(frac("recall", answer_ok) + [Fraction(0)] * (answer_planned - len(answer_ok))),
                    "recall_upper_bound_one_imputed": mean(frac("recall", answer_ok) + [Fraction(1)] * (answer_planned - len(answer_ok))),
                    "success_lower_bound": rate(success, answer_planned),
                    "success_upper_bound": rate(success + answer_planned - len(answer_ok), answer_planned)},
                "case_level": {
                    "recall": mean(sum(frac("recall", rows), Fraction(0)) / len(rows) for rows in by_query.values()),
                    "queries_scored": rate(len(by_query), len(answer_queries))},
            },
            "controls": {
                "false_positive_rate": rate(fp, len(control_ok)),
                "clean_all_assignments": rate(len(control_ok) - fp, control_planned),
            },
            "forbidden": {
                "hit_rate": rate(fhit, len(forbidden_ok)),
                "clean_all_assignments": rate(len(forbidden_ok) - fhit, forbidden_planned),
            },
        }
    observed = [s for s in ok if s["exposure"] is not None]
    exposure = {"observed": rate(len(observed), len(ok)),
                "recall": mean(Fraction(s["exposure"]["recall"]["numerator"], s["exposure"]["recall"]["denominator"])
                               for s in observed if s["answerable"]),
                "forbidden_delivered": rate(sum(1 for s in observed if s["exposure"]["forbidden_delivered"]),
                                            sum(1 for s in observed if queries[s["query_id"]]["forbidden_ids"])),
                "control_false_positive": rate(sum(1 for s in observed if not s["answerable"] and s["exposure"]["false_positive"]),
                                               sum(1 for s in observed if not s["answerable"]))}
    latencies = [attempts_by_id[s["assignment_id"]]["latency_ns"] for s in ok]
    latency = {"count": len(latencies), "median_ns": _nearest_rank(latencies, 0.5),
               "p95_ns": _nearest_rank(latencies, 0.95), "max_ns": max(latencies) if latencies else None}
    strata = {}
    for s in scored:
        strata.setdefault(s["stratum"], {"planned": 0, "scorable": 0})
        strata[s["stratum"]]["scorable"] += s["scorable"]
    for r in roster:
        strata.setdefault(queries[r["query_id"]]["stratum"], {"planned": 0, "scorable": 0})["planned"] += 1
    return {"coverage": coverage, "planned_by_kind": {"answerable": answer_planned, "controls": control_planned,
                                                     "with_forbidden": forbidden_planned},
            "strata": strata, "cutoffs": per_cutoff, "exposure": exposure, "latency_ok": latency,
            "attempts": scored}


def summarize(spec: dict, attempts: list) -> dict:
    """Summarize validated attempts for a normalized spec, per arm.

    Every attempt is validated against the spec; duplicate assignment IDs fail
    closed. Arms are never pooled. Missing roster entries are counted, not
    dropped. No pass threshold or qualification judgment is applied.
    """
    queries = {q["id"]: q for q in spec["queries"]}
    if not isinstance(attempts, list):
        raise ContractError("TYPE", "/attempts", "must be an array of attempt objects")
    by_id = {}
    for i, raw in enumerate(attempts):
        try:
            attempt = validate_attempt(raw, spec)
        except ContractError as exc:
            raise ContractError(exc.code, f"/attempts/{i}{exc.path}", exc.message) from exc
        if attempt["assignment_id"] in by_id:
            raise ContractError("DUPLICATE_ID", f"/attempts/{i}/assignment_id", "each assignment has at most one attempt")
        by_id[attempt["assignment_id"]] = attempt
    return {"schema_version": SUMMARY_SCHEMA, "experiment_id": spec["experiment_id"], "cutoffs": spec["cutoffs"],
            "seeds": spec["seeds"], "seeds_are_repetitions": len(spec["seeds"]) > 1,
            "arms": {arm["id"]: _arm_summary(spec, arm["id"], by_id, queries) for arm in spec["arms"]}}
