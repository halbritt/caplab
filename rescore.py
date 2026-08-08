#!/usr/bin/env python3
"""Re-score retained runs against the corrected anchor path, buying nothing.

Every measured pair kept its two arms on disk, so the anchor defects fixed on
2026-08-08 -- findings[].element_anchor read as the only anchor channel, and a
normalizer that mangled any slug beginning with e/l/: -- can be undone without
dispatching a single lane again.

Anchored detection is reported beside the verdict metric on purpose. The
verdict metric scores a control-arm refusal as a false alarm because the
control artifact reached `fate == final`, but an artifact being accepted does
not make a reviewer citing a real gap in it wrong; codex's control refusals
are specific and anchored, not noise. Anchored detection asks the narrower
question the injection can actually adjudicate: did the lane name the element
we broke? A standing critique does not anchor to the injection, so strictness
neither earns nor loses credit.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys

import bench


def outputs_for(run_dir: str, dispatch_id: str, arm: str) -> list[str]:
    pattern = os.path.join(run_dir, "arms", dispatch_id[:12], f"{arm}-ws", "work",
                           "outputs", "*")
    return sorted(glob.glob(pattern))


def review_in(paths: list[str]) -> dict | None:
    for path in paths:
        if os.path.basename(path) == "ASSUMPTIONS.md":
            continue
        try:
            with open(path, errors="replace") as handle:
                doc = bench.extract_json(handle.read())
        except OSError:
            continue
        if isinstance(doc, dict):
            return doc
    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", default="eval-runs")
    parser.add_argument("--min-pairs", type=int, default=13)
    args = parser.parse_args()

    families: dict[str, dict] = {}
    for results in sorted(glob.glob(os.path.join(args.runs, "*", "results.jsonl"))):
        run_dir = os.path.dirname(results)
        run = os.path.basename(run_dir)
        if not re.match(r"^(revbench|sweep|cc|confirm|agyfix)-", run):
            continue
        name = re.sub(r"^(revbench|sweep|cc|confirm|agyfix)-", "", run)
        name = name.replace("-20260807", "")
        stat = families.setdefault(name, dict(n=0, caught=0, alarms=0, was=0,
                                              now=0, anchors=0, rescored=0))
        for line in open(results):
            row = json.loads(line)
            if not row.get("usable"):
                continue
            if not (row.get("mutant_json_valid") or row.get("control_json_valid")):
                continue
            stat["n"] += 1
            stat["caught"] += bool(row.get("caught"))
            stat["alarms"] += bool(row.get("false_alarm"))
            stat["was"] += bool(row.get("anchor_hit"))
            injected = row.get("defect_anchor") or ""
            doc = review_in(outputs_for(run_dir, row["dispatch_id"], "mutant"))
            if doc is None:
                continue
            stat["rescored"] += 1
            anchors = bench.anchors_of(doc.get("findings") or [])
            stat["anchors"] += len(anchors)
            stat["now"] += bool(bench.anchor_hits(injected, anchors))

    rows = [(s["now"] / s["n"], name, s) for name, s in families.items()
            if s["n"] >= args.min_pairs and s["rescored"]]
    if not rows:
        print("no retained arms to re-score", file=sys.stderr)
        raise SystemExit(1)

    print("ANCHORED DETECTION, re-scored from retained arms (no new dispatches)")
    print("%-26s %4s %9s %9s %8s %8s %8s" % (
        "tuple", "n", "anchored", "was", "catch", "false", "anchors"))
    for share, name, s in sorted(rows, reverse=True):
        print("%-26s %4d %8.0f%% %8.0f%% %7.0f%% %7.0f%% %8d" % (
            name, s["n"], 100 * share, 100 * s["was"] / s["n"],
            100 * s["caught"] / s["n"], 100 * s["alarms"] / s["n"], s["anchors"]))


if __name__ == "__main__":
    main()
