#!/usr/bin/env python3
"""Assemble the targeted-reproduction report for sweep seed 20260820.

The two flash effort tuples re-measured exactly the 19 cells that separated
them in seeds 20260817 and 20260819, under fresh injections drawn from seed
20260820. This script computes the matched contrast (annotated as
outcome-selected), the per-cell reproduction table, the promotion gate over
every contrast the campaign holds, and the anchor reliability/drift blocks.
No Scored claim is derived — the runs are outcome-selected by construction.
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "src"))

from caplab.advisory.anchor import drift, reliability            # noqa: E402
from caplab.advisory.compare import (annotate_from_summaries,    # noqa: E402
                                     paired_comparison)
from caplab.advisory.discrimination import promotion_candidates  # noqa: E402
from caplab.advisory.executor import advisory_control_context    # noqa: E402

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
POOL = os.path.join(REPO, "advisory", "pool-runs")

RUN_A = os.path.join(POOL, "replay-agy-gemini-3-7-flash-high-20260820")
RUN_B = os.path.join(POOL, "replay-agy-gemini-3-7-flash-medium-20260820")
LABEL_A = "agy-gemini-3-7-flash-high"
LABEL_B = "agy-gemini-3-7-flash-medium"
PRIOR = {
    LABEL_A: "sweep-agy-gemini-3-7-flash-high-20260819",
    LABEL_B: "sweep-agy-gemini-3-7-flash-medium-20260819",
}
CELLS_DOC = os.path.join(REPO, "advisory", "replay",
                         "replay-flash-effort-20260820.json")
PRIOR_CONTRASTS = [
    "gemini-3-7-flash-high-vs-medium-20260817.json",
    "gemini-3-7-flash-high-vs-medium-20260819.json",
]
OUT_CONTRAST = "gemini-3-7-flash-high-vs-medium-20260820-replay.json"


def rows(run_dir: str) -> list[dict]:
    with open(os.path.join(run_dir, "results.jsonl"), encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def main() -> int:
    adjudications, substrate_sources = advisory_control_context()
    report: dict = {"seed": 20260820,
                    "case_selection": "targeted-reproduction"}

    for label, run in ((LABEL_A, RUN_A), (LABEL_B, RUN_B)):
        with open(os.path.join(run, "summary.json"), encoding="utf-8") as f:
            if json.load(f).get("aborted"):
                report["aborted"] = {label: "run aborted; stopping — a "
                                     "truncated reproduction set drops "
                                     "named cells silently"}
                print(json.dumps(report, indent=2))
                return 1

    doc = annotate_from_summaries(
        paired_comparison(RUN_A, RUN_B, label_a=LABEL_A, label_b=LABEL_B,
                          adjudications=adjudications,
                          substrate_sources=substrate_sources),
        RUN_A, RUN_B)
    out_dir = os.path.join(REPO, "advisory", "comparisons")
    with open(os.path.join(out_dir, OUT_CONTRAST), "w", encoding="utf-8") as f:
        f.write(json.dumps(doc, ensure_ascii=False, indent=2, sort_keys=True)
                + "\n")
    report["contrast"] = {k: v for k, v in doc.items()}

    # Per-cell reproduction: for each of the 19 targeted cells, what happened
    # this sweep. "separated-same-direction" is what the gate can promote;
    # everything else is the honest cost of regression to the mean.
    with open(CELLS_DOC, encoding="utf-8") as f:
        cells = json.load(f)["cells"]
    a_rows = {(r["substrate_id"], r["defect_class"]): r for r in rows(RUN_A)
              if r.get("usable") and not r.get("anchor")}
    b_rows = {(r["substrate_id"], r["defect_class"]): r for r in rows(RUN_B)
              if r.get("usable") and not r.get("anchor")}
    table = []
    for cell in cells:
        sid = cell["substrate_id"]
        key = (sid, cell["operator"])
        prior_direction = {e["caught_by"] for e in cell["separated_in"]}
        ra, rb = a_rows.get(key), b_rows.get(key)
        if ra is None or rb is None:
            outcome = "not-measured (pair discarded)"
        else:
            ca, cb = bool(ra["caught"]), bool(rb["caught"])
            if ca == cb:
                outcome = ("concordant-both-caught" if ca
                           else "concordant-both-missed")
            else:
                now = LABEL_A if ca else LABEL_B
                outcome = ("separated-same-direction"
                           if prior_direction == {now}
                           else "separated-direction-flip")
        table.append({"substrate_id": sid, "operator": cell["operator"],
                      "prior_caught_by": sorted(prior_direction),
                      "outcome": outcome})
    report["reproduction"] = {
        "cells": table,
        "counts": {o: sum(1 for t in table if t["outcome"] == o)
                   for o in sorted({t["outcome"] for t in table})},
    }

    all_docs = [doc]
    for name in PRIOR_CONTRASTS:
        with open(os.path.join(out_dir, name), encoding="utf-8") as f:
            all_docs.append(json.load(f))
    report["promotion"] = promotion_candidates(
        all_docs, adjudications, substrate_sources=substrate_sources)
    report["promotion_input_contrasts"] = [
        {"a": d["a"], "b": d["b"], "sweep_seed": d.get("sweep_seed")}
        for d in all_docs]

    report["reliability"] = {}
    report["cross_seed_anchor_drift"] = {}
    for label, run in ((LABEL_A, RUN_A), (LABEL_B, RUN_B)):
        report["reliability"][label] = reliability(rows(run))
        prior = os.path.join(POOL, PRIOR[label])
        if os.path.isdir(prior):
            report["cross_seed_anchor_drift"][label] = drift(
                rows(run), rows(prior))

    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
