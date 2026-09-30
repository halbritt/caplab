"""Copy frozen labels into a new runnable spec with explicit adapter paths."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cairn-binary", type=Path)
    parser.add_argument("--cairn-checkout", type=Path)
    args = parser.parse_args(argv)
    if bool(args.cairn_binary) != bool(args.cairn_checkout):
        parser.error("give both --cairn-binary and --cairn-checkout, or neither")
    spec = json.loads(Path(__file__).with_name("spec.json").read_text(encoding="utf-8"))
    if args.cairn_binary is not None:
        spec["experiment_id"] = "retrieval-cairn-lexical-v1"
        spec["arms"] = [{"id": "cairn-lexical", "adapter": "cairn", "configuration": {
            "binary": str(args.cairn_binary.resolve()), "checkout": str(args.cairn_checkout.resolve()),
            "semantic_mode": "off"}}]
    else:
        for arm in spec["arms"]:
            arm["configuration"]["argv"][:2] = [sys.executable, str(Path(__file__).with_name("fixture.py").resolve())]
    try:
        with args.output.open("x", encoding="utf-8") as destination:
            json.dump(spec, destination, ensure_ascii=False, indent=2, allow_nan=False)
            destination.write("\n")
    except OSError as error:
        print(f"cannot create new spec: {error.strerror}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
