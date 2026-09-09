#!/usr/bin/env python3
"""Inspect one bounded, independently hash-identified native stdout file."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from caplab.native_tool_pairs import FORMATS, build_native_tool_pair_report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--format", choices=FORMATS, required=True)
    parser.add_argument("--expected-sha256", required=True)
    parser.add_argument("--expected-root-id", required=True)
    parser.add_argument("--max-bytes", type=int, required=True)
    args = parser.parse_args()
    if args.max_bytes <= 0:
        parser.error("--max-bytes must be positive")
    with args.source.open("rb") as source:
        content = source.read(args.max_bytes + 1)
    report = build_native_tool_pair_report(content, format=args.format,
        expected_sha256=args.expected_sha256, expected_root_id=args.expected_root_id,
        max_bytes=args.max_bytes)
    print(json.dumps(report, indent=2, ensure_ascii=True, allow_nan=False))


if __name__ == "__main__":
    main()
