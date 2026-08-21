#!/usr/bin/env python3
"""Assemble the codex-sol-high seed-20260819 report: the first completed
cross-family contrasts of the campaign.

Sol ran the identical seed-20260819 case set the two flash tuples completed
on 2026-08-19, so both contrasts are matched. The promotion gate re-runs
over every contrast the campaign holds; sol-pair cells enter at one sweep.
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "src"))

from caplab.advisory.anchor import reliability                   # noqa: E402
from caplab.advisory.compare import (annotate_from_summaries,    # noqa: E402
                                     paired_comparison)
from caplab.advisory.discrimination import promotion_candidates  # noqa: E402
from caplab.advisory.executor import advisory_control_context    # noqa: E402
from caplab.advisory.scoring import score_backends               # noqa: E402

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
POOL = os.path.join(REPO, "advisory", "pool-runs")

SOL = ("codex-sol-high", os.path.join(POOL, "sweep-codex-sol-high-20260819"))
FLASH = {
    "agy-gemini-3-7-flash-high":
        os.path.join(POOL, "sweep-agy-gemini-3-7-flash-high-20260819"),
    "agy-gemini-3-7-flash-medium":
        os.path.join(POOL, "sweep-agy-gemini-3-7-flash-medium-20260819"),
}
ALL_CONTRASTS = [
    "gemini-3-7-flash-high-vs-medium-20260817.json",
    "gemini-3-7-flash-high-vs-medium-20260819.json",
    "gemini-3-7-flash-high-vs-medium-20260820-replay.json",
]


def rows(run_dir: str) -> list[dict]:
    with open(os.path.join(run_dir, "results.jsonl"), encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def main() -> int:
    adjudications, substrate_sources = advisory_control_context()
    report: dict = {"seed": 20260819, "subject": SOL[0], "contrasts": []}

    out_dir = os.path.join(REPO, "advisory", "comparisons")
    docs = []
    for flash_label, flash_run in FLASH.items():
        doc = annotate_from_summaries(
            paired_comparison(SOL[1], flash_run, label_a=SOL[0],
                              label_b=flash_label,
                              adjudications=adjudications,
                              substrate_sources=substrate_sources),
            SOL[1], flash_run)
        name = f"sol-high-vs-{flash_label.replace('agy-gemini-3-7-', '')}-20260819.json"
        with open(os.path.join(out_dir, name), "w", encoding="utf-8") as f:
            f.write(json.dumps(doc, ensure_ascii=False, indent=2,
                               sort_keys=True) + "\n")
        docs.append(doc)
        report["contrasts"].append(doc)

    all_docs = list(docs)
    for name in ALL_CONTRASTS:
        with open(os.path.join(out_dir, name), encoding="utf-8") as f:
            all_docs.append(json.load(f))
    report["promotion"] = promotion_candidates(
        all_docs, adjudications, substrate_sources=substrate_sources)

    report["reliability"] = {SOL[0]: reliability(rows(SOL[1]))}
    scored = score_backends([SOL[1]], adjudications=adjudications,
                            substrate_sources=substrate_sources)
    report["absolute"] = scored.get(SOL[0], scored)

    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
