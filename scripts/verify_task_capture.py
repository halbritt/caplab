"""Inspect task capture integrity against an independently retained attempt digest."""

import argparse
import json
from pathlib import Path

from caplab.task_capture_verify import CaptureVerificationError, verify_task_capture


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("custody", type=Path)
    parser.add_argument("--expected-attempt-sha256", required=True)
    parser.add_argument("--max-receipt-bytes", required=True, type=int)
    args = parser.parse_args()
    try:
        report = verify_task_capture(args.custody, expected_attempt_sha256=args.expected_attempt_sha256,
                                     max_receipt_bytes=args.max_receipt_bytes)
    except (CaptureVerificationError, OSError) as error:
        parser.error(str(error))
    print(json.dumps(report, indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
