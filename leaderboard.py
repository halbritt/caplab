#!/usr/bin/env python3
"""Render the review-benchmark leaderboard from bench.py run summaries.

This document is what a backend declaration's `quality.benchmark_ref` points
at when a tuple's review class is raised above baseline, so it states the
sample it rests on as prominently as the score. A tuple measured on eleven
examples has earned an eleven-example claim and nothing more.

Usage:
  python3 leaderboard.py --runs eval-runs/bench-* --out docs/results/review-benchmark-2026-08-07.md
"""

from __future__ import annotations

import argparse
import json
import os

COLUMNS = [
    ("backend", "tuple", None),
    ("n", "n", None),
    ("balanced_accuracy", "balanced acc", "pct"),
    ("caught_revised", "caught revised", "pct"),
    ("passed_final", "passed final", "pct"),
    ("accept_rate", "accept rate", "pct"),
    ("json_valid", "json valid", "pct"),
    ("fate_agreement", "raw agree", "pct"),
    ("mean_seconds", "mean s", "num"),
    ("cost_per_review_usd", "$/review", "usd"),
]


def cell(value, style) -> str:
    if value is None:
        return "—"
    if style == "pct":
        return f"{value * 100:.0f}%"
    if style == "usd":
        return f"${value:.3f}"
    if style == "num":
        return f"{value:g}"
    return str(value)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", nargs="+", required=True, help="bench.py output directories")
    ap.add_argument("--out", required=True)
    ap.add_argument("--date", required=True, help="measurement date, YYYY-MM-DD")
    args = ap.parse_args()

    summaries = []
    for run in args.runs:
        path = os.path.join(run, "summary.json")
        if not os.path.isfile(path):
            print(f"skip {run}: no summary.json")
            continue
        with open(path) as f:
            summary = json.load(f)
        summary["_run"] = os.path.basename(run.rstrip("/"))
        summaries.append(summary)
    summaries.sort(key=lambda s: (-(s.get("balanced_accuracy") or -1), s["backend"]))

    lines = [
        f"# Review benchmark — {args.date}",
        "",
        "Every tuple measured through its own declared `adapter.command`, the way the",
        "Lane Supervisor invokes it. Endpoint lanes take the prompt on stdin and are read",
        "from stdout; harness lanes run in an isolated per-example workspace with the",
        "sealed dispatch bundle materialized into it, and are scored on the output id the",
        "dispatch manifest marks required, read by name.",
        "",
        "**Ranked on `balanced acc`, not raw agreement, and the reason matters.** The",
        "adjudicated outcomes in this corpus are lopsided and lopsided in a way that tracks",
        "prompt size: of the examples small enough to inline, 9 of 11 ended `final` (accept",
        "was right), while 21 of 23 large ones ended `revised` (refuse was right). A model",
        "that simply always accepts therefore scores 82% on the small group and 9% on the",
        "large one, and neither figure is skill. The 2026-08-07 audit read the first of",
        "those as \"codex-class\"; DeepSeek V4 Flash reproduces it exactly, at a 94% accept",
        "rate and a balanced accuracy of 0.477 — below chance.",
        "",
        "`balanced acc` is the mean of `caught revised` and `passed final`, so any constant",
        "answer scores 0.50 whatever the class mix. Raw agreement is kept in the table only",
        "so older numbers remain locatable; it must not be used to rank.",
        "",
        "**Read the `n` column before the scores.** The held-out split's 98 examples are",
        "not one benchmark: 64 of them inline to 8-14MB because a packet change-set review",
        "pins an expanded base repository tree, and 23 more land between 430KB and 1MB. A",
        "one-shot endpoint tuple is measured only on the examples that fit the context",
        "window its own declaration states, and `n` is that count. Harness lanes keep their",
        "declaration's spill transport and see the whole split.",
        "",
        "Scores cover rows whose review subject was actually reachable (`subject_visible`).",
        "The 2026-08-07 runs that did not check this are superseded, not amended: see",
        "`docs/audits/OPENROUTER_ADAPTER_INVESTIGATION_2026-08-07.md`.",
        "",
        "| " + " | ".join(label for _, label, _ in COLUMNS) + " |",
        "|" + "|".join("---" for _ in COLUMNS) + "|",
    ]
    for summary in summaries:
        lines.append(
            "| " + " | ".join(cell(summary.get(key), style) for key, _, style in COLUMNS) + " |"
        )

    lines += ["", "## Sample and exclusions", "",
              "| tuple | transport | eligible | over context | subject invisible | errors |",
              "|---|---|---|---|---|---|"]
    for summary in summaries:
        lines.append(
            f"| {summary['backend']} | {summary.get('transport', '—')} | "
            f"{summary.get('eligible_of_split', '—')} | "
            f"{summary.get('excluded_over_context', 0)} | "
            f"{summary.get('excluded_subject_invisible', 0)} | "
            f"{summary.get('errors', 0)} |"
        )

    lines += ["", "## Verdict distribution and routing", ""]
    for summary in summaries:
        lines.append(f"### {summary['backend']}")
        lines.append("")
        lines.append(f"- run: `{summary['_run']}`")
        lines.append(f"- verdicts: `{summary.get('verdict_distribution')}`")
        if summary.get("providers"):
            lines.append(f"- served by: `{summary['providers']}`")
        if summary.get("mean_reasoning_tokens") is not None:
            lines.append(f"- mean reasoning tokens: {summary['mean_reasoning_tokens']:,}")
        if summary.get("cost_total_usd") is not None:
            lines.append(f"- total spend: ${summary['cost_total_usd']:.3f} "
                         f"over {summary.get('cost_rows', 0)} accounted rows")
        lines.append("")

    lines += [
        "## What a score here does and does not license",
        "",
        "`fate_agreement` is agreement with the adjudicated outcome of the candidate the",
        "review was about — whether the work was ultimately taken as final or revised. It",
        "is the closest thing here to a review being *right*. `side_match` and `exact`",
        "compare against the frontier reference review's verdict, which is a strong signal",
        "and not ground truth.",
        "",
        "Raising a declaration's `quality.classes.review` above `baseline` on this document",
        "means citing it as `benchmark_ref` with `basis: measured`. A tuple whose `n` is",
        "small has earned a small claim; say so in the declaration rather than rounding up.",
        "",
    ]

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as f:
        f.write("\n".join(lines))
    print(f"wrote {args.out} ({len(summaries)} tuples)")


if __name__ == "__main__":
    main()
