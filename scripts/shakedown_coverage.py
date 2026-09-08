"""Read explicit structural metadata and print an exact coverage plan."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from caplab.codex_events import CodexEventError, parse_native_json
from caplab.coverage_plan import plan_shakedown_coverage


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="caplab-shakedown-coverage-input/1 JSON")
    args = parser.parse_args()
    try:
        raw = args.input.read_bytes()
        report = plan_shakedown_coverage(parse_native_json(raw.decode("utf-8")))
    except (OSError, UnicodeError, CodexEventError, ValueError) as error:
        parser.error(str(error))
    report["input_sha256"] = hashlib.sha256(raw).hexdigest()
    print(json.dumps(report, indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
