"""Matched comparison between two bindings measured on the same cases.

Prospective runs must establish common frozen conditions and a reconciled
population; a shared seed or case ID alone cannot prove this. Historical
unversioned runs retain their original intersection-based interpretation.
Verified common conditions permit a *paired* comparison,
which is both more sensitive and more honest than comparing two independent
rates: it conditions on the cases, so a difference in case difficulty cannot
masquerade as a difference in capability.

The test is the exact binomial (sign) test over discordant pairs — McNemar's
test without the chi-square approximation, which small samples do not earn.
Concordant pairs (both caught, both missed) carry no information about which
subject is better and are excluded from the test by construction, though
they are reported so the reader can see how much of the sample was
uninformative.
"""

from __future__ import annotations

import json
import hashlib
import math
import os

from .scoring import completed
from . import run_spec


_SUBJECT_FIELDS = {"backend", "declaration_sha256", "declared_lanes"}
_COMMON_FIELDS = {
    "plan", "case_selection", "sweep_seed", "partition", "per_operator", "max_cases",
    "timeout", "abort_after_empty", "replicates", "mutant_replicates", "requested_workers",
    "environment", "sandbox_available", "base_registry_sha256", "response_validation",
    "anchor_matching", "pair_validation", "instrument_sources", "python_version",
}


def _frozen_rows(run_dir: str, summary: dict, frozen: dict) -> tuple[dict, str, set]:
    """Reconcile a prospective population without dropping missing observations."""
    spec = frozen["spec"]
    for field in ("backend", "sweep_seed", "partition", "case_selection", "environment",
                  "replicates", "base_registry_sha256", "response_validation",
                  "anchor_matching", "pair_validation"):
        if summary.get(field) != spec[field]:
            raise ValueError(f"{run_dir}: summary differs from frozen {field}")
    planned = {}
    for assignment in spec["plan"]:
        case = assignment["case"]
        key = f"{case['substrate_id']}:{case['operator']}:{case['seed']}"
        if key in planned:
            raise ValueError(f"{run_dir}: duplicate planned case")
        planned[key] = assignment
    with open(os.path.join(run_dir, "results.jsonl"), "rb") as raw:
        content = raw.read()
    seen, measured, unavailable = set(), set(), 0
    paired = {}
    for line in content.splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        key = row.get("dispatch_id")
        if key not in planned or key in seen:
            raise ValueError(f"{run_dir}: unexpected or duplicate result row")
        seen.add(key)
        assignment = planned[key]
        case = assignment["case"]
        if (row.get("run_spec_sha256") != frozen["sha256"]
                or row.get("backend_measured") != spec["backend"]
                or row.get("substrate_id") != case["substrate_id"]
                or row.get("defect_class") != case["operator"]
                or row.get("anchor") is not assignment["anchor"]):
            raise ValueError(f"{run_dir}: row identity differs from frozen plan")
        for field in ("response_validation", "anchor_matching", "pair_validation"):
            if row.get(field) != spec[field]:
                raise ValueError(f"{run_dir}: row differs from frozen {field}")
        if row.get("usable") is False:
            if (not str(row.get("error", "")).startswith("not applicable:")
                    or row.get("control_attempts") or row.get("mutant_attempts")):
                raise ValueError(f"{run_dir}: incomplete planned case")
            unavailable += 1
            continue
        if (row.get("usable") is not True or row.get("control_json_valid") is not True
                or row.get("mutant_json_valid") is not True
                or type(row.get("caught")) is not bool or type(row.get("false_alarm")) is not bool
                # iso-v1 rows inherit their environment from the frozen run;
                # the tree-v1 producer additionally stamps it on every row.
                or row.get("environment", "iso-v1") != spec["environment"]):
            raise ValueError(f"{run_dir}: incomplete or invalid measured case")
        measured.add(key)
        if not assignment["anchor"]:
            paired[key] = row
    if seen != set(planned):
        raise ValueError(f"{run_dir}: missing planned result rows")
    counts = {"pairs_planned": len(planned), "pairs_usable": len(measured),
              "pairs_missing": 0, "pairs_incomplete": 0,
              "pairs_not_applicable": unavailable, "pairs_discarded": unavailable}
    for field, expected in counts.items():
        if type(summary.get(field)) is not int or summary[field] != expected:
            raise ValueError(f"{run_dir}: summary {field} disagrees with retained population")
    return paired, hashlib.sha256(content).hexdigest(), measured


