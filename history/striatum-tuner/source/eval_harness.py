#!/usr/bin/env python3
"""Replay the held-out review split through a backend's DECLARED adapter command.

The endpoint runner (eval.py) can only measure tuples the fleet reaches over
HTTP. A tuple with a coding harness configured — claude-code/claude-harm, codex,
agy — must be measured through that harness, never by pointing the eval at the
same model on an aggregator: same weights, different lane (different system
prompt, tool surface, and output discipline), so the number would describe a
lane that does not exist. Principal ruling, 2026-08-07: "don't use OpenRouter
for lanes that have a coding harness configured."

So this runner reads backends/<id>/backend.yaml, invokes `adapter.command` the
way the supervisor does (prompt on `prompt_mode`: arg or stdin), captures
stdout, and scores it with eval.py's own functions — identical extraction and
identical metrics, so harness rows and endpoint rows are comparable.

Usage:
  python3 eval_harness.py --backend codex-terra-high \
      --backends-root ~/git/striatum-next/backends \
      --eval sft/review.eval.jsonl --analysis corpus/analysis.json \
      --limit 25 --out eval-runs/harness-codex-terra-high
"""

from __future__ import annotations

import argparse
import collections
import json
import os
import subprocess
import time

import yaml

from eval import VERDICTS, extract_json, side


def load_declaration(backends_root: str, backend_id: str) -> dict:
    path = os.path.join(backends_root, backend_id, "backend.yaml")
    with open(path) as f:
        declaration = yaml.safe_load(f)
    if declaration.get("id") != backend_id:
        raise SystemExit(f"eval_harness: {path} declares id {declaration.get('id')!r}")
    return declaration


def invoke(declaration: dict, prompt: str, timeout: int, workspace: str) -> dict:
    """Run the declared adapter command exactly as the supervisor would.

    A coding-harness lane does not print its artifact: it WRITES the declared
    output file into the workspace and prints a summary line ("Review ledger
    written: outputs/review-ledger — verdict: accept"). Only stdout-only lanes
    (`stdout_output: single-required-output`, e.g. striatum-openai-lane) put the
    document on stdout. Scoring stdout for a harness lane measures the summary
    sentence, not the review — so run each example in its own workspace and
    read the produced output file, falling back to stdout for stdout-only lanes.
    """
    adapter = declaration.get("adapter") or {}
    command = adapter.get("command")
    if not command:
        raise SystemExit("eval_harness: declaration has no adapter.command")
    mode = adapter.get("prompt_mode", "stdin")
    argv = list(command)
    stdin_data = None
    if mode == "arg":
        argv.append(prompt)
    elif mode == "stdin":
        stdin_data = prompt
    else:
        raise SystemExit(f"eval_harness: unsupported prompt_mode {mode!r}")

    started = time.time()
    try:
        completed = subprocess.run(
            argv,
            input=stdin_data,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=workspace,
        )
        stdout, code, stderr = completed.stdout, completed.returncode, completed.stderr
    except subprocess.TimeoutExpired:
        stdout, code, stderr = "", -1, f"timeout after {timeout}s"

    content, source = stdout or "", "stdout"
    if adapter.get("stdout_output") != "single-required-output":
        produced = None
        outputs_dir = os.path.join(workspace, "outputs")
        if os.path.isdir(outputs_dir):
            candidates = sorted(
                (os.path.join(outputs_dir, name) for name in os.listdir(outputs_dir)),
                key=os.path.getmtime,
            )
            produced = candidates[-1] if candidates else None
        if produced:
            with open(produced, errors="replace") as f:
                content, source = f.read(), os.path.relpath(produced, workspace)
    return {
        "content": content,
        "content_source": source,
        "stdout_head": (stdout or "")[:300],
        "finish_reason": "exit-0" if code == 0 else f"exit-{code}",
        "exit_code": code,
        "stderr_head": (stderr or "")[:500],
        "seconds": round(time.time() - started, 1),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", required=True, help="backend id (directory under --backends-root)")
    ap.add_argument("--backends-root", default=os.path.expanduser("~/git/striatum-next/backends"))
    ap.add_argument("--eval", default="sft/review.eval.jsonl")
    ap.add_argument("--analysis", default="corpus/analysis.json")
    ap.add_argument("--timeout", type=int, default=1800)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--out", required=True, help="output directory")
    args = ap.parse_args()

    declaration = load_declaration(args.backends_root, args.backend)
    if declaration.get("status", "accepted") != "accepted":
        print(f"note: {args.backend} is status {declaration.get('status')!r} — measuring anyway")

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
                workspace = os.path.join(args.out, "workspaces", did[:12])
                os.makedirs(workspace, exist_ok=True)
                resp = invoke(declaration, prompt, args.timeout, workspace)
                error = None if resp["exit_code"] == 0 else resp["stderr_head"]
            except Exception as e:  # noqa: BLE001 — record and continue
                resp, error = {}, str(e)
            doc = extract_json(resp.get("content", ""))
            verdict = doc.get("verdict") if isinstance(doc, dict) else None
            f = fate.get(did) or {}
            row = {
                "dispatch_id": did,
                "backend_reference": ex["meta"]["backend_id"],
                "backend_measured": args.backend,
                "error": error,
                "finish_reason": resp.get("finish_reason"),
                "content_source": resp.get("content_source"),
                "stdout_head": resp.get("stdout_head"),
                "seconds": resp.get("seconds"),
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

    current = {ex["meta"]["dispatch_id"] for ex in examples}
    rows = [r for line in open(results_path)
            if (r := json.loads(line))["dispatch_id"] in current]
    n = len(rows)
    scored_fate = [r for r in rows if r["agrees_with_fate"] is not None]
    summary = {
        "backend": args.backend,
        "lane": "declared-adapter-command",
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
        "mean_seconds": round(sum(r["seconds"] or 0 for r in rows) / n, 1) if n else None,
    }
    with open(os.path.join(args.out, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
