#!/usr/bin/env python3
"""Benchmark a packet assembler against the Python compatibility oracle."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PYTHON_ASSEMBLER = ROOT / "doctrine" / "tools" / "assemble_packet.py"
SCHEMA_VERSION = "assemble-packet-benchmark/1"
NORMALIZED_FIELDS = (
    "retriever_version",
    "packet_content_sha256",
    "packet_id",
)
CANONICAL_ARGUMENTS = (
    "--role",
    "coding-agent",
    "--task",
    "implementation",
    "--question",
    "Should this packet introduce a new interface?",
    "--signal",
    "public API",
    "--language",
    "Go",
    "--risk",
    "correctness",
    "--render",
    "json",
)


class BenchmarkFailure(RuntimeError):
    """A benchmark invocation could not produce trustworthy evidence."""


def positive_int(text: str) -> int:
    parsed = int(text)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return parsed


def nonnegative_int(text: str) -> int:
    parsed = int(text)
    if parsed < 0:
        raise argparse.ArgumentTypeError("must be zero or greater")
    return parsed


def positive_float(text: str) -> float:
    parsed = float(text)
    if not math.isfinite(parsed) or parsed <= 0:
        raise argparse.ArgumentTypeError("must be finite and greater than zero")
    return parsed


def canonical_content_hash(packet: dict[str, Any]) -> str:
    content = dict(packet)
    content.pop("packet_id", None)
    content.pop("packet_content_sha256", None)
    canonical = json.dumps(
        content,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def validate_packet_identity(packet: object, label: str) -> dict[str, Any]:
    if not isinstance(packet, dict):
        raise BenchmarkFailure(f"{label}: assembler output must be a JSON object")
    for field in NORMALIZED_FIELDS:
        if not isinstance(packet.get(field), str) or not packet[field]:
            raise BenchmarkFailure(f"{label}: packet is missing string field '{field}'")
    digest = canonical_content_hash(packet)
    if packet["packet_content_sha256"] != digest:
        raise BenchmarkFailure(
            f"{label}: packet_content_sha256 does not match recomputed content hash"
        )
    expected_packet_id = f"pkt-{digest[:16]}"
    if packet["packet_id"] != expected_packet_id:
        raise BenchmarkFailure(f"{label}: packet_id does not match recomputed content hash")
    return packet


def normalized_packet(packet: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in packet.items() if key not in NORMALIZED_FIELDS}


def execute_assembler(
    command: list[str], label: str, environment: dict[str, str]
) -> tuple[float, dict[str, Any]]:
    started = time.perf_counter_ns()
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            env=environment,
            text=True,
            capture_output=True,
            check=False,
        )
    except OSError as error:
        raise BenchmarkFailure(f"{label}: unable to execute assembler: {error}") from error
    elapsed_ms = (time.perf_counter_ns() - started) / 1_000_000
    if completed.returncode != 0:
        error_output = completed.stderr.strip() or completed.stdout.strip()
        suffix = f": {error_output}" if error_output else ""
        raise BenchmarkFailure(
            f"{label}: assembler exited with status {completed.returncode}{suffix}"
        )
    try:
        decoded = json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        raise BenchmarkFailure(f"{label}: assembler emitted invalid JSON: {error}") from error
    return elapsed_ms, validate_packet_identity(decoded, label)


def nearest_rank_p95(values: list[float]) -> float:
    ordered = sorted(values)
    return ordered[math.ceil(0.95 * len(ordered)) - 1]


def round_report_number(number: float) -> float:
    return round(number, 6)


def latency_summary(samples: list[float]) -> dict[str, Any]:
    return {
        "median_ms": round_report_number(statistics.median(samples)),
        "p95_ms": round_report_number(nearest_rank_p95(samples)),
        "raw_ms": [round_report_number(sample) for sample in samples],
    }


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Gate a packet assembler against Python parity and latency targets."
    )
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument(
        "--index",
        type=Path,
        default=None,
        help="optional SQLite index passed only to the candidate",
    )
    parser.add_argument(
        "--python-assembler",
        type=Path,
        default=DEFAULT_PYTHON_ASSEMBLER,
        help="Python compatibility oracle",
    )
    parser.add_argument("--warmups", type=nonnegative_int, default=5)
    parser.add_argument("--samples", type=positive_int, default=25)
    parser.add_argument("--max-median-ms", type=positive_float, default=50.0)
    parser.add_argument("--max-p95-ms", type=positive_float, default=75.0)
    parser.add_argument("--min-speedup", type=positive_float, default=8.0)
    return parser.parse_args()


def report_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(ROOT).as_posix()
    except ValueError:
        return str(resolved)


def initial_report(args: argparse.Namespace) -> dict[str, Any]:
    candidate = args.candidate.resolve()
    python_assembler = args.python_assembler.resolve()
    index = args.index.resolve() if args.index is not None else None
    return {
        "case": {
            "arguments": list(CANONICAL_ARGUMENTS),
            "name": "canonical-implementation",
        },
        "checks": {
            "candidate_median": False,
            "candidate_p95": False,
            "median_speedup": False,
            "parity": False,
        },
        "configuration": {
            "candidate": report_path(candidate),
            "index": report_path(index) if index is not None else None,
            "measurement_order": "alternating baseline/candidate pairs",
            "python_assembler": report_path(python_assembler),
            "samples": args.samples,
            "thresholds": {
                "max_median_ms": args.max_median_ms,
                "max_p95_ms": args.max_p95_ms,
                "min_speedup": args.min_speedup,
            },
            "warmups": args.warmups,
        },
        "errors": [],
        "first_calls": {},
        "measurements": {
            "baseline": {"median_ms": None, "p95_ms": None, "raw_ms": []},
            "candidate": {"median_ms": None, "p95_ms": None, "raw_ms": []},
            "median_speedup": None,
        },
        "parity": {
            "normalized_fields": list(NORMALIZED_FIELDS),
            "semantic_equal": False,
        },
        "schema_version": SCHEMA_VERSION,
        "status": "fail",
    }


def assembler_commands(args: argparse.Namespace) -> dict[str, list[str]]:
    candidate = args.candidate.resolve()
    python_assembler = args.python_assembler.resolve()
    index = args.index.resolve() if args.index is not None else None
    baseline_command = [
        sys.executable,
        str(python_assembler),
        *CANONICAL_ARGUMENTS,
    ]
    candidate_command = [str(candidate)]
    if index is not None:
        candidate_command.extend(("--index", str(index)))
    candidate_command.extend(CANONICAL_ARGUMENTS)
    return {"baseline": baseline_command, "candidate": candidate_command}


def alternating_order(iteration: int) -> tuple[str, str]:
    if iteration % 2 == 0:
        return "baseline", "candidate"
    return "candidate", "baseline"


class PacketBenchmarkSession:
    def __init__(self, args: argparse.Namespace, report: dict[str, Any]) -> None:
        self.args = args
        self.report = report
        self.commands = assembler_commands(args)
        self.environment = os.environ.copy()
        self.environment["PYTHONDONTWRITEBYTECODE"] = "1"
        self.baseline_semantics: dict[str, Any] | None = None

    def observe(self, implementation: str, phase: str) -> float:
        elapsed, packet = execute_assembler(
            self.commands[implementation],
            f"{implementation} {phase}",
            self.environment,
        )
        if phase == "first call":
            self.record_first_call(implementation, elapsed, packet)
        semantic_packet = normalized_packet(packet)
        if self.baseline_semantics is None:
            self.baseline_semantics = semantic_packet
        elif semantic_packet != self.baseline_semantics:
            raise BenchmarkFailure(
                f"{implementation} {phase}: semantic packet mismatch against Python baseline"
            )
        return elapsed

    def record_first_call(
        self, implementation: str, elapsed: float, packet: dict[str, Any]
    ) -> None:
        self.report["first_calls"][implementation] = {
            "elapsed_ms": round_report_number(elapsed),
            "packet_content_sha256": packet["packet_content_sha256"],
            "packet_id": packet["packet_id"],
            "retriever_version": packet["retriever_version"],
        }

    def run_first_calls(self) -> None:
        self.observe("baseline", "first call")
        self.observe("candidate", "first call")
        self.report["parity"]["semantic_equal"] = True
        self.report["checks"]["parity"] = True

    def run_warmups(self) -> None:
        for warmup in range(self.args.warmups):
            for implementation in alternating_order(warmup):
                self.observe(implementation, f"warmup {warmup + 1}")

    def measured_samples(self) -> dict[str, list[float]]:
        samples: dict[str, list[float]] = {"baseline": [], "candidate": []}
        for sample in range(self.args.samples):
            for implementation in alternating_order(sample):
                samples[implementation].append(self.observe(implementation, f"sample {sample + 1}"))
        return samples


def threshold_failures(checks: dict[str, bool]) -> list[str]:
    messages = (
        ("candidate_median", "candidate median exceeds max-median-ms threshold"),
        ("candidate_p95", "candidate p95 exceeds max-p95-ms threshold"),
        ("median_speedup", "median speedup is below min-speedup threshold"),
    )
    return [message for check, message in messages if not checks[check]]


def record_measurements(
    report: dict[str, Any], args: argparse.Namespace, samples: dict[str, list[float]]
) -> None:
    baseline_median = statistics.median(samples["baseline"])
    candidate_median = statistics.median(samples["candidate"])
    candidate_p95 = nearest_rank_p95(samples["candidate"])
    speedup = baseline_median / candidate_median
    report["measurements"] = {
        "baseline": latency_summary(samples["baseline"]),
        "candidate": latency_summary(samples["candidate"]),
        "median_speedup": round_report_number(speedup),
    }
    checks = report["checks"]
    checks["candidate_median"] = candidate_median <= args.max_median_ms
    checks["candidate_p95"] = candidate_p95 <= args.max_p95_ms
    checks["median_speedup"] = speedup >= args.min_speedup
    report["errors"].extend(threshold_failures(checks))


def run_benchmark(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    report = initial_report(args)
    session = PacketBenchmarkSession(args, report)

    try:
        session.run_first_calls()
        session.run_warmups()
        record_measurements(report, args, session.measured_samples())
    except BenchmarkFailure as error:
        report["errors"].append(str(error))

    if not report["errors"] and all(report["checks"].values()):
        report["status"] = "pass"
        return report, 0
    return report, 1


def main() -> int:
    report, status = run_benchmark(parse_arguments())
    sys.stdout.write(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
    return status


if __name__ == "__main__":
    raise SystemExit(main())
