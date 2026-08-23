#!/usr/bin/env python3
"""Emit the raw-data snapshot: every number, mechanically, as markdown.

    PYTHONPATH=src python3 scripts/raw_data_snapshot.py > docs/records/raw-data-<date>.md
"""
from __future__ import annotations

import glob
import json
import os
import sys
from collections import Counter
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
from caplab.advisory.discrimination import promotion_candidates  # noqa: E402
from caplab.advisory.executor import advisory_control_context    # noqa: E402

S = {"dropped_section", "truncated_tail", "duplicated_section", "swapped_section_bodies",
     "hollow_delivery", "base_dropped", "dangling_reference", "broken_internal_crossref",
     "hash_mismatch", "decorative_check"}


def fmt(x, d=3):
    return "—" if x is None else f"{x:.{d}f}"


def main() -> int:
    today = date.today().isoformat()
    claims = [json.loads(l) for l in open("advisory/claims.jsonl") if l.strip()]
    print(f"# CAPLAB raw result data — snapshot {today}\n")
    print("Mechanically generated (`scripts/raw_data_snapshot.py`) from `advisory/claims.jsonl`, "
          "`advisory/comparisons/`, the promotion gate, and `advisory/control-adjudications.jsonl`. "
          "Compare only within one instrument, custody class, and case seed.\n")

    print("## 1. Review claims (`review.defect_discrimination/1`)\n")
    print("| subject | as_of | custody | seed | instrument | selection | pairs | catch | catch CI95 | FA | FA CI95 | unaudited | disc | anchored |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    rows = []
    for c in claims:
        if c.get("construct", "review.defect_discrimination/1") != "review.defect_discrimination/1":
            continue
        m = c["metrics"]
        def cell(k):
            e = m.get(k) or {}
            return e.get("value"), e.get("ci95"), e.get("unaudited_refusals")
        seeds, insts, pairs, sel = set(), set(), 0, set()
        for e in c.get("evidence", []):
            if isinstance(e, dict):
                if e.get("sweep_seed"): seeds.add(str(e["sweep_seed"]))
                if e.get("instrument"): insts.add(e["instrument"])
                pairs += e.get("rows_used") or 0
                run = e.get("run") or ""
                sel.add("profile-remeasurement" if run.startswith("remeasure-") else
                        "targeted" if run.startswith("replay-") else "seeded")
        cv, cci, _ = cell("catch_rate"); fv, fci, un = cell("false_alarm_rate")
        dv, _, _ = cell("discrimination"); av, _, _ = cell("anchored_detection")
        inst = "synthetic" if any("synthetic" in i for i in insts) else "dispatch"
        rows.append((c["subject"]["source_id"], c["as_of"][:10], c.get("custody"),
                     ",".join(sorted(seeds)) or "?", inst, ",".join(sorted(sel)), pairs,
                     cv, cci, fv, fci, un, dv, av))
    ci = lambda c: "—" if not c else f"{c[0]:.2f}–{c[1]:.2f}"
    for r in sorted(rows, key=lambda r: (r[2], r[3], r[0], r[1])):
        s, ao, cu, sd, inst, sel, p, cv, cci, fv, fci, un, dv, av = r
        print(f"| {s} | {ao} | {cu} | {sd} | {inst} | {sel} | {p} | {fmt(cv)} | {ci(cci)} | {fmt(fv)} | {ci(fci)} | {un if un is not None else '—'} | {fmt(dv)} | {fmt(av)} |")

    print("\n## 2. Per-run breadth splits (all pool runs)\n")
    print("| run | usable | breadth | catch | FA | disc | structural | semantic | anchors | anchor FA | discarded |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    for d in sorted(glob.glob("advisory/pool-runs/*/results.jsonl")):
        run = d.split("/")[2]
        rws = [json.loads(l) for l in open(d) if l.strip()]
        u = [r for r in rws if r.get("usable")]
        b = [r for r in u if not r.get("anchor")]; a = [r for r in u if r.get("anchor")]
        if not b:
            continue
        st = [r for r in b if r["defect_class"] in S]; se = [r for r in b if r["defect_class"] not in S]
        c = sum(r["caught"] for r in b); fa = sum(1 for r in b if r["false_alarm"])
        print(f"| {run} | {len(u)} | {len(b)} | {c}/{len(b)} | {fa} | {(c - fa) / len(b):+.3f} | "
              f"{sum(r['caught'] for r in st)}/{len(st)} | {sum(r['caught'] for r in se)}/{len(se)} | "
              f"{sum(r['caught'] for r in a)}/{len(a)} | {sum(1 for r in a if r['false_alarm'])} | {len(rws) - len(u)} |")

    print("\n## 3. Matched contrasts (adjudication-aware false alarms)\n")
    print("| a | b | seed | shared | a-only | b-only | p | FA a | FA b | defective excl | unaudited | FA p | selection |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    docs = []
    for f in sorted(glob.glob("advisory/comparisons/*.json")):
        d = json.load(open(f))
        if "shared_cases" not in d:
            continue
        docs.append(d)
        print(f"| {d['a']} | {d['b']} | {d.get('sweep_seed') or '?'} | {d['shared_cases']} | "
              f"{d['a_only_caught']} | {d['b_only_caught']} | {d['sign_test_p']:.4f} | "
              f"{d['a_false_alarms']} | {d['b_false_alarms']} | {d.get('false_alarm_defective_controls_excluded', 0)} | "
              f"{d.get('false_alarm_unaudited_pairs', 0)} | {d['false_alarm_sign_test_p']:.3f} | {d.get('case_selection', '')} |")

    adj, src = advisory_control_context()
    r = promotion_candidates([d for d in docs if "discordant_cases" in d], adj, substrate_sources=src)
    print(f"\n## 4. Promotion gate — {len(r['promoted'])} promoted, {len(r['withheld'])} withheld\n")
    print("| substrate | class | pair | sweeps |\n|---|---|---|---|")
    for p in r["promoted"]:
        print(f"| {p['substrate_id']} | {p['defect_class']} | {p['pair'][0]} > {p['pair'][1]} | {', '.join(map(str, p['sweeps']))} |")
    print("\nWithheld by reason:")
    for reason, count in Counter(w["reason"][:58] for w in r["withheld"]).most_common():
        print(f"- {count} × {reason}")

    print("\n## 5. Control adjudications\n")
    print("| key | disposition | basis | authority | as_of |\n|---|---|---|---|---|")
    for line in open("advisory/control-adjudications.jsonl"):
        a = json.loads(line)
        print(f"| {a['dispatch_id'][:20]}… | {a['disposition']} | {a['basis_kind']} | {a['adjudicated_by'][:44]} | {a['as_of'][:10]} |")

    print("\n## 6. Build construct (`build.packet_delivery/1`)\n")
    print("| subject | gated n | checks-pass | CI95 | delivery |\n|---|---|---|---|---|")
    for c in claims:
        if c.get("construct") != "build.packet_delivery/1":
            continue
        m = c["metrics"]; pc = m.get("packet_checks_pass_rate") or {}; dl = m.get("delivery_rate") or {}
        cc = pc.get("ci95"); cis = f"{cc[0]:.2f}–{cc[1]:.2f}" if cc else "—"
        print(f"| {c['subject']['source_id']} | {pc.get('denominator', '—')} | {fmt(pc.get('value'))} | {cis} | {fmt(dl.get('value'))} |")

    print("\n## 7. Tier A and Tier B production constructs\n")
    print("| construct | subject | metric | value | n |\n|---|---|---|---|---|")
    for c in sorted(claims, key=lambda c: (c.get("construct", ""), c["subject"]["source_id"])):
        con = c.get("construct", "")
        if con in ("review.defect_discrimination/1", "build.packet_delivery/1"):
            continue
        for k, v in c["metrics"].items():
            if k == "n_pairs":
                continue
            print(f"| {con} | {c['subject']['source_id']} | {k} | {fmt(v.get('value'))} | {v.get('denominator')} |")

    print("\n## 8. Records index\n")
    for f in sorted(glob.glob("docs/records/*2026-08*.md")):
        print(f"- `{f}`")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
