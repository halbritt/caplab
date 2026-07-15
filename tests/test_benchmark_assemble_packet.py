import hashlib
import json
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BENCHMARK_CLI = ROOT / "doctrine" / "tools" / "benchmark_assemble_packet.py"

CANONICAL_ARGUMENTS = [
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
]


def content_address(packet):
    content = dict(packet)
    content.pop("packet_id", None)
    content.pop("packet_content_sha256", None)
    canonical = json.dumps(content, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return {
        **content,
        "packet_content_sha256": digest,
        "packet_id": f"pkt-{digest[:16]}",
    }


def packet_for(retriever_version, *, question="Should this packet introduce a new interface?"):
    return content_address(
        {
            "schema_version": "evidence-packet/2",
            "question": question,
            "retriever_version": retriever_version,
            "activated_concepts": ["universal-evidence-before-intervention"],
        }
    )


def write_fake_assembler(
    path,
    packet,
    *,
    label,
    log_path=None,
    exit_status=0,
    delay_seconds=0.0,
    raw_output=None,
):
    source = f"""#!/usr/bin/env python3
import json
import sys
import time

PACKET = {packet!r}
LOG_PATH = {str(log_path) if log_path is not None else None!r}
RAW_OUTPUT = {raw_output!r}

if LOG_PATH is not None:
    with open(LOG_PATH, "a", encoding="utf-8") as stream:
        stream.write(json.dumps({{"label": {label!r}, "arguments": sys.argv[1:]}}) + "\\n")
if {exit_status}:
    print("intentional failure", file=sys.stderr)
    raise SystemExit({exit_status})
time.sleep({delay_seconds})
if RAW_OUTPUT is None:
    print(json.dumps(PACKET, indent=2, sort_keys=True, ensure_ascii=False))
else:
    print(RAW_OUTPUT)
"""
    path.write_text(source, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


class AssemblePacketBenchmarkTests(unittest.TestCase):
    def run_benchmark(self, candidate, python_assembler, *arguments):
        return subprocess.run(
            [
                sys.executable,
                str(BENCHMARK_CLI),
                "--candidate",
                str(candidate),
                "--python-assembler",
                str(python_assembler),
                *arguments,
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_success_reports_first_calls_raw_samples_parity_and_thresholds(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            baseline = temp_path / "baseline.py"
            candidate = temp_path / "candidate"
            write_fake_assembler(
                baseline,
                packet_for("retriever-python-test"),
                label="baseline",
            )
            write_fake_assembler(
                candidate,
                packet_for("retriever-go-test"),
                label="candidate",
            )

            result = self.run_benchmark(
                candidate,
                baseline,
                "--warmups",
                "0",
                "--samples",
                "1",
                "--max-median-ms",
                "10000",
                "--max-p95-ms",
                "10000",
                "--min-speedup",
                "0.001",
            )

            self.assertEqual(0, result.returncode, result.stderr or result.stdout)
            report = json.loads(result.stdout)
            self.assertEqual("assemble-packet-benchmark/1", report["schema_version"])
            self.assertEqual("pass", report["status"])
            self.assertEqual(CANONICAL_ARGUMENTS, report["case"]["arguments"])
            self.assertEqual({"baseline", "candidate"}, set(report["first_calls"]))
            for first_call in report["first_calls"].values():
                self.assertEqual(
                    {
                        "elapsed_ms",
                        "packet_content_sha256",
                        "packet_id",
                        "retriever_version",
                    },
                    set(first_call),
                )
                self.assertRegex(first_call["packet_content_sha256"], r"^[0-9a-f]{64}$")
                self.assertRegex(first_call["packet_id"], r"^pkt-[0-9a-f]{16}$")
            self.assertEqual(1, len(report["measurements"]["baseline"]["raw_ms"]))
            self.assertEqual(1, len(report["measurements"]["candidate"]["raw_ms"]))
            self.assertTrue(report["parity"]["semantic_equal"])
            self.assertEqual([], report["errors"])
            self.assertTrue(all(report["checks"].values()))
            self.assertEqual(
                result.stdout,
                json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            )

    def test_measurements_alternate_and_index_is_candidate_only(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            baseline = temp_path / "baseline.py"
            candidate = temp_path / "candidate"
            index = temp_path / "doctrine-index.sqlite3"
            log_path = temp_path / "calls.jsonl"
            index.write_bytes(b"index fixture")
            write_fake_assembler(
                baseline,
                packet_for("retriever-python-test"),
                label="baseline",
                log_path=log_path,
            )
            write_fake_assembler(
                candidate,
                packet_for("retriever-go-test"),
                label="candidate",
                log_path=log_path,
            )

            result = self.run_benchmark(
                candidate,
                baseline,
                "--index",
                str(index),
                "--warmups",
                "1",
                "--samples",
                "3",
                "--max-median-ms",
                "10000",
                "--max-p95-ms",
                "10000",
                "--min-speedup",
                "0.001",
            )

            self.assertEqual(0, result.returncode, result.stderr or result.stdout)
            calls = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines()]
            measured = calls[4:]
            self.assertEqual(
                [
                    "baseline",
                    "candidate",
                    "candidate",
                    "baseline",
                    "baseline",
                    "candidate",
                ],
                [call["label"] for call in measured],
            )
            for call in calls:
                if call["label"] == "candidate":
                    self.assertEqual(
                        ["--index", str(index), *CANONICAL_ARGUMENTS],
                        call["arguments"],
                    )
                else:
                    self.assertEqual(CANONICAL_ARGUMENTS, call["arguments"])

    def test_semantic_mismatch_fails_but_preserves_first_call_diagnostics(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            baseline = temp_path / "baseline.py"
            candidate = temp_path / "candidate"
            write_fake_assembler(
                baseline,
                packet_for("retriever-python-test"),
                label="baseline",
            )
            write_fake_assembler(
                candidate,
                packet_for(
                    "retriever-go-test",
                    question="A semantically different question",
                ),
                label="candidate",
            )

            result = self.run_benchmark(
                candidate,
                baseline,
                "--warmups",
                "0",
                "--samples",
                "1",
                "--max-median-ms",
                "10000",
                "--max-p95-ms",
                "10000",
                "--min-speedup",
                "0.001",
            )

            self.assertEqual(1, result.returncode, result.stderr or result.stdout)
            report = json.loads(result.stdout)
            self.assertEqual("fail", report["status"])
            self.assertEqual({"baseline", "candidate"}, set(report["first_calls"]))
            self.assertFalse(report["parity"]["semantic_equal"])
            self.assertTrue(any("semantic packet mismatch" in error for error in report["errors"]))

    def test_candidate_must_carry_its_own_recomputable_content_identity(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            baseline = temp_path / "baseline.py"
            candidate = temp_path / "candidate"
            invalid_candidate = packet_for("retriever-go-test")
            invalid_candidate["packet_content_sha256"] = "0" * 64
            write_fake_assembler(
                baseline,
                packet_for("retriever-python-test"),
                label="baseline",
            )
            write_fake_assembler(
                candidate,
                invalid_candidate,
                label="candidate",
            )

            result = self.run_benchmark(
                candidate,
                baseline,
                "--warmups",
                "0",
                "--samples",
                "1",
                "--max-median-ms",
                "10000",
                "--max-p95-ms",
                "10000",
                "--min-speedup",
                "0.001",
            )

            self.assertEqual(1, result.returncode, result.stderr or result.stdout)
            report = json.loads(result.stdout)
            self.assertEqual("fail", report["status"])
            self.assertTrue(
                any(
                    "packet_content_sha256 does not match recomputed content hash" in error
                    for error in report["errors"]
                )
            )

    def test_nonzero_candidate_exit_fails_with_the_observed_status(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            baseline = temp_path / "baseline.py"
            candidate = temp_path / "candidate"
            write_fake_assembler(
                baseline,
                packet_for("retriever-python-test"),
                label="baseline",
            )
            write_fake_assembler(
                candidate,
                packet_for("retriever-go-test"),
                label="candidate",
                exit_status=7,
            )

            result = self.run_benchmark(
                candidate,
                baseline,
                "--warmups",
                "0",
                "--samples",
                "1",
                "--max-median-ms",
                "10000",
                "--max-p95-ms",
                "10000",
                "--min-speedup",
                "0.001",
            )

            self.assertEqual(1, result.returncode, result.stderr or result.stdout)
            report = json.loads(result.stdout)
            self.assertEqual("fail", report["status"])
            self.assertTrue(
                any(
                    "candidate first call: assembler exited with status 7" in error
                    for error in report["errors"]
                )
            )

    def test_invalid_json_candidate_output_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            baseline = temp_path / "baseline.py"
            candidate = temp_path / "candidate"
            write_fake_assembler(
                baseline,
                packet_for("retriever-python-test"),
                label="baseline",
            )
            write_fake_assembler(
                candidate,
                packet_for("retriever-go-test"),
                label="candidate",
                raw_output="not json",
            )

            result = self.run_benchmark(
                candidate,
                baseline,
                "--warmups",
                "0",
                "--samples",
                "1",
                "--max-median-ms",
                "10000",
                "--max-p95-ms",
                "10000",
                "--min-speedup",
                "0.001",
            )

            self.assertEqual(1, result.returncode, result.stderr or result.stdout)
            report = json.loads(result.stdout)
            self.assertTrue(
                any("assembler emitted invalid JSON" in error for error in report["errors"])
            )

    def test_each_performance_threshold_is_a_failing_gate(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            baseline = temp_path / "baseline.py"
            candidate = temp_path / "candidate"
            write_fake_assembler(
                baseline,
                packet_for("retriever-python-test"),
                label="baseline",
            )
            write_fake_assembler(
                candidate,
                packet_for("retriever-go-test"),
                label="candidate",
                delay_seconds=0.02,
            )

            result = self.run_benchmark(
                candidate,
                baseline,
                "--warmups",
                "0",
                "--samples",
                "3",
                "--max-median-ms",
                "1",
                "--max-p95-ms",
                "1",
                "--min-speedup",
                "1000",
            )

            self.assertEqual(1, result.returncode, result.stderr or result.stdout)
            report = json.loads(result.stdout)
            self.assertEqual("fail", report["status"])
            self.assertTrue(report["checks"]["parity"])
            self.assertFalse(report["checks"]["candidate_median"])
            self.assertFalse(report["checks"]["candidate_p95"])
            self.assertFalse(report["checks"]["median_speedup"])
            self.assertEqual(
                [
                    "candidate median exceeds max-median-ms threshold",
                    "candidate p95 exceeds max-p95-ms threshold",
                    "median speedup is below min-speedup threshold",
                ],
                report["errors"],
            )


if __name__ == "__main__":
    unittest.main()
