"""Apply narrow, hash-bound FLA 0.5.2 fixes for Qwen on Hopper."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
from pathlib import Path
from typing import Any

from .contract import ContractError


PACKAGE = "fla-core"
VERSION = "0.5.2"
CHUNK_SOURCE = Path("fla/ops/gated_delta_rule/chunk.py")
CHUNK_PREIMAGE_SHA256 = "fd4e01dc22a8c139c2a6eb61e47ae472a50322e4b4fff006cc5039a4602b310e"
CHUNK_POSTIMAGE_SHA256 = "4facb155ff109eee67212c8eb0fcfffc44a1d193d7a278137cda3eb6d0ffe03f"
PREIMAGE_DECORATORS = b"@dispatch('gated_delta_rule')\n@torch.compiler.disable\ndef chunk_gated_delta_rule("
POSTIMAGE_DECORATORS = b"@dispatch('gated_delta_rule')\ndef chunk_gated_delta_rule("
BACKEND_SOURCE = Path("fla/ops/gated_delta_rule/backends/flash_qla.py")
BACKEND_PREIMAGE_SHA256 = "0945c6e915814a5ac26b98aa9cfc78f67b0452442b95f305c914b0fb2d2dd160"
BACKEND_POSTIMAGE_SHA256 = "c417f9782dc25b065b8ed899df95a1e015469deaa70196d250eebe875ee13436"
BACKEND_REJECTIONS = b"""        if kwargs.get('use_gate_in_kernel'):
            return False, "FlashQLA does not support use_gate_in_kernel"
        if use_beta_sigmoid_in_kernel:
            return False, "FlashQLA does not support use_beta_sigmoid_in_kernel"
        if allow_neg_eigval:
            return False, "FlashQLA does not support allow_neg_eigval"
"""
BACKEND_ADMISSION = b"""        if kwargs.get('use_gate_in_kernel') and not isinstance(kwargs.get('A_log'), torch.Tensor):
            return False, "FlashQLA gate adaptation requires A_log"
        if allow_neg_eigval and not use_beta_sigmoid_in_kernel:
            return False, "allow_neg_eigval requires use_beta_sigmoid_in_kernel"
"""
BACKEND_RETURN = b"""        import flash_qla

        return flash_qla.chunk_gated_delta_rule(
"""
BACKEND_ADAPTATION = b"""        import flash_qla

        if kwargs.get('use_gate_in_kernel'):
            from fla.ops.gated_delta_rule.gate import naive_gdn_gate

            g = naive_gdn_gate(g, kwargs['A_log'], kwargs.get('dt_bias'))
        if use_beta_sigmoid_in_kernel:
            beta = beta.float().sigmoid()
            if allow_neg_eigval:
                beta = beta * 2

        return flash_qla.chunk_gated_delta_rule(
"""


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def patch_source(
    content: bytes,
    *,
    preimage_sha256: str = CHUNK_PREIMAGE_SHA256,
    postimage_sha256: str = CHUNK_POSTIMAGE_SHA256,
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


def patch_backend_source(
    content: bytes,
    *,
    preimage_sha256: str = BACKEND_PREIMAGE_SHA256,
    postimage_sha256: str = BACKEND_POSTIMAGE_SHA256,
) -> tuple[bytes, str]:
    """Adapt only FlashQLA calls that use Qwen's fused gate input contract."""
    digest = _sha256(content)
    if digest == postimage_sha256:
        return content, "already-patched"
    if digest != preimage_sha256:
        raise ContractError(
            "FLA FlashQLA compatibility patch refused unknown source: "
            f"expected {preimage_sha256}, found {digest}"
        )
    for preimage in (BACKEND_REJECTIONS, BACKEND_RETURN):
        if content.count(preimage) != 1:
            raise ContractError("FLA FlashQLA compatibility preimage is not unique")
    patched = content.replace(BACKEND_REJECTIONS, BACKEND_ADMISSION, 1)
    patched = patched.replace(BACKEND_RETURN, BACKEND_ADAPTATION, 1)
    patched_digest = _sha256(patched)
    if patched_digest != postimage_sha256:
        raise ContractError(
            "FLA FlashQLA compatibility postimage mismatch: "
            f"expected {postimage_sha256}, found {patched_digest}"
        )
    return patched, "patched"


def _distribution() -> importlib.metadata.Distribution:
    distribution = importlib.metadata.distribution(PACKAGE)
    version = distribution.version
    if version != VERSION:
        raise ContractError(
            f"FLA dispatch compatibility requires {PACKAGE} {VERSION}, found {version}"
        )
    return distribution


def _persist(
    target: Path,
    patcher: Any,
    expected_postimage: str,
) -> dict[str, str]:
    original = target.read_bytes()
    patched, status = patcher(original)
    if status == "patched":
        target.write_bytes(patched)
    persisted = target.read_bytes()
    if _sha256(persisted) != expected_postimage:
        raise ContractError("FLA dispatch compatibility patch did not persist")
    return {
        "source": str(target),
        "source_sha256": expected_postimage,
        "status": status,
    }


def validate_install() -> dict[str, str]:
    """Require both compatibility postimages in the installed distribution."""
    distribution = _distribution()
    expected = {
        CHUNK_SOURCE.as_posix(): CHUNK_POSTIMAGE_SHA256,
        BACKEND_SOURCE.as_posix(): BACKEND_POSTIMAGE_SHA256,
    }
    observed = {
        relative: _sha256(Path(distribution.locate_file(relative)).read_bytes())
        for relative in expected
    }
    if observed != expected:
        raise ContractError(f"FLA compatibility install mismatch: {observed!r}")
    return observed


def apply_patch() -> dict[str, Any]:
    """Patch exact installed wheel sources, refusing package or source drift."""
    distribution = _distribution()
    sources = [
        _persist(
            Path(distribution.locate_file(CHUNK_SOURCE)),
            patch_source,
            CHUNK_POSTIMAGE_SHA256,
        ),
        _persist(
            Path(distribution.locate_file(BACKEND_SOURCE)),
            patch_backend_source,
            BACKEND_POSTIMAGE_SHA256,
        ),
    ]
    validate_install()
    return {"package": PACKAGE, "version": VERSION, "sources": sources}


def main() -> None:
    print(json.dumps(apply_patch(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
