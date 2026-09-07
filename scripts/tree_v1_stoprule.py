#!/usr/bin/env python3
"""Read the tree-v1 stop rule for one binding (plan §5, pre-registration
record of 2026-09-06): per base class, refusals of sound controls and catch,
pooled and as paired changes from the binding's iso-v1 run on the same
cases, with the exact two-sided sign test on discordant pairs.

Usage: tree_v1_stoprule.py <tree-v1 run dir> <iso-v1 run dir> [--json out]
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
from caplab.advisory.adjudication import Adjudications  # noqa: E402
from caplab.advisory.compare import _binom_two_sided  # noqa: E402
from caplab.advisory.executor import advisory_control_context  # noqa: E402

DECISION_GRADE = {"whole-tree", "none-by-design"}
FLOOR = 6  # one-directional discordant pairs for p <= 0.031


def rows(run_dir):
    out = {}
    with open(os.path.join(run_dir, "results.jsonl"), encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            if r.get("usable") and r.get("control_json_valid") and r.get("mutant_json_valid") and not r.get("anchor"):
                out[r["dispatch_id"]] = r
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("tree_run")
    ap.add_argument("iso_run")
    ap.add_argument("--json")
    args = ap.parse_args()
    adj, sources = advisory_control_context(
        os.path.join(ROOT, "advisory", "control-adjudications.jsonl"))
    sources = sources or {}
    registry = json.load(open(os.path.join(ROOT, "advisory", "tree-v1-bases.json")))["bases"]

    def ckey(r):
        return sources.get(r.get("substrate_id")) or r["dispatch_id"]

    tree, iso = rows(args.tree_run), rows(args.iso_run)
    per = collections.defaultdict(lambda: collections.Counter())
    paired = collections.defaultdict(lambda: collections.Counter())
    for d, r in tree.items():
        cls = r.get("base_source") or registry.get(r["substrate_id"], {}).get("base_source") or "(unknown)"
        c = per[cls]
        c["pairs"] += 1
        c["caught"] += int(bool(r["caught"]))
        sound = not adj.is_defective(ckey(r))
        if sound:
            c["sound_controls"] += 1
            c["refused"] += int(bool(r["false_alarm"]))
        if d in iso:
            i = iso[d]
            p = paired[cls]
            p["shared"] += 1
            if sound:
                p["shared_sound"] += 1
                if i["false_alarm"] and not r["false_alarm"]:
                    p["refusal_cleared"] += 1        # tree fixed it
                elif r["false_alarm"] and not i["false_alarm"]:
                    p["refusal_new"] += 1            # tree broke it
            if i["caught"] and not r["caught"]:
                p["catch_lost"] += 1
            elif r["caught"] and not i["caught"]:
                p["catch_gained"] += 1
    report = {"tree_run": args.tree_run, "iso_run": args.iso_run, "classes": {}}
    for cls in sorted(per):
        c, p = per[cls], paired[cls]
        fa_p = _binom_two_sided(min(p["refusal_cleared"], p["refusal_new"]), p["refusal_cleared"] + p["refusal_new"]) \
            if (p["refusal_cleared"] + p["refusal_new"]) else None
        catch_p = _binom_two_sided(min(p["catch_lost"], p["catch_gained"]), p["catch_lost"] + p["catch_gained"]) \
            if (p["catch_lost"] + p["catch_gained"]) else None
        grade = "decision" if cls in DECISION_GRADE and c["sound_controls"] >= FLOOR else "diagnostic"
        report["classes"][cls] = {
            "grade": grade,
            "pairs": c["pairs"], "caught": c["caught"],
            "catch": round(c["caught"] / c["pairs"], 3) if c["pairs"] else None,
            "sound_controls": c["sound_controls"], "refused": c["refused"],
            "false_alarm": round(c["refused"] / c["sound_controls"], 3) if c["sound_controls"] else None,
            "paired": dict(p),
            "refusals_fell_established": bool(fa_p is not None and fa_p < 0.05 and p["refusal_cleared"] > p["refusal_new"]),
            "refusals_rose_established": bool(fa_p is not None and fa_p < 0.05 and p["refusal_new"] > p["refusal_cleared"]),
            "catch_fell_established": bool(catch_p is not None and catch_p < 0.05 and p["catch_lost"] > p["catch_gained"]),
            "sign_test_p": {"false_alarm": fa_p, "catch": catch_p},
        }
    print(json.dumps(report, indent=1))
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
