"""Inspect native collection integrity against an independently retained digest."""

import argparse
import json
from pathlib import Path

from caplab.native_collection_verify import verify_native_collection
from caplab.task_capture_verify import CaptureVerificationError


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("custody", type=Path)
    parser.add_argument("--policy", required=True, type=Path)
    parser.add_argument("--expected-collection-sha256", required=True)
    parser.add_argument("--max-receipt-bytes", required=True, type=int)
    args = parser.parse_args()
    try:
        report = verify_native_collection(args.policy, args.custody,
            expected_collection_sha256=args.expected_collection_sha256, max_receipt_bytes=args.max_receipt_bytes)
    except (CaptureVerificationError, OSError) as error:
        parser.error(str(error))
    print(json.dumps(report, indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
