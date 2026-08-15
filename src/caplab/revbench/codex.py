"""Pinned Codex CLI response and credential adapters for live Revbench."""

from __future__ import annotations

import base64
import contextlib
import fcntl
import importlib
import importlib.resources
import json
import os
import platform
import re
import selectors
import signal
import stat
import struct
import subprocess
import sys
import sysconfig
import tempfile
import time
from collections.abc import Iterator, Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Sequence

from caplab.producer import ProducerIdentityError, producer_identity
from caplab.runtime.canonical import canonical_json, sha256_hex

from .custody import FreshProcessCapture


class CodexAdapterError(ValueError):
    """A Codex-specific input cannot be interpreted without ambiguity."""


class CodexJSONLTransportError(CodexAdapterError):
    """The pinned Codex JSONL lifecycle is incomplete or ambiguous."""


class CodexResponseSchemaError(CodexAdapterError):
    """A completed Codex turn returned text outside the native response schema."""


_HEX_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_SOURCE_COMMIT = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
_IDENTIFIER = re.compile(r"^[a-z0-9][a-z0-9._-]{0,127}$")
_JSON_POINTER = re.compile(r"^(?:/(?:[^~/]|~[01])*)*$")
_MAX_CREDENTIAL_BYTES = 1024 * 1024
_EXECUTOR_RUNTIME_MODULES = (
    "_hashlib",
    "_json",
    "_posixsubprocess",
    "_socket",
    "_ssl",
    "_strptime",
    "_struct",
    "base64",
    "binascii",
    "contextlib",
    "dataclasses",
    "datetime",
    "fcntl",
    "hashlib",
    "importlib",
    "importlib.readers",
    "importlib.metadata",
    "importlib.resources",
    "importlib.resources._itertools",
    "importlib.resources.readers",
    "json",
    "json.decoder",
    "json.encoder",
    "json.scanner",
    "os",
    "pathlib",
    "platform",
    "re",
    "selectors",
    "signal",
    "socket",
    "ssl",
    "stat",
    "struct",
    "subprocess",
    "tempfile",
    "threading",
    "time",
    "typing",
)
_LIVE_PYCACHE_PREFIX = "/nonexistent/caplab-revbench-pycache-v1"
_BEHAVIOR_FLAG_NAMES = (
    "debug",
    "inspect",
    "interactive",
    "optimize",
    "dont_write_bytecode",
    "no_user_site",
    "no_site",
    "ignore_environment",
    "verbose",
    "bytes_warning",
    "quiet",
    "hash_randomization",
    "isolated",
    "dev_mode",
    "utf8_mode",
    "warn_default_encoding",
    "safe_path",
    "int_max_str_digits",
)
CODEX_NATIVE_BUNDLE_POLICY_SHA256 = (
    "211354874f4e3443a6e11fbe8b09cf54205c9cfc767f1a9a7ca2d7a9b210a68e"
)
CODEX_NATIVE_BUNDLE_POLICY_SCHEMA = "caplab-revbench-codex-native-bundle-policy/1"


def codex_native_bundle_policy_bytes() -> bytes:
    """Load the exact bundle policy shipped in the installed package."""

    resource = importlib.resources.files("caplab.revbench").joinpath(
        "contracts/codex-native-bundle-v1.json"
    )
    try:
        payload = resource.read_bytes()
    except OSError as error:
        raise CodexAdapterError("codex_bundle_policy_unavailable") from error
    if sha256_hex(payload) != CODEX_NATIVE_BUNDLE_POLICY_SHA256:
        raise CodexAdapterError("codex_bundle_policy_digest_mismatch")
    return payload


def codex_native_bundle_policy() -> dict[str, Any]:
    """Return the pinned policy as an owned JSON object."""

    payload = codex_native_bundle_policy_bytes()
    try:
        document = json.loads(payload, object_pairs_hook=_unique_object)
    except (UnicodeError, json.JSONDecodeError, ValueError) as error:
        raise CodexAdapterError("codex_bundle_policy_invalid") from error
    if (
        not isinstance(document, dict)
        or document.get("schema_version") != CODEX_NATIVE_BUNDLE_POLICY_SCHEMA
    ):
        raise CodexAdapterError("codex_bundle_policy_invalid")
    return document


def validate_credential_profile(profile: Mapping[str, Any]) -> dict[str, Any]:
    """Validate and own the nonsecret, operator-declared profile contract."""

    return _validate_profile(profile)


def validate_execution_apparatus_receipt(
    receipt: Mapping[str, Any],
    *,
    allow_dirty: bool = False,
) -> dict[str, Any]:
    """Validate the exact self-describing apparatus inventory contract."""

    owned = _canonical_copy(receipt)
    if (
        set(owned)
        != {
            "schema_version",
            "apparatus_id",
            "caplab",
            "python",
            "protocol",
            "ambient_observation",
        }
        or owned["schema_version"] != "caplab-revbench-execution-apparatus/1"
    ):
        raise CodexAdapterError("execution_apparatus_shape_invalid")
    caplab = owned["caplab"]
    if not isinstance(caplab, dict) or set(caplab) != {
        "package_version",
        "source_commit",
        "checkout_state",
        "package_tree_sha256",
        "package_members",
    }:
        raise CodexAdapterError("execution_apparatus_caplab_invalid")
    if not isinstance(caplab["package_version"], str) or not caplab["package_version"]:
        raise CodexAdapterError("execution_apparatus_caplab_invalid")
    if (
        not isinstance(caplab["source_commit"], str)
        or _SOURCE_COMMIT.fullmatch(caplab["source_commit"]) is None
    ):
        raise CodexAdapterError("execution_apparatus_caplab_invalid")
    allowed_checkout_states = {"clean", "archive-installed"}
    if allow_dirty:
        allowed_checkout_states.add("dirty")
    if caplab["checkout_state"] not in allowed_checkout_states:
        raise CodexAdapterError("execution_apparatus_caplab_invalid")
    members = caplab["package_members"]
    if not isinstance(members, list) or not members:
        raise CodexAdapterError("execution_apparatus_package_members_invalid")
    retained_paths: list[str] = []
    for member in members:
        if not isinstance(member, dict) or set(member) != {
            "path",
            "sha256",
            "byte_count",
        }:
            raise CodexAdapterError("execution_apparatus_package_members_invalid")
        path = member["path"]
        if (
            not isinstance(path, str)
            or not path
            or Path(path).is_absolute()
            or ".." in Path(path).parts
            or path in retained_paths
            or not isinstance(member["sha256"], str)
            or _HEX_DIGEST.fullmatch(member["sha256"]) is None
            or isinstance(member["byte_count"], bool)
            or not isinstance(member["byte_count"], int)
            or member["byte_count"] < 0
        ):
            raise CodexAdapterError("execution_apparatus_package_members_invalid")
        retained_paths.append(path)
    expected_member_order = [
        path.as_posix() for path in sorted(Path(value) for value in retained_paths)
    ]
    if retained_paths != expected_member_order or caplab[
        "package_tree_sha256"
    ] != sha256_hex(canonical_json(members)):
        raise CodexAdapterError("execution_apparatus_package_identity_invalid")

    python = owned["python"]
    if not isinstance(python, dict) or set(python) != {
        "implementation",
        "version",
        "build",
        "cache_tag",
        "abi_flags",
        "behavior_flags",
        "executable_sha256",
        "executable_byte_count",
        "dependency_members",
        "loaded_runtime_members",
        "loaded_runtime_inventory_sha256",
        "runtime_inventory_basis",
        "runtime_symlink_policy",
    }:
        raise CodexAdapterError("execution_apparatus_python_invalid")
    if any(
        not isinstance(python[field], str) or not python[field]
        for field in ("implementation", "version")
    ) or (
        not isinstance(python["build"], list)
        or len(python["build"]) != 2
        or any(not isinstance(value, str) for value in python["build"])
    ):
        raise CodexAdapterError("execution_apparatus_python_invalid")
    if (
        not isinstance(python["cache_tag"], str)
        or not python["cache_tag"]
        or not isinstance(python["abi_flags"], str)
        or not isinstance(python["behavior_flags"], dict)
        or set(python["behavior_flags"]) != set(_BEHAVIOR_FLAG_NAMES)
        or any(
            isinstance(value, bool) or not isinstance(value, int)
            for value in python["behavior_flags"].values()
        )
        or python["behavior_flags"]["optimize"] != 0
    ):
        raise CodexAdapterError("execution_apparatus_python_flags_invalid")
    if (
        not isinstance(python["executable_sha256"], str)
        or _HEX_DIGEST.fullmatch(python["executable_sha256"]) is None
        or isinstance(python["executable_byte_count"], bool)
        or not isinstance(python["executable_byte_count"], int)
        or python["executable_byte_count"] <= 0
    ):
        raise CodexAdapterError("execution_apparatus_python_invalid")
    dependencies = python["dependency_members"]
    if not isinstance(dependencies, list) or not dependencies:
        raise CodexAdapterError("execution_apparatus_dependencies_invalid")
    modules: list[str] = []
    for dependency in dependencies:
        if not isinstance(dependency, dict) or set(dependency) != {
            "module",
            "storage",
            "sha256",
            "byte_count",
        }:
            raise CodexAdapterError("execution_apparatus_dependencies_invalid")
        if (
            not isinstance(dependency["module"], str)
            or not dependency["module"]
            or dependency["module"] in modules
            or dependency["storage"]
            not in {"module-file", "python-executable-built-in"}
            or not isinstance(dependency["sha256"], str)
            or _HEX_DIGEST.fullmatch(dependency["sha256"]) is None
            or isinstance(dependency["byte_count"], bool)
            or not isinstance(dependency["byte_count"], int)
            or dependency["byte_count"] <= 0
        ):
            raise CodexAdapterError("execution_apparatus_dependencies_invalid")
        modules.append(dependency["module"])
    if modules != sorted(modules):
        raise CodexAdapterError("execution_apparatus_dependencies_invalid")
    if python["runtime_inventory_basis"] != (
        "isolated-no-cache-source-complete-runtime-trees-and-executable-elf-mappings"
    ) or python["runtime_symlink_policy"] != (
        "logical-entry-identity-with-dereferenced-regular-target-bytes"
    ):
        raise CodexAdapterError("execution_apparatus_runtime_inventory_invalid")
    runtime_members = python["loaded_runtime_members"]
    if not isinstance(runtime_members, list) or not runtime_members:
        raise CodexAdapterError("execution_apparatus_runtime_inventory_invalid")
    identities: list[str] = []
    for member in runtime_members:
        if not isinstance(member, dict) or set(member) != {
            "identity",
            "storage",
            "sha256",
            "byte_count",
        }:
            raise CodexAdapterError("execution_apparatus_runtime_inventory_invalid")
        if (
            not isinstance(member["identity"], str)
            or not member["identity"]
            or member["identity"] in identities
            or member["storage"]
            not in {
                "python-runtime-file",
                "mapped-native-file",
            }
            or not isinstance(member["sha256"], str)
            or _HEX_DIGEST.fullmatch(member["sha256"]) is None
            or isinstance(member["byte_count"], bool)
            or not isinstance(member["byte_count"], int)
            or member["byte_count"] < 0
        ):
            raise CodexAdapterError("execution_apparatus_runtime_inventory_invalid")
        identities.append(member["identity"])
    if identities != sorted(identities) or python[
        "loaded_runtime_inventory_sha256"
    ] != sha256_hex(canonical_json(runtime_members)):
        raise CodexAdapterError("execution_apparatus_runtime_inventory_invalid")

    protocol = owned["protocol"]
    if not isinstance(protocol, dict) or protocol != {
        "bundle_policy_source_sha256": CODEX_NATIVE_BUNDLE_POLICY_SHA256,
        "launch_plan_schema": "caplab-revbench-live-launch-plan/1",
        "response_adapter": "codex-jsonl-final-agent-message/1",
    }:
        raise CodexAdapterError("execution_apparatus_protocol_invalid")
    ambient = owned["ambient_observation"]
    if (
        not isinstance(ambient, dict)
        or set(ambient) != {"system", "release", "machine", "trust"}
        or ambient["trust"] != "observed-not-bundle-member"
        or any(
            not isinstance(ambient[field], str) or not ambient[field]
            for field in ("system", "release", "machine")
        )
    ):
        raise CodexAdapterError("execution_apparatus_ambient_invalid")
    identity = _canonical_copy(owned)
    apparatus_id = identity.pop("apparatus_id")
    if apparatus_id != "apparatus-" + sha256_hex(canonical_json(identity)):
        raise CodexAdapterError("execution_apparatus_id_invalid")
    return owned


