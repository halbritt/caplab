"""CAPLAB's deterministic revbench experiment adapter."""

from caplab.revbench._core import (
    ArtifactRegistrar,
    ContentRef,
    RevbenchContractError,
    prepare,
    score,
)

__all__ = [
    "ArtifactRegistrar",
    "ContentRef",
    "RevbenchContractError",
    "prepare",
    "score",
]
