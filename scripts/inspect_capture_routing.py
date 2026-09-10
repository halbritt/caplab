"""Inspect completed routing custody using independently supplied anchors."""

import argparse
import json
from pathlib import Path

from caplab.capture_network_verify import verify_capture_routing
from caplab.codex_events import parse_native_json
from caplab.task_capture_verify import _open, _read_file


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--policy", required=True, type=Path)
    parser.add_argument("--expected-policy-sha256", required=True)
    parser.add_argument("--expected-terminal-sha256", required=True)
    parser.add_argument("--expected-ready-sha256", required=True)
    parser.add_argument("--expected-peer-pid", required=True, type=int)
    args = parser.parse_args()
    try:
        with _open(None, args.policy.parent, directory=True) as parent:
            raw, _, _ = _read_file(parent, args.policy.name, 65536, retain=True)
        plan = parse_native_json(raw.decode("utf-8"))
        report = verify_capture_routing(
            args.root,
            plan=plan,
            expected_policy_sha256=args.expected_policy_sha256,
            expected_terminal_sha256=args.expected_terminal_sha256,
            expected_ready_sha256=args.expected_ready_sha256,
            expected_peer_pid=args.expected_peer_pid,
        )
    except (OSError, ValueError, RecursionError) as error:
        parser.error(str(error))
    print(json.dumps(report, sort_keys=True, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