def _comparison_inputs(run_a: str, run_b: str) -> tuple[dict, dict, dict | None]:
    summaries = []
    for run in (run_a, run_b):
        with open(os.path.join(run, "summary.json"), encoding="utf-8") as f:
            summaries.append(json.load(f))
    versioned = ["run_spec_sha256" in summary or os.path.exists(os.path.join(run, run_spec.FILENAME))
                 for run, summary in zip((run_a, run_b), summaries)]
    if not any(versioned):
        return _rows(run_a), _rows(run_b), None
    if not all(versioned):
        raise ValueError("cannot mix frozen and historical comparison evidence")
    frozen = [run_spec.read(run) for run in (run_a, run_b)]
    conditions = []
    for summary, document in zip(summaries, frozen):
        spec = document["spec"]
        if summary.get("run_spec_sha256") != document["sha256"]:
            raise ValueError("summary does not identify its frozen run specification")
        if not (_SUBJECT_FIELDS | _COMMON_FIELDS) <= spec.keys():
            raise ValueError("incomplete frozen comparison conditions")
        if spec["case_selection"] not in ("seeded-draw", "profile-remeasurement",
                                           "targeted-reproduction", "admission-gate"):
            raise ValueError("unknown case selection in comparison conditions")
        conditions.append({key: value for key, value in spec.items() if key not in _SUBJECT_FIELDS})
    condition_hashes = [run_spec.digest(condition) for condition in conditions]
    if condition_hashes[0] != condition_hashes[1] or summaries[0].get("instrument") != summaries[1].get("instrument"):
        differing = sorted(key for key in conditions[0].keys() | conditions[1].keys()
                           if key not in conditions[0] or key not in conditions[1]
                           or run_spec.digest(conditions[0][key]) != run_spec.digest(conditions[1][key]))
        raise ValueError("different comparison conditions: " + ", ".join(differing or ["instrument"]))
    a, sha_a, measured_a = _frozen_rows(run_a, summaries[0], frozen[0])
    b, sha_b, measured_b = _frozen_rows(run_b, summaries[1], frozen[1])
    if measured_a != measured_b:
        raise ValueError("different measurable populations under common comparison conditions")
    for key in a:
        for field in ("defect_anchor", "calibration_profile", "base_manifest_digest",
                      "base_source", "operator_version", "review_preamble"):
            if a[key].get(field) != b[key].get(field):
                raise ValueError(f"case {key}: different measured {field}")
    basis = {"record": "caplab-paired-conditions/1",
             "common_conditions_sha256": condition_hashes[0],
             "planned_cases": len(conditions[0]["plan"]), "paired_cases": len(a),
             "not_applicable_cases": summaries[0]["pairs_not_applicable"],
             "anchor_cases": sum(item["anchor"] for item in conditions[0]["plan"]),
             "case_selection": conditions[0]["case_selection"],
             "sweep_seed": conditions[0]["sweep_seed"],
             "subjects": [{**{key: doc["spec"][key] for key in sorted(_SUBJECT_FIELDS)},
                           "run_spec_sha256": doc["sha256"], "results_sha256": sha}
                          for doc, sha in zip(frozen, (sha_a, sha_b))],
             "interpretation": "Common recorded conditions only; native Binding identity, semantic validity, and placement are not established."}
    return a, b, basis


def _rows(run_dir: str) -> dict[str, dict]:
    path = os.path.join(run_dir, "results.jsonl")
    out = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            if "run_spec_sha256" in row:
                raise ValueError("frozen result row cannot use the historical comparison path")
            if not row.get("usable"):
                continue
            if not (row.get("mutant_json_valid") and row.get("control_json_valid")):
                # A pair with an unmeasured arm is not a measurement of the
                # subject; pairing it against the other subject's real answer
                # would manufacture a discordance the subject never produced.
                continue
            if row.get("anchor"):
                # Anchor rows measure the instrument, not the corpus.
                continue
            out[row["dispatch_id"]] = row
    return out


