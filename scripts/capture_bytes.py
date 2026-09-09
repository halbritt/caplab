"""Report retained capture bytes by surface against independent receipt anchors."""

import argparse
import json
from pathlib import Path

from caplab.capture_accounting import build_capture_byte_report
from caplab.task_capture_verify import CaptureVerificationError


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task_custody", type=Path)
    parser.add_argument("collection_custody", type=Path)
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--expected-attempt-sha256", required=True)
    parser.add_argument("--expected-collection-sha256", required=True)
    parser.add_argument("--max-receipt-bytes", type=int, required=True)
    args = parser.parse_args()
    try:
        report = build_capture_byte_report(args.policy, args.task_custody, args.collection_custody,
            expected_attempt_sha256=args.expected_attempt_sha256,
            expected_collection_sha256=args.expected_collection_sha256,
            max_receipt_bytes=args.max_receipt_bytes)
    except (CaptureVerificationError, OSError) as error:
        parser.error(str(error))
    print(json.dumps(report, indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
