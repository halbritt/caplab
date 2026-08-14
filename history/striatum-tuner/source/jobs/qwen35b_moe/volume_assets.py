"""Verify immutable model assets preloaded on the RunPod network volume."""

from __future__ import annotations

import hashlib
from collections.abc import Mapping
from pathlib import Path
import re

from .contract import ContractError, sha256_file


_MANIFEST_LINE = re.compile(r"([0-9a-f]{64})  ([^\x00\r\n]+)")
ASSET_MANIFEST_SHA256 = (
    "2d56aa53dc94146a01f044b04d7d161015c2f848f575779b49fa5307fe295ff8"
)
ASSET_FILES = 41
ASSET_BYTES = 142_993_858_696


def validate_asset_receipt(receipt: Mapping[str, object]) -> dict[str, object]:
    expected = {
        "protocol": "striatum-volume-assets/1",
        "manifest_sha256": ASSET_MANIFEST_SHA256,
        "files": ASSET_FILES,
        "bytes": ASSET_BYTES,
    }
    if dict(receipt) != expected:
        raise ContractError("volume asset receipt is invalid")
    return dict(receipt)


def _manifest_entries(manifest_path: Path) -> tuple[tuple[str, Path], ...]:
    try:
        lines = manifest_path.read_text().splitlines()
    except OSError as error:
        raise ContractError(f"volume asset manifest is unavailable: {manifest_path}") from error
    if not lines:
        raise ContractError("volume asset manifest is empty")
    entries: list[tuple[str, Path]] = []
    seen: set[Path] = set()
    for line in lines:
        match = _MANIFEST_LINE.fullmatch(line)
        if match is None:
            raise ContractError("volume asset manifest contains an invalid line")
        relative = Path(match.group(2))
        if (
            relative.is_absolute()
            or "\\" in match.group(2)
            or any(part in {"", ".", ".."} for part in relative.parts)
        ):
            raise ContractError("volume asset manifest contains an unsafe path")
        if relative in seen:
            raise ContractError(f"volume asset manifest repeats a path: {relative}")
        seen.add(relative)
        entries.append((match.group(1), relative))
    return tuple(entries)


def verify_asset_manifest(
    root: Path,
    *,
    manifest_path: Path,
    expected_manifest_sha256: str,
) -> dict[str, object]:
    """Hash every declared asset and reject missing, extra, or linked entries."""
    if not re.fullmatch(r"[0-9a-f]{64}", expected_manifest_sha256):
        raise ContractError("expected volume asset manifest hash is invalid")
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise ContractError("volume asset manifest is missing or not a regular file")
    actual_manifest_sha256 = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    if actual_manifest_sha256 != expected_manifest_sha256:
        raise ContractError("volume asset manifest hash mismatch")
    if root.is_symlink() or not root.is_dir():
        raise ContractError("volume asset root is missing or not a directory")

    entries = _manifest_entries(manifest_path)
    expected_files = {relative for _digest, relative in entries}
    expected_directories = {
        parent
        for relative in expected_files
        for parent in relative.parents
        if parent != Path(".")
    }
    actual_files: set[Path] = set()
    actual_directories: set[Path] = set()
    for path in root.rglob("*"):
        relative = path.relative_to(root)
        if path.is_symlink():
            raise ContractError(f"volume asset tree contains a symlink: {relative}")
        if path.is_file():
            actual_files.add(relative)
        elif path.is_dir():
            actual_directories.add(relative)
        else:
            raise ContractError(f"volume asset tree contains a non-regular entry: {relative}")
    if actual_files != expected_files or actual_directories != expected_directories:
        raise ContractError("volume asset tree has missing or extra entries")

    total_bytes = 0
    for expected_sha256, relative in entries:
        path = root.joinpath(*relative.parts)
        total_bytes += path.stat().st_size
        if sha256_file(path) != expected_sha256:
            raise ContractError(f"volume asset hash mismatch: {relative}")
    return {
        "protocol": "striatum-volume-assets/1",
        "manifest_sha256": actual_manifest_sha256,
        "files": len(entries),
        "bytes": total_bytes,
    }
