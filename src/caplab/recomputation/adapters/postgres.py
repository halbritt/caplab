"""Read-only PostgreSQL access to one frozen Study 001 registration."""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

from caplab.runtime.canonical import canonical_json


def _plain(value: object) -> object:
    return json.loads(canonical_json(value).decode("utf-8"))


class PostgresRecomputationStore:
    def __init__(
        self,
        conninfo: str,
        *,
        connect: Callable[..., Any] | None = None,
    ) -> None:
        if connect is None:
            import psycopg

            connect = psycopg.connect
        self.conninfo = conninfo
        self._connect = connect

    def get(self, manifest_sha256: str) -> dict[str, object] | None:
        with self._connect(self.conninfo) as connection:
            connection.execute("SET TRANSACTION READ ONLY")
            row = connection.execute(
                "SELECT body FROM caplab_v0.study_registrations "
                "WHERE manifest_sha256 = %s",
                (manifest_sha256,),
            ).fetchone()
        if row is None:
            return None
        retained = _plain(row[0])
        if not isinstance(retained, dict):
            raise RuntimeError("registered Study 001 manifest is not an object")
        return retained

    def locator(self, content_sha256: str) -> dict[str, object] | None:
        with self._connect(self.conninfo) as connection:
            connection.execute("SET TRANSACTION READ ONLY")
            row = connection.execute(
                "SELECT object_key, local_copy_key, byte_count "
                "FROM caplab_v0.study_objects WHERE content_sha256 = %s",
                (content_sha256,),
            ).fetchone()
        if row is None:
            return None
        return {
            "object_key": row[0],
            "local_copy_key": row[1],
            "byte_count": row[2],
        }
