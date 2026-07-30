#!/usr/bin/env python3
"""Build SFT train/eval JSONL from an extracted corpus.

Selects admitted, complete, prompt-clean records for one pass; emits OpenAI
messages format (one {"messages": [...]} object per line, extra metadata under
"meta") with a time-ordered train/eval split so eval is strictly newer than
train.

Usage:
  python3 make_sft.py --corpus corpus/corpus.jsonl --pass review --out sft/
"""

from __future__ import annotations

import argparse
import collections
import json
import os

VERDICTS = {"accept", "accept_with_findings", "needs_revision", "reject"}

# Verdict vocabulary drift: early ledgers said "revise"; the current gate
# contract (internal/gate/verdict.go) says "needs_revision". Targets are
# normalized to the current contract so training matches inference.
LEGACY_VERDICTS = {"revise": "needs_revision"}


def normalize_review_body(body: str) -> str | None:
    """Return the body (legacy verdicts normalized), or None if unusable."""
    try:
        doc = json.loads(body)
    except json.JSONDecodeError:
        return None
    if not isinstance(doc, dict):
        return None
    verdict = doc.get("verdict")
    if verdict in VERDICTS:
        return body
    if verdict in LEGACY_VERDICTS:
        doc["verdict"] = LEGACY_VERDICTS[verdict]
        return json.dumps(doc, ensure_ascii=False, indent=2)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", default="corpus/corpus.jsonl")
    ap.add_argument("--pass", dest="pass_id", default="review")
    ap.add_argument("--out", default="sft")
    ap.add_argument("--max-prompt-bytes", type=int, default=128 * 1024,
                    help="drop examples whose rendered prompt exceeds this")
    ap.add_argument("--eval-fraction", type=float, default=0.1)
    ap.add_argument("--exclude-backends", default="local-qwen,glm,kimi,local",
                    help="comma-separated backend ids to exclude (default: the "
                         "baseline lanes we are trying to replace)")
    ap.add_argument("--require-admitted", action=argparse.BooleanOptionalAction, default=True)
    args = ap.parse_args()

    excluded = set(filter(None, args.exclude_backends.split(",")))
    drop = collections.Counter()
    kept = []

    with open(args.corpus) as f:
        for line in f:
            r = json.loads(line)
            if r["pass"] != args.pass_id:
                continue
            drop["candidates"] += 1
            if r["backend_id"] in excluded:
                drop["excluded_backend"] += 1
                continue
            if r["status"] != "complete":
                drop["status_not_complete"] += 1
                continue
            if args.require_admitted and not r["labels"]["admitted"]:
                drop["not_admitted"] += 1
                continue
            if not r["prompt_utf8_clean"] or r.get("prompt_truncated"):
                drop["prompt_not_clean"] += 1
                continue
            if r["prompt_bytes"] > args.max_prompt_bytes:
                drop["prompt_too_large"] += 1
                continue
            outputs = r["outputs"]
            if len(outputs) != 1:
                drop["not_single_output"] += 1
                continue
            (out_id, out), = outputs.items()
            if out.get("truncated") or not out.get("utf8_clean"):
                drop["output_not_clean"] += 1
                continue
            body = out["body"]
            if args.pass_id == "review":
                body = normalize_review_body(body)
                if body is None:
                    drop["review_verdict_unparseable"] += 1
                    continue
            kept.append(r | {"_out_id": out_id, "_out_body": body})
            drop["kept"] += 1

    kept.sort(key=lambda r: r["written_at"] or "")
    n_eval = max(1, int(len(kept) * args.eval_fraction)) if kept else 0

    # Candidate-aware split: dual-signal review means the same candidate
    # (identity, content_hash of the primary pinned input) is often reviewed
    # more than once. A whole candidate group lands on one side of the split —
    # newest groups (by their latest example) become eval — so no eval
    # candidate ever appears in train.
    def candidate_key(r):
        for i in r.get("inputs") or []:
            path = (i.get("path") or "").split("/", 1)[-1]
            if path in ("00-base-pin", "01-base") or path.startswith("02-work-graph"):
                continue
            if "diagnostic" in path:
                continue
            return (i.get("identity"), i.get("content_hash"))
        return (r["dispatch_id"], None)

    groups = collections.defaultdict(list)
    for r in kept:
        groups[candidate_key(r)].append(r)
    ordered = sorted(groups.values(), key=lambda g: max(r["written_at"] or "" for r in g))
    eval_rows, i = [], len(ordered)
    while len(eval_rows) < n_eval and i > 0:
        i -= 1
        eval_rows = [r for g in ordered[i:] for r in g]
    train_rows = [r for g in ordered[:i] for r in g]
    train_rows.sort(key=lambda r: r["written_at"] or "")
    eval_rows.sort(key=lambda r: r["written_at"] or "")
    splits = {"train": train_rows, "eval": eval_rows}

    os.makedirs(args.out, exist_ok=True)
    for name, rows in splits.items():
        path = os.path.join(args.out, f"{args.pass_id}.{name}.jsonl")
        with open(path, "w") as f:
            for r in rows:
                f.write(json.dumps({
                    "messages": [
                        {"role": "user", "content": r["prompt"]},
                        {"role": "assistant", "content": r["_out_body"]},
                    ],
                    "meta": {
                        "dispatch_id": r["dispatch_id"],
                        "run_ref": r["run_ref"],
                        "pass": r["pass"],
                        "backend_id": r["backend_id"],
                        "written_at": r["written_at"],
                        "output_id": r["_out_id"],
                        "prompt_bytes": r["prompt_bytes"],
                        "prompt_hash_verified": r["prompt_hash_verified"],
                    },
                }, ensure_ascii=False) + "\n")
        print(f"{path}: {len(rows)} examples")

    print(json.dumps(dict(drop), indent=2))
    by_backend = collections.Counter(r["backend_id"] for r in kept)
    print("kept by backend:", json.dumps(dict(by_backend.most_common()), indent=2))


if __name__ == "__main__":
    main()
