#!/usr/bin/env python3
"""Build DPO preference pairs from dual-signal reviews.

Striatum's dual-signal verification reviews the same candidate independently
on two lanes. Where two backends reviewed the same (identity, content_hash)
and their verdict *sides* disagree (accepting vs refusing), the candidate's
fate (analyze.py) adjudicates: the review on the side that matched fate is
"chosen", the other "rejected".

The two lanes saw near-identical prompts (same sealed inputs/environment;
only the workspace path and any relaunch corrective differ). The pair uses
the chosen record's prompt for both completions — standard DPO practice, and
the semantic context is identical by construction.

Emits LLaMA-Factory-compatible ranking records:
  {"messages": [user], "chosen": {assistant}, "rejected": {assistant}, "meta": …}
"""

from __future__ import annotations

import argparse
import collections
import json

from analyze import ACCEPTING, REFUSING
from make_sft import normalize_review_body

MAX_PROMPT_BYTES = 128 * 1024


def side(verdict: str) -> str | None:
    if verdict in ACCEPTING:
        return "accepting"
    if verdict in REFUSING:
        return "refusing"
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", default="corpus/corpus.jsonl")
    ap.add_argument("--analysis", default="corpus/analysis.json")
    ap.add_argument("--out", default="sft/review.dpo.jsonl")
    ap.add_argument("--exclude-eval", default="sft/review.eval.jsonl",
                    help="drop pairs whose candidate appears in this eval split "
                         "(leakage guard); empty string disables")
    args = ap.parse_args()

    with open(args.analysis) as f:
        analysis = json.load(f)
    fate_by_dispatch = {r["dispatch_id"]: r for r in analysis["reviews"]}

    eval_candidates = set()
    if args.exclude_eval:
        import os
        if os.path.isfile(args.exclude_eval):
            with open(args.exclude_eval) as f:
                for line in f:
                    did = json.loads(line)["meta"]["dispatch_id"]
                    fr = fate_by_dispatch.get(did)
                    if fr:
                        eval_candidates.add((fr["candidate_identity"], fr["candidate_hash"]))

    records = {}
    with open(args.corpus) as f:
        for line in f:
            r = json.loads(line)
            if r["pass"] == "review" and r["dispatch_id"] in fate_by_dispatch:
                records[r["dispatch_id"]] = r

    groups = collections.defaultdict(list)
    for did, fr in fate_by_dispatch.items():
        groups[(fr["candidate_identity"], fr["candidate_hash"])].append(fr)

    pairs, stats = [], collections.Counter()
    for (identity, chash), reviews in groups.items():
        if (identity, chash) in eval_candidates:
            stats["excluded_eval_candidate"] += 1
            continue
        fate = reviews[0]["fate"]
        if fate not in ("final", "revised"):
            stats["fate_unknown"] += 1
            continue
        correct_side = "accepting" if fate == "final" else "refusing"
        winners = [r for r in reviews if side(r["verdict"]) == correct_side]
        losers = [r for r in reviews if side(r["verdict"]) not in (correct_side, None)]
        if not winners or not losers:
            stats["no_disagreement"] += 1
            continue
        for w in winners:
            for l in losers:
                cw, cl = records.get(w["dispatch_id"]), records.get(l["dispatch_id"])
                if not cw or not cl:
                    stats["missing_record"] += 1
                    continue
                if cw["prompt_bytes"] > MAX_PROMPT_BYTES or not cw["prompt_utf8_clean"]:
                    stats["prompt_unusable"] += 1
                    continue
                chosen = normalize_review_body((cw["outputs"].get("review-ledger") or {}).get("body", ""))
                rejected = normalize_review_body((cl["outputs"].get("review-ledger") or {}).get("body", ""))
                if not chosen or not rejected:
                    stats["body_unusable"] += 1
                    continue
                pairs.append({
                    "messages": [{"role": "user", "content": cw["prompt"]}],
                    "chosen": {"role": "assistant", "content": chosen},
                    "rejected": {"role": "assistant", "content": rejected},
                    "meta": {
                        "candidate_identity": identity,
                        "candidate_hash": chash,
                        "fate": fate,
                        "chosen_backend": w["backend_id"],
                        "chosen_verdict": w["verdict"],
                        "rejected_backend": l["backend_id"],
                        "rejected_verdict": l["verdict"],
                        "written_at": cw["written_at"],
                    },
                })
                stats["pairs"] += 1

    with open(args.out, "w") as f:
        for p in sorted(pairs, key=lambda p: p["meta"]["written_at"] or ""):
            f.write(json.dumps(p, ensure_ascii=False) + "\n")

    print(f"wrote {len(pairs)} pairs to {args.out}")
    print(json.dumps(dict(stats), indent=2))
    by = collections.Counter(
        (p["meta"]["chosen_backend"], p["meta"]["rejected_backend"]) for p in pairs
    )
    for k, v in by.most_common(12):
        print(v, k)


if __name__ == "__main__":
    main()
