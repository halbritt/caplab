"""Frozen source identities for one bounded historical admission."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath


SHA256 = re.compile(r"\A[0-9a-f]{64}\Z")
COMMIT = re.compile(r"\A[0-9a-f]{40}\Z")
IDENTIFIER = re.compile(r"\A[a-z][a-z0-9-]{2,127}\Z")


def _safe_relative_path(value: str, label: str) -> str:
    path = PurePosixPath(value)
    if not value or path.is_absolute() or ".." in path.parts or str(path) != value:
        raise ValueError(f"{label} must be a normalized relative POSIX path")
    return value


@dataclass(frozen=True, slots=True)
class GitRecord:
    record_id: str
    commit: str
    path: str
    content_sha256: str
    already_preserved_path: str | None = None

    def __post_init__(self) -> None:
        if not IDENTIFIER.fullmatch(self.record_id):
            raise ValueError("Git record id is not a bounded lowercase identifier")
        if not COMMIT.fullmatch(self.commit):
            raise ValueError("Git commit must be 40 lowercase hexadecimal characters")
        _safe_relative_path(self.path, "Git path")
        if not SHA256.fullmatch(self.content_sha256):
            raise ValueError("Git content SHA-256 is invalid")
        if self.already_preserved_path is not None:
            _safe_relative_path(self.already_preserved_path, "preserved Git path")


@dataclass(frozen=True, slots=True)
class SourceSet:
    study_id: str
    preservation_root: Path
    preservation_manifest_sha256: str
    git_records: tuple[GitRecord, ...]
    expected_preservation_records: int
    expected_total_records: int
    expected_attempts: int

    def __post_init__(self) -> None:
        if not IDENTIFIER.fullmatch(self.study_id):
            raise ValueError("study id is not a bounded lowercase identifier")
        if (
            not self.preservation_root.is_absolute()
            or self.preservation_root.is_symlink()
        ):
            raise ValueError("preservation root must be an absolute non-symlink path")
        if not SHA256.fullmatch(self.preservation_manifest_sha256):
            raise ValueError("preservation manifest SHA-256 is invalid")
        if self.expected_preservation_records < 1:
            raise ValueError("expected preservation record count must be positive")
        if self.expected_total_records < self.expected_preservation_records + 1:
            raise ValueError("total record count must include the governing manifest")
        if self.expected_attempts < 0:
            raise ValueError("expected attempt count must not be negative")
