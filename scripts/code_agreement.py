"""Read one explicit input file and print a descriptive agreement report."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from caplab.code_agreement import build_code_agreement_report
from caplab.codex_events import CodexEventError, parse_native_json


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="caplab-code-agreement-input/1 JSON")
    args = parser.parse_args()
    try:
        raw = args.input.read_bytes()
        report = build_code_agreement_report(parse_native_json(raw.decode("utf-8")))
    except (OSError, UnicodeError, CodexEventError, ValueError) as error:
        parser.error(str(error))
    report["input_sha256"] = hashlib.sha256(raw).hexdigest()
    print(json.dumps(report, indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
