"""Second-lease controller for the CAPLAB-16 r2 native evaluation."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

from .training_evaluation import validate_adapter_seal
from .training_session import (
    EXPECTED_BOOT_ID,
    LeaseSession,
    SessionContractError,
    _canonical,
    _exclusive_bytes,
    _require,
    validate_fleet_sample,
)


class EvaluationSession(LeaseSession):
    """Hold one exact fleet lease while serving and evaluating the sealed adapter."""

    def _start_server(self, boot_id: str) -> subprocess.Popen[bytes]:
        shared_python = (
            "C:/Users/halbr/caplab/experiments/"
            "caplab-review-dissent-qwen27b-qlora-r1/.venv/Scripts/python.exe"
        )
        identity = f"{self.remote_root}/evaluation-server-process-identity.json"
        outcome = f"{self.remote_root}/evaluation-server-process-outcome.json"
        command = [
            "ssh",
            "-o",
            "BatchMode=yes",
            "peecee",
            shared_python,
            f"{self.remote_root}/input/training_supervisor.py",
            "--pulse",
            f"{self.remote_root}/lease-pulse.json",
            "--identity",
            identity,
            "--outcome",
            outcome,
            "--lease-id",
            self.lease_id,
            "--host-boot-id",
            boot_id,
            "--ttl-seconds",
            "45",
            "--poll-seconds",
            "2",
            "--",
            shared_python,
            f"{self.remote_root}/input/caplab_qwen27b_eval_server.py",
            "--experiment",
            f"{self.remote_root}/input/training-experiment.json",
            "--model-dir",
            "C:/Users/halbr/caplab/models/Qwen3.6-27B-6a9e13bd6fc8f0983b9b99948120bc37f49c13e9",
            "--adapter-dir",
            f"{self.remote_root}/training-output/final-adapter",
            "--bind",
            "0.0.0.0",
            "--port",
            "18081",
            "--ready-file",
            f"{self.remote_root}/evaluation-server-ready.json",
        ]
        return subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def _sample_until_ready(self, process: subprocess.Popen[bytes]) -> dict[str, object]:
        observations = self.local_custody / "evaluation-fleet-observations.jsonl"
        deadline = time.monotonic() + 900
        with observations.open("xb") as stream:
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    stderr = process.stderr.read().decode("utf-8", errors="replace") if process.stderr else ""
                    raise SessionContractError(
                        f"evaluation_server_start_failed:{process.returncode}:{stderr.strip()}"
                    )
                sample = self._fleet_sample()
                validate_fleet_sample(sample, lease_id=self.lease_id)
                stream.write(_canonical(sample) + b"\n")
                stream.flush()
                os.fsync(stream.fileno())
                try:
                    ready = json.loads(
                        self._read_remote(f"{self.remote_root}/evaluation-server-ready.json")
                    )
                    return ready
                except (SessionContractError, json.JSONDecodeError):
                    time.sleep(5)
        raise SessionContractError("evaluation_server_ready_timeout")

    def _run_evaluator(self, server: subprocess.Popen[bytes]) -> None:
        output = self.local_custody / "evaluation"
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "caplab.review_dissent.training_evaluation",
                "--endpoint",
                "http://100.113.63.58:18081/v1",
                "--training-root",
                str(self.local_custody.parent / "training-output"),
                "--study-root",
                "docs/product/studies/review-dissent-001",
                "--controls",
                "docs/product/training/caplab-review-dissent-local-qwen-r1/general-coding-controls.json",
                "--output",
                str(output),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        observations = self.local_custody / "evaluation-runtime-observations.jsonl"
        with observations.open("xb") as stream:
            while process.poll() is None:
                if server.poll() is not None:
                    process.terminate()
                    raise SessionContractError("evaluation_server_exited_during_calls")
                if self._pulse_error is not None:
                    process.terminate()
                    raise SessionContractError(f"remote_pulse_failed:{self._pulse_error}")
                sample = self._fleet_sample()
                validate_fleet_sample(sample, lease_id=self.lease_id)
                stream.write(_canonical(sample) + b"\n")
                stream.flush()
                os.fsync(stream.fileno())
                time.sleep(5)
        stdout, stderr = process.communicate()
        _exclusive_bytes(self.local_custody / "evaluation.stdout", stdout)
        _exclusive_bytes(self.local_custody / "evaluation.stderr", stderr)
        if process.returncode != 0:
            raise SessionContractError(f"native_evaluation_failed:{process.returncode}")

    def _stop_server(self, process: subprocess.Popen[bytes]) -> None:
        identity_bytes = self._read_remote(
            f"{self.remote_root}/evaluation-server-process-identity.json"
        )
        identity = json.loads(identity_bytes)
        _require(identity.get("lease_id") == self.lease_id, "evaluation_server_lease_mismatch")
        child_pid = identity.get("child_pid")
        _require(isinstance(child_pid, int), "evaluation_server_pid_missing")
        self._powershell(f"Stop-Process -Id {child_pid} -Force")
        try:
            process.wait(timeout=30)
        except subprocess.TimeoutExpired as error:
            process.terminate()
            raise SessionContractError("evaluation_server_stop_timeout") from error
        marker = {
            "schema": "caplab.training.eval-server-stop/v1",
            "lease_id": self.lease_id,
            "child_pid": child_pid,
            "supervisor_return_code": process.returncode,
            "stop_reason": "authorized-evaluation-complete",
        }
        _exclusive_bytes(
            self.local_custody / "evaluation-server-stop.json",
            _canonical(marker) + b"\n",
        )

    def run_evaluation(self) -> None:
        boot_id = self._host_boot_id()
        _require(boot_id == EXPECTED_BOOT_ID, "authorized_host_boot_identity_changed")
        adapter_sha256 = validate_adapter_seal(self.local_custody.parent / "training-output")
        self._start_pulses()
        server: subprocess.Popen[bytes] | None = None
        try:
            server = self._start_server(boot_id)
            ready = self._sample_until_ready(server)
            _require(
                ready == {
                    "schema": "caplab.training.eval-server-ready/v1",
                    "bind": "0.0.0.0",
                    "port": 18081,
                    "models": [
                        "caplab-qwen3.6-27b-base",
                        "caplab-qwen3.6-27b-tuned",
                    ],
                    "adapter_sha256": adapter_sha256,
                },
                "evaluation_server_ready_contract_mismatch",
            )
            self._run_evaluator(server)
            self._stop_server(server)
            _require(self._host_boot_id() == boot_id, "host_rebooted_during_evaluation")
        finally:
            self._pulse_stop.set()
            if self._pulse_thread is not None:
                self._pulse_thread.join(timeout=10)
            for name in (
                "evaluation-server-ready.json",
                "evaluation-server-process-identity.json",
                "evaluation-server-process-outcome.json",
            ):
                self._preserve_remote_file(f"{self.remote_root}/{name}", name)
            if server is not None and server.poll() is None:
                server.terminate()
            cleanup = {
                "schema": "caplab.training.evaluation-cleanup/v1",
                "lease_id": self.lease_id,
                "host_boot_id_after": None,
                "ollama_available": False,
                "gpu_reachable": False,
            }
            try:
                cleanup["host_boot_id_after"] = self._host_boot_id()
                cleanup["ollama_available"] = subprocess.run(
                    ["ssh", "-o", "BatchMode=yes", "peecee", "ollama", "list"],
                    check=False,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=20,
                ).returncode == 0
                cleanup["gpu_reachable"] = subprocess.run(
                    ["ssh", "-o", "BatchMode=yes", "peecee", "nvidia-smi"],
                    check=False,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=20,
                ).returncode == 0
            finally:
                _exclusive_bytes(
                    self.local_custody / "cleanup.json",
                    _canonical(cleanup) + b"\n",
                )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--remote-root", required=True)
    parser.add_argument("--local-custody", required=True, type=Path)
    parser.add_argument("--db", default="gpu_fleet")
    args = parser.parse_args()
    try:
        EvaluationSession(args.remote_root, args.local_custody, args.db).run_evaluation()
        return 0
    except Exception as error:
        print(f"caplab-evaluation-session: {type(error).__name__}: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
