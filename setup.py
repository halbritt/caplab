"""Build hooks that retain the exact CAPLAB source commit in artifacts."""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

from setuptools import setup
from setuptools.command.build_py import build_py
from setuptools.command.sdist import sdist


_STAMP = Path("src/caplab/_source_commit.txt")
_PLACEHOLDER = "$Format:%H$"
_COMMIT = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})")
_CONTRACTS = (
    "qualification-schema-catalog-v1.json",
    "qualification-claim-v1.schema.json",
    "qualification-export-v1.schema.json",
    "qualification-records-v1.schema.json",
    "revbench-live-native-v1.schema.json",
    "revbench-v1.schema.json",
)


def _source_commit() -> str:
    stamped = _STAMP.read_text(encoding="ascii").strip()
    if _COMMIT.fullmatch(stamped):
        return stamped
    if stamped != _PLACEHOLDER:
        raise RuntimeError("CAPLAB source-commit stamp is invalid")
    try:
        result = subprocess.run(
            ["/usr/bin/git", "rev-parse", "--show-toplevel", "HEAD"],
            env={"LC_ALL": "C"},
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        raise RuntimeError("CAPLAB source commit is unavailable") from error
    lines = result.stdout.splitlines()
    if len(lines) != 2:
        raise RuntimeError("CAPLAB source checkout is invalid")
    try:
        repository_root = Path(lines[0]).resolve(strict=True)
        stamp = _STAMP.resolve(strict=True)
    except OSError as error:
        raise RuntimeError("CAPLAB source checkout is invalid") from error
    if stamp != repository_root / _STAMP:
        raise RuntimeError("CAPLAB source checkout is invalid")
    commit = lines[1].strip()
    if not _COMMIT.fullmatch(commit):
        raise RuntimeError("CAPLAB source commit is invalid")
    return commit


class _BuildPy(build_py):
    def run(self) -> None:
        super().run()
        package_root = Path(self.build_lib) / "caplab"
        stamp = package_root / "_source_commit.txt"
        stamp.write_text(_source_commit() + "\n", encoding="ascii")
        source_contracts = Path("docs/product/contracts")
        packaged_contracts = package_root / "qualification" / "contracts"
        packaged_contracts.mkdir(parents=True, exist_ok=True)
        for filename in _CONTRACTS:
            shutil.copyfile(
                source_contracts / filename,
                packaged_contracts / filename,
            )


class _Sdist(sdist):
    def make_release_tree(self, base_dir: str, files: list[str]) -> None:
        super().make_release_tree(base_dir, files)
        stamp = Path(base_dir) / _STAMP
        stamp.write_text(_source_commit() + "\n", encoding="ascii")


setup(cmdclass={"build_py": _BuildPy, "sdist": _Sdist})
