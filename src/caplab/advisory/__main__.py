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

    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
