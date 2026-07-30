#!/usr/bin/env python3
"""Replay an SFT eval split against an OpenAI-compatible endpoint and score it.

Mirrors the production lane (cmd/striatum-openai-lane): one user message,
temperature 0.6, content extracted like the supervisor's stdout bridge
(fenced JSON block, else first parseable JSON value). By default requests
`chat_template_kwargs={"enable_thinking": false}` — the serving configuration
the fine-tuned lane will use — so before/after runs are apples-to-apples;
--think mirrors today's production lane (thinking on) instead.

Scores per example: JSON validity, verdict, exact-verdict match and
verdict-side match against the frontier reference, and (via analysis.json)
agreement with the candidate's adjudicated fate.

Resumable: existing dispatch_ids in the results file are skipped.

Usage:
  python3 eval.py --eval sft/review.eval.jsonl --analysis corpus/analysis.json \
      --out eval-runs/baseline-35b-nothink
"""

from __future__ import annotations

import argparse
import collections
import json
import os
import re
import time
import urllib.request

ACCEPTING = {"accept", "accept_with_findings"}
VERDICTS = {"accept", "accept_with_findings", "needs_revision", "reject"}


def extract_json(content: str):
    """Supervisor-bridge-style extraction: fenced block first, then the first
    parseable JSON value in the text."""
    for m in re.finditer(r"```(?:json)?\s*\n(.*?)```", content, re.DOTALL):
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            continue
    dec = json.JSONDecoder()
    for i, ch in enumerate(content):
        if ch in "{[":
            try:
                doc, _ = dec.raw_decode(content[i:])
                return doc
            except json.JSONDecodeError:
                continue
    return None


def side(verdict) -> str | None:
    if verdict in ACCEPTING:
        return "accepting"
    if verdict in VERDICTS:
        return "refusing"
    return None


def call(base_url, model, prompt, max_tokens, think, timeout):
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.6,
    }
    if not think:
        payload["chat_template_kwargs"] = {"enable_thinking": False}
    req = urllib.request.Request(
        base_url.rstrip("/") + "/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    started = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = json.load(resp)
    choice = (body.get("choices") or [{}])[0]
    usage = body.get("usage") or {}
    return {
        "content": (choice.get("message") or {}).get("content") or "",
        "finish_reason": choice.get("finish_reason"),
        "prompt_tokens": usage.get("prompt_tokens"),
        "completion_tokens": usage.get("completion_tokens"),
        "seconds": round(time.time() - started, 1),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--eval", default="sft/review.eval.jsonl")
    ap.add_argument("--analysis", default="corpus/analysis.json")
    ap.add_argument("--base-url", default="http://127.0.0.1:8081/v1")
    ap.add_argument("--model", default="qwen3.6-35b-a3b")
    ap.add_argument("--max-tokens", type=int, default=32768)
    ap.add_argument("--think", action="store_true",
                    help="leave model thinking on (mirrors today's production lane)")
    ap.add_argument("--timeout", type=int, default=1800)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--out", required=True, help="output directory")
    args = ap.parse_args()

    fate = {}
    if os.path.isfile(args.analysis):
        with open(args.analysis) as f:
            fate = {r["dispatch_id"]: r for r in json.load(f)["reviews"]}

    os.makedirs(args.out, exist_ok=True)
    results_path = os.path.join(args.out, "results.jsonl")
    done = set()
    if os.path.isfile(results_path):
        with open(results_path) as f:
            done = {json.loads(line)["dispatch_id"] for line in f}

    examples = []
    with open(args.eval) as f:
        for line in f:
            examples.append(json.loads(line))
    if args.limit:
        examples = examples[: args.limit]

    with open(results_path, "a") as out:
        for i, ex in enumerate(examples):
            did = ex["meta"]["dispatch_id"]
            if did in done:
                continue
            prompt = ex["messages"][0]["content"]
            reference = json.loads(ex["messages"][1]["content"])
            try:
                resp = call(args.base_url, args.model, prompt,
                            args.max_tokens, args.think, args.timeout)
                error = None
            except Exception as e:  # noqa: BLE001 — record and continue
                resp, error = {}, str(e)
            doc = extract_json(resp.get("content", "")) if not error else None
            verdict = doc.get("verdict") if isinstance(doc, dict) else None
            f = fate.get(did) or {}
            row = {
                "dispatch_id": did,
                "backend_reference": ex["meta"]["backend_id"],
                "error": error,
                "finish_reason": resp.get("finish_reason"),
                "seconds": resp.get("seconds"),
                "prompt_tokens": resp.get("prompt_tokens"),
                "completion_tokens": resp.get("completion_tokens"),
                "json_valid": isinstance(doc, dict),
                "verdict": verdict,
                "verdict_legal": verdict in VERDICTS,
                "reference_verdict": reference.get("verdict"),
                "verdict_exact_match": verdict == reference.get("verdict"),
                "side_match": side(verdict) is not None
                and side(verdict) == side(reference.get("verdict")),
                "fate": f.get("fate"),
                "agrees_with_fate": (
                    None if f.get("fate") not in ("final", "revised") or side(verdict) is None
                    else side(verdict) == ("accepting" if f["fate"] == "final" else "refusing")
                ),
                "raw_content_head": (resp.get("content") or "")[:2000],
            }
            out.write(json.dumps(row, ensure_ascii=False) + "\n")
            out.flush()
            print(f"[{i + 1}/{len(examples)}] {did[:12]} verdict={verdict} "
                  f"ref={reference.get('verdict')} {resp.get('seconds')}s", flush=True)

    # Summary over the current eval set only (the results file may hold rows
    # from an earlier revision of the split; those are kept but not scored).
    current = {ex["meta"]["dispatch_id"] for ex in examples}
    rows = [r for line in open(results_path)
            if (r := json.loads(line))["dispatch_id"] in current]
    n = len(rows)
    scored_fate = [r for r in rows if r["agrees_with_fate"] is not None]
    summary = {
        "model": args.model,
        "think": args.think,
        "n": n,
        "errors": sum(1 for r in rows if r["error"]),
        "json_valid": sum(1 for r in rows if r["json_valid"]) / n if n else None,
        "verdict_legal": sum(1 for r in rows if r["verdict_legal"]) / n if n else None,
        "verdict_exact_match": sum(1 for r in rows if r["verdict_exact_match"]) / n if n else None,
        "side_match": sum(1 for r in rows if r["side_match"]) / n if n else None,
        "fate_agreement": (
            sum(1 for r in scored_fate if r["agrees_with_fate"]) / len(scored_fate)
            if scored_fate else None
        ),
        "fate_scored": len(scored_fate),
        "verdict_distribution": dict(collections.Counter(str(r["verdict"]) for r in rows)),
        "mean_seconds": round(
            sum(r["seconds"] or 0 for r in rows) / n, 1) if n else None,
    }
    with open(os.path.join(args.out, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
