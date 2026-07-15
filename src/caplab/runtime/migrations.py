"""Content-identified, forward-only migration planning."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from .canonical import sha256_hex


MIGRATION_NAME = re.compile(r"\A[0-9]{4}_[a-z0-9_]+\.sql\Z")


class ChecksumDrift(RuntimeError):
    """An applied migration filename now has different bytes."""


@dataclass(frozen=True, slots=True)
class Migration:
    filename: str
    sha256: str
    sql: str


def discover_migrations(root: Path) -> list[Migration]:
    migrations: list[Migration] = []
    for path in sorted(root.iterdir()):
        if not path.is_file() or path.is_symlink() or not MIGRATION_NAME.fullmatch(path.name):
            continue
        data = path.read_bytes()
        migrations.append(
            Migration(filename=path.name, sha256=sha256_hex(data), sql=data.decode("utf-8"))
        )
    if not migrations:
        raise ValueError("no migration files found")
    return migrations


def pending_migrations(
    migrations: list[Migration], applied: Mapping[str, str]
) -> list[Migration]:
    known = {migration.filename for migration in migrations}
    unexpected = set(applied) - known
    if unexpected:
        raise ChecksumDrift(f"applied migrations are absent from source: {sorted(unexpected)!r}")
    pending: list[Migration] = []
    for migration in migrations:
        applied_sha256 = applied.get(migration.filename)
        if applied_sha256 is None:
            pending.append(migration)
        elif applied_sha256 != migration.sha256:
            raise ChecksumDrift(f"checksum drift for applied migration {migration.filename}")
    return pending
