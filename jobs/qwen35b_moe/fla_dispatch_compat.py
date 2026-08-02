"""Apply the narrow FLA 0.5.2 dispatch fix required by Torch 2.8."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
from typing import Any

from .contract import ContractError


PACKAGE = "fla-core"
VERSION = "0.5.2"
RELATIVE_SOURCE = Path("fla/ops/gated_delta_rule/chunk.py")
PREIMAGE_SHA256 = "fd4e01dc22a8c139c2a6eb61e47ae472a50322e4b4fff006cc5039a4602b310e"
POSTIMAGE_SHA256 = "4facb155ff109eee67212c8eb0fcfffc44a1d193d7a278137cda3eb6d0ffe03f"
PREIMAGE_DECORATORS = b"@dispatch('gated_delta_rule')\n@torch.compiler.disable\ndef chunk_gated_delta_rule("
POSTIMAGE_DECORATORS = b"@dispatch('gated_delta_rule')\ndef chunk_gated_delta_rule("


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def patch_source(
    content: bytes,
    *,
    preimage_sha256: str = PREIMAGE_SHA256,
    postimage_sha256: str = POSTIMAGE_SHA256,
) -> tuple[bytes, str]:
    """Return the corrected source and whether it was changed or already patched."""
    digest = _sha256(content)
    if digest == postimage_sha256:
        return content, "already-patched"
    if digest != preimage_sha256:
        raise ContractError(
            "FLA dispatch compatibility patch refused unknown source: "
            f"expected {preimage_sha256}, found {digest}"
        )
    if content.count(PREIMAGE_DECORATORS) != 1:
        raise ContractError("FLA dispatch compatibility preimage is not unique")
    patched = content.replace(PREIMAGE_DECORATORS, POSTIMAGE_DECORATORS, 1)
    patched_digest = _sha256(patched)
    if patched_digest != postimage_sha256:
        raise ContractError(
            "FLA dispatch compatibility postimage mismatch: "
            f"expected {postimage_sha256}, found {patched_digest}"
        )
    return patched, "patched"


def installed_source() -> Path:
    distribution = importlib.metadata.distribution(PACKAGE)
    version = distribution.version
    if version != VERSION:
        raise ContractError(
            f"FLA dispatch compatibility requires {PACKAGE} {VERSION}, found {version}"
        )
    return Path(distribution.locate_file(RELATIVE_SOURCE))


def apply_patch(source: Path | None = None) -> dict[str, Any]:
    """Patch the exact installed wheel source, refusing package or source drift."""
    target = installed_source() if source is None else source
    original = target.read_bytes()
    patched, status = patch_source(original)
    if status == "patched":
        target.write_bytes(patched)
    persisted = target.read_bytes()
    if _sha256(persisted) != POSTIMAGE_SHA256:
        raise ContractError("FLA dispatch compatibility patch did not persist")
    return {
        "package": PACKAGE,
        "version": VERSION,
        "source": str(target),
        "source_sha256": POSTIMAGE_SHA256,
        "status": status,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path)
    args = parser.parse_args()
    print(json.dumps(apply_patch(args.source), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