def _within_logical_path(path: Path, root: Path) -> bool:
    absolute = Path(os.path.abspath(path))
    absolute_root = Path(os.path.abspath(root))
    return absolute == absolute_root or absolute_root in absolute.parents


def _runtime_tree_roots() -> list[tuple[str, Path]]:
    retained: list[tuple[str, Path]] = []
    seen: set[Path] = set()
    for name in ("stdlib", "platstdlib"):
        configured = sysconfig.get_path(name)
        if not isinstance(configured, str) or not configured:
            raise CodexAdapterError("execution_apparatus_runtime_root_unavailable")
        root = Path(os.path.abspath(configured))
        resolved = root.resolve()
        if resolved in seen:
            continue
        if not root.is_dir() or root.is_symlink():
            raise CodexAdapterError("execution_apparatus_runtime_root_unavailable")
        retained.append((name, root))
        seen.add(resolved)
    return retained


def _python_behavior_flags() -> dict[str, int]:
    return {name: int(getattr(sys.flags, name)) for name in _BEHAVIOR_FLAG_NAMES}


def _require_live_source_invocation(package_root: Path) -> None:
    expected_flags = {
        "optimize": 0,
        "dont_write_bytecode": 1,
        "no_user_site": 1,
        "no_site": 1,
        "ignore_environment": 1,
        "isolated": 1,
        "safe_path": 1,
    }
    observed_flags = _python_behavior_flags()
    if any(observed_flags[name] != value for name, value in expected_flags.items()):
        raise CodexAdapterError("live_source_invocation_profile_required")
    if sys.prefix != sys.base_prefix or sys.pycache_prefix != _LIVE_PYCACHE_PREFIX:
        raise CodexAdapterError("live_source_invocation_profile_required")
    if Path(_LIVE_PYCACHE_PREFIX).exists():
        raise CodexAdapterError("live_source_pycache_prefix_must_be_absent")
    main_module = sys.modules.get("__main__")
    main_path_value = getattr(main_module, "__file__", None)
    expected_entrypoint = package_root / "revbench" / "live_entrypoint.py"
    expected_interpreter_argv = [
        "/usr/bin/python3",
        "-I",
        "-S",
        "-B",
        "-X",
        f"pycache_prefix={_LIVE_PYCACHE_PREFIX}",
    ]
    if (
        not isinstance(main_path_value, str)
        or Path(main_path_value).resolve() != expected_entrypoint.resolve()
        or sys.orig_argv[: len(expected_interpreter_argv)] != expected_interpreter_argv
        or len(sys.orig_argv) <= len(expected_interpreter_argv)
        or Path(sys.orig_argv[len(expected_interpreter_argv)]).resolve()
        != expected_entrypoint.resolve()
        or sys._xoptions != {"pycache_prefix": _LIVE_PYCACHE_PREFIX}
        or sys.warnoptions
    ):
        raise CodexAdapterError("live_source_entrypoint_required")
    package_module = sys.modules.get("caplab")
    package_path = getattr(package_module, "__path__", None)
    package_file = getattr(package_module, "__file__", None)
    if (
        not isinstance(package_file, str)
        or Path(package_file).resolve() != (package_root / "__init__.py").resolve()
        or list(package_path or ()) != [str(package_root)]
    ):
        raise CodexAdapterError("live_source_path_invalid")
    runtime_roots = [root.resolve() for _, root in _runtime_tree_roots()]
    expected_zip = Path(
        f"{runtime_roots[0].parent}/python{sys.version_info.major}{sys.version_info.minor}.zip"
    )
    if expected_zip.exists():
        raise CodexAdapterError("live_source_unsealed_python_zip_refused")
    for entry in sys.path:
        path = Path(entry).resolve()
        if path == expected_zip or any(
            path == root or root in path.parents for root in runtime_roots
        ):
            continue
        raise CodexAdapterError("live_source_path_invalid")


def _require_exact_tracked_package(repository: Path, package_root: Path) -> None:
    """Reject symlinks and non-cache files outside the exact tracked tree."""

    actual: set[str] = set()
    for path in sorted(package_root.rglob("*")):
        if path.is_symlink():
            raise CodexAdapterError("execution_apparatus_package_symlink_refused")
        if not path.is_file():
            continue
        relative = path.relative_to(package_root)
        if "__pycache__" in relative.parts or path.suffix in {".pyc", ".pyo"}:
            # The required -B invocation and absent external pycache prefix
            # prevent these pre-existing ignored cache files from loading.
            continue
        actual.add(relative.as_posix())
    try:
        result = subprocess.run(
            [
                "/usr/bin/git",
                "ls-files",
                "--stage",
                "-z",
                "--",
                "src/caplab",
            ],
            cwd=repository,
            env={"LC_ALL": "C"},
            check=True,
            capture_output=True,
        )
    except (OSError, subprocess.SubprocessError) as error:
        raise CodexAdapterError("execution_apparatus_git_observation_failed") from error
    tracked: set[str] = set()
    try:
        entries = result.stdout.split(b"\0")
        for entry in entries:
            if not entry:
                continue
            metadata, path_bytes = entry.split(b"\t", 1)
            mode, _object_id, stage = metadata.split(b" ", 2)
            path = path_bytes.decode("utf-8")
            relative = Path(path).relative_to("src/caplab").as_posix()
            if mode not in {b"100644", b"100755"} or stage != b"0":
                raise ValueError
            tracked.add(relative)
    except (UnicodeError, ValueError) as error:
        raise CodexAdapterError("execution_apparatus_tracked_tree_invalid") from error
    if actual != tracked:
        raise CodexAdapterError("execution_apparatus_untracked_package_member")


