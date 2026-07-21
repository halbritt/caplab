"""Lease-bound local controller for the CAPLAB-16 r2 Windows training session."""

from __future__ import annotations

import argparse
import base64
import json
import os
import signal
import subprocess
import sys
import threading
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


QUALIFICATION_SCHEMA = "caplab.training.host-qualification/v1"
ACCEPTANCE_SCHEMA = "caplab.training.host-qualification-acceptance/v1"
EXPECTED_BOOT_ID = "2026-07-21T03:19:59.5000000Z"


class SessionContractError(RuntimeError):
    """The lease-bound training session departed from its frozen contract."""


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise SessionContractError(reason)


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _exclusive_bytes(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(content)
        stream.flush()
        os.fsync(stream.fileno())


def validate_fleet_sample(sample: dict[str, Any], *, lease_id: str) -> str:
    """Validate one externally observed exact-slot sample and return its heartbeat."""
    _require(sample.get("node") == "peecee", "fleet_node_mismatch")
    _require(sample.get("slot_id") == 1, "fleet_slot_mismatch")
    _require(sample.get("status") == "routable", "fleet_slot_not_routable")
    _require(sample.get("alive") is True, "fleet_slot_not_alive")
    _require(sample.get("fresh") is True, "fleet_heartbeat_stale")
    _require(sample.get("lease_id") == lease_id, "fleet_lease_mismatch")
    heartbeat = sample.get("heartbeat_ts")
    _require(isinstance(heartbeat, str) and heartbeat, "fleet_heartbeat_missing")
    return heartbeat


def validate_qualification(qualification: dict[str, Any]) -> None:
    """Require a representative no-update qualification result."""
    _require(qualification.get("schema") == QUALIFICATION_SCHEMA, "qualification_schema_mismatch")
    _require(
        qualification.get("experiment_id") == "caplab-review-dissent-qwen27b-qlora-r2",
        "qualification_experiment_mismatch",
    )
    try:
        duration = float(qualification["duration_seconds"])
    except (KeyError, TypeError, ValueError) as error:
        raise SessionContractError("qualification_duration_invalid") from error
    _require(duration >= 60, "qualification_duration_floor")
    _require(
        isinstance(qualification.get("iterations"), int)
        and qualification["iterations"] > 0,
        "qualification_iterations_missing",
    )
    _require(qualification.get("optimizer_steps") == 0, "qualification_optimizer_step")
    before = qualification.get("adapter_sha256_before")
    after = qualification.get("adapter_sha256_after")
    _require(
        isinstance(before, str) and len(before) == 64 and before == after,
        "qualification_updated_adapter",
    )


def qualification_acceptance(
    *,
    lease_id: str,
    host_boot_id: str,
    qualification_sha256: str,
    heartbeat_timestamps: list[str],
) -> dict[str, Any]:
    """Create the exact marker that permits the training-start transition."""
    distinct = list(dict.fromkeys(heartbeat_timestamps))
    _require(len(distinct) >= 4, "qualification_heartbeat_floor")
    _require(len(qualification_sha256) == 64, "qualification_sha256_invalid")
    return {
        "schema": ACCEPTANCE_SCHEMA,
        "experiment_id": "caplab-review-dissent-qwen27b-qlora-r2",
        "lease_id": lease_id,
        "host_boot_id": host_boot_id,
        "qualification_sha256": qualification_sha256,
        "distinct_fleet_heartbeats": len(distinct),
        "first_fleet_heartbeat": distinct[0],
        "last_fleet_heartbeat": distinct[-1],
        "accepted_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
    }


class LeaseSession:
    def __init__(self, remote_root: str, local_custody: Path, db: str) -> None:
        self.remote_root = remote_root.rstrip("/")
        self.local_custody = local_custody
        self.db = db
        self.lease_id = os.environ.get("GPU_FLEET_LEASE_ID", "")
        _require(os.environ.get("GPU_FLEET_NODE") == "peecee", "leased_node_mismatch")
        _require(os.environ.get("GPU_FLEET_SLOT_ID") == "1", "leased_slot_mismatch")
        _require(os.environ.get("GPU_FLEET_SERVED_MODEL") == "marker", "leased_model_mismatch")
        _require(bool(self.lease_id), "lease_id_missing")
        _require(not local_custody.exists(), "local_custody_exists")
        local_custody.mkdir(parents=True)
        self._pulse_stop = threading.Event()
        self._pulse_error: BaseException | None = None
        self._pulse_thread: threading.Thread | None = None

    @staticmethod
    def _encoded_powershell(source: str) -> str:
        return base64.b64encode(source.encode("utf-16le")).decode("ascii")

    def _powershell(self, source: str, *, timeout: float = 20) -> str:
        completed = subprocess.run(
            [
                "ssh",
                "-o",
                "BatchMode=yes",
                "peecee",
                "powershell.exe",
                "-NoProfile",
                "-NonInteractive",
                "-EncodedCommand",
                self._encoded_powershell(
                    "$ProgressPreference='SilentlyContinue';" + source
                ),
            ],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            text=True,
        )
        if completed.returncode != 0:
            raise SessionContractError(
                f"remote_powershell_failed:{completed.returncode}:{completed.stderr.strip()}"
            )
        return completed.stdout

    @staticmethod
    def _prefixed_line(output: str, prefix: str) -> str:
        for line in output.splitlines():
            clean = line.strip()
            if clean.startswith(prefix):
                return clean[len(prefix):]
        raise SessionContractError(f"remote_output_missing:{prefix}")

    @staticmethod
    def _ps_literal(value: str) -> str:
        return "'" + value.replace("'", "''") + "'"

    def _write_remote(self, path: str, content: bytes) -> None:
        encoded = base64.b64encode(content).decode("ascii")
        literal = self._ps_literal(path)
        temporary = self._ps_literal(path + ".next")
        self._powershell(
            f"$bytes=[Convert]::FromBase64String('{encoded}');"
            f"[IO.File]::WriteAllBytes({temporary},$bytes);"
            f"Move-Item -LiteralPath {temporary} -Destination {literal} -Force"
        )

    def _read_remote(self, path: str) -> bytes:
        output = self._powershell(
            f"$bytes=[IO.File]::ReadAllBytes({self._ps_literal(path)});"
            "Write-Output ('CAPLAB_BYTES='+[Convert]::ToBase64String($bytes))"
        )
        return base64.b64decode(self._prefixed_line(output, "CAPLAB_BYTES="))

    def _remote_sha256(self, path: str) -> str:
        output = self._powershell(
            f"$hash=(Get-FileHash -Algorithm SHA256 -LiteralPath {self._ps_literal(path)}).Hash.ToLowerInvariant();"
            "Write-Output ('CAPLAB_SHA256='+$hash)"
        )
        return self._prefixed_line(output, "CAPLAB_SHA256=")

    def _host_boot_id(self) -> str:
        output = self._powershell(
            "$os=Get-CimInstance Win32_OperatingSystem;"
            "$boot=$os.LastBootUpTime.ToUniversalTime().ToString('o');"
            "Write-Output ('CAPLAB_BOOT='+$boot)"
        )
        return self._prefixed_line(output, "CAPLAB_BOOT=")

    def _write_pulse(self, sequence: int) -> None:
        pulse = _canonical({
            "schema": "caplab.training.remote-pulse/v1",
            "lease_id": self.lease_id,
            "sequence": sequence,
        }) + b"\n"
        self._write_remote(f"{self.remote_root}/lease-pulse.json", pulse)

    def _pulse_loop(self) -> None:
        sequence = 1
        try:
            while not self._pulse_stop.is_set():
                self._write_pulse(sequence)
                sequence += 1
                self._pulse_stop.wait(5)
        except BaseException as error:
            self._pulse_error = error
            self._pulse_stop.set()

    def _start_pulses(self) -> None:
        self._pulse_thread = threading.Thread(
            target=self._pulse_loop,
            name="caplab-lease-pulse",
            daemon=True,
        )
        self._pulse_thread.start()
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            if self._pulse_error is not None:
                raise self._pulse_error
            try:
                self._read_remote(f"{self.remote_root}/lease-pulse.json")
                return
            except SessionContractError:
                time.sleep(0.25)
        raise SessionContractError("initial_remote_pulse_timeout")

    def _fleet_sample(self) -> dict[str, Any]:
        query = (
            "SELECT json_build_object("
            "'node',node,'slot_id',slot_id,'status',status,'alive',alive,"
            "'fresh',heartbeat_ts > now() - interval '45 seconds',"
            "'lease_id',lease_id::text,'heartbeat_ts',to_char(heartbeat_ts AT TIME ZONE 'UTC','YYYY-MM-DD\"T\"HH24:MI:SS.US\"Z\"')) "
            "FROM gpu_slots WHERE node='peecee' AND slot_id=1"
        )
        completed = subprocess.run(
            ["psql", "-d", self.db, "-At", "-c", query],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10,
        )
        if completed.returncode != 0:
            raise SessionContractError(
                f"fleet_sample_failed:{completed.returncode}:{completed.stderr.strip()}"
            )
        try:
            return json.loads(completed.stdout)
        except json.JSONDecodeError as error:
            raise SessionContractError("fleet_sample_invalid_json") from error

    def _run_phase(self, phase: str, boot_id: str) -> list[str]:
        identity = f"{self.remote_root}/{phase}-process-identity.json"
        outcome = f"{self.remote_root}/{phase}-process-outcome.json"
        shared_python = (
            "C:/Users/halbr/caplab/experiments/"
            "caplab-review-dissent-qwen27b-qlora-r1/.venv/Scripts/python.exe"
        )
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
            "powershell.exe",
            "-NoProfile",
            "-NonInteractive",
            "-File",
            f"{self.remote_root}/input/caplab16_peecee_r2.ps1",
            "-Root",
            self.remote_root,
            "-Phase",
            phase,
            "-LeaseId",
            self.lease_id,
            "-HostBootId",
            boot_id,
        ]
        process = subprocess.Popen(command)
        heartbeats: list[str] = []
        observation_path = self.local_custody / f"{phase}-fleet-observations.jsonl"
        with observation_path.open("xb") as observations:
            while process.poll() is None:
                if self._pulse_error is not None:
                    process.terminate()
                    raise SessionContractError(f"remote_pulse_failed:{self._pulse_error}")
                sample = self._fleet_sample()
                heartbeats.append(validate_fleet_sample(sample, lease_id=self.lease_id))
                observations.write(_canonical(sample) + b"\n")
                observations.flush()
                os.fsync(observations.fileno())
                time.sleep(5)
        if process.returncode != 0:
            raise SessionContractError(f"remote_phase_failed:{phase}:{process.returncode}")
        _require(self._host_boot_id() == boot_id, f"host_rebooted_during_{phase}")
        return heartbeats

    def _preserve_remote_file(self, remote_path: str, local_name: str) -> bool:
        try:
            content = self._read_remote(remote_path)
        except Exception:
            return False
        target = self.local_custody / local_name
        if not target.exists():
            _exclusive_bytes(target, content)
        return True

    def _preserve_custody(self, *, require_complete: bool = False) -> None:
        missing: list[str] = []
        for name in (
            "qualification-process-identity.json",
            "qualification-process-outcome.json",
            "training-process-identity.json",
            "training-process-outcome.json",
            "qualification-accepted.json",
        ):
            if not self._preserve_remote_file(f"{self.remote_root}/{name}", name):
                missing.append(name)
        for directory in ("qualification-output", "training-output"):
            target = self.local_custody / directory
            if target.exists():
                continue
            completed = subprocess.run(
                ["scp", "-q", "-r", f"peecee:{self.remote_root}/{directory}", str(target)],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=120,
            )
            if completed.returncode != 0 or not target.is_dir():
                missing.append(directory)
        if require_complete and missing:
            raise SessionContractError(f"training_custody_incomplete:{','.join(missing)}")

    def run(self) -> None:
        boot_id = self._host_boot_id()
        _require(boot_id == EXPECTED_BOOT_ID, "authorized_host_boot_identity_changed")
        self._start_pulses()
        try:
            qualification_heartbeats = self._run_phase("Qualification", boot_id)
            qualification_path = f"{self.remote_root}/qualification-output/qualification.json"
            qualification_bytes = self._read_remote(qualification_path)
            qualification = json.loads(qualification_bytes)
            validate_qualification(qualification)
            qualification_hash = self._remote_sha256(qualification_path)
            acceptance = qualification_acceptance(
                lease_id=self.lease_id,
                host_boot_id=boot_id,
                qualification_sha256=qualification_hash,
                heartbeat_timestamps=qualification_heartbeats,
            )
            acceptance_bytes = _canonical(acceptance) + b"\n"
            _exclusive_bytes(self.local_custody / "qualification-accepted.json", acceptance_bytes)
            self._write_remote(f"{self.remote_root}/qualification-accepted.json", acceptance_bytes)
            self._run_phase("Training", boot_id)
            self._preserve_custody(require_complete=True)
        finally:
            self._pulse_stop.set()
            if self._pulse_thread is not None:
                self._pulse_thread.join(timeout=10)
            self._preserve_custody()
            cleanup = {
                "schema": "caplab.training.session-cleanup/v1",
                "lease_id": self.lease_id,
                "host_boot_id_before": boot_id,
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--remote-root", required=True)
    parser.add_argument("--local-custody", type=Path, required=True)
    parser.add_argument("--db", default="gpu_fleet")
    args = parser.parse_args(argv)
    interrupted: list[int] = []

    def on_signal(signum: int, _frame: object) -> None:
        interrupted.append(signum)
        raise SessionContractError(f"session_signal:{signum}")

    old_term = signal.signal(signal.SIGTERM, on_signal)
    old_int = signal.signal(signal.SIGINT, on_signal)
    try:
        LeaseSession(args.remote_root, args.local_custody, args.db).run()
        return 0
    except Exception as error:
        print(f"caplab-training-session: {type(error).__name__}: {error}", file=sys.stderr)
        return 128 + interrupted[0] if interrupted else 1
    finally:
        signal.signal(signal.SIGTERM, old_term)
        signal.signal(signal.SIGINT, old_int)


if __name__ == "__main__":
    raise SystemExit(main())
