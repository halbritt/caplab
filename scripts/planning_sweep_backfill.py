#!/usr/bin/env python3
"""Re-score stored graphs in place to backfill verdict fields.

The run root keeps every produced graph, so a verdict field added after a
sweep costs a re-score, never a re-spend. Rows are rewritten only where the
recomputed verdict agrees with the stored one on every field that was
already there; a disagreement means the oracle or the registry moved under
the run and the row is left alone and reported.
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.dirname(__file__))

from planning_sweep import REGISTRY, RUNS, _verdict_flags  # noqa: E402
from caplab.advisory.planning_corpus import score_graph  # noqa: E402

STABLE = ("parse_ok", "index_ok", "legality_ok", "resolvable_ok",
          "all_checks_ok", "packets", "depth_width_product")


def backfill(run_dir: str) -> dict:
    path = os.path.join(run_dir, "results.jsonl")
    if not os.path.isfile(path):
        return {"run": run_dir, "skipped": "no results"}
    with open(path, encoding="utf-8") as f:
        rows = [json.loads(line) for line in f if line.strip()]
    updated = drifted = 0
    for row in rows:
        if not row.get("usable") or "graph" not in row:
            continue
        if "parse_error" in row:
            continue
        fresh = _verdict_flags(score_graph(row["graph"], registry_path=REGISTRY))
        if any(row.get(k) != fresh.get(k) for k in STABLE if k in row):
            drifted += 1
            continue
        row.update(fresh)
        updated += 1
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
        f.flush()
        os.fsync(f.fileno())
    return {"run": os.path.basename(run_dir), "rows": len(rows),
            "updated": updated, "drifted": drifted}


if __name__ == "__main__":
    targets = sys.argv[1:] or [
        os.path.join(RUNS, d) for d in sorted(os.listdir(RUNS))
        if d.startswith("plan-") and "calibration" not in d]
    for target in targets:
        print(json.dumps(backfill(target), sort_keys=True))