def _repository_head(repository: Path) -> str:
    """Observe source HEAD through the fixed repository-owned Git seam."""

    try:
        result = subprocess.run(
            ["/usr/bin/git", "rev-parse", "HEAD"],
            cwd=repository,
            env={"LC_ALL": "C"},
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.SubprocessError) as error:
        raise CodexAdapterError("execution_apparatus_git_observation_failed") from error
    commit = result.stdout.strip()
    if _SOURCE_COMMIT.fullmatch(commit) is None:
        raise CodexAdapterError("execution_apparatus_source_commit_invalid")
    return commit


def _loaded_runtime_inventory(
    package_root: Path, *, reject_external_modules: bool
) -> list[dict[str, Any]]:
    """Identify complete Python runtime trees, caches, and native mappings."""

    retained: dict[str, dict[str, Any]] = {}
    runtime_roots = _runtime_tree_roots()
    excluded_roots = {
        Path(os.path.abspath(value))
        for name in ("purelib", "platlib")
        if isinstance((value := sysconfig.get_path(name)), str) and value
    }
    for root_name, runtime_root in runtime_roots:
        for path in sorted(runtime_root.rglob("*")):
            if any(_within_logical_path(path, excluded) for excluded in excluded_roots):
                continue
            try:
                if not path.is_file():
                    continue
                payload = path.read_bytes()
            except OSError as error:
                raise CodexAdapterError(
                    "execution_apparatus_runtime_member_unavailable"
                ) from error
            relative = path.relative_to(runtime_root).as_posix()
            identity = f"python-runtime:{root_name}:{relative}"
            retained[identity] = {
                "identity": identity,
                "storage": "python-runtime-file",
                "sha256": sha256_hex(payload),
                "byte_count": len(payload),
            }

    for module_name, module in sorted(sys.modules.items()):
        if module is None:
            continue
        module_path_value = getattr(module, "__file__", None)
        if not isinstance(module_path_value, str):
            continue
        module_path = Path(os.path.abspath(module_path_value))
        if _within_logical_path(module_path, package_root):
            continue
        if any(
            _within_logical_path(module_path, excluded) for excluded in excluded_roots
        ):
            if reject_external_modules:
                raise CodexAdapterError(
                    "execution_apparatus_unexpected_external_module"
                )
            continue
        if any(_within_logical_path(module_path, root) for _, root in runtime_roots):
            continue
        if reject_external_modules:
            raise CodexAdapterError("execution_apparatus_unexpected_external_module")
    try:
        mappings = Path("/proc/self/maps").read_text(encoding="utf-8")
    except OSError as error:
        raise CodexAdapterError(
            "execution_apparatus_native_maps_unavailable"
        ) from error
    native_payloads: dict[tuple[str, int], tuple[str, bytes]] = {}
    for line in mappings.splitlines():
        fields = line.split(maxsplit=5)
        if len(fields) != 6 or "x" not in fields[1] or not fields[5].startswith("/"):
            continue
        path = Path(fields[5])
        try:
            metadata = path.stat()
            if not stat.S_ISREG(metadata.st_mode):
                continue
            key = (str(path), metadata.st_ino)
            if key in native_payloads:
                continue
            payload = path.read_bytes()
            if not payload.startswith(b"\x7fELF"):
                continue
            native_payloads[key] = (path.name, payload)
        except OSError as error:
            raise CodexAdapterError(
                "execution_apparatus_runtime_member_unavailable"
            ) from error
    for (_path, _inode), (name, payload) in sorted(native_payloads.items()):
        digest = sha256_hex(payload)
        identity = f"mapped-native:{name}:{digest}"
        retained[identity] = {
            "identity": identity,
            "storage": "mapped-native-file",
            "sha256": digest,
            "byte_count": len(payload),
        }
    return [retained[key] for key in sorted(retained)]


def _bootstrap_live_execution_apparatus() -> None:
    """Load the fixed live-executor surface before taking its byte inventory."""

    # Resource traversal has lazy imports.  Both authority preflight and live
    # execution must cross this same boundary before deriving an apparatus ID.
    codex_native_bundle_policy()
    for module_name in _EXECUTOR_RUNTIME_MODULES:
        importlib.import_module(module_name)
    # Authorization, intent, and completion checks all use this exact UTC
    # parser.  Exercise it here so its lazy dependency is present in both the
    # no-effect authority preflight and the later live-execution process.
    datetime.strptime("2000-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ")


def execution_apparatus_receipt(*, require_clean: bool = True) -> dict[str, Any]:
    """Mechanically identify the CAPLAB/Python measurement apparatus bytes."""

    _bootstrap_live_execution_apparatus()
    package_root = Path(__file__).resolve().parents[1]
    repository = Path(__file__).resolve().parents[3]
    if require_clean:
        _require_live_source_invocation(package_root)
        _require_exact_tracked_package(repository, package_root)
    package_members: list[dict[str, Any]] = []
    for path in sorted(package_root.rglob("*")):
        if (
            not path.is_file()
            or path.is_symlink()
            or "__pycache__" in path.parts
            or path.suffix in {".pyc", ".pyo"}
        ):
            continue
        payload = path.read_bytes()
        package_members.append(
            {
                "path": path.relative_to(package_root).as_posix(),
                "sha256": sha256_hex(payload),
                "byte_count": len(payload),
            }
        )
    if not package_members:
        raise CodexAdapterError("execution_apparatus_package_empty")

    try:
        package_version, commit, package_sha256 = producer_identity()
    except ProducerIdentityError as error:
        raise CodexAdapterError("execution_apparatus_producer_unavailable") from error
    observed_package_sha256 = sha256_hex(canonical_json(package_members))
    if observed_package_sha256 != package_sha256:
        raise CodexAdapterError("execution_apparatus_package_identity_mismatch")

    checkout_state = "archive-installed"
    if (repository / ".git").exists():
        if _repository_head(repository) != commit:
            raise CodexAdapterError("execution_apparatus_source_commit_mismatch")
        try:
            status_result = subprocess.run(
                [
                    "/usr/bin/git",
                    "status",
                    "--porcelain=v1",
                    "--untracked-files=all",
                ],
                cwd=repository,
                env={"LC_ALL": "C"},
                check=True,
                capture_output=True,
            )
        except (OSError, subprocess.SubprocessError) as error:
            raise CodexAdapterError(
                "execution_apparatus_git_observation_failed"
            ) from error
        checkout_state = "clean" if not status_result.stdout else "dirty"
    if require_clean and checkout_state != "clean":
        raise CodexAdapterError("execution_apparatus_not_clean_repository_commit")

    executable_path = Path(sys.executable).resolve()
    executable = executable_path.read_bytes()
    dependencies: list[dict[str, Any]] = []
    for module_name in (
        "fcntl",
        "hashlib",
        "json",
        "selectors",
        "ssl",
        "subprocess",
        "tempfile",
    ):
        module = importlib.import_module(module_name)
        module_path_value = getattr(module, "__file__", None)
        if isinstance(module_path_value, str):
            module_path = Path(module_path_value).resolve()
            payload = module_path.read_bytes()
            storage = "module-file"
        else:
            payload = executable
            storage = "python-executable-built-in"
        dependencies.append(
            {
                "module": module_name,
                "storage": storage,
                "sha256": sha256_hex(payload),
                "byte_count": len(payload),
            }
        )

    if sys.flags.optimize != 0:
        raise CodexAdapterError("execution_apparatus_optimized_python_refused")
    runtime_members = _loaded_runtime_inventory(
        package_root, reject_external_modules=require_clean
    )

    identity: dict[str, Any] = {
        "schema_version": "caplab-revbench-execution-apparatus/1",
        "apparatus_id": "",
        "caplab": {
            "package_version": package_version,
            "source_commit": commit,
            "checkout_state": checkout_state,
            "package_tree_sha256": package_sha256,
            "package_members": package_members,
        },
        "python": {
            "implementation": platform.python_implementation(),
            "version": platform.python_version(),
            "build": list(platform.python_build()),
            "cache_tag": sys.implementation.cache_tag,
            "abi_flags": sys.abiflags,
            "behavior_flags": _python_behavior_flags(),
            "executable_sha256": sha256_hex(executable),
            "executable_byte_count": len(executable),
            "dependency_members": dependencies,
            "loaded_runtime_members": runtime_members,
            "loaded_runtime_inventory_sha256": sha256_hex(
                canonical_json(runtime_members)
            ),
            "runtime_inventory_basis": (
                "isolated-no-cache-source-complete-runtime-trees-and-executable-elf-mappings"
            ),
            "runtime_symlink_policy": (
                "logical-entry-identity-with-dereferenced-regular-target-bytes"
            ),
        },
        "protocol": {
            "bundle_policy_source_sha256": CODEX_NATIVE_BUNDLE_POLICY_SHA256,
            "launch_plan_schema": "caplab-revbench-live-launch-plan/1",
            "response_adapter": "codex-jsonl-final-agent-message/1",
        },
        "ambient_observation": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "trust": "observed-not-bundle-member",
        },
    }
    receipt_identity = _canonical_copy(identity)
    receipt_identity.pop("apparatus_id")
    identity["apparatus_id"] = "apparatus-" + sha256_hex(
        canonical_json(receipt_identity)
    )
    return validate_execution_apparatus_receipt(identity, allow_dirty=not require_clean)


