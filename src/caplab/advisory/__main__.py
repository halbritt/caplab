"""caplab.advisory CLI.

  python3 -m caplab.advisory seed --runs-root ... --backends-root ...
  python3 -m caplab.advisory export --out advisory/caplab-advisory-export.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys

from .claims import Ledger
from .export import write_export
from .seed import seed_claims

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))
DEFAULT_LEDGER = os.path.join(REPO_ROOT, "advisory", "claims.jsonl")
DEFAULT_RUNS = os.path.expanduser("~/git/striatum-tuner/eval-runs")
DEFAULT_BACKENDS = os.path.expanduser("~/git/striatum-next/backends")


def cmd_seed(args):
    result = seed_claims(args.runs_root, args.backends_root)
    ledger = Ledger(args.ledger)
    outcome = ledger.append(result["claims"])
    print(json.dumps({
        "claims_built": len(result["claims"]),
        "skipped_incomplete_runs": result["skipped_incomplete"],
        **outcome,
    }, indent=2))


def cmd_export(args):
    write_export(Ledger(args.ledger), args.out)
    print(f"wrote {args.out}")


def cmd_run(args):
    from .executor import claims_from_runs, run_advisory

    receipt = run_advisory(
        backend=args.backend, pairs=args.pairs, out_dir=args.out,
        seed=args.seed, workers=args.workers, timeout=args.timeout,
        max_pairs=args.max_pairs)
    print(json.dumps(receipt, indent=2))
    if not receipt["completed"]:
        print("run did not complete; no claims derived", file=sys.stderr)
        return 2
    if args.claim:
        claims = claims_from_runs([args.out], args.backends_root)
        print(json.dumps(Ledger(args.ledger).append(claims), indent=2))
    return 0


def cmd_claim_runs(args):
    from .executor import claims_from_runs

    claims = claims_from_runs(args.run_dirs, args.backends_root)
    print(json.dumps(Ledger(args.ledger).append(claims), indent=2))


def cmd_sweep(args):
    """Plan (and optionally execute) stale-claim re-measurement."""
    import datetime as _dt

    with open(args.config, encoding="utf-8") as f:
        config = json.load(f)
    ledger = Ledger(args.ledger)
    freshest: dict[str, str] = {}
    for claim in ledger.read():
        subject = claim["subject"]["source_id"]
        if claim["as_of"] > freshest.get(subject, ""):
            freshest[subject] = claim["as_of"]
    now = _dt.datetime.now(_dt.timezone.utc)
    horizon = now - _dt.timedelta(days=config["freshness_days"])

    supervised = set(config["population"]["supervised_only_runtimes"])
    planned, deferred = [], []
    subjects = sorted(freshest) + [
        c["binding"] for c in config.get("challengers", [])
        if c["binding"] not in freshest]
    for subject in subjects:
        as_of = freshest.get(subject)
        if as_of and _dt.datetime.fromisoformat(
                as_of.replace("Z", "+00:00")) >= horizon:
            continue
        runtime = None
        declaration = os.path.join(args.backends_root, subject, "backend.yaml")
        if os.path.isfile(declaration):
            import yaml
            with open(declaration, encoding="utf-8") as f:
                runtime = (yaml.safe_load(f) or {}).get("runtime_id")
        entry = {"binding": subject, "runtime": runtime,
                 "stale_since": as_of or "(never measured)",
                 "pairs": config["default_pairs"]}
        if runtime is None:
            entry["skip"] = "no current declaration"
            deferred.append(entry)
        elif runtime in supervised:
            entry["skip"] = "supervised-only runtime"
            deferred.append(entry)
        else:
            planned.append(entry)
    plan = {"planned": planned, "deferred": deferred,
            "execute": bool(args.execute)}
    print(json.dumps(plan, indent=2))
    if not args.execute:
        return 0
    from .executor import claims_from_runs, run_advisory

    stamp = now.strftime("%Y%m%d")
    for entry in planned:
        out_dir = os.path.join(REPO_ROOT, "advisory", "runs",
                               f"sweep-{entry['binding']}-{stamp}")
        receipt = run_advisory(
            backend=entry["binding"], pairs=entry["pairs"], out_dir=out_dir,
            max_pairs=config["max_pairs"])
        print(json.dumps(receipt, indent=2))
        if receipt["completed"]:
            claims = claims_from_runs([out_dir], args.backends_root)
            print(json.dumps(ledger.append(claims), indent=2))
    return 0


def cmd_harvest(args):
    import subprocess

    from .corpus import SubstrateRegistry, harvest_docs, harvest_exchange

    registry = SubstrateRegistry(args.registry)
    substrates = []
    if args.exchange and args.analysis:
        substrates += harvest_exchange(args.exchange, args.analysis)
    for repo in args.doc_repo or []:
        commit = subprocess.run(["git", "-C", repo, "rev-parse", "HEAD"],
                                capture_output=True, text=True,
                                check=True).stdout.strip()
        substrates += harvest_docs(
            repo, ["rfcs/*/*.md", "decisions/*.md", "docs/**/*.md"], commit)
    print(json.dumps(registry.append(substrates), indent=2))


def cmd_calibrate(args):
    from .calibrate import calibrate_case, load_substrate_body
    from .corpus import SubstrateRegistry, sample_cases

    substrates = SubstrateRegistry(args.registry).read()
    cases = sample_cases(substrates, sweep_seed=args.seed,
                         per_operator=args.per_operator)
    repos = {}
    for repo in args.doc_repo or []:
        repos[os.path.basename(os.path.normpath(repo))] = repo
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    counts = {}
    with open(args.out, "a", encoding="utf-8") as f:
        for i, case in enumerate(cases):
            body = load_substrate_body(case, args.exchange, repos)
            if body is None:
                row = {"case": case, "status": "substrate-unreachable"}
            else:
                row = calibrate_case(case, body)
            counts[row["status"]] = counts.get(row["status"], 0) + 1
            flag = row.get("difficulty_flag", "")
            print(f"[{i+1}/{len(cases)}] {case['operator']:26} "
                  f"{row['status']} {flag}", flush=True)
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
            f.flush()
    print(json.dumps(counts, indent=2))


def cmd_validate_pending(args):
    from .calibrate import (load_substrate_body, strong_reviewer_from_declaration,
                            validate_pending)

    repos = {os.path.basename(os.path.normpath(r)): r
             for r in args.doc_repo or []}

    def load_body(case):
        return load_substrate_body(case, args.exchange, repos)

    reviewer = strong_reviewer_from_declaration(args.backends_root, args.reference)
    rows = validate_pending(args.calibration, reviewer, load_body)
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    counts = {}
    with open(args.out, "a", encoding="utf-8") as f:
        for row in rows:
            counts[row.get("difficulty_flag", row["status"])] = \
                counts.get(row.get("difficulty_flag", row["status"]), 0) + 1
            print(f"{row['case']['operator']:26} "
                  f"{row.get('difficulty_flag', row['status'])}", flush=True)
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
            f.flush()
    print(json.dumps(counts, indent=2))


def main(argv=None):
    ap = argparse.ArgumentParser(prog="caplab.advisory")
    ap.add_argument("--ledger", default=DEFAULT_LEDGER)
    sub = ap.add_subparsers(dest="command", required=True)

    p = sub.add_parser("seed", help="admit the historical tuner sweep as seed claims")
    p.add_argument("--runs-root", default=DEFAULT_RUNS)
    p.add_argument("--backends-root", default=DEFAULT_BACKENDS)
    p.set_defaults(fn=cmd_seed)

    p = sub.add_parser("export", help="write the caplab-advisory-export/1 document")
    p.add_argument("--out", default=os.path.join(
        REPO_ROOT, "advisory", "caplab-advisory-export.json"))
    p.set_defaults(fn=cmd_export)

    p = sub.add_parser("run", help="CAPLAB-directed advisory-grade matched-pair run")
    p.add_argument("--backend", required=True)
    p.add_argument("--pairs", type=int, required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--seed", type=int, default=20260815)
    p.add_argument("--workers", type=int, default=2)
    p.add_argument("--timeout", type=int, default=1800)
    p.add_argument("--max-pairs", type=int, default=21,
                   help="hard refusal bound; the authorized budget, not a hint")
    p.add_argument("--backends-root", default=DEFAULT_BACKENDS)
    p.add_argument("--claim", action="store_true",
                   help="derive and append caplab-advisory claims on completion")
    p.set_defaults(fn=cmd_run)

    p = sub.add_parser("claim-runs", help="score existing CAPLAB-directed runs into claims")
    p.add_argument("run_dirs", nargs="+")
    p.add_argument("--backends-root", default=DEFAULT_BACKENDS)
    p.set_defaults(fn=cmd_claim_runs)

    p = sub.add_parser("sweep", help="plan (default) or execute stale-claim re-measurement")
    p.add_argument("--config", default=os.path.join(
        REPO_ROOT, "advisory", "sweep-config.json"))
    p.add_argument("--backends-root", default=DEFAULT_BACKENDS)
    p.add_argument("--execute", action="store_true",
                   help="actually run the planned AFK-eligible measurements")
    p.set_defaults(fn=cmd_sweep)

    default_exchange = os.path.expanduser(
        "~/.local/share/striatum/exchange/019f22ef-0cb4-780f-9b82-b210bab24325")
    p = sub.add_parser("harvest", help="harvest substrates into the registry")
    p.add_argument("--registry", default=os.path.join(
        REPO_ROOT, "advisory", "substrates.jsonl"))
    p.add_argument("--exchange", default=default_exchange)
    p.add_argument("--analysis", default=os.path.expanduser(
        "~/git/striatum-tuner/corpus/analysis.json"))
    p.add_argument("--doc-repo", action="append")
    p.set_defaults(fn=cmd_harvest)

    p = sub.add_parser("calibrate", help="calibrate sampled cases vs the weak reference")
    p.add_argument("--registry", default=os.path.join(
        REPO_ROOT, "advisory", "substrates.jsonl"))
    p.add_argument("--exchange", default=default_exchange)
    p.add_argument("--doc-repo", action="append")
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--per-operator", type=int, default=2)
    p.add_argument("--out", required=True)
    p.set_defaults(fn=cmd_calibrate)

    p = sub.add_parser("validate-pending",
                       help="run pending calibration cases against a strong reference")
    p.add_argument("--calibration", required=True)
    p.add_argument("--reference", default="claude-fable-5-high")
    p.add_argument("--backends-root", default=DEFAULT_BACKENDS)
    p.add_argument("--exchange", default=default_exchange)
    p.add_argument("--doc-repo", action="append")
    p.add_argument("--out", required=True)
    p.set_defaults(fn=cmd_validate_pending)

    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