def _binom_two_sided(k: int, n: int, p: float = 0.5) -> float:
    """Exact two-sided binomial p-value (equal-tail doubling for p=0.5)."""
    if n == 0:
        return 1.0

    def pmf(i):
        return math.comb(n, i) * p ** i * (1 - p) ** (n - i)

    tail = sum(pmf(i) for i in range(0, k + 1)) if k <= n / 2 else \
        sum(pmf(i) for i in range(k, n + 1))
    return min(1.0, 2 * tail)


def paired_comparison(run_a: str, run_b: str, label_a: str = "",
                      label_b: str = "", adjudications=None,
                      substrate_sources: dict | None = None) -> dict:
    """Compare two completed runs on the cases they both measured.

    False-alarm pairing is conditioned on control adjudications for the same
    reason the scorer is: a pair whose control is established defective
    cannot say which subject erred, because refusing it was correct.
    `substrate_sources` maps a pool-run row's substrate_id to the striatum
    dispatch its control came from, since adjudications key by the latter.
    """
    from .adjudication import Adjudications

    if adjudications is None:
        adjudications = Adjudications([])
    for run in (run_a, run_b):
        if not completed(run):
            raise ValueError(f"{run}: not a completed run; refusing to compare")
    a, b, basis = _comparison_inputs(run_a, run_b)
    shared = sorted(set(a) & set(b))

    a_only_caught = b_only_caught = both = neither = 0
    a_alarms = b_alarms = 0
    a_only_alarm = b_only_alarm = 0
    defective_controls = unaudited_alarm_pairs = 0
    per_class: dict[str, dict] = {}
    discordant_cases: list[dict] = []
    for dispatch in shared:
        ra, rb = a[dispatch], b[dispatch]
        ca, cb = bool(ra.get("caught")), bool(rb.get("caught"))
        if ca and cb:
            both += 1
        elif ca:
            a_only_caught += 1
        elif cb:
            b_only_caught += 1
        else:
            neither += 1
        if ca != cb:
            # Which cases separated the pair, not only how many: the
            # promotion gate for the discrimination corpus needs the ids.
            discordant_cases.append({
                "dispatch_id": dispatch,
                "substrate_id": ra.get("substrate_id"),
                "defect_class": ra.get("defect_class") or "(unknown)",
                # The prompt profile travels with the cell so the promotion
                # gate can quarantine contracts later found contaminated
                # (v1-changeset, per the 2026-08-21 OOM postmortem).
                "calibration_profile": ra.get("calibration_profile"),
                "caught_by": "a" if ca else "b"})
        control_key = ((substrate_sources or {}).get(ra.get("substrate_id"))
                       or dispatch)
        if adjudications.is_defective(control_key):
            defective_controls += 1
            fa = fb = False
        else:
            fa, fb = bool(ra.get("false_alarm")), bool(rb.get("false_alarm"))
            if adjudications.disposition(control_key) == "unadjudicated" and (fa or fb):
                unaudited_alarm_pairs += 1
        a_alarms += fa
        b_alarms += fb
        # A false alarm is a refusal of a control arm the other subject
        # cleared. Discrimination is catch minus false alarm, so a subject
        # that catches well while refusing sound work is not the better
        # reviewer -- and a catch-rate test alone cannot see that.
        if fa and not fb:
            a_only_alarm += 1
        elif fb and not fa:
            b_only_alarm += 1
        cell = per_class.setdefault(ra.get("defect_class") or "(unknown)",
                                    {"n": 0, "a": 0, "b": 0})
        cell["n"] += 1
        cell["a"] += int(ca)
        cell["b"] += int(cb)

    discordant = a_only_caught + b_only_caught
    p_value = _binom_two_sided(min(a_only_caught, b_only_caught), discordant)
    alarm_discordant = a_only_alarm + b_only_alarm
    alarm_p = _binom_two_sided(min(a_only_alarm, b_only_alarm), alarm_discordant)
    n = len(shared)
    result = {
        "a": label_a or os.path.basename(run_a),
        "b": label_b or os.path.basename(run_b),
        "shared_cases": n,
        "a_only_caught": a_only_caught,
        "b_only_caught": b_only_caught,
        "both_caught": both,
        "neither_caught": neither,
        "discordant_pairs": discordant,
        "uninformative_pairs": both + neither,
        "a_catch_rate": (both + a_only_caught) / n if n else None,
        "b_catch_rate": (both + b_only_caught) / n if n else None,
        "a_false_alarms": a_alarms,
        "b_false_alarms": b_alarms,
        "sign_test_p": p_value,
        "significant_at_05": p_value < 0.05,
        "a_only_false_alarm": a_only_alarm,
        "b_only_false_alarm": b_only_alarm,
        "false_alarm_discordant_pairs": alarm_discordant,
        "false_alarm_sign_test_p": alarm_p,
        "false_alarm_significant_at_05": alarm_p < 0.05,
        "false_alarm_defective_controls_excluded": defective_controls,
        "false_alarm_unaudited_pairs": unaudited_alarm_pairs,
        "false_alarm_audit_status": (
            "established" if unaudited_alarm_pairs == 0
            else "contains-unaudited-refusals"),
        "a_discrimination": ((both + a_only_caught) - a_alarms) / n if n else None,
        "b_discrimination": ((both + b_only_caught) - b_alarms) / n if n else None,
        "by_defect_class": {k: dict(v) for k, v in sorted(per_class.items())},
        "discordant_cases": discordant_cases,
        "reading": (
            "no shared cases; not a matched comparison" if not n else
            f"catch: {discordant} of {n} shared cases discriminate, exact "
            f"sign test p={p_value:.3f}"
            + ("" if p_value < 0.05 else " (not established)")
            + f"; false alarms: {alarm_discordant} discordant, p="
            f"{alarm_p:.3f}"
            + ("" if alarm_p < 0.05 else " (not established)")
            + (f", {unaudited_alarm_pairs} on unaudited controls"
               if unaudited_alarm_pairs else "")),
    }
    if basis is not None:
        result["comparison_basis"] = basis
        result["case_selection"] = basis["case_selection"]
        result["sweep_seed"] = basis["sweep_seed"]
        if basis["case_selection"] in {"targeted-reproduction", "admission-gate"}:
            for field in ("sign_test_p", "significant_at_05", "false_alarm_sign_test_p",
                          "false_alarm_significant_at_05"):
                result[field] = None
            result["reading"] = "outcome-selected cells: descriptive paired counts only; no discovery test"
        result["reading"] += "; common recorded conditions verified; no reviewer ranking or placement decision"
    else:
        result["comparison_basis"] = {
            "record": "caplab-paired-conditions/1", "status": "unverified-historical",
            "interpretation": "Historical case-ID intersection; common experiment conditions were not verified."}
        result["reading"] += "; historical conditions unverified; not evidence for reviewer ranking"
    return result