def is_static_linux_elf(payload: bytes) -> bool:
    """Return whether an ELF has no userspace interpreter dependency."""

    if len(payload) < 64 or payload[:4] != b"\x7fELF":
        return False
    elf_class = payload[4]
    byte_order = payload[5]
    endian = "<" if byte_order == 1 else ">" if byte_order == 2 else None
    if endian is None:
        return False
    try:
        if elf_class == 2:
            program_offset = struct.unpack_from(f"{endian}Q", payload, 32)[0]
            entry_size = struct.unpack_from(f"{endian}H", payload, 54)[0]
            entry_count = struct.unpack_from(f"{endian}H", payload, 56)[0]
        elif elf_class == 1:
            program_offset = struct.unpack_from(f"{endian}I", payload, 28)[0]
            entry_size = struct.unpack_from(f"{endian}H", payload, 42)[0]
            entry_count = struct.unpack_from(f"{endian}H", payload, 44)[0]
        else:
            return False
    except struct.error:
        return False
    if entry_size < 4 or entry_count == 0:
        return False
    if program_offset + entry_size * entry_count > len(payload):
        return False
    for index in range(entry_count):
        try:
            program_type = struct.unpack_from(
                f"{endian}I", payload, program_offset + entry_size * index
            )[0]
        except struct.error:
            return False
        if program_type == 3:  # PT_INTERP
            return False
    return True


@dataclass(frozen=True)
class DerivedCodexResponse:
    """Deterministic projection of one complete Codex JSONL turn."""

    response: dict[str, Any]
    response_bytes: bytes
    selected_event_index: int
    selected_item_id: str
    extracted_text_sha256: str


@dataclass(frozen=True)
class SealedCredential:
    """Anonymous credential descriptor plus an in-memory leak quarantine."""

    descriptor: int
    _secret_values: tuple[bytes, ...] = field(repr=False, compare=False)

    def assert_streams_safe(self, stdout: bytes, stderr: bytes) -> None:
        """Refuse any stream containing exact credential or identity material."""

        if not isinstance(stdout, bytes) or not isinstance(stderr, bytes):
            raise CodexAdapterError("credential_quarantine_stream_not_bytes")
        if any(
            secret in stream
            for secret in self._secret_values
            for stream in (stdout, stderr)
        ):
            raise CodexAdapterError("credential_secret_quarantine")

    def stream_quarantine(self) -> ExactSecretStreamQuarantine:
        """Create a cross-chunk gate that withholds possible secret prefixes."""

        return ExactSecretStreamQuarantine(self._secret_values)


class ExactSecretStreamQuarantine:
    """Withhold overlap so exact known secrets never reach a durable sink."""

    def __init__(self, secret_values: tuple[bytes, ...]) -> None:
        if not secret_values or any(not value for value in secret_values):
            raise CodexAdapterError("credential_secret_set_invalid")
        self._secret_values = secret_values
        self._overlap = max(len(value) for value in secret_values) - 1
        self._pending = b""
        self.quarantined = False
        self._finished = False

    def feed(self, payload: bytes) -> bytes:
        if self._finished:
            raise CodexAdapterError("credential_quarantine_finished")
        if not isinstance(payload, bytes):
            raise CodexAdapterError("credential_quarantine_stream_not_bytes")
        if self.quarantined:
            return b""
        combined = self._pending + payload
        matches = [
            position
            for secret in self._secret_values
            if (position := combined.find(secret)) >= 0
        ]
        if matches:
            self.quarantined = True
            self._pending = b""
            return combined[: min(matches)]
        retained = min(len(combined), self._overlap)
        if retained == 0:
            self._pending = b""
            return combined
        emitted = combined[:-retained]
        self._pending = combined[-retained:]
        return emitted

    def finish(self) -> bytes:
        """Release a safe final overlap only after the stream reached EOF."""

        if self._finished:
            return b""
        self._finished = True
        if self.quarantined:
            self._pending = b""
            return b""
        emitted = self._pending
        self._pending = b""
        return emitted

    def abandon(self) -> None:
        """Discard withheld overlap when EOF was not observed."""

        self._finished = True
        self._pending = b""


@dataclass(frozen=True)
class CodexProcessObservation:
    """Bounded process outcome backed by durable private stream custody."""

    launch_attempted_at: str | None
    process_started_at: str | None
    process_completed_at: str | None
    completion_recorded_at: str
    stdout: bytes
    stdout_complete: bool
    stderr: bytes
    stderr_complete: bool
    exit_code: int | None
    termination: str
    invocation_state: str


@dataclass(frozen=True)
class CodexExecutionBundle:
    """Resolved bytes and identities of the registered live runtime bundle."""

    runtime_ref_sha256: str
    apparatus_sha256: str
    review_command_ref_sha256: str
    version_command_ref_sha256: str
    credential_profile_id: str
    credential_profile_sha256: str
    executable: bytes
    adapter: bytes
    adapter_loader: bytes
    adapter_libraries: tuple[tuple[str, bytes], ...]
    ca_certificates: bytes
    resolver: bytes
    nsswitch: bytes
    response_schema: bytes
    environment: dict[str, str]


def normalized_codex_containment_argv(logical_argv: Sequence[str]) -> list[str]:
    """Return the pinned outer argv with stable path/fd placeholders."""

    policy = codex_native_bundle_policy()
    launcher = policy["launcher"]
    if list(logical_argv) == launcher["version_argv"]:
        return list(policy["version_containment_argv_template"])
    if list(logical_argv) != launcher["review_argv"]:
        raise CodexAdapterError("codex_logical_argv_not_pinned")
    contained = [launcher["contained_executable"], *logical_argv[1:]]
    result: list[str] = []
    for token in policy["review_containment_argv_template"]:
        if token == "{contained_command...}":
            result.extend(contained)
        else:
            result.append(token)
    return result


def run_codex_process(
    logical_argv: Sequence[str],
    stdin: bytes,
    *,
    bundle: CodexExecutionBundle,
    capture: FreshProcessCapture,
    credential: SealedCredential | None,
    monotonic_deadline: float,
) -> CodexProcessObservation:
    """Materialize only pinned members and run the exact contained command."""

    policy = codex_native_bundle_policy()
    _validate_execution_bundle(bundle, policy)
    current_apparatus = execution_apparatus_receipt()
    if sha256_hex(canonical_json(current_apparatus)) != bundle.apparatus_sha256:
        raise CodexAdapterError("execution_apparatus_drift_before_launch")
    launcher = policy["launcher"]
    is_review = list(logical_argv) == launcher["review_argv"]
    if not is_review and list(logical_argv) != launcher["version_argv"]:
        raise CodexAdapterError("codex_logical_argv_not_pinned")
    if is_review != (credential is not None):
        raise CodexAdapterError("codex_credential_process_kind_mismatch")
    command_ref_sha256 = (
        bundle.review_command_ref_sha256
        if is_review
        else bundle.version_command_ref_sha256
    )
    normalized = normalized_codex_containment_argv(logical_argv)
    with tempfile.TemporaryDirectory(
        prefix="caplab-revbench-codex-adapter-"
    ) as temporary:
        stage = Path(temporary)
        loader_path = stage / "ld-linux-x86-64.so.2"
        adapter_path = stage / "bwrap"
        library_directory = stage / "lib"
        library_directory.mkdir(mode=0o700)
        loader_mode = int(policy["adapter_runtime"]["loader"]["mode"], 8)
        _write_runtime_member(loader_path, bundle.adapter_loader, loader_mode)
        _write_runtime_member(adapter_path, bundle.adapter, 0o700)
        library_modes = {
            member["name"]: int(member["mode"], 8)
            for member in policy["adapter_runtime"]["libraries"]
        }
        for name, payload in bundle.adapter_libraries:
            _write_runtime_member(
                library_directory / name, payload, library_modes[name]
            )
        with contextlib.ExitStack() as stack:
            descriptors = {
                "{codex_executable_fd}": stack.enter_context(
                    _sealed_data_memfd("codex-executable", bundle.executable)
                )
            }
            if is_review:
                assert credential is not None
                os.lseek(credential.descriptor, 0, os.SEEK_SET)
                descriptors.update(
                    {
                        "{credential_fd}": credential.descriptor,
                        "{response_schema_fd}": stack.enter_context(
                            _sealed_data_memfd(
                                "response-schema", bundle.response_schema
                            )
                        ),
                        "{ca_certificates_fd}": stack.enter_context(
                            _sealed_data_memfd(
                                "ca-certificates", bundle.ca_certificates
                            )
                        ),
                        "{resolver_fd}": stack.enter_context(
                            _sealed_data_memfd("resolver", bundle.resolver)
                        ),
                        "{nsswitch_fd}": stack.enter_context(
                            _sealed_data_memfd("nsswitch", bundle.nsswitch)
                        ),
                    }
                )
            replacements = {
                "{adapter_loader}": str(loader_path),
                "{adapter_library_directory}": str(library_directory),
                "{adapter_executable}": str(adapter_path),
                **{key: str(value) for key, value in descriptors.items()},
            }
            actual = _resolve_actual_containment_argv(normalized, replacements)
            return _run_owned_process(
                actual,
                normalized,
                logical_argv,
                stdin,
                contained_environment=bundle.environment if is_review else {},
                runtime_ref_sha256=bundle.runtime_ref_sha256,
                apparatus_sha256=bundle.apparatus_sha256,
                command_ref_sha256=command_ref_sha256,
                credential_profile_id=bundle.credential_profile_id,
                credential_profile_sha256=bundle.credential_profile_sha256,
                pass_fds=tuple(descriptors.values()),
                capture=capture,
                credential=credential,
                monotonic_deadline=monotonic_deadline,
            )


