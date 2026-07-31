"""Complete the private fate gate locally after artifact recovery."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .contract import ContractError
from .evaluate import side
from .runtime import training_config


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--analysis", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    fate = {
        item["dispatch_id"]: item
        for item in json.loads(args.analysis.read_text())["reviews"]
    }
    rows = [json.loads(line) for line in args.results.read_text().splitlines()]
    scored = []
    for row in rows:
        disposition = fate.get(row["dispatch_id"], {}).get("fate")
        if disposition not in ("final", "revised") or side(row.get("verdict")) is None:
            continue
        agrees = side(row["verdict"]) == (
            "accepting" if disposition == "final" else "refusing"
        )
        scored.append(agrees)
    if len(scored) != 85:
        raise ContractError(f"expected 85 fate-scored examples, found {len(scored)}")
    agreement = sum(scored) / len(scored)
    baseline = training_config()["quality_gate"]["strictly_beat"]["fate_agreement"]
    receipt = {
        "protocol": "striatum-local-fate-gate/1",
        "fate_scored": len(scored),
        "fate_agreement": agreement,
        "baseline": baseline,
        "passed": agreement > baseline,
    }
    args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    if not receipt["passed"]:
        raise ContractError("fate agreement did not strictly beat the 35B baseline")


if __name__ == "__main__":
    main()