def annotate_from_summaries(contrast: dict, run_a: str, run_b: str) -> dict:
    """Stamp the contrast with what its runs' summaries establish about it.

    The sweep seed: a contrast is matched only within one seed, and the
    annotation is what lets the promotion gate count distinct-sweep
    reproductions. The selection mode: on a targeted-reproduction run the
    cases were chosen because they separated before, so the sign test stops
    being a discovery statistic — the honest reading of such a contrast is
    the reproduction rate, and the document must say so itself rather than
    rely on every reader knowing the run's history.
    """
    seeds, selections = set(), set()
    for run in (run_a, run_b):
        with open(os.path.join(run, "summary.json"), encoding="utf-8") as f:
            summary = json.load(f)
        seeds.add(summary.get("sweep_seed"))
        selections.add(summary.get("case_selection"))
    contrast["sweep_seed"] = seeds.pop() if len(seeds) == 1 else None
    if contrast["sweep_seed"] is None:
        contrast["reading"] += "; WARNING: runs carry different sweep seeds"
    if "targeted-reproduction" in selections:
        contrast["case_selection"] = "targeted-reproduction"
        contrast["reading"] += (
            "; cases were selected on prior outcome (targeted reproduction) "
            "— the sign test is not a discovery statistic here; read the "
            "per-cell reproduction against the promotion gate instead")
    return contrast
