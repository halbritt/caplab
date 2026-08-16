"""CAPLAB's deterministic revbench experiment adapter."""

from caplab.revbench._core import (
    ArtifactRegistrar,
    ContentRef,
    RevbenchContractError,
    prepare,
    score,
)
from caplab.revbench.execution import execute

__all__ = [
    "ArtifactRegistrar",
    "ContentRef",
    "RevbenchContractError",
    "execute",
    "prepare",
    "score",
]
