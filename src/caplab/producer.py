"""Verified source and package identity for the executing CAPLAB code."""

from __future__ import annotations

import importlib.metadata
import re
import subprocess
import tomllib
from pathlib import Path

from caplab.runtime.canonical import canonical_json, sha256_hex


_COMMIT = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})")
_ARCHIVE_PLACEHOLDER = "$Format:%H$"


class ProducerIdentityError(ValueError):
    """The executing CAPLAB package cannot be identified exactly."""


def producer_identity() -> tuple[str, str, str]:
    """Return distribution version, source commit, and package-byte digest."""

    package_root = Path(__file__).resolve().parent
    version = _distribution_version(package_root)
    commit = _source_commit(package_root)
    inventory: list[dict[str, object]] = []
    for path in sorted(package_root.rglob("*")):
        if path.is_symlink():
            raise ProducerIdentityError("producer_package_symlink_refused")
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        if path.suffix in {".pyc", ".pyo"}:
            continue
        try:
            payload = path.read_bytes()
        except OSError as error:
            raise ProducerIdentityError("producer_package_unreadable") from error
        inventory.append(
            {
                "path": path.relative_to(package_root).as_posix(),
                "sha256": sha256_hex(payload),
                "byte_count": len(payload),
            }
        )
    if not inventory:
        raise ProducerIdentityError("producer_package_empty")
    return version, commit, sha256_hex(canonical_json(inventory))


def _distribution_version(package_root: Path) -> str:
    try:
        version = importlib.metadata.version("agent-capability-lab")
    except importlib.metadata.PackageNotFoundError:
        version = _source_version(package_root)
    if not isinstance(version, str) or not version:
        raise ProducerIdentityError("producer_version_invalid")
    return version


def _source_version(package_root: Path) -> str:
    for parent in package_root.parents:
        project = parent / "pyproject.toml"
        if not project.is_file():
            continue
        try:
            with project.open("rb") as stream:
                version = tomllib.load(stream)["project"]["version"]
        except (OSError, KeyError, TypeError, tomllib.TOMLDecodeError) as error:
            raise ProducerIdentityError("producer_version_unavailable") from error
        if isinstance(version, str) and version:
            return version
        break
    raise ProducerIdentityError("producer_version_unavailable")


def _source_commit(package_root: Path) -> str:
    stamp = package_root / "_source_commit.txt"
    try:
        stamped = stamp.read_text(encoding="ascii").strip()
    except OSError as error:
        raise ProducerIdentityError("producer_commit_stamp_unavailable") from error
    if _COMMIT.fullmatch(stamped):
        return stamped
    if stamped != _ARCHIVE_PLACEHOLDER:
        raise ProducerIdentityError("producer_commit_stamp_invalid")
    try:
        result = subprocess.run(
            [
                "/usr/bin/git",
                "-C",
                str(package_root),
                "rev-parse",
                "--show-toplevel",
                "HEAD",
            ],
            env={"LC_ALL": "C"},
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        raise ProducerIdentityError("producer_commit_unavailable") from error
    lines = result.stdout.splitlines()
    if len(lines) != 2:
        raise ProducerIdentityError("producer_commit_checkout_invalid")
    try:
        repository_root = Path(lines[0]).resolve(strict=True)
        resolved_package_root = package_root.resolve(strict=True)
    except OSError as error:
        raise ProducerIdentityError("producer_commit_checkout_invalid") from error
    if resolved_package_root != repository_root / "src" / "caplab":
        # An installed package can sit under an unrelated ambient repository.
        # Its HEAD is not CAPLAB provenance and must never satisfy the archive
        # placeholder fallback.
        raise ProducerIdentityError("producer_commit_checkout_invalid")
    commit = lines[1].strip()
    if not _COMMIT.fullmatch(commit):
        raise ProducerIdentityError("producer_commit_invalid")
    return commit
