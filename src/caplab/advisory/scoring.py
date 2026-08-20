"""Deterministic scoring over matched-pair defect-injection run directories.

One scorer for both custody classes: the historical striatum-tuner sweep
(`historical-seed`) and CAPLAB-directed advisory executions
(`caplab-advisory`) leave the same on-disk shape — a run directory holding
`results.jsonl`, `summary.json`, and retained `arms/` — and are scored by the
same code path, so a custody difference is never silently a semantics
difference.

Scoring rules, stated once:

- A run without `summary.json` was killed mid-flight and is excluded whole
  (the abort path writes no record; requiring the record is the fix).
- Only rows with `usable: true` and at least one parseable arm count.
- Anchored detection is computed ONLY by re-scoring retained mutant arms with
  the corrected anchor path (`_tuner_vendored`). Row-level `anchor_hit`
  fields recorded before the 2026-08-08 correction are parser artifacts and
  are never read. A pair whose arms were not retained contributes to verdict
  metrics but not to anchored detection, and the denominator says so.
- Rows are merged across runs by the row's own `backend_measured`. Repeated
  dispatch ids across runs are counted as repeated trials of the same case
  and reported, because unique-case coverage is the number that cannot be
  inflated by re-running.
"""

from __future__ import annotations

import collections
import glob
import hashlib
import json
import os

from ._tuner_vendored import anchor_hits, anchors_of, extract_json

MATCHED_PAIR_INSTRUMENT = "matched-pair defect injection"
SYNTHETIC_CONTRACT_INSTRUMENT = "matched-pair defect injection (synthetic contract)"
#: Both profiles produce the same on-disk shape and are scored by this same
#: code, but they measure different tasks: one renders striatum's dispatch
#: prompt, the other a stated contract. They live in separate run roots so a
#: caller must choose, and every claim records which produced it.
SCOREABLE_INSTRUMENTS = {MATCHED_PAIR_INSTRUMENT, SYNTHETIC_CONTRACT_INSTRUMENT}


def completed(run_dir: str) -> bool:
    """Whether this run reached its own end with a measurement to report.

    `summary.json` alone is NOT sufficient. The instrument writes its summary
    and THEN raises its abort, so a run killed by an account session limit
    leaves a complete-looking directory holding a truncated sample — on
    2026-08-16 that admitted a 7-pair claim for claude-fable-5-high from a
    run the vendor cut off at "You've hit your session limit". A run that
    aborted measured whatever it managed before the failure, under
    conditions it did not control, and its numbers describe the outage as
    much as the subject. Both conditions are required: the summary exists
    and it carries no abort.
    """
    summary_path = os.path.join(run_dir, "summary.json")
    if not os.path.isfile(summary_path):
        return False
    try:
        with open(summary_path, encoding="utf-8") as f:
            summary = json.load(f)
    except (OSError, json.JSONDecodeError):
        return False
    return not summary.get("aborted")


def outcome_selected(run_dir: str) -> bool:
    """Whether this run's cases were chosen for what they previously scored.

    A targeted-reproduction sweep re-measures exactly the cells that
    separated a Binding pair, so its sample is conditioned on the outcome
    under test: the subject that caught those cells before is flattered and
    the one that missed them is punished, by construction. Such a run is
    evidence for the discrimination corpus only — claim-grade scoring must
    refuse it whole, the way `completed` refuses an aborted run.
    """
    summary_path = os.path.join(run_dir, "summary.json")
    if not os.path.isfile(summary_path):
        return False
    try:
        with open(summary_path, encoding="utf-8") as f:
            summary = json.load(f)
    except (OSError, json.JSONDecodeError):
        return False
    return summary.get("case_selection") == "targeted-reproduction"


def is_matched_pair_run(run_dir: str) -> bool:
    if not completed(run_dir):
        return False
    with open(os.path.join(run_dir, "summary.json"), encoding="utf-8") as f:
        summary = json.load(f)
    return summary.get("instrument") in SCOREABLE_INSTRUMENTS


