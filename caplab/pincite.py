"""Resolve and verify CAPLAB's exact Pincite release dependency."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys


DEPENDENCY_FILENAME = "pincite-dependency.json"
DEFAULT_CAPLAB_ROOT = Path(__file__).resolve().parents[1]


class PinciteDependencyError(ValueError):
    pass


def load_dependency(caplab_root: Path) -> dict[str, str]:
    path = caplab_root / DEPENDENCY_FILENAME
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except OSError as error:
        raise PinciteDependencyError(f"cannot read {path}: {error}") from error
    except json.JSONDecodeError as error:
        raise PinciteDependencyError(f"invalid JSON in {path}: {error}") from error
    if not isinstance(document, dict):
        raise PinciteDependencyError(f"{path} must contain a JSON object")
    expected_schema = "caplab-pincite-dependency/1"
    if document.get("schema_version") != expected_schema:
        raise PinciteDependencyError(
            f"{path} must use schema_version {expected_schema}"
        )
    required = (
        "repository",
        "release_tag",
        "commit",
        "corpus_id",
        "doctrine_id",
    )
    for field in required:
        if not isinstance(document.get(field), str) or not document[field]:
            raise PinciteDependencyError(f"{path} requires non-empty {field}")
    return {field: document[field] for field in required}


def default_pincite_home() -> Path:
    configured = os.environ.get("PINCITE_RELEASE_HOME")
    if configured:
        return Path(configured).expanduser()
    return Path.home() / ".local" / "share" / "pincite" / "release"


def verify_dependency(caplab_root: Path, pincite_home: Path) -> str:
    dependency = load_dependency(caplab_root)
    binary = pincite_home / "doctrine" / "bin" / "pincite"
    index = pincite_home / "doctrine" / "runtime" / "doctrine-index.sqlite3"
    doctrine_root = pincite_home / "doctrine"
    if not binary.is_file():
        raise PinciteDependencyError(f"Pincite binary is missing: {binary}")
    if not index.is_file():
        raise PinciteDependencyError(f"Pincite index is missing: {index}")

    commit_process = subprocess.run(
        ["git", "-C", str(pincite_home), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
    )
    if commit_process.returncode:
        message = commit_process.stderr.strip() or "git rev-parse failed"
        raise PinciteDependencyError(f"cannot identify Pincite commit: {message}")
    actual_commit = commit_process.stdout.strip()
    if actual_commit != dependency["commit"]:
        raise PinciteDependencyError(
            f"Pincite commit mismatch: expected {dependency['commit']}, "
            f"found {actual_commit}"
        )

    tag_process = subprocess.run(
        [
            "git",
            "-C",
            str(pincite_home),
            "rev-parse",
            f"refs/tags/{dependency['release_tag']}^{{commit}}",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if tag_process.returncode:
        message = tag_process.stderr.strip() or "release tag lookup failed"
        raise PinciteDependencyError(
            f"cannot resolve Pincite release tag "
            f"{dependency['release_tag']}: {message}"
        )
    tagged_commit = tag_process.stdout.strip()
    if tagged_commit != dependency["commit"]:
        raise PinciteDependencyError(
            f"Pincite release tag {dependency['release_tag']} points to "
            f"{tagged_commit}, expected {dependency['commit']}"
        )

    gate_process = subprocess.run(
        [
            str(binary),
            "--check-retrieval-state",
            "--index",
            str(index),
            "--doctrine-root",
            str(doctrine_root),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if gate_process.returncode:
        message = gate_process.stderr.strip() or gate_process.stdout.strip()
        raise PinciteDependencyError(
            f"Pincite retrieval-state gate failed: {message}"
        )
    gate_output = gate_process.stdout.strip()
    for identity in (dependency["corpus_id"], dependency["doctrine_id"]):
        if identity not in gate_output:
            raise PinciteDependencyError(
                f"Pincite retrieval-state output does not contain {identity}"
            )
    return (
        f"Pincite dependency verified: release {dependency['release_tag']}; "
        f"commit {actual_commit}; "
        f"corpus {dependency['corpus_id']}; doctrine {dependency['doctrine_id']}"
    )


def parse_arguments(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=DEFAULT_CAPLAB_ROOT)
    parser.add_argument("--pincite-home", type=Path, default=default_pincite_home())
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    arguments = parse_arguments(argv if argv is not None else sys.argv[1:])
    try:
        print(
            verify_dependency(
                arguments.repo_root.resolve(), arguments.pincite_home.resolve()
            )
        )
        return 0
    except (OSError, PinciteDependencyError) as error:
        print(f"Pincite dependency error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
