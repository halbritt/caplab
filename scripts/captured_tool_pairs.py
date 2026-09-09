#!/usr/bin/env python3
"""Inspect tool-pair availability through an independently anchored task capture."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from caplab.native_tool_pairs import FORMATS, inspect_captured_tool_pairs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("custody", type=Path)
    parser.add_argument("--expected-attempt-sha256", required=True)
    parser.add_argument("--format", choices=FORMATS, required=True)
    parser.add_argument("--expected-root-id", required=True)
    parser.add_argument("--max-receipt-bytes", type=int, required=True)
    parser.add_argument("--max-event-bytes", type=int, required=True)
    args = parser.parse_args()
    try:
        report = inspect_captured_tool_pairs(args.custody,
            expected_attempt_sha256=args.expected_attempt_sha256, format=args.format,
            expected_root_id=args.expected_root_id, max_receipt_bytes=args.max_receipt_bytes,
            max_event_bytes=args.max_event_bytes)
    except (ValueError, OSError) as error:
        parser.error(str(error))
    print(json.dumps(report, indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