def _resolve_actual_containment_argv(
    normalized: Sequence[str], replacements: Mapping[str, str]
) -> list[str]:
    """Resolve only declared stage paths/descriptors in the semantic template."""

    allowed = {
        "{adapter_loader}",
        "{adapter_library_directory}",
        "{adapter_executable}",
        "{codex_executable_fd}",
        "{credential_fd}",
        "{response_schema_fd}",
        "{ca_certificates_fd}",
        "{resolver_fd}",
        "{nsswitch_fd}",
    }
    if any(
        key not in allowed or not isinstance(value, str) or not value
        for key, value in replacements.items()
    ):
        raise CodexAdapterError("codex_containment_substitution_invalid")
    actual: list[str] = []
    used: set[str] = set()
    for token in normalized:
        if token.startswith("{") and token.endswith("}"):
            if token not in allowed or token not in replacements:
                raise CodexAdapterError("codex_containment_template_unresolved")
            actual.append(replacements[token])
            used.add(token)
        else:
            actual.append(token)
    if used != set(replacements):
        raise CodexAdapterError("codex_containment_substitution_unused")
    for token, resolved in zip(normalized, actual, strict=True):
        if token not in allowed and token != resolved:
            raise CodexAdapterError("codex_containment_literal_drift")
        if token.endswith("_fd}") and not resolved.isdecimal():
            raise CodexAdapterError("codex_containment_descriptor_invalid")
    return actual


def _validate_execution_bundle(
    bundle: CodexExecutionBundle, policy: Mapping[str, Any]
) -> None:
    """Recheck every resolved member before materializing a live process."""

    for value in (
        bundle.runtime_ref_sha256,
        bundle.apparatus_sha256,
        bundle.review_command_ref_sha256,
        bundle.version_command_ref_sha256,
        bundle.credential_profile_sha256,
    ):
        if not isinstance(value, str) or _HEX_DIGEST.fullmatch(value) is None:
            raise CodexAdapterError("codex_execution_bundle_ref_invalid")
    if (
        not isinstance(bundle.credential_profile_id, str)
        or _IDENTIFIER.fullmatch(bundle.credential_profile_id) is None
    ):
        raise CodexAdapterError("codex_execution_bundle_profile_invalid")

    launcher = policy["launcher"]
    _require_member(
        bundle.executable,
        launcher["executable_sha256"],
        launcher["executable_byte_count"],
        "executable",
    )
    if not is_static_linux_elf(bundle.executable):
        raise CodexAdapterError("codex_execution_bundle_executable_format_invalid")
    containment = policy["containment"]
    _require_member(
        bundle.adapter,
        containment["adapter_sha256"],
        containment["adapter_byte_count"],
        "adapter",
    )
    adapter_runtime = policy["adapter_runtime"]
    loader = adapter_runtime["loader"]
    _require_member(
        bundle.adapter_loader,
        loader["sha256"],
        loader["byte_count"],
        "adapter_loader",
    )
    expected_libraries = adapter_runtime["libraries"]
    if [name for name, _payload in bundle.adapter_libraries] != [
        member["name"] for member in expected_libraries
    ]:
        raise CodexAdapterError("codex_execution_bundle_library_order_invalid")
    for (name, payload), member in zip(
        bundle.adapter_libraries, expected_libraries, strict=True
    ):
        _require_member(
            payload, member["sha256"], member["byte_count"], f"library:{name}"
        )
    resources = policy["pinned_host_resources"]
    for name, payload in (
        ("ca_certificates", bundle.ca_certificates),
        ("resolver", bundle.resolver),
        ("nsswitch", bundle.nsswitch),
    ):
        member = resources[name]
        _require_member(payload, member["sha256"], member["byte_count"], name)
    if bundle.response_schema != canonical_json(policy["response_schema"]):
        raise CodexAdapterError("codex_execution_bundle_response_schema_invalid")
    if canonical_json(bundle.environment) != canonical_json(policy["environment"]):
        raise CodexAdapterError("codex_execution_bundle_environment_invalid")


def _require_member(
    payload: bytes, expected_digest: str, expected_size: int, label: str
) -> None:
    if (
        not isinstance(payload, bytes)
        or len(payload) != expected_size
        or sha256_hex(payload) != expected_digest
    ):
        raise CodexAdapterError(f"codex_execution_bundle_member_invalid:{label}")


def _write_runtime_member(path: Path, payload: bytes, mode: int) -> None:
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor: int | None = None
    try:
        descriptor = os.open(path, flags, mode)
        os.fchmod(descriptor, mode)
        _write_all(descriptor, payload)
        os.fsync(descriptor)
        metadata = os.fstat(descriptor)
        if (
            not stat.S_ISREG(metadata.st_mode)
            or metadata.st_uid != os.geteuid()
            or stat.S_IMODE(metadata.st_mode) != mode
            or metadata.st_size != len(payload)
        ):
            raise CodexAdapterError("codex_runtime_member_materialization_invalid")
    except OSError as error:
        raise CodexAdapterError(
            "codex_runtime_member_materialization_failed"
        ) from error
    finally:
        if descriptor is not None:
            os.close(descriptor)


@contextlib.contextmanager
def _sealed_data_memfd(name: str, payload: bytes) -> Iterator[int]:
    descriptor: int | None = None
    try:
        flags = os.MFD_CLOEXEC | getattr(os, "MFD_ALLOW_SEALING", 0)
        descriptor = os.memfd_create(f"caplab-revbench-{name}", flags)
        _write_all(descriptor, payload)
        os.fdatasync(descriptor)
        os.lseek(descriptor, 0, os.SEEK_SET)
        seals = (
            fcntl.F_SEAL_SEAL
            | fcntl.F_SEAL_SHRINK
            | fcntl.F_SEAL_GROW
            | fcntl.F_SEAL_WRITE
        )
        fcntl.fcntl(descriptor, fcntl.F_ADD_SEALS, seals)
        yield descriptor
    except OSError as error:
        raise CodexAdapterError("codex_runtime_memfd_failed") from error
    finally:
        if descriptor is not None:
            os.close(descriptor)


def build_live_launch_plan(
    effect_scope: Mapping[str, Any],
    *,
    logical_argv: Sequence[str],
    normalized_containment_argv: Sequence[str],
    stdin: bytes,
    contained_environment: Mapping[str, str],
    runtime_ref_sha256: str,
    apparatus_sha256: str,
    command_ref_sha256: str,
    credential_profile_id: str,
    credential_profile_sha256: str,
    timeout_seconds: int,
    execution_deadline_at: str,
    stdout_limit: int,
    stderr_limit: int,
) -> dict[str, Any]:
    """Build the exact process plan later rechecked at the Popen boundary."""

    return {
        "schema_version": "caplab-revbench-live-launch-plan/1",
        "effect_scope": _canonical_copy(effect_scope),
        "argv_sha256": sha256_hex(canonical_json(list(logical_argv))),
        "containment_argv_sha256": sha256_hex(
            canonical_json(list(normalized_containment_argv))
        ),
        "stdin_sha256": sha256_hex(stdin),
        "environment_sha256": sha256_hex(canonical_json(contained_environment)),
        "runtime_bundle_sha256": runtime_ref_sha256,
        "apparatus_sha256": apparatus_sha256,
        "command_sha256": command_ref_sha256,
        "credential_profile_id": credential_profile_id,
        "credential_profile_sha256": credential_profile_sha256,
        "timeout_seconds": timeout_seconds,
        "execution_deadline_at": execution_deadline_at,
        "stdout_limit": stdout_limit,
        "stderr_limit": stderr_limit,
    }


