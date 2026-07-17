from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "doctrine" / "tools"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class EvaluationDefectLedgerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.ledger = load_module(
            "evaluation_defect_ledger_test",
            TOOLS / "evaluation_defect_ledger.py",
        )

    def test_observation_is_idempotent_and_later_events_do_not_rewrite_it(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            ledger_path = Path(temporary_directory) / "gate-defects.jsonl"
            observation = self.ledger.record_observation(
                ledger_path,
                candidate={"mode": "replay", "result": "failed"},
                baseline={"mode": "replay", "result": "passed"},
                config={"floor": 1.0},
                violations=["canaries: contract_pass_rate below floor"],
                recorded_at="2026-07-17T00:00:00Z",
            )
            with self.assertRaises(jsonschema.ValidationError):
                self.ledger.record_disposition(
                    ledger_path,
                    defect_id=observation["defect_id"],
                    status="remediated",
                    rationale="Fixed.",
                    decided_by="owner",
                    authority="",
                    recorded_at="2026-07-17T00:30:00Z",
                )
            self.assertEqual(1, len(self.ledger.load_ledger(ledger_path)))
            first_line = ledger_path.read_text(encoding="utf-8").splitlines()[0]
            duplicate = self.ledger.record_observation(
                ledger_path,
                candidate={"mode": "replay", "result": "failed"},
                baseline={"mode": "replay", "result": "passed"},
                config={"floor": 1.0},
                violations=["canaries: contract_pass_rate below floor"],
                recorded_at="2026-07-17T01:00:00Z",
            )
            self.assertEqual(observation["event_id"], duplicate["event_id"])

            diagnosis = self.ledger.record_diagnosis(
                ledger_path,
                defect_id=observation["defect_id"],
                summary="The canary fixture no longer satisfies its contract.",
                evidence=["tests/test_doctrine_scaffolding.py"],
                rivals_considered=["The baseline may be stale."],
                diagnosed_by="agent-books-backlog-drain",
                recorded_at="2026-07-17T02:00:00Z",
            )
            disposition = self.ledger.record_disposition(
                ledger_path,
                defect_id=observation["defect_id"],
                status="remediated",
                rationale="The fixture contract was repaired and the gate reran cleanly.",
                decided_by="owner",
                authority="repository owner",
                recorded_at="2026-07-17T03:00:00Z",
            )

            events = self.ledger.load_ledger(ledger_path)

        self.assertEqual(first_line, json.dumps(events[0], sort_keys=True))
        self.assertEqual(observation["observation_sha256"], diagnosis["observation_sha256"])
        self.assertEqual(
            observation["observation_sha256"],
            disposition["observation_sha256"],
        )
        self.assertEqual(["observation", "diagnosis", "disposition"], [
            event["event_type"] for event in events
        ])

    def test_disposition_requires_recorded_decision_authority(self) -> None:
        schema = json.loads(
            (ROOT / "doctrine/evaluations/gate-defect-event.schema.json").read_text()
        )
        disposition = {
            "schema_version": "evaluation-gate-defect-event/1",
            "event_type": "disposition",
            "event_id": "disp-0123456789abcdef",
            "defect_id": "gate-0123456789abcdef",
            "observation_event_id": "obs-0123456789abcdef",
            "observation_sha256": "0" * 64,
            "recorded_at": "2026-07-17T00:00:00Z",
            "assertion_type": "decision",
            "status": "remediated",
            "rationale": "Fixed.",
            "decided_by": "owner"
        }

        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.Draft202012Validator(schema).validate(disposition)


if __name__ == "__main__":
    unittest.main()
