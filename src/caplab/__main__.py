"""Top-level CAPLAB command dispatcher."""

from __future__ import annotations

import sys
from collections.abc import Callable
from datetime import datetime

from caplab.runtime.canonical import canonical_json


def main(
    arguments: list[str] | None = None,
    *,
    clock: Callable[[], datetime] | None = None,
) -> int:
    argv = list(sys.argv[1:] if arguments is None else arguments)
    if not argv:
        sys.stderr.buffer.write(
            canonical_json({"error": "command_required:qualification_or_revbench"})
            + b"\n"
        )
        return 2
    command, remaining = argv[0], argv[1:]
    if command == "qualification":
        from caplab.qualification.__main__ import main as qualification_main

        if clock is None:
            return qualification_main(remaining)
        return qualification_main(remaining, clock=clock)
    if command == "revbench":
        try:
            from caplab.revbench.__main__ import main as revbench_main
        except ModuleNotFoundError as error:
            if error.name not in {"caplab.revbench", "caplab.revbench.__main__"}:
                raise
            sys.stderr.buffer.write(
                canonical_json({"error": "revbench_unavailable"}) + b"\n"
            )
            return 2
        return revbench_main(remaining)
    sys.stderr.buffer.write(
        canonical_json({"error": f"unknown_command:{command}"}) + b"\n"
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
