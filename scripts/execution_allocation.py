"""Print proposed arm/account/lane slots; no resources are read or reserved."""

import argparse
import hashlib
import json
from pathlib import Path

from caplab.codex_events import CodexEventError, parse_native_json
from caplab.execution_allocation import plan_execution_allocation


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path, help='caplab-execution-allocation-input/1 JSON')
    args = parser.parse_args()
    try:
        with args.input.open('rb') as source:
            raw = source.read(1024 * 1024 + 1)
        if len(raw) > 1024 * 1024:
            raise ValueError('allocation input exceeds 1 MiB')
        report = plan_execution_allocation(parse_native_json(raw.decode('utf-8')))
    except (OSError, UnicodeError, CodexEventError, ValueError) as error:
        parser.error(str(error))
    report['input_sha256'] = hashlib.sha256(raw).hexdigest()
    print(json.dumps(report, indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
