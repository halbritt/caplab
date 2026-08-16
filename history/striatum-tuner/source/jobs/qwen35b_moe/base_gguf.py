"""Fail-closed receipts for the local BF16 GGUF and legacy OCI-safe splits."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Any

from .contract import MODEL, ContractError, sha256_file
from .export import LLAMA_CPP_COMMIT


BASE_GGUF_NAME = "base-bf16.gguf"
BASE_RECEIPT_NAME = "base-bf16.receipt.json"
SPLIT_RECEIPT_NAME = "base-bf16.split-receipt.json"
SPLIT_MAX_SIZE = "4G"
MAX_SHARD_BYTES = 4 * 1024**3
_SHARD_PATTERN = re.compile(r"base-bf16-(\d{5})-of-(\d{5})\.gguf")


@dataclass(frozen=True)
class BaseGgufArtifacts:
    source: Path
    source_receipt: dict[str, Any]
    split_receipt: dict[str, Any]
    shards: tuple[Path, ...]

    @property
    def first_shard(self) -> Path:
        return self.shards[0]


def _load_receipt(path: Path) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise ContractError(f"required regular receipt is missing: {path}")
    try:
        value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise ContractError(f"could not read receipt {path}: {error}") from error
    if not isinstance(value, dict):
        raise ContractError(f"receipt is not a JSON object: {path}")
    return value


def validate_source_receipt(
    model_snapshot: Path, *, verify_hash: bool = True
) -> tuple[Path, dict[str, Any]]:
    source = model_snapshot / BASE_GGUF_NAME
    if source.is_symlink() or not source.is_file():
        raise ContractError(f"required regular base GGUF is missing: {source}")
    receipt = _load_receipt(model_snapshot / BASE_RECEIPT_NAME)
    expected = {
        "protocol": "striatum-base-gguf-readiness/1",
        "model_revision": MODEL.revision,
        "llama_cpp_commit": LLAMA_CPP_COMMIT,
        "size": source.stat().st_size,
    }
    for key, value in expected.items():
        if receipt.get(key) != value:
            raise ContractError(
                f"base GGUF receipt {key} mismatch: {receipt.get(key)!r} != {value!r}"
            )
    if Path(str(receipt.get("path", ""))).name != BASE_GGUF_NAME:
        raise ContractError("base GGUF receipt names an unexpected source file")
    digest = receipt.get("sha256")
    if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise ContractError("base GGUF receipt has an invalid sha256")
    if verify_hash and sha256_file(source) != digest:
        raise ContractError("base GGUF sha256 does not match its receipt")
    return source, receipt


def discover_split_shards(model_snapshot: Path) -> tuple[Path, ...]:
    shards = tuple(sorted(model_snapshot.glob("base-bf16-*-of-*.gguf")))
    if not shards:
        raise ContractError("no native split GGUF shards were found")
    parsed: list[tuple[int, int, Path]] = []
    for shard in shards:
        if shard.is_symlink() or not shard.is_file():
            raise ContractError(f"split GGUF is not a regular file: {shard}")
        match = _SHARD_PATTERN.fullmatch(shard.name)
        if match is None:
            raise ContractError(f"split GGUF has an invalid name: {shard.name}")
        parsed.append((int(match.group(1)), int(match.group(2)), shard))
    totals = {total for _, total, _ in parsed}
    if len(totals) != 1:
        raise ContractError("split GGUF names disagree on the total shard count")
    total = totals.pop()
    if total != len(parsed) or [index for index, _, _ in parsed] != list(
        range(1, total + 1)
    ):
        raise ContractError("split GGUF set is incomplete or non-contiguous")
    for _, _, shard in parsed:
        size = shard.stat().st_size
        if size <= 0 or size > MAX_SHARD_BYTES:
            raise ContractError(
                f"split GGUF shard violates the 4 GiB OCI limit: {shard.name} ({size})"
            )
    return tuple(shard for _, _, shard in parsed)


def validate_base_gguf_artifacts(
    model_snapshot: Path, *, verify_hashes: bool = True
) -> BaseGgufArtifacts:
    source, source_receipt = validate_source_receipt(
        model_snapshot, verify_hash=verify_hashes
    )
    shards = discover_split_shards(model_snapshot)
    receipt = _load_receipt(model_snapshot / SPLIT_RECEIPT_NAME)
    expected = {
        "protocol": "striatum-base-gguf-split/1",
        "model_revision": MODEL.revision,
        "llama_cpp_commit": LLAMA_CPP_COMMIT,
        "source_size": source_receipt["size"],
        "source_sha256": source_receipt["sha256"],
        "split_max_size": SPLIT_MAX_SIZE,
        "first_shard": shards[0].name,
    }
    for key, value in expected.items():
        if receipt.get(key) != value:
            raise ContractError(
                f"split GGUF receipt {key} mismatch: {receipt.get(key)!r} != {value!r}"
            )
    entries = receipt.get("shards")
    if not isinstance(entries, list) or len(entries) != len(shards):
        raise ContractError("split GGUF receipt has an unexpected shard list")
    for shard, entry in zip(shards, entries, strict=True):
        if not isinstance(entry, dict):
            raise ContractError("split GGUF receipt contains a non-object entry")
        expected_entry = {"path": shard.name, "size": shard.stat().st_size}
        for key, value in expected_entry.items():
            if entry.get(key) != value:
                raise ContractError(
                    f"split GGUF receipt entry mismatch for {shard.name}: {key}"
                )
        digest = entry.get("sha256")
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ContractError(f"split GGUF receipt has a bad hash for {shard.name}")
        if verify_hashes and sha256_file(shard) != digest:
            raise ContractError(f"split GGUF hash mismatch: {shard.name}")
    total_split_bytes = sum(shard.stat().st_size for shard in shards)
    if total_split_bytes < source.stat().st_size:
        raise ContractError("split GGUF set is smaller than its source")
    return BaseGgufArtifacts(source, source_receipt, receipt, shards)
