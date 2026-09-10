"""Real tracer output is withheld until raw and decoded strings pass quarantine."""

import fcntl
import hashlib
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

from caplab.exec_trace_buffer import buffered_exec_trace
from caplab.capture_quarantine import CaptureQuarantineError
from caplab.revbench.codex import ExactSecretStreamQuarantine


class ExecTraceBufferTests(unittest.TestCase):
    @unittest.skipUnless(
        Path("/usr/bin/strace").is_file() and Path("/usr/bin/prlimit").is_file(),
        "strace and prlimit required",
    )
    def test_real_trace_is_sealed_and_preserved_only_after_quarantine(self):
        before = set(os.listdir("/proc/self/fd"))
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "exec.trace"
            with buffered_exec_trace(
                max_bytes=1048576,
                quarantine_factory=lambda: ExactSecretStreamQuarantine(
                    (b"private-control",)
                ),
            ) as buffer:
                command = [
                    "/usr/bin/prlimit",
                    "--fsize=1048576:1048576",
                    "--core=0",
                    "--",
                    "/usr/bin/strace",
                    "-f",
                    "-v",
                    "-xx",
                    "-s",
                    "65536",
                    "-e",
                    "trace=execve,execveat",
                    "-o",
                    str(buffer.path),
                    "--",
                    "/usr/bin/true",
                    "CAPLAB café trace",
                ]
                result = subprocess.run(
                    command,
                    env={"PATH": "/usr/bin:/bin"},
                    capture_output=True,
                    timeout=5,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertFalse(target.exists())
                raw = os.pread(buffer.descriptor, 1048576, 0)
                self.assertNotIn("café".encode(), raw)
                receipt = buffer.retain(target)
                self.assertEqual(target.read_bytes(), raw)
                self.assertEqual(
                    receipt["trace_sha256"], hashlib.sha256(raw).hexdigest()
                )
                self.assertGreater(receipt["decoded_strings"], 0)
                self.assertTrue(receipt["quarantine_applied"])
                self.assertNotEqual(
                    receipt["source_identity"], receipt["retained_identity"]
                )
                self.assertEqual(
                    fcntl.fcntl(buffer.descriptor, fcntl.F_GET_SEALS),
                    receipt["source_seals"],
                )
                with self.assertRaises(OSError):
                    os.pwrite(buffer.descriptor, b"changed", 0)
                descriptor = buffer.descriptor
            with self.assertRaises(OSError):
                os.fstat(descriptor)
        self.assertEqual(before, set(os.listdir("/proc/self/fd")))

    @unittest.skipUnless(
        Path("/usr/bin/strace").is_file() and Path("/usr/bin/prlimit").is_file(),
        "strace and prlimit required",
    )
    def test_encoded_credential_in_real_exec_is_refused_before_any_output_file(self):
        secret = "synthetic-private-café-token".encode()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with buffered_exec_trace(
                max_bytes=1048576,
                quarantine_factory=lambda: ExactSecretStreamQuarantine((secret,)),
            ) as buffer:
                result = subprocess.run(
                    [
                        "/usr/bin/prlimit",
                        "--fsize=1048576:1048576",
                        "--core=0",
                        "--",
                        "/usr/bin/strace",
                        "-f",
                        "-v",
                        "-xx",
                        "-s",
                        "65536",
                        "-e",
                        "trace=execve,execveat",
                        "-o",
                        str(buffer.path),
                        "--",
                        "/usr/bin/true",
                        secret.decode(),
                    ],
                    env={"PATH": "/usr/bin:/bin"},
                    capture_output=True,
                    timeout=5,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                raw = os.pread(buffer.descriptor, 1048576, 0)
                self.assertNotIn(secret, raw)
                with self.assertRaisesRegex(
                    CaptureQuarantineError, "^capture output quarantined$"
                ):
                    buffer.retain(root / "exec.trace")
                self.assertEqual(list(root.iterdir()), [])
                with self.assertRaisesRegex(ValueError, "already attempted"):
                    buffer.retain(root / "retry.trace")

    def test_malformed_limited_raw_and_decoded_inputs_cannot_be_published(self):
        cases = [
            b"raw-private\n",
            b'17 execve("raw-private", [], []) = 0\n',
            b'17 "\\x72\\x61\\x77\\x2d\\x70\\x72\\x69\\x76\\x61\\x74\\x65"\n',
            b'17 "\\x00\\xG0"\n',
            b'17 "\\x61\n',
            b'17 "\\x61"...\n',
            b'17 "\\x61"',
            b"\xff\n",
            b"",
        ]
        before = set(os.listdir("/proc/self/fd"))
        for raw in cases:
            with self.subTest(raw=raw), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                with buffered_exec_trace(
                    max_bytes=1024,
                    quarantine_factory=lambda: ExactSecretStreamQuarantine(
                        (b"raw-private",)
                    ),
                ) as buffer:
                    os.write(buffer.descriptor, raw)
                    with self.assertRaises((ValueError, CaptureQuarantineError)):
                        buffer.retain(root / "trace")
                    self.assertEqual(list(root.iterdir()), [])
        with tempfile.TemporaryDirectory() as temporary:
            for size in (1024, 1025):
                with (
                    self.subTest(size=size),
                    buffered_exec_trace(
                        max_bytes=1024,
                        quarantine_factory=lambda: ExactSecretStreamQuarantine(
                            (b"private",)
                        ),
                    ) as buffer,
                ):
                    os.write(buffer.descriptor, b" " * (size - 1) + b"\n")
                    with self.assertRaisesRegex(ValueError, "byte limit"):
                        buffer.retain(Path(temporary) / "trace")
                    self.assertEqual(list(Path(temporary).iterdir()), [])
        self.assertEqual(before, set(os.listdir("/proc/self/fd")))

    def test_custody_refuses_replacement_and_closes_on_caller_failure(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "existing"
            target.write_bytes(b"prior evidence")
            with buffered_exec_trace(
                max_bytes=1024,
                quarantine_factory=lambda: ExactSecretStreamQuarantine((b"private",)),
            ) as buffer:
                os.write(buffer.descriptor, b"1 +++ exited with 0 +++\n")
                with self.assertRaises(FileExistsError):
                    buffer.retain(target)
                self.assertEqual(target.read_bytes(), b"prior evidence")
            with self.assertRaisesRegex(RuntimeError, "caller failure"):
                with buffered_exec_trace(
                    max_bytes=1024,
                    quarantine_factory=lambda: ExactSecretStreamQuarantine(
                        (b"private",)
                    ),
                ) as buffer:
                    descriptor = buffer.descriptor
                    raise RuntimeError("caller failure")
            with self.assertRaises(OSError):
                os.fstat(descriptor)
