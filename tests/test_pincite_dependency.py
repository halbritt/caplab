import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class PinciteDependencyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.workspace = Path(self.temporary_directory.name)
        self.caplab_root = self.workspace / "caplab"
        self.pincite_home = self.workspace / "pincite"
        self.caplab_root.mkdir()
        binary = self.pincite_home / "doctrine" / "bin" / "pincite"
        binary.parent.mkdir(parents=True)
        binary.write_text(
            "#!/bin/sh\n"
            "echo 'retrieval state clean: corpus corpus-test, doctrine doctrine-test'\n",
            encoding="utf-8",
        )
        binary.chmod(binary.stat().st_mode | stat.S_IXUSR)
        runtime = self.pincite_home / "doctrine" / "runtime"
        runtime.mkdir()
        (runtime / "doctrine-index.sqlite3").write_bytes(b"test-index")
        subprocess.run(["git", "init", "-q"], cwd=self.pincite_home, check=True)
        subprocess.run(
            ["git", "config", "user.email", "caplab-test@example.invalid"],
            cwd=self.pincite_home,
            check=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "CAPLAB Test"],
            cwd=self.pincite_home,
            check=True,
        )
        subprocess.run(["git", "add", "."], cwd=self.pincite_home, check=True)
        subprocess.run(
            ["git", "commit", "-qm", "fixture"], cwd=self.pincite_home, check=True
        )
        self.commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=self.pincite_home,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        subprocess.run(
            ["git", "tag", "pincite-release-test"],
            cwd=self.pincite_home,
            check=True,
        )
        self.write_dependency(commit=self.commit)

    def write_dependency(self, *, commit: str) -> None:
        document = {
            "schema_version": "caplab-pincite-dependency/1",
            "repository": "https://github.com/halbritt/pincite",
            "release_tag": "pincite-release-test",
            "commit": commit,
            "corpus_id": "corpus-test",
            "doctrine_id": "doctrine-test",
        }
        (self.caplab_root / "pincite-dependency.json").write_text(
            json.dumps(document), encoding="utf-8"
        )

    def run_check(self) -> subprocess.CompletedProcess[str]:
        environment = dict(os.environ)
        environment["PYTHONPATH"] = str(ROOT)
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "caplab.pincite",
                "--repo-root",
                str(self.caplab_root),
                "--pincite-home",
                str(self.pincite_home),
            ],
            cwd=ROOT,
            env=environment,
            capture_output=True,
            text=True,
        )

    def test_check_accepts_the_exact_validated_pincite_release(self) -> None:
        completed = self.run_check()

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn(self.commit, completed.stdout)
        self.assertIn("corpus-test", completed.stdout)
        self.assertIn("doctrine-test", completed.stdout)

    def test_check_rejects_a_missing_release_tag(self) -> None:
        dependency_path = self.caplab_root / "pincite-dependency.json"
        dependency = json.loads(dependency_path.read_text(encoding="utf-8"))
        dependency["release_tag"] = "missing-release"
        dependency_path.write_text(json.dumps(dependency), encoding="utf-8")

        completed = self.run_check()

        self.assertEqual(completed.returncode, 1)
        self.assertIn("cannot resolve Pincite release tag", completed.stderr)


if __name__ == "__main__":
    unittest.main()
