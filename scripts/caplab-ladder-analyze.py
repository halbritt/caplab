#!/usr/bin/env python3
"""Recompute an advisory-selection ladder from append-only custody."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from caplab.ladder_analysis import LadderAnalysisError, analyze_ladder


def _json_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _save_idempotent(path: Path, value: object) -> None:
    encoded = _json_bytes(value)
    if path.exists():
        if path.read_bytes() != encoded:
            raise LadderAnalysisError(
                f"refusing to replace different analysis evidence: {path}"
            )
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as output:
            output.write(encoded)
    except BaseException:
        path.unlink(missing_ok=True)
        raise


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign-root", type=Path, required=True)
    parser.add_argument(
        "--score-root",
        action="append",
        type=Path,
        required=True,
        help="rater output root; repeat for each scoring wave",
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--threshold", type=float, default=0.35)
    return parser


def main() -> int:
    arguments = _parser().parse_args()
    try:
        result = analyze_ladder(
            arguments.campaign_root,
            arguments.score_root,
            threshold=arguments.threshold,
        )
        _save_idempotent(arguments.output, result)
    except (LadderAnalysisError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    for item in result["tuple_results"]:
        print(
            f"{item['tuple']:13} "
            f"none={item['none_mean']:.3f} "
            f"delta={item['delta']:+.3f} "
            f"mde={item['empirical_mde']:.3f} "
            f"bar={item['operative_bar']:.3f} "
            f"measurable={str(item['measurable']).lower()}"
        )
    print(f"conclusion: {result['conclusion']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
