#!/usr/bin/env python3
"""Production review criterion study — reproducible harvest.

Joins striatum's production packet-review verdicts to their downstream fate
and to CAPLAB's Revbench claims. Usage:

    python3 scripts/production_review_study.py <ledger-dump.jsonl>

Emits the study tables as markdown on stdout. Guards the empty-ledger trap.
"""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict

MIN_LEDGER_LINES = 200_000


def main(path: str) -> int:
    events = [json.loads(l) for l in open(path, encoding="utf-8")
              if l.strip()]
    if len(events) < MIN_LEDGER_LINES:
        raise SystemExit(f"ledger dump holds {len(events)} records, below "
                         f"the {MIN_LEDGER_LINES} guard — refuse to study "
                         f"an empty read")

    backend_of_run = {}
    for e in events:
        if e["type"] == "lane_binding":
            backend_of_run[e["payload"].get("run_ref")] = \
                e["payload"].get("backend_id")
    hash_to_backend = {}
    for e in events:
        if e["type"] == "artifact_admitted":
            p = e["payload"]
            h, b = p.get("content_hash"), \
                (p.get("attribution") or {}).get("backend_id")
            if h and b:
                hash_to_backend[h] = b

    reviews = []          # (backend, outcome, subject identity, vseq, hash)
    for e in events:
        if e["type"] != "gate_result" \
                or e["payload"].get("gate_id") != "packet-review":
            continue
        backend = None
        for item in e["payload"]["evidence"]:
            run = (item.get("producing_run") or {}).get("run_ref")
            backend = backend_of_run.get(run)
            if backend:
                break
            h = item.get("content_hash") or \
                (item.get("pin") or {}).get("content_hash")
            backend = hash_to_backend.get(h)
            if backend:
                break
        s = e["payload"].get("subject") or {}
        reviews.append((backend, e["payload"]["outcome"], s.get("identity"),
                        s.get("version_seq"), s.get("content_hash")))

    by_identity = defaultdict(list)
    for r in reviews:
        by_identity[r[2]].append(r)

    per = defaultdict(lambda: {"pass": 0, "fail": 0, "vindicated": 0,
                               "flipflop": 0, "unresolved": 0})
    for backend, outcome, ident, vseq, chash in reviews:
        cell = per[backend]
        cell[outcome] += 1
        if outcome != "fail":
            continue
        later = [x for x in by_identity[ident]
                 if x[3] is not None and vseq is not None and x[3] > vseq]
        if any(x[4] != chash and x[1] == "pass" for x in later):
            cell["vindicated"] += 1
        elif any(x[4] == chash and x[1] == "pass" for x in later):
            cell["flipflop"] += 1
        else:
            cell["unresolved"] += 1

    print("| reviewer | reviews | refusal | vindicated | flip-flop | unresolved |")
    print("|---|---|---|---|---|---|")
    for b, c in sorted(per.items(), key=lambda kv: -(kv[1]['pass'] + kv[1]['fail'])):
        n = c["pass"] + c["fail"]
        print(f"| {b} | {n} | {c['fail'] / n:.1%} | {c['vindicated']} | "
              f"{c['flipflop']} | {c['unresolved']} |")
    total_fail = sum(c["fail"] for c in per.values())
    total_vind = sum(c["vindicated"] for c in per.values())
    total_flip = sum(c["flipflop"] for c in per.values())
    print(f"\nTotals: {sum(c['pass'] + c['fail'] for c in per.values())} "
          f"reviews, {total_fail} refusals, {total_vind} vindicated, "
          f"{total_flip} flip-flops.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