def eligible_run_dirs(runs_root: str) -> tuple[list[str], list[str]]:
    """(eligible, skipped_incomplete) among matched-pair run directories."""
    eligible, skipped = [], []
    for results in sorted(glob.glob(os.path.join(runs_root, "*", "results.jsonl"))):
        run_dir = os.path.dirname(results)
        if is_matched_pair_run(run_dir):
            eligible.append(run_dir)
        elif not completed(run_dir):
            skipped.append(run_dir)
    return eligible, skipped


def _mutant_review(run_dir: str, dispatch_id: str) -> dict | None:
    pattern = os.path.join(run_dir, "arms", dispatch_id[:12], "mutant-ws",
                           "work", "outputs", "*")
    for path in sorted(glob.glob(pattern)):
        if os.path.basename(path) == "ASSUMPTIONS.md":
            continue
        try:
            with open(path, errors="replace", encoding="utf-8") as handle:
                doc = extract_json(handle.read())
        except OSError:
            continue
        if isinstance(doc, dict):
            return doc
    return None


def _sha256_file(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def score_backends(run_dirs: list[str], adjudications=None,
                   substrate_sources: dict | None = None) -> dict[str, dict]:
    """Per-backend merged metrics over the given completed run directories.

    `adjudications` supplies what is known about each control arm. A control
    established as defective cannot measure a false alarm — refusing it is
    correct — so those pairs leave the false-alarm denominator entirely
    rather than being scored either way. Unexamined refusals are still
    counted, because the alternative lets a subject escape the metric by
    refusing everything, but their number is reported so an unexamined rate
    is never mistaken for an established one.

    `substrate_sources` maps a pool-run row's substrate_id to the striatum
    dispatch id its control came from. Adjudications key by that dispatch
    id, while pool rows key by substrate; without the mapping, a control
    proven defective still charges the reviewer that correctly refused it.
    Historical rows carry the dispatch id directly and need no mapping.
    """
    from .adjudication import Adjudications
    from .wilson import wilson

    if adjudications is None:
        adjudications = Adjudications([])

    per_backend: dict[str, dict] = {}
    run_instruments: dict[str, str] = {}
    for run_dir in run_dirs:
        results_path = os.path.join(run_dir, "results.jsonl")
        run_name = os.path.basename(run_dir)
        results_sha = _sha256_file(results_path)
        with open(os.path.join(run_dir, "summary.json"), encoding="utf-8") as f:
            run_instrument = json.load(f).get("instrument")
        run_instruments[run_dir] = run_instrument
        with open(results_path, encoding="utf-8") as f:
            rows = [json.loads(line) for line in f if line.strip()]
        for row in rows:
            if not row.get("usable"):
                continue
            if not (row.get("mutant_json_valid") and row.get("control_json_valid")):
                # A pair counts only when both arms answered. One dead arm
                # used to slip through here: a dead mutant arm scored as a
                # miss, a dead control arm as a clean clearance (four such
                # rows in sweep 20260817).
                continue
            if row.get("anchor"):
                # Anchor cases are replayed by every sweep to measure the
                # instrument. Counting them here would let one fixed subset
                # inflate a claim's distinct-defect coverage and drag its
                # rates toward whatever those twelve cases happen to do.
                stat = per_backend.setdefault(
                    row.get("backend_measured") or "(unknown)",
                    {"rows": [], "runs": {}, "dispatches": collections.Counter()})
                stat.setdefault("anchor_rows", []).append(row)
                continue
            backend = row.get("backend_measured") or "(unknown)"
            stat = per_backend.setdefault(backend, {
                "rows": [], "runs": {}, "dispatches": collections.Counter(),
            })
            stat["rows"].append((run_dir, row))
            stat["dispatches"][row.get("dispatch_id")] += 1
            entry = stat["runs"].setdefault(run_name, {
                "run": run_name, "results_sha256": results_sha, "rows_used": 0})
            entry["rows_used"] += 1
            stat.setdefault("instruments", set()).add(run_instrument)
            if row.get("calibration_profile"):
                stat.setdefault("profiles", set()).add(row["calibration_profile"])

    scored: dict[str, dict] = {}
    for backend, stat in sorted(per_backend.items()):
        rows = stat["rows"]
        n = len(rows)
        caught = sum(1 for _, r in rows if r.get("caught"))

        # False-alarm accounting, conditioned on what is known about controls.
        def _control_key(r):
            return ((substrate_sources or {}).get(r.get("substrate_id"))
                    or r.get("dispatch_id"))

        alarm_rows = [r for _, r in rows
                      if not adjudications.is_defective(_control_key(r))]
        excluded_defective = n - len(alarm_rows)
        alarms = sum(1 for r in alarm_rows if r.get("false_alarm"))
        unaudited_alarms = sum(
            1 for r in alarm_rows if r.get("false_alarm")
            and adjudications.disposition(_control_key(r)) == "unadjudicated")
        alarm_n = len(alarm_rows)

        anchored = rescored = from_rows = from_arms = 0
        for run_dir, row in rows:
            doc = _mutant_review(run_dir, row["dispatch_id"])
            if doc is not None:
                emitted = anchors_of(doc.get("findings") or [])
                from_arms += 1
            elif (run_instruments.get(run_dir) == SYNTHETIC_CONTRACT_INSTRUMENT
                  and row.get("anchors_emitted") is not None):
                # Pool runs retain no arms/, but their rows record the
                # anchors the mutant review emitted, extracted by the
                # corrected parser at run time. Historical rows carry no such
                # field and stay excluded — only their retained arms count.
                emitted = row["anchors_emitted"]
                from_rows += 1
            else:
                continue
            rescored += 1
            anchored += bool(anchor_hits(row.get("defect_anchor") or "", emitted))

        by_class: dict = collections.defaultdict(lambda: {"n": 0, "caught": 0})
        for _, row in rows:
            cell = by_class[row.get("defect_class") or "(unknown)"]
            cell["n"] += 1
            cell["caught"] += int(bool(row.get("caught")))

        metrics = {
            "n_pairs": {"value": n},
            "n_distinct_cases": {"value": len(stat["dispatches"])},
            "catch_rate": {"value": caught / n, "ci95": list(wilson(caught, n))},
            "false_alarm_rate": (
                {"value": alarms / alarm_n,
                 "ci95": list(wilson(alarms, alarm_n)),
                 "denominator": alarm_n,
                 "excluded_defective_controls": excluded_defective,
                 "unaudited_refusals": unaudited_alarms,
                 "audit_status": ("established" if unaudited_alarms == 0
                                  else "contains-unaudited-refusals")}
                if alarm_n else
                {"value": None, "denominator": 0,
                 "excluded_defective_controls": excluded_defective,
                 "unaudited_refusals": 0,
                 "audit_status": "no-measurable-controls"}),
            "discrimination": {"value": (caught / n) - (alarms / alarm_n)
                               if alarm_n else None,
                               "scale": [-1.0, 1.0]},
            "findings_per_mutant": {"value": sum(
                r.get("mutant_findings") or 0 for _, r in rows) / n},
            "json_valid_mutant": {"value": sum(
                1 for _, r in rows if r.get("mutant_json_valid")) / n},
        }
        if rescored:
            metrics["anchored_detection"] = {
                "value": anchored / rescored,
                "ci95": list(wilson(anchored, rescored)),
                "denominator": rescored,
                "basis": ("rescored-retained-arms" if not from_rows
                          else "recorded-anchors" if not from_arms
                          else "rescored-retained-arms+recorded-anchors"),
            }
        from .anchor import reliability as _anchor_reliability

        scored[backend] = {
            "backend": backend,
            "instrument_reliability": _anchor_reliability(
                stat.get("anchor_rows") or []),
            "instruments": sorted(stat.get("instruments") or []),
            "profiles": sorted(stat.get("profiles") or []),
            "metrics": metrics,
            "by_defect_class": {k: dict(v) for k, v in sorted(by_class.items())},
            "repeated_case_trials": n - len(stat["dispatches"]),
            "runs": sorted(stat["runs"].values(), key=lambda e: e["run"]),
        }
    return scored
