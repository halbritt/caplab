#!/usr/bin/env python3
"""Prepare, execute once, and inspect a fixed offline native capture diagnostic."""

import argparse
import json
from pathlib import Path

from scripted_native.lifecycle import execute, prepare


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    preparation = commands.add_parser(
        "prepare", help="pin explicit inputs; do not launch"
    )
    preparation.add_argument("output", type=Path)
    preparation.add_argument("--codex-root", required=True, type=Path)
    preparation.add_argument("--websockets-root", required=True, type=Path)
    preparation.add_argument("--task-input", type=Path)
    preparation.add_argument("--task-input-sha256")
    preparation.add_argument("--resource-profile", choices=("cgroup-usage/v1",))
    preparation.add_argument(
        "--child-observation-profile", choices=("supervisor-poll/v1",)
    )
    preparation.add_argument(
        "--launch-profile",
        default="codex-scripted-local/v1",
        choices=(
            "codex-scripted-local/v1",
            "codex-scripted-routed/v1",
            "codex-scripted-routed/v2",
        ),
    )
    execution = commands.add_parser(
        "execute", help="consume one separately authorized attempt"
    )
    execution.add_argument("output", type=Path)
    execution.add_argument("--preparation-sha256", required=True)
    execution.add_argument("--authorization", required=True, type=Path)
    execution.add_argument("--authorization-sha256", required=True)
    inspection = commands.add_parser(
        "inspect", help="verify anchored capture and preserve outcomes"
    )
    inspection.add_argument("output", type=Path)
    inspection.add_argument("--preparation-sha256", required=True)
    inspection.add_argument("--result-sha256", required=True)
    worker = commands.add_parser("worker", help=argparse.SUPPRESS)
    worker.add_argument("output", type=Path)
    worker.add_argument("--unit", required=True)
    worker.add_argument("--preparation-sha256", required=True)
    routed_worker = commands.add_parser("routed-worker", help=argparse.SUPPRESS)
    routed_worker.add_argument("output", type=Path)
    routed_worker.add_argument("--unit", required=True)
    routed_worker.add_argument("--preparation-sha256", required=True)
    args = parser.parse_args(argv)
    if args.command == "prepare":
        result = prepare(
            args.output,
            codex_root=args.codex_root,
            websockets_root=args.websockets_root,
            task_input=args.task_input,
            task_input_sha256=args.task_input_sha256,
            launch_profile=args.launch_profile,
            resource_profile=args.resource_profile,
            child_observation_profile=args.child_observation_profile,
        )
    elif args.command == "execute":
        result = execute(
            args.output,
            expected_preparation_sha256=args.preparation_sha256,
            authorization_path=args.authorization,
            expected_authorization_sha256=args.authorization_sha256,
        )
    elif args.command == "inspect":
        from scripted_native.inspection import inspect

        result = inspect(
            args.output,
            expected_preparation_sha256=args.preparation_sha256,
            expected_result_sha256=args.result_sha256,
        )
    elif args.command == "routed-worker":
        from scripted_native.routed_network import enter_outer

        enter_outer(args.output, args.unit, args.preparation_sha256)
        return 0
    else:
        from scripted_native.runner import inside

        inside(args.output, args.unit, args.preparation_sha256)
        return 0
    print(json.dumps(result, indent=2))
    if args.command == "execute" and not result["native_attempt_succeeded"]:
        return 1
    if args.command == "inspect" and result.get("status") == "unavailable":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
