#!/usr/bin/env python3
"""Probe-gated resume for a pool run against a flaky endpoint.

`run_pool` aborts after a streak of empty lanes. That guard is right — it
stops a sweep from burning budget against a dead endpoint — but the agy
backend takes intermittent multi-minute outages, and a blip that trips the
guard is not a dead endpoint. This supervisor tells the two apart by asking:
it probes the adapter with a trivial prompt, and only resumes when the
endpoint answers.

Between attempts it releases the cases the outage killed. `run_pool` builds
its skip-set from every dispatch_id in results.jsonl, failures included, so
resuming without this would silently retire those cases -- recording a runner
failure as though the subject had been asked and had nothing to say. The
failed rows are appended to a sidecar so the telemetry survives.

Usage:
  supervise_sweep.py <backend> <out_dir> [--attempts N]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "src"))

from caplab.advisory.pool_runner import (  # noqa: E402
    invoke, load_declaration, run_pool)

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
BACKENDS = os.path.expanduser("~/git/striatum-next/backends")
REGISTRY = os.path.join(REPO, "advisory", "substrates.jsonl")
ANCHORS = os.path.join(REPO, "advisory", "anchor-set.json")

# The sweep's identity defaults. Every attempt must use the same values, or
# the resumed rows would not belong to the same measurement — they are
# arguments (not per-attempt state) for exactly that reason, and the defaults
# reproduce the 20260819 breadth sweep this script was written for.
SWEEP_DEFAULTS = dict(sweep_seed=20260819, per_operator=4, max_cases=60,
                      partition="open", replicates=3, mutant_replicates=1,
                      workers=2)

QUOTA_MARKERS = ("usage limit", "quota", "rate limit exceeded",
                 "resource_exhausted")


def probe(adapter: dict, timeout: int = 180) -> tuple[bool, str]:
    """Is the endpoint answering at all? Returns (alive, detail)."""
    try:
        result = invoke(adapter, "Reply with exactly: PROBE-OK", timeout)
    except Exception as exc:                      # noqa: BLE001
        return False, f"probe raised {exc!r}"
    head = (result.get("raw_head") or "")
    lowered = head.lower()
    for marker in QUOTA_MARKERS:
        if marker in lowered:
            return False, f"endpoint reports {marker!r}: {head[:160]}"
    if result.get("exit_code") == 0 and head:
        return True, "alive"
    return False, (f"exit={result.get('exit_code')} "
                   f"timed_out={result.get('timed_out')} head={head[:160]!r}")


def release_failures(out_dir: str) -> int:
    """Keep only usable rows; park the rest so their cases are re-measured."""
    path = os.path.join(out_dir, "results.jsonl")
    if not os.path.isfile(path):
        return 0
    with open(path, encoding="utf-8") as f:
        rows = [json.loads(line) for line in f if line.strip()]
    keep = [r for r in rows if r.get("usable")]
    released = [r for r in rows if not r.get("usable")]
    if not released:
        return 0
    with open(os.path.join(out_dir, "results.jsonl.released"), "a",
              encoding="utf-8") as f:
        for row in released:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    with open(path, "w", encoding="utf-8") as f:
        for row in keep:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    return len(released)


def usable_count(out_dir: str) -> int:
    path = os.path.join(out_dir, "results.jsonl")
    if not os.path.isfile(path):
        return 0
    with open(path, encoding="utf-8") as f:
        return sum(1 for line in f if line.strip()
                   and json.loads(line).get("usable"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("backend")
    ap.add_argument("out_dir")
    ap.add_argument("--attempts", type=int, default=25)
    ap.add_argument("--target", type=int, default=69)
    ap.add_argument("--probe-retries", type=int, default=10)
    ap.add_argument("--probe-wait", type=int, default=600)
    ap.add_argument("--timeout", type=int, default=1800)
    ap.add_argument("--sweep-seed", type=int,
                    default=SWEEP_DEFAULTS["sweep_seed"])
    ap.add_argument("--per-operator", type=int,
                    default=SWEEP_DEFAULTS["per_operator"])
    ap.add_argument("--max-cases", type=int,
                    default=SWEEP_DEFAULTS["max_cases"])
    ap.add_argument("--cases", default=None,
                    help="targeted-cell document; see pool-run --cases")
    args = ap.parse_args()
    sweep = dict(SWEEP_DEFAULTS, sweep_seed=args.sweep_seed,
                 per_operator=args.per_operator, max_cases=args.max_cases)

    adapter = load_declaration(BACKENDS, args.backend)["adapter"]
    stalled = 0
    for attempt in range(1, args.attempts + 1):
        have = usable_count(args.out_dir)
        if have >= args.target:
            print(f"[{args.backend}] complete: {have}/{args.target} usable",
                  flush=True)
            return 0

        alive = False
        for probe_try in range(1, args.probe_retries + 1):
            alive, detail = probe(adapter)
            print(f"[{args.backend}] probe {probe_try}: {detail}", flush=True)
            if alive:
                break
            # A quota wall is not something waiting a few minutes fixes, and
            # a supervisor that hammers one is worse than one that stops.
            if "usage limit" in detail or "quota" in detail:
                print(f"[{args.backend}] endpoint is quota-walled; stopping "
                      f"at {have}/{args.target}", flush=True)
                return 3
            time.sleep(args.probe_wait)
        if not alive:
            print(f"[{args.backend}] endpoint never answered; stopping at "
                  f"{have}/{args.target}", flush=True)
            return 4

        released = release_failures(args.out_dir)
        print(f"[{args.backend}] attempt {attempt}: {have} usable, "
              f"{released} case(s) released for re-measurement", flush=True)
        summary = run_pool(backend=args.backend, backends_root=BACKENDS,
                           registry_path=REGISTRY, out_dir=args.out_dir,
                           anchor_path=ANCHORS, timeout=args.timeout,
                           cases_path=args.cases, **sweep)
        now = usable_count(args.out_dir)
        print(f"[{args.backend}] attempt {attempt} ended: "
              f"aborted={summary.get('aborted')!r} usable {have} -> {now}",
              flush=True)
        stalled = stalled + 1 if now <= have else 0
        if stalled >= 3:
            print(f"[{args.backend}] three attempts added nothing; stopping "
                  f"at {now}/{args.target}", flush=True)
            return 5
    print(f"[{args.backend}] attempts exhausted at "
          f"{usable_count(args.out_dir)}/{args.target}", flush=True)
    return 6


if __name__ == "__main__":
    raise SystemExit(main())
