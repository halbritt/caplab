import json
import tempfile
import unittest
from pathlib import Path

from caplab.review_dissent.training_supervisor import (
    PULSE_SCHEMA,
    SupervisorConfig,
    SupervisorContractError,
    run_supervised,
)


class FakeProcess:
    def __init__(self, pid: int, returns: list[int | None]) -> None:
        self.pid = pid
        self._returns = iter(returns)
        self._last: int | None = None

    def poll(self) -> int | None:
        try:
            self._last = next(self._returns)
        except StopIteration:
            pass
        return self._last


class FakeRuntime:
    def __init__(self, returns: list[int | None], times: list[float]) -> None:
        self.process = FakeProcess(42, returns)
        self._times = iter(times)
        self.launched: tuple[str, ...] | None = None
        self.terminated = False
        self.closed = False

    def clock(self) -> float:
        return next(self._times)

    def sleep(self, _seconds: float) -> None:
        return None

    def launch_contained(self, command: tuple[str, ...]) -> FakeProcess:
        self.launched = command
        return self.process

    def terminate(self, _process: FakeProcess) -> None:
        self.terminated = True

    def close(self) -> None:
        self.closed = True


class TrainingSupervisorTests(unittest.TestCase):
    def _config(self, root: Path) -> SupervisorConfig:
        return SupervisorConfig(
            pulse_path=root / "pulse.json",
            identity_path=root / "identity.json",
            outcome_path=root / "outcome.json",
            lease_id="lease-1",
            host_boot_id="2026-07-21T03:19:59.5000000Z",
            ttl_seconds=45,
            poll_seconds=5,
            command=("powershell.exe", "-File", "train.ps1"),
        )

    def _pulse(self, path: Path, sequence: int, lease_id: str = "lease-1") -> None:
        path.write_text(
            json.dumps({
                "schema": PULSE_SCHEMA,
                "lease_id": lease_id,
                "sequence": sequence,
            }),
            encoding="utf-8",
        )

    def test_valid_pulse_and_clean_child_exit_leave_custody(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config = self._config(root)
            self._pulse(config.pulse_path, 1)
            runtime = FakeRuntime([None, 0], [0, 5])

            status = run_supervised(config, runtime)

            self.assertEqual(status, 0)
            self.assertEqual(runtime.launched, config.command)
            self.assertFalse(runtime.terminated)
            self.assertTrue(runtime.closed)
            identity = json.loads(config.identity_path.read_text(encoding="utf-8"))
            outcome = json.loads(config.outcome_path.read_text(encoding="utf-8"))
            self.assertEqual(identity["child_pid"], 42)
            self.assertEqual(identity["host_boot_id"], config.host_boot_id)
            self.assertEqual(outcome["status"], "completed")
            self.assertEqual(outcome["child_exit_code"], 0)

    def test_expired_pulse_terminates_contained_tree(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config = self._config(root)
            self._pulse(config.pulse_path, 1)
            runtime = FakeRuntime([None] * 11, [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50])

            status = run_supervised(config, runtime)

            self.assertEqual(status, 75)
            self.assertTrue(runtime.terminated)
            self.assertTrue(runtime.closed)
            outcome = json.loads(config.outcome_path.read_text(encoding="utf-8"))
            self.assertEqual(outcome["status"], "remote-pulse-expired-tree-terminated")

    def test_wrong_initial_lease_pulse_refuses_launch(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config = self._config(root)
            self._pulse(config.pulse_path, 1, lease_id="other-lease")
            runtime = FakeRuntime([], [])

            with self.assertRaisesRegex(SupervisorContractError, "pulse_lease_mismatch"):
                run_supervised(config, runtime)

            self.assertIsNone(runtime.launched)


if __name__ == "__main__":
    unittest.main()
