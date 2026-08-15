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

    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
