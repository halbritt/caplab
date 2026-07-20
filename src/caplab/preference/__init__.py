"""Fail-closed, model-free preference-study instrumentation."""

from .instrument import (
    PreferenceContractError,
    assess_study_state,
    build_blinded_packet,
    load_instrument,
    render_task,
    run_canned_attempt,
)

__all__ = [
    "PreferenceContractError",
    "assess_study_state",
    "build_blinded_packet",
    "load_instrument",
    "render_task",
    "run_canned_attempt",
]
