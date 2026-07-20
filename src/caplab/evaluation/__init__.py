"""CAPLAB-native, model-free evaluation replay."""

from .defects import (
    DefectLedgerError,
    load_defect_ledger,
    record_defect_disposition,
    record_defect_inference,
    record_gate_observation,
)
from .replay import EvaluationContractError, EvaluationReplay, replay_synthetic_fixture
from .snapshot import (
    EvaluationGateResult,
    EvaluationScenario,
    SnapshotContractError,
    build_evaluation_snapshot,
    compare_evaluation_snapshots,
)

__all__ = [
    "EvaluationContractError",
    "DefectLedgerError",
    "EvaluationReplay",
    "EvaluationGateResult",
    "EvaluationScenario",
    "SnapshotContractError",
    "build_evaluation_snapshot",
    "compare_evaluation_snapshots",
    "load_defect_ledger",
    "record_defect_disposition",
    "record_defect_inference",
    "record_gate_observation",
    "replay_synthetic_fixture",
]