def _run_owned_process(
    popen_argv: Sequence[str],
    normalized_containment_argv: Sequence[str],
    logical_argv: Sequence[str],
    stdin: bytes,
    *,
    contained_environment: Mapping[str, str],
    runtime_ref_sha256: str,
    apparatus_sha256: str,
    command_ref_sha256: str,
    credential_profile_id: str,
    credential_profile_sha256: str,
    pass_fds: Sequence[int],
    capture: FreshProcessCapture,
    credential: SealedCredential | None,
    monotonic_deadline: float,
) -> CodexProcessObservation:
    """Run one internally constructed process and durably capture safe bytes."""

    plan = capture.intent["launch_plan"]
    expected = build_live_launch_plan(
        plan["effect_scope"],
        logical_argv=logical_argv,
        normalized_containment_argv=normalized_containment_argv,
        stdin=stdin,
        contained_environment=contained_environment,
        runtime_ref_sha256=runtime_ref_sha256,
        apparatus_sha256=apparatus_sha256,
        command_ref_sha256=command_ref_sha256,
        credential_profile_id=credential_profile_id,
        credential_profile_sha256=credential_profile_sha256,
        timeout_seconds=plan["timeout_seconds"],
        execution_deadline_at=plan["execution_deadline_at"],
        stdout_limit=plan["stdout_limit"],
        stderr_limit=plan["stderr_limit"],
    )
    if canonical_json(plan) != canonical_json(expected):
        raise CodexAdapterError("live_launch_plan_actual_mismatch")
    if not popen_argv or any(not isinstance(token, str) for token in popen_argv):
        raise CodexAdapterError("live_containment_argv_invalid")
    now_utc = datetime.now(UTC)
    remaining_authority = (
        datetime.strptime(plan["execution_deadline_at"], "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=UTC
        )
        - now_utc
    ).total_seconds()
    remaining_monotonic = monotonic_deadline - time.monotonic()
    if remaining_authority <= 0 or remaining_monotonic <= 0:
        observation = CodexProcessObservation(
            None,
            None,
            None,
            _timestamp(),
            b"",
            True,
            b"",
            True,
            None,
            "authorization-expired",
            "not-invoked",
        )
        capture.complete(_completion(capture, observation))
        return observation
    timeout_seconds = min(
        float(plan["timeout_seconds"]),
        remaining_authority,
        remaining_monotonic,
    )
    launch_attempted_at = _timestamp()
    process: subprocess.Popen[bytes] | None = None
    try:
        process = subprocess.Popen(
            list(popen_argv),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd="/",
            env={},
            start_new_session=True,
            pass_fds=tuple(pass_fds),
        )
    except OSError:
        observation = CodexProcessObservation(
            launch_attempted_at,
            None,
            None,
            _timestamp(),
            b"",
            True,
            b"",
            True,
            None,
            "spawn-failure",
            "not-invoked",
        )
        capture.complete(_completion(capture, observation))
        return observation

    process_started_at = _timestamp()

    selector: selectors.BaseSelector | None = None
    try:
        if process.stdin is None or process.stdout is None or process.stderr is None:
            raise CodexAdapterError("live_process_pipe_unavailable")
        selector = selectors.DefaultSelector()
        os.set_blocking(process.stdin.fileno(), False)
        os.set_blocking(process.stdout.fileno(), False)
        os.set_blocking(process.stderr.fileno(), False)
        stdin_view = memoryview(stdin)
        stdin_position = 0
        if stdin:
            selector.register(process.stdin, selectors.EVENT_WRITE, ("stdin", 0))
        else:
            process.stdin.close()
        selector.register(
            process.stdout,
            selectors.EVENT_READ,
            ("stdout", plan["stdout_limit"]),
        )
        selector.register(
            process.stderr,
            selectors.EVENT_READ,
            ("stderr", plan["stderr_limit"]),
        )
        streams = {
            "stdout": process.stdout,
            "stderr": process.stderr,
        }
        buffers = {"stdout": bytearray(), "stderr": bytearray()}
        raw_counts = {"stdout": 0, "stderr": 0}
        complete = {"stdout": True, "stderr": True}
        gates: dict[str, ExactSecretStreamQuarantine | _PassThroughQuarantine] = {
            name: credential.stream_quarantine()
            if credential is not None
            else _PassThroughQuarantine()
            for name in ("stdout", "stderr")
        }
        termination = "exited"
        killed = False
        deadline = time.monotonic() + timeout_seconds
        while selector.get_map():
            remaining = deadline - time.monotonic()
            if remaining <= 0 and not killed:
                termination = "timeout"
                killed = True
                _terminate_process_group(process)
            events = selector.select(
                max(0.0, min(remaining, 0.1)) if not killed else 0.1
            )
            for key, _mask in events:
                name, limit = key.data
                if name == "stdin":
                    try:
                        count = os.write(key.fd, stdin_view[stdin_position:])
                    except BlockingIOError:
                        count = 0
                    except BrokenPipeError:
                        count = 0
                        _unregister_close(selector, key.fileobj)
                    stdin_position += count
                    if not key.fileobj.closed and stdin_position == len(stdin):
                        _unregister_close(selector, key.fileobj)
                    continue
                try:
                    chunk = os.read(key.fd, 65536)
                except BlockingIOError:
                    continue
                if not chunk:
                    tail = gates[name].finish()
                    _retain_safe_chunk(capture, name, tail, buffers[name])
                    _unregister_close(selector, key.fileobj)
                    continue
                available = max(0, limit - raw_counts[name])
                retained_chunk = chunk[:available]
                raw_counts[name] += len(retained_chunk)
                safe = gates[name].feed(retained_chunk)
                _retain_safe_chunk(capture, name, safe, buffers[name])
                if gates[name].quarantined:
                    complete[name] = False
                    termination = "privacy-quarantine"
                    if not killed:
                        killed = True
                        _terminate_process_group(process)
                elif len(chunk) > available:
                    complete[name] = False
                    if termination == "exited":
                        termination = f"{name}-limit"
                    if not killed:
                        killed = True
                        _terminate_process_group(process)
            if killed and process.poll() is not None and not events:
                for name, stream in streams.items():
                    if not stream.closed:
                        complete[name] = False
                        gates[name].abandon()
                        _unregister_close(selector, stream)
                break
        exit_code = process.wait(timeout=1)
        if credential is not None and termination != "privacy-quarantine":
            credential.assert_streams_safe(
                bytes(buffers["stdout"]), bytes(buffers["stderr"])
            )
        observation = CodexProcessObservation(
            launch_attempted_at,
            process_started_at,
            _timestamp(),
            _timestamp(),
            bytes(buffers["stdout"]),
            complete["stdout"],
            bytes(buffers["stderr"]),
            complete["stderr"],
            exit_code,
            termination,
            "invoked",
        )
        capture.complete(_completion(capture, observation))
        return observation
    except BaseException:
        _terminate_process_group(process)
        try:
            process.wait(timeout=1)
        except subprocess.TimeoutExpired:
            _terminate_process_group(process, force=True)
            process.wait()
        for stream in (process.stdin, process.stdout, process.stderr):
            if stream is not None and not stream.closed:
                stream.close()
        capture.close()
        raise
    finally:
        if selector is not None:
            selector.close()


class _PassThroughQuarantine:
    quarantined = False

    def feed(self, payload: bytes) -> bytes:
        return payload

    def finish(self) -> bytes:
        return b""

    def abandon(self) -> None:
        return None


def _retain_safe_chunk(
    capture: FreshProcessCapture,
    stream_name: str,
    payload: bytes,
    buffer: bytearray,
) -> None:
    if not payload:
        return
    if stream_name == "stdout":
        capture.write_stdout(payload)
    else:
        capture.write_stderr(payload)
    buffer.extend(payload)


def _completion(
    capture: FreshProcessCapture, observation: CodexProcessObservation
) -> dict[str, Any]:
    return {
        "schema_version": "caplab-revbench-live-process-completion/1",
        "process_id": capture.intent["process_id"],
        "launch_attempted_at": observation.launch_attempted_at,
        "process_started_at": observation.process_started_at,
        "process_completed_at": observation.process_completed_at,
        "completion_recorded_at": observation.completion_recorded_at,
        "stdout_complete": observation.stdout_complete,
        "stderr_complete": observation.stderr_complete,
        "exit_code": observation.exit_code,
        "termination": observation.termination,
        "invocation_state": observation.invocation_state,
    }


def _terminate_process_group(
    process: subprocess.Popen[bytes], *, force: bool = False
) -> None:
    signal_number = signal.SIGKILL if force else signal.SIGTERM
    try:
        os.killpg(process.pid, signal_number)
    except ProcessLookupError:
        return
    if force:
        return
    try:
        process.wait(timeout=1)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass


def _unregister_close(selector: selectors.BaseSelector, stream: Any) -> None:
    try:
        selector.unregister(stream)
    except KeyError:
        pass
    stream.close()


