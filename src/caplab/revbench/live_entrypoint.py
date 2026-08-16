"""Source-only isolated entrypoint for live Revbench authority and execution."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


_PYCACHE_PREFIX = "/nonexistent/caplab-revbench-pycache-v1"


def _refuse(message: str) -> int:
    document = {
        "schema_version": "caplab-revbench-error/1",
        "error_type": "RevbenchContractError",
        "code": message,
        "message": message,
    }
    sys.stderr.write(
        json.dumps(
            document,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )
        + "\n"
    )
    return 2


def _main() -> int:
    entrypoint = str(Path(__file__).resolve())
    expected_interpreter_argv = [
        "/usr/bin/python3",
        "-I",
        "-S",
        "-B",
        "-X",
        f"pycache_prefix={_PYCACHE_PREFIX}",
    ]
    if (
        sys.orig_argv[: len(expected_interpreter_argv)] != expected_interpreter_argv
        or len(sys.orig_argv) <= len(expected_interpreter_argv)
        or Path(sys.orig_argv[len(expected_interpreter_argv)]).resolve()
        != Path(entrypoint)
        or sys._xoptions != {"pycache_prefix": _PYCACHE_PREFIX}
        or sys.warnoptions
    ):
        return _refuse("live_source_invocation_profile_required")
    required_flags = {
        "optimize": 0,
        "dont_write_bytecode": 1,
        "no_user_site": 1,
        "no_site": 1,
        "ignore_environment": 1,
        "isolated": 1,
        "safe_path": 1,
    }
    if any(
        int(getattr(sys.flags, name)) != value for name, value in required_flags.items()
    ):
        return _refuse("live_source_invocation_profile_required")
    if sys.prefix != sys.base_prefix or sys.pycache_prefix != _PYCACHE_PREFIX:
        return _refuse("live_source_invocation_profile_required")
    if Path(_PYCACHE_PREFIX).exists():
        return _refuse("live_source_pycache_prefix_must_be_absent")
    package_root = Path(entrypoint).parents[1]
    if any(path.is_symlink() for path in package_root.rglob("*")):
        return _refuse("live_source_package_symlink_refused")
    package_init = package_root / "__init__.py"
    specification = importlib.util.spec_from_file_location(
        "caplab",
        package_init,
        submodule_search_locations=[str(package_root)],
    )
    if specification is None or specification.loader is None:
        return _refuse("live_source_package_load_failed")
    package = importlib.util.module_from_spec(specification)
    sys.modules["caplab"] = package
    try:
        specification.loader.exec_module(package)
    except Exception:
        return _refuse("live_source_package_load_failed")

    from caplab.revbench.__main__ import main

    return main(live_source=True)


if __name__ == "__main__":
    raise SystemExit(_main())
