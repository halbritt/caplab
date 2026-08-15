from __future__ import annotations

import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from caplab.producer import (
    ProducerIdentityError,
    _source_commit,
    producer_identity,
)


class ProducerIdentityTests(unittest.TestCase):
    def test_complete_package_stamp_never_consults_ambient_git(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            package_root = Path(temporary) / "caplab"
            package_root.mkdir()
            commit = "a" * 40
            (package_root / "_source_commit.txt").write_text(
                commit + "\n", encoding="ascii"
            )
            with mock.patch("caplab.producer.subprocess.run") as run:
                self.assertEqual(_source_commit(package_root), commit)
            run.assert_not_called()

    def test_placeholder_package_cannot_inherit_an_ambient_repository_head(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repository_root = Path(temporary)
            package_root = repository_root / "site-packages" / "caplab"
            package_root.mkdir(parents=True)
            (package_root / "_source_commit.txt").write_text(
                "$Format:%H$\n", encoding="ascii"
            )
            observed = subprocess.CompletedProcess(
                args=[],
                returncode=0,
                stdout=f"{repository_root}\n{'b' * 40}\n",
                stderr="",
            )
            with mock.patch("caplab.producer.subprocess.run", return_value=observed):
                with self.assertRaisesRegex(
                    ProducerIdentityError, "producer_commit_checkout_invalid"
                ):
                    _source_commit(package_root)

    def test_source_commit_observation_ignores_path_git_shims(self) -> None:
        package_root = Path(__file__).resolve().parents[1] / "src" / "caplab"
        with tempfile.TemporaryDirectory() as temporary:
            shim = Path(temporary) / "git"
            shim.write_text(
                "#!/bin/sh\nprintf '%s\\n%s\\n' /tmp/not-caplab "
                + "'"
                + "f" * 40
                + "'\n",
                encoding="utf-8",
            )
            shim.chmod(0o700)
            with mock.patch.dict(os.environ, {"PATH": temporary}):
                observed = _source_commit(package_root)

        expected = subprocess.run(
            ["/usr/bin/git", "rev-parse", "HEAD"],
            cwd=package_root,
            env={"LC_ALL": "C"},
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        self.assertEqual(observed, expected)
        self.assertNotEqual(observed, "f" * 40)

    def test_source_checkout_reports_actual_commit_and_package_digest(self) -> None:
        version, commit, package_sha256 = producer_identity()
        expected_commit = subprocess.run(
            ["/usr/bin/git", "rev-parse", "HEAD"],
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