def _timestamp() -> str:
    return datetime.now(UTC).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")


def derive_codex_response(raw_stdout: bytes) -> DerivedCodexResponse:
    """Extract the final agent message from one complete Codex JSONL turn."""

    if (
        not isinstance(raw_stdout, bytes)
        or not raw_stdout
        or not raw_stdout.endswith(b"\n")
    ):
        raise CodexJSONLTransportError("codex_jsonl_not_complete")
    lines = raw_stdout.splitlines()
    events: list[dict[str, Any]] = []
    for index, line in enumerate(lines):
        if not line:
            raise CodexJSONLTransportError(f"codex_jsonl_empty_line:{index}")
        try:
            event = json.loads(line, object_pairs_hook=_unique_object)
        except (UnicodeError, json.JSONDecodeError, ValueError) as error:
            raise CodexJSONLTransportError(
                f"codex_jsonl_invalid_event:{index}"
            ) from error
        if not isinstance(event, dict) or not isinstance(event.get("type"), str):
            raise CodexJSONLTransportError(f"codex_jsonl_invalid_event:{index}")
        events.append(event)
    thread_starts = [
        index for index, event in enumerate(events) if event["type"] == "thread.started"
    ]
    if thread_starts != [0]:
        raise CodexJSONLTransportError("codex_jsonl_missing_thread_start")
    turn_starts = [
        index for index, event in enumerate(events) if event["type"] == "turn.started"
    ]
    if len(turn_starts) != 1 or turn_starts[0] <= 0:
        raise CodexJSONLTransportError("codex_jsonl_turn_start_invalid")
    turn_start = turn_starts[0]
    terminal = [
        index for index, event in enumerate(events) if event["type"] == "turn.completed"
    ]
    if terminal != [len(events) - 1]:
        raise CodexJSONLTransportError("codex_jsonl_terminal_turn_invalid")
    if any(event["type"] in {"turn.failed", "error"} for event in events):
        raise CodexJSONLTransportError("codex_jsonl_failed_turn")
    messages: list[tuple[int, dict[str, Any]]] = []
    for index, event in enumerate(events[:-1]):
        if event["type"] != "item.completed":
            continue
        item = event.get("item")
        if (
            isinstance(item, dict)
            and item.get("type") == "agent_message"
            and isinstance(item.get("id"), str)
            and item["id"]
            and isinstance(item.get("text"), str)
        ):
            if index <= turn_start:
                raise CodexJSONLTransportError("codex_jsonl_agent_message_outside_turn")
            messages.append((index, item))
    if not messages:
        raise CodexJSONLTransportError("codex_jsonl_agent_message_missing")
    event_index, item = messages[-1]
    text = item["text"]
    try:
        response = _native_response(text.encode("utf-8"))
    except CodexAdapterError as error:
        raise CodexResponseSchemaError(str(error)) from error
    return DerivedCodexResponse(
        response=response,
        response_bytes=canonical_json(response),
        selected_event_index=event_index,
        selected_item_id=item["id"],
        extracted_text_sha256=sha256_hex(text.encode("utf-8")),
    )


def response_derivation_document(
    derived: DerivedCodexResponse,
    raw_stdout_ref: Mapping[str, Any],
    derived_response_ref: Mapping[str, Any],
) -> dict[str, Any]:
    """Bind registered response bytes to their exact raw JSONL source."""

    return {
        "schema_version": "caplab-revbench-response-derivation/1",
        "adapter": "codex-jsonl-final-agent-message/1",
        "raw_stdout_ref": _canonical_copy(raw_stdout_ref),
        "selected_event_index": derived.selected_event_index,
        "selected_event_type": "item.completed",
        "selected_item_id": derived.selected_item_id,
        "extracted_text_sha256": derived.extracted_text_sha256,
        "derived_response_ref": _canonical_copy(derived_response_ref),
    }


@contextlib.contextmanager
def credential_memfd(
    source: Path,
    profile: Mapping[str, Any],
    *,
    credential_root: Path,
) -> Iterator[SealedCredential]:
    """Validate a dedicated credential and expose bytes in a sealed memfd.

    The source path and credential bytes are operational inputs.  They are not
    returned, hashed as a whole, registered, or written to a named staging file.
    """

    owned_profile = _validate_profile(profile)
    source = Path(source)
    root = Path(credential_root)
    if not source.is_absolute() or not root.is_absolute() or source.parent != root:
        raise CodexAdapterError("credential_source_outside_configured_root")
    if source.name in {"", ".", ".."}:
        raise CodexAdapterError("credential_source_outside_configured_root")
    root_descriptor: int | None = None
    source_descriptor: int | None = None
    credential_descriptor: int | None = None
    try:
        root_flags = os.O_RDONLY | os.O_CLOEXEC
        if hasattr(os, "O_DIRECTORY"):
            root_flags |= os.O_DIRECTORY
        if hasattr(os, "O_NOFOLLOW"):
            root_flags |= os.O_NOFOLLOW
        try:
            root_descriptor = os.open(root, root_flags)
        except OSError as error:
            raise CodexAdapterError("credential_root_open_failed") from error
        root_metadata = os.fstat(root_descriptor)
        if (
            not stat.S_ISDIR(root_metadata.st_mode)
            or root_metadata.st_uid != os.geteuid()
            or stat.S_IMODE(root_metadata.st_mode) != 0o700
        ):
            raise CodexAdapterError("credential_root_owner_or_mode_invalid")
        # A configured direct child is not trusted to be regular until after
        # fstat.  Nonblocking open prevents an owner-mode FIFO from hanging a
        # durable effect intent while preserving ordinary regular-file reads.
        flags = os.O_RDONLY | os.O_CLOEXEC | os.O_NONBLOCK
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        try:
            source_descriptor = os.open(source.name, flags, dir_fd=root_descriptor)
        except OSError as error:
            raise CodexAdapterError("credential_source_open_failed") from error
        metadata = os.fstat(source_descriptor)
        if (
            not stat.S_ISREG(metadata.st_mode)
            or metadata.st_uid != os.geteuid()
            or stat.S_IMODE(metadata.st_mode) != 0o600
            or metadata.st_nlink != 1
            or metadata.st_size <= 0
            or metadata.st_size > _MAX_CREDENTIAL_BYTES
        ):
            raise CodexAdapterError("credential_source_owner_or_mode_invalid")
        payload = _read_bounded(source_descriptor, metadata.st_size)
        retained_metadata = os.fstat(source_descriptor)
        metadata_identity = (
            "st_dev",
            "st_ino",
            "st_uid",
            "st_mode",
            "st_nlink",
            "st_size",
            "st_mtime_ns",
            "st_ctime_ns",
        )
        if any(
            getattr(retained_metadata, field) != getattr(metadata, field)
            for field in metadata_identity
        ):
            raise CodexAdapterError("credential_source_changed_during_read")
        secret_values = _validate_credential_payload(payload, owned_profile)
        memfd_flags = os.MFD_CLOEXEC | getattr(os, "MFD_ALLOW_SEALING", 0)
        credential_descriptor = os.memfd_create(
            "caplab-revbench-codex-auth", memfd_flags
        )
        _write_all(credential_descriptor, payload)
        os.fdatasync(credential_descriptor)
        os.lseek(credential_descriptor, 0, os.SEEK_SET)
        seals = (
            fcntl.F_SEAL_SEAL
            | fcntl.F_SEAL_SHRINK
            | fcntl.F_SEAL_GROW
            | fcntl.F_SEAL_WRITE
        )
        fcntl.fcntl(credential_descriptor, fcntl.F_ADD_SEALS, seals)
        yield SealedCredential(credential_descriptor, secret_values)
    finally:
        if source_descriptor is not None:
            os.close(source_descriptor)
        if root_descriptor is not None:
            os.close(root_descriptor)
        if credential_descriptor is not None:
            os.close(credential_descriptor)


def _native_response(payload: bytes) -> dict[str, Any]:
    try:
        response = json.loads(payload, object_pairs_hook=_unique_object)
    except (UnicodeError, json.JSONDecodeError, ValueError) as error:
        raise CodexAdapterError("codex_response_invalid_json") from error
    if not isinstance(response, dict) or set(response) != {
        "schema_version",
        "verdict",
        "anchors",
    }:
        raise CodexAdapterError("codex_response_shape_invalid")
    if response["schema_version"] != "caplab-revbench-native-response/1":
        raise CodexAdapterError("codex_response_schema_invalid")
    verdict = response["verdict"]
    anchors = response["anchors"]
    if verdict not in {"clean", "defect"} or not isinstance(anchors, list):
        raise CodexAdapterError("codex_response_value_invalid")
    if any(
        not isinstance(anchor, str) or _JSON_POINTER.fullmatch(anchor) is None
        for anchor in anchors
    ):
        raise CodexAdapterError("codex_response_anchor_invalid")
    if anchors != sorted(set(anchors)):
        raise CodexAdapterError("codex_response_anchors_not_sorted_unique")
    if (verdict == "clean" and anchors) or (verdict == "defect" and not anchors):
        raise CodexAdapterError("codex_response_verdict_anchor_mismatch")
    return response


