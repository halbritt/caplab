#!/usr/bin/env python3
"""Assemble the seed-20260819 discrimination report.

Runs the three matched contrasts, the promotion gate over both seeds, the
anchor reliability block, and the cross-seed anchor drift that seed 20260817
made available for the first time. Prints JSON; writes the contrast documents
to advisory/comparisons/.
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "src"))

from caplab.advisory.anchor import drift, reliability          # noqa: E402
from caplab.advisory.compare import paired_comparison          # noqa: E402
from caplab.advisory.discrimination import promotion_candidates  # noqa: E402
from caplab.advisory.executor import advisory_control_context  # noqa: E402
from caplab.advisory.scoring import score_backends             # noqa: E402

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
POOL = os.path.join(REPO, "advisory", "pool-runs")

SUBJECTS = {
    "agy-gemini-3-7-flash-high": "sweep-agy-gemini-3-7-flash-high-20260819",
    "agy-gemini-3-7-flash-medium": "sweep-agy-gemini-3-7-flash-medium-20260819",
    "codex-harm-sol-max": "sweep-codex-harm-sol-max-20260819",
}
PRIOR = {
    "agy-gemini-3-7-flash-high": "sweep-agy-gemini-3-7-flash-high-20260817b",
    "agy-gemini-3-7-flash-medium": "sweep-agy-gemini-3-7-flash-medium-20260817",
    "claude-harm-fable-5-high": "sweep-claude-harm-fable-5-high-20260817c",
}
CONTRASTS = [
    ("agy-gemini-3-7-flash-high", "agy-gemini-3-7-flash-medium",
     "gemini-3-7-flash-high-vs-medium-20260819.json"),
    ("agy-gemini-3-7-flash-high", "codex-harm-sol-max",
     "gemini-3-7-flash-high-vs-sol-max-20260819.json"),
    ("agy-gemini-3-7-flash-medium", "codex-harm-sol-max",
     "gemini-3-7-flash-medium-vs-sol-max-20260819.json"),
]
PRIOR_CONTRASTS = ["gemini-3-7-flash-high-vs-medium-20260817.json"]


def rows(run_dir: str) -> list[dict]:
    path = os.path.join(run_dir, "results.jsonl")
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def seed_of(run_dir: str):
    with open(os.path.join(run_dir, "summary.json"), encoding="utf-8") as f:
        return json.load(f).get("sweep_seed")


def main() -> int:
    adjudications, substrate_sources = advisory_control_context()
    report: dict = {"seed": 20260819, "contrasts": [], "reliability": {},
                    "cross_seed_anchor_drift": {}, "absolute": {}}

    for subject, run in SUBJECTS.items():
        d = os.path.join(POOL, run)
        report["reliability"][subject] = reliability(rows(d))
        with open(os.path.join(d, "summary.json"), encoding="utf-8") as f:
            summary = json.load(f)
        if summary.get("aborted"):
            # An aborted run measured whatever it reached before the outage,
            # in plan order — which is grouped by operator, so the surviving
            # sample is skewed by defect class rather than a random subset.
            # It gets a descriptive block and no claim, no contrast.
            report["incomplete"] = report.get("incomplete", {})
            report["incomplete"][subject] = {
                "aborted": summary["aborted"],
                "usable_rows": summary.get("pairs_usable"),
                "breadth_rows": sum(1 for r in rows(d)
                                    if r.get("usable") and not r.get("anchor")),
                "reading": ("not a completed run: no Scored claim and no "
                            "matched contrast; the surviving sample is "
                            "operator-skewed, not a random subsample")}
            continue
        prior = PRIOR.get(subject)
        if prior and os.path.isdir(os.path.join(POOL, prior)):
            report["cross_seed_anchor_drift"][subject] = drift(
                rows(d), rows(os.path.join(POOL, prior)))
        scored = score_backends([d], adjudications=adjudications,
                                substrate_sources=substrate_sources)
        report["absolute"][subject] = scored.get(subject, scored)

    docs = []
    out_dir = os.path.join(REPO, "advisory", "comparisons")
    for a, b, name in CONTRASTS:
        if a in report.get("incomplete", {}) or b in report.get("incomplete", {}):
            report["contrasts"].append({
                "a": a, "b": b, "computed": False,
                "reading": ("not computable: a run in this pair did not "
                            "complete, and comparing against a truncated "
                            "sample would contrast on a biased slice")})
            continue
        ra, rb = os.path.join(POOL, SUBJECTS[a]), os.path.join(POOL, SUBJECTS[b])
        doc = paired_comparison(ra, rb, label_a=a, label_b=b,
                                adjudications=adjudications,
                                substrate_sources=substrate_sources)
        seeds = {seed_of(ra), seed_of(rb)}
        doc["sweep_seed"] = seeds.pop() if len(seeds) == 1 else None
        if doc["sweep_seed"] is None:
            doc["reading"] += "; WARNING: runs carry different sweep seeds"
        with open(os.path.join(out_dir, name), "w", encoding="utf-8") as f:
            f.write(json.dumps(doc, ensure_ascii=False, indent=2,
                               sort_keys=True) + "\n")
        docs.append(doc)
        report["contrasts"].append({k: v for k, v in doc.items()
                                    if k != "discordant_cases"})
        report["contrasts"][-1]["discordant_cases"] = doc["discordant_cases"]

    # The gate reads every contrast the campaign holds, not only today's, so a
    # separation seen on two seeds can graduate.
    all_docs = list(docs)
    for name in PRIOR_CONTRASTS:
        path = os.path.join(out_dir, name)
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as f:
                all_docs.append(json.load(f))
    report["promotion"] = promotion_candidates(
        all_docs, adjudications, substrate_sources=substrate_sources)
    report["promotion_input_contrasts"] = [
        {"a": d["a"], "b": d["b"], "sweep_seed": d.get("sweep_seed")}
        for d in all_docs]

    # Diagnostic, not a gate decision: how many separations would reproduce
    # if reproduction were keyed on the substrate alone, as the module
    # docstring describes, rather than on (substrate, defect_class).
    by_substrate: dict[tuple, set] = {}
    for d in all_docs:
        for e in d.get("discordant_cases") or []:
            key = (e.get("substrate_id"), (d["a"], d["b"]))
            by_substrate.setdefault(key, set()).add(d.get("sweep_seed"))
    report["diagnostic_substrate_level_repeats"] = sorted(
        [{"substrate_id": k[0], "pair": list(k[1]), "sweeps": sorted(map(str, v))}
         for k, v in by_substrate.items() if len(v) > 1],
        key=lambda x: x["substrate_id"] or "")

    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
