import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCTRINE = ROOT / "doctrine"
BUILD = DOCTRINE / "tools" / "build_packet_assembler.py"
INDEX_BUILD = DOCTRINE / "tools" / "build_doctrine_index.py"


class PacketAssemblerBuildTests(unittest.TestCase):
    def run_build(self, *arguments):
        environment = os.environ.copy()
        environment.update(
            {
                "GOTOOLCHAIN": "local",
                "PYTHONDONTWRITEBYTECODE": "1",
            }
        )
        return subprocess.run(
            [sys.executable, str(BUILD), *arguments],
            cwd=ROOT,
            env=environment,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_version_is_content_derived_and_schema_compatible(self):
        first = self.run_build("--print-version")
        second = self.run_build("--print-version")

        self.assertEqual(0, first.returncode, first.stderr)
        self.assertEqual(first.stdout, second.stdout)
        self.assertRegex(first.stdout.strip(), r"^retriever-[0-9a-f]{16}$")

    def test_fresh_builds_are_byte_identical_and_current_output_is_not_replaced(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            first_path = temp_path / "assemble-packet-a"
            second_path = temp_path / "assemble-packet-b"

            first = self.run_build("--out", str(first_path))
            second = self.run_build("--out", str(second_path))
            self.assertEqual(0, first.returncode, first.stderr)
            self.assertEqual(0, second.returncode, second.stderr)
            self.assertEqual(first_path.read_bytes(), second_path.read_bytes())
            self.assertTrue(os.access(first_path, os.X_OK))

            before = first_path.stat().st_mtime_ns
            time.sleep(0.01)
            unchanged = self.run_build("--out", str(first_path))
            self.assertEqual(0, unchanged.returncode, unchanged.stderr)
            self.assertIn("current", unchanged.stdout)
            self.assertEqual(before, first_path.stat().st_mtime_ns)

    def test_built_binary_emits_the_content_derived_retriever_identity(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            binary = temp_path / "assemble-packet"
            index = temp_path / "doctrine-index.sqlite3"
            build = self.run_build("--out", str(binary))
            self.assertEqual(0, build.returncode, build.stderr)
            index_build = subprocess.run(
                [
                    sys.executable,
                    str(INDEX_BUILD),
                    "--out",
                    str(index),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, index_build.returncode, index_build.stderr)

            packet = subprocess.run(
                [
                    str(binary),
                    "--index",
                    str(index),
                    "--role",
                    "coding-agent",
                    "--task",
                    "implementation",
                    "--question",
                    "Should this packet introduce a new interface?",
                    "--render",
                    "json",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, packet.returncode, packet.stderr)
            decoded = json.loads(packet.stdout)
            expected_version = self.run_build("--print-version").stdout.strip()
            self.assertEqual(expected_version, decoded["retriever_version"])

            unhashed = dict(decoded)
            unhashed.pop("packet_id")
            unhashed.pop("packet_content_sha256")
            digest = hashlib.sha256(
                json.dumps(
                    unhashed,
                    ensure_ascii=False,
                    separators=(",", ":"),
                    sort_keys=True,
                ).encode("utf-8")
            ).hexdigest()
            self.assertEqual(digest, decoded["packet_content_sha256"])


if __name__ == "__main__":
    unittest.main()
