"""Report coder agreement, optionally compared with an explicit reference file."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from caplab.code_agreement import build_code_agreement_report, build_code_reference_report
from caplab.codex_events import CodexEventError, parse_native_json


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="caplab-code-agreement-input/1 JSON")
    parser.add_argument("--reference", type=Path, help="caplab-code-reference-input/1 JSON")
    args = parser.parse_args()
    try:
        raw = args.input.read_bytes()
        document = parse_native_json(raw.decode("utf-8"))
        if args.reference is None:
            report = build_code_agreement_report(document)
        else:
            reference_raw = args.reference.read_bytes()
            reference = parse_native_json(reference_raw.decode("utf-8"))
            report = build_code_reference_report(document, reference)
            report["reference_sha256"] = hashlib.sha256(reference_raw).hexdigest()
    except (OSError, UnicodeError, CodexEventError, ValueError) as error:
        parser.error(str(error))
    report["input_sha256"] = hashlib.sha256(raw).hexdigest()
    print(json.dumps(report, indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