def _validate_profile(profile: Mapping[str, Any]) -> dict[str, Any]:
    owned = _canonical_copy(profile)
    if set(owned) != {
        "schema_version",
        "profile_id",
        "provider",
        "auth_method",
        "identity_basis",
        "provider_account_id_sha256",
        "provider_subject_sha256",
        "identity_token_issuer",
        "identity_token_audience",
    }:
        raise CodexAdapterError("credential_profile_shape_invalid")
    if owned["schema_version"] != "caplab-revbench-codex-credential-profile/1":
        raise CodexAdapterError("credential_profile_schema_invalid")
    if (
        not isinstance(owned["profile_id"], str)
        or _IDENTIFIER.fullmatch(owned["profile_id"]) is None
    ):
        raise CodexAdapterError("credential_profile_id_invalid")
    if owned["provider"] != "openai" or owned["auth_method"] != "chatgpt":
        raise CodexAdapterError("credential_auth_method_invalid")
    if owned["identity_basis"] != "operator-declared-unverified-token-claims":
        raise CodexAdapterError("credential_identity_basis_invalid")
    for identity_field in ("provider_account_id_sha256", "provider_subject_sha256"):
        if (
            not isinstance(owned[identity_field], str)
            or _HEX_DIGEST.fullmatch(owned[identity_field]) is None
        ):
            raise CodexAdapterError(f"credential_{identity_field}_invalid")
    if owned["identity_token_issuer"] != "https://auth.openai.com":
        raise CodexAdapterError("credential_identity_token_issuer_invalid")
    audience = owned["identity_token_audience"]
    if (
        not isinstance(audience, list)
        or not audience
        or audience != sorted(set(audience))
        or any(not isinstance(value, str) or not value for value in audience)
    ):
        raise CodexAdapterError("credential_identity_token_audience_invalid")
    return owned


def _validate_credential_payload(
    payload: bytes, profile: Mapping[str, Any]
) -> tuple[bytes, ...]:
    try:
        document = json.loads(payload, object_pairs_hook=_unique_object)
    except (UnicodeError, json.JSONDecodeError, ValueError) as error:
        raise CodexAdapterError("credential_document_invalid") from error
    if not isinstance(document, dict) or set(document) != {
        "auth_mode",
        "OPENAI_API_KEY",
        "tokens",
        "last_refresh",
    }:
        raise CodexAdapterError("credential_document_shape_invalid")
    if document.get("auth_mode") != "chatgpt" or document["OPENAI_API_KEY"] is not None:
        raise CodexAdapterError("credential_auth_method_mismatch")
    try:
        datetime.strptime(document["last_refresh"], "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=UTC
        )
    except (TypeError, ValueError) as error:
        raise CodexAdapterError("credential_last_refresh_invalid") from error
    tokens = document.get("tokens")
    if not isinstance(tokens, dict) or set(tokens) != {
        "id_token",
        "access_token",
        "refresh_token",
        "account_id",
    }:
        raise CodexAdapterError("credential_tokens_invalid")
    if any(
        not isinstance(tokens[field], str) or len(tokens[field]) < 12
        for field in ("id_token", "access_token", "refresh_token", "account_id")
    ):
        raise CodexAdapterError("credential_tokens_invalid")
    account_id = tokens["account_id"]
    if (
        len(account_id.encode("utf-8")) < 16
        or sha256_hex(account_id.encode("utf-8"))
        != profile["provider_account_id_sha256"]
    ):
        raise CodexAdapterError("credential_provider_account_mismatch")
    token_parts = tokens["id_token"].split(".")
    if len(token_parts) != 3:
        raise CodexAdapterError("credential_identity_token_invalid")
    try:
        encoded_header = token_parts[0].encode("ascii")
        header = json.loads(
            base64.urlsafe_b64decode(
                encoded_header + b"=" * (-len(encoded_header) % 4)
            ),
            object_pairs_hook=_unique_object,
        )
        encoded = token_parts[1].encode("ascii")
        claims = json.loads(
            base64.urlsafe_b64decode(encoded + b"=" * (-len(encoded) % 4)),
            object_pairs_hook=_unique_object,
        )
    except (UnicodeError, ValueError, json.JSONDecodeError) as error:
        raise CodexAdapterError("credential_identity_token_invalid") from error
    if (
        not isinstance(header, dict)
        or set(header) != {"alg", "kid", "typ"}
        or header["alg"] != "RS256"
        or header["typ"] != "JWT"
        or not isinstance(header["kid"], str)
        or len(header["kid"]) < 8
    ):
        raise CodexAdapterError("credential_identity_token_algorithm_invalid")
    subject = claims.get("sub") if isinstance(claims, dict) else None
    if not isinstance(subject, str) or len(subject.encode("utf-8")) < 16:
        raise CodexAdapterError("credential_provider_subject_invalid")
    if sha256_hex(subject.encode("utf-8")) != profile["provider_subject_sha256"]:
        raise CodexAdapterError("credential_provider_subject_mismatch")
    if claims.get("iss") != profile["identity_token_issuer"]:
        raise CodexAdapterError("credential_identity_token_issuer_mismatch")
    audience = claims.get("aud")
    if isinstance(audience, str):
        audience = [audience]
    if audience != profile["identity_token_audience"]:
        raise CodexAdapterError("credential_identity_token_audience_mismatch")
    issued_at = claims.get("iat")
    expires_at = claims.get("exp")
    now = int(datetime.now(UTC).timestamp())
    if (
        isinstance(issued_at, bool)
        or not isinstance(issued_at, int)
        or isinstance(expires_at, bool)
        or not isinstance(expires_at, int)
        or issued_at >= expires_at
        or expires_at <= now
    ):
        raise CodexAdapterError("credential_identity_token_expiry_invalid")
    try:
        signature = base64.urlsafe_b64decode(
            token_parts[2].encode("ascii") + b"=" * (-len(token_parts[2]) % 4)
        )
    except (UnicodeError, ValueError) as error:
        raise CodexAdapterError(
            "credential_identity_token_signature_invalid"
        ) from error
    if len(signature) < 12:
        raise CodexAdapterError("credential_identity_token_signature_invalid")
    # The local JWT parser is only an operator-provisioned mismatch guard; it
    # does not authenticate provider identity.  Treat every decoded string
    # scalar as sensitive for the exact-scalar streaming quarantine, including
    # unknown/private claims such as email, name, workspace, or organization.
    # Also retain each encoded JWT segment so a partial token echo is caught.
    secret_values = {
        tokens["id_token"].encode("utf-8"),
        tokens["access_token"].encode("utf-8"),
        tokens["refresh_token"].encode("utf-8"),
        account_id.encode("utf-8"),
        subject.encode("utf-8"),
        header["kid"].encode("utf-8"),
        document["last_refresh"].encode("utf-8"),
    }
    standard_claims = {"sub", "iss", "aud", "iat", "exp"}
    for key, value in claims.items():
        if isinstance(key, str) and key and key not in standard_claims:
            secret_values.add(key.encode("utf-8"))
            secret_values.update(_credential_string_scalars(value))
    secret_values.update(part.encode("ascii") for part in token_parts if part)
    if not secret_values:
        raise CodexAdapterError("credential_secret_set_invalid")
    return tuple(sorted(secret_values, key=lambda value: (len(value), value)))


def _credential_string_scalars(value: Any) -> tuple[bytes, ...]:
    """Return every nonempty decoded string value without retaining paths."""

    scalars: list[bytes] = []
    if isinstance(value, str):
        encoded = value.encode("utf-8")
        if encoded:
            scalars.append(encoded)
    elif isinstance(value, Mapping):
        for child in value.values():
            scalars.extend(_credential_string_scalars(child))
    elif isinstance(value, list):
        for child in value:
            scalars.extend(_credential_string_scalars(child))
    return tuple(scalars)


def _read_bounded(descriptor: int, expected_size: int) -> bytes:
    chunks: list[bytes] = []
    remaining = expected_size + 1
    while remaining:
        chunk = os.read(descriptor, min(65536, remaining))
        if not chunk:
            break
        chunks.append(chunk)
        remaining -= len(chunk)
    payload = b"".join(chunks)
    if len(payload) != expected_size:
        raise CodexAdapterError("credential_source_changed_during_read")
    return payload


def _write_all(descriptor: int, payload: bytes) -> None:
    view = memoryview(payload)
    written = 0
    while written < len(view):
        count = os.write(descriptor, view[written:])
        if count <= 0:
            raise CodexAdapterError("credential_memfd_write_failed")
        written += count


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _canonical_copy(value: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise CodexAdapterError("document_not_object")
    try:
        copied = json.loads(canonical_json(value))
    except (TypeError, ValueError) as error:
        raise CodexAdapterError("document_not_canonicalizable") from error
    if not isinstance(copied, dict):
        raise CodexAdapterError("document_not_object")
    return copied
