"""Inspect declared capture slots without substituting zero for unavailable pairs."""

import argparse
import json
from pathlib import Path

from caplab.capture_accounting import build_capture_population_report
from caplab.task_capture_verify import CaptureVerificationError


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--policy', type=Path, required=True)
    parser.add_argument('--expected-input-sha256', required=True)
    parser.add_argument('--max-input-bytes', type=int, required=True)
    parser.add_argument('--max-slots', type=int, required=True)
    parser.add_argument('--max-receipt-bytes', type=int, required=True)
    args = parser.parse_args()
    try:
        if args.max_input_bytes <= 0:
            raise CaptureVerificationError('input byte allowance must be positive')
        with args.input.open('rb') as stream:
            content = stream.read(args.max_input_bytes + 1)
        report = build_capture_population_report(args.policy, content,
            expected_input_sha256=args.expected_input_sha256, max_input_bytes=args.max_input_bytes,
            max_slots=args.max_slots, max_receipt_bytes=args.max_receipt_bytes)
    except (CaptureVerificationError, OSError) as error:
        parser.error(str(error))
    print(json.dumps(report, indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
