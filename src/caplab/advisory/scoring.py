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


def completed(run_dir: str) -> bool:
    return os.path.isfile(os.path.join(run_dir, "summary.json"))


def is_matched_pair_run(run_dir: str) -> bool:
    if not completed(run_dir):
        return False
    with open(os.path.join(run_dir, "summary.json"), encoding="utf-8") as f:
        summary = json.load(f)
    return summary.get("instrument") == MATCHED_PAIR_INSTRUMENT


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


def score_backends(run_dirs: list[str]) -> dict[str, dict]:
    """Per-backend merged metrics over the given completed run directories."""
    from .wilson import wilson

    per_backend: dict[str, dict] = {}
    for run_dir in run_dirs:
        results_path = os.path.join(run_dir, "results.jsonl")
        run_name = os.path.basename(run_dir)
        results_sha = _sha256_file(results_path)
        with open(results_path, encoding="utf-8") as f:
            rows = [json.loads(line) for line in f if line.strip()]
        for row in rows:
            if not row.get("usable"):
                continue
            if not (row.get("mutant_json_valid") or row.get("control_json_valid")):
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

    scored: dict[str, dict] = {}
    for backend, stat in sorted(per_backend.items()):
        rows = stat["rows"]
        n = len(rows)
        caught = sum(1 for _, r in rows if r.get("caught"))
        alarms = sum(1 for _, r in rows if r.get("false_alarm"))

        anchored = rescored = 0
        for run_dir, row in rows:
            doc = _mutant_review(run_dir, row["dispatch_id"])
            if doc is None:
                continue
            rescored += 1
            emitted = anchors_of(doc.get("findings") or [])
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
            "false_alarm_rate": {"value": alarms / n, "ci95": list(wilson(alarms, n))},
            "discrimination": {"value": (caught - alarms) / n,
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
                "basis": "rescored-retained-arms",
            }
        scored[backend] = {
            "backend": backend,
            "metrics": metrics,
            "by_defect_class": {k: dict(v) for k, v in sorted(by_class.items())},
            "repeated_case_trials": n - len(stat["dispatches"]),
            "runs": sorted(stat["runs"].values(), key=lambda e: e["run"]),
        }
    return scored
