from __future__ import annotations

import re
import subprocess
import unittest

from caplab.producer import producer_identity


class ProducerIdentityTests(unittest.TestCase):
    def test_source_checkout_reports_actual_commit_and_package_digest(self) -> None:
        version, commit, package_sha256 = producer_identity()
        expected_commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

        self.assertEqual(version, "0.1.0")
        self.assertEqual(commit, expected_commit)
        self.assertRegex(commit, re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$"))
        self.assertRegex(package_sha256, re.compile(r"^[0-9a-f]{64}$"))
        self.assertNotEqual(commit, package_sha256)


if __name__ == "__main__":
    unittest.main()
