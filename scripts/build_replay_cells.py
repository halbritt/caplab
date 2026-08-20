#!/usr/bin/env python3
"""Build a targeted-cell document from contrast files' discordant cases.

The promotion gate withholds every separator seen in only one sweep, and the
seeded sampler cannot revisit them (2 of 57 cells recurred across two
independent seeds). This emits the withheld cells as a `--cases` document for
a targeted-reproduction pool run: same (substrate, defect class) cells, fresh
injections under the new sweep seed.

Usage:
  python3 scripts/build_replay_cells.py --out advisory/replay/NAME.json \
      advisory/comparisons/A.json [advisory/comparisons/B.json ...]

Cells are deduplicated on (substrate_id, operator) across the input
contrasts; provenance records which contrast(s) and sweep seed(s) each cell
separated in, and in which direction.
"""

from __future__ import annotations

import argparse
import json
import os


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("contrasts", nargs="+")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    cells: dict[tuple, dict] = {}
    pairs = set()
    for path in args.contrasts:
        with open(path, encoding="utf-8") as f:
            doc = json.load(f)
        pairs.add((doc["a"], doc["b"]))
        for entry in doc.get("discordant_cases") or []:
            key = (entry["substrate_id"], entry["defect_class"])
            cell = cells.setdefault(key, {
                "substrate_id": entry["substrate_id"],
                "operator": entry["defect_class"],
                "separated_in": []})
            cell["separated_in"].append({
                "contrast": os.path.basename(path),
                "sweep_seed": doc.get("sweep_seed"),
                "caught_by": doc[entry["caught_by"]]})
    if len(pairs) != 1:
        raise SystemExit(f"contrasts span {len(pairs)} Binding pairs; a "
                         f"targeted set reproduces one pair: {sorted(pairs)}")
    pair = pairs.pop()
    document = {
        "record": "caplab-targeted-cells/1",
        "purpose": ("targeted reproduction for the promotion gate; runs on "
                    "these cells are outcome-selected and never claim-grade"),
        "pair": list(pair),
        "source_contrasts": [os.path.basename(p) for p in args.contrasts],
        "cells": sorted(cells.values(),
                        key=lambda c: (c["substrate_id"], c["operator"])),
    }
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(document, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")
    print(json.dumps({"out": args.out, "cells": len(document["cells"]),
                      "pair": document["pair"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
