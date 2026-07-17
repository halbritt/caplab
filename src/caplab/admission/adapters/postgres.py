"""Append-only PostgreSQL projection for a frozen study admission manifest."""

from __future__ import annotations

import json
from collections.abc import Callable
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from caplab.runtime.canonical import canonical_json
from caplab.runtime.errors import OperationConflict


def _plain(value: object) -> object:
    return json.loads(canonical_json(value).decode("utf-8"))


class PostgresAdmissionStore:
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

    @staticmethod
    def _jsonb(value: object) -> Any:
        from psycopg.types.json import Jsonb

        return Jsonb(_plain(value))

    def _connection(self) -> Any:
        return self._connect(self.conninfo)

    @contextmanager
    def object_guard(self, content_sha256: str) -> Iterator[None]:
        key = int(content_sha256[:16], 16)
        if key >= 2**63:
            key -= 2**64
        connection = self._connection()
        try:
            connection.autocommit = True
            connection.execute("SELECT pg_advisory_lock(%s)", (key,))
            try:
                yield
            finally:
                row = connection.execute(
                    "SELECT pg_advisory_unlock(%s)", (key,)
                ).fetchone()
                if row is None or row[0] is not True:
                    raise RuntimeError("CAPLAB admission object lock was not held")
        finally:
            connection.close()

    @staticmethod
    def _expect(retained: object, expected: object, label: str) -> None:
        if retained != _plain(expected):
            raise OperationConflict(f"{label} identity collision")

    def freeze(self, manifest: dict[str, object]) -> bool:
        digest = str(manifest["manifest_sha256"])
        study_id = str(manifest["study_id"])
        with self._connection() as connection:
            with connection.transaction():
                existing_study = connection.execute(
                    "SELECT manifest_sha256, body FROM caplab_v0.study_registrations WHERE study_id = %s",
                    (study_id,),
                ).fetchone()
                if existing_study is not None:
                    if existing_study[0] != digest:
                        raise OperationConflict(
                            "study already has a different frozen admission manifest"
                        )
                    self._expect(existing_study[1], manifest, "admission manifest")
                    return True
                connection.execute(
                    """
                    INSERT INTO caplab_v0.study_registrations
                        (manifest_sha256, study_id, body)
                    VALUES (%s, %s, %s)
                    """,
                    (digest, study_id, self._jsonb(manifest)),
                )
                records = manifest["records"]
                assert isinstance(records, list)
                objects: dict[str, dict[str, object]] = {}
                for record in records:
                    assert isinstance(record, dict)
                    objects.setdefault(str(record["content_sha256"]), record)
                for content_sha256, record in objects.items():
                    connection.execute(
                        """
                        INSERT INTO caplab_v0.study_objects
                            (content_sha256, object_key, local_copy_key, byte_count)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (content_sha256) DO NOTHING
                        """,
                        (
                            content_sha256,
                            record["object_key"],
                            record["local_copy_key"],
                            record["byte_count"],
                        ),
                    )
                    retained = connection.execute(
                        """
                        SELECT object_key, local_copy_key, byte_count
                        FROM caplab_v0.study_objects WHERE content_sha256 = %s
                        """,
                        (content_sha256,),
                    ).fetchone()
                    if retained != (
                        record["object_key"],
                        record["local_copy_key"],
                        record["byte_count"],
                    ):
                        raise OperationConflict("study object identity collision")
                for record in records:
                    assert isinstance(record, dict)
                    connection.execute(
                        """
                        INSERT INTO caplab_v0.study_evidence_records
                            (manifest_sha256, record_id, source_kind, source_commit,
                             source_path, content_sha256, media_type, disposition, record_body)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            digest,
                            record["record_id"],
                            record["source_kind"],
                            record.get("source_commit"),
                            record["source_path"],
                            record["content_sha256"],
                            record["media_type"],
                            record["disposition"],
                            self._jsonb(record),
                        ),
                    )
                for identity in manifest["identity_records"]:
                    connection.execute(
                        """
                        INSERT INTO caplab_v0.study_identity_records
                            (manifest_sha256, kind, identity_sha256, body)
                        VALUES (%s, %s, %s, %s)
                        """,
                        (
                            digest,
                            identity["kind"],
                            identity["identity_sha256"],
                            self._jsonb(identity["body"]),
                        ),
                    )
                for assignment in manifest["assignments"]:
                    connection.execute(
                        """
                        INSERT INTO caplab_v0.study_trial_assignments
                            (manifest_sha256, identity_sha256, sequence, block, task, condition, body)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            digest,
                            assignment["identity_sha256"],
                            assignment["sequence"],
                            assignment["block"],
                            assignment["task"],
                            assignment["condition"],
                            self._jsonb(assignment["body"]),
                        ),
                    )
                for attempt in manifest["attempts"]:
                    connection.execute(
                        """
                        INSERT INTO caplab_v0.study_attempts
                            (manifest_sha256, identity_sha256, assignment_sha256,
                             attempt_number, body)
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        (
                            digest,
                            attempt["identity_sha256"],
                            attempt["assignment_sha256"],
                            attempt["attempt_number"],
                            self._jsonb(attempt["body"]),
                        ),
                    )
                for outcome in manifest["outcomes"]:
                    connection.execute(
                        """
                        INSERT INTO caplab_v0.study_outcomes
                            (manifest_sha256, identity_sha256, attempt_sha256, body)
                        VALUES (%s, %s, %s, %s)
                        """,
                        (
                            digest,
                            outcome["identity_sha256"],
                            outcome["attempt_sha256"],
                            self._jsonb(outcome["body"]),
                        ),
                    )
                connection.execute(
                    """
                    INSERT INTO caplab_v0.audit_events (event_type, event_body)
                    VALUES ('study-admission-completed', %s)
                    """,
                    (
                        self._jsonb(
                            {
                                "study_id": study_id,
                                "manifest_sha256": digest,
                                "record_count": manifest["summary"]["record_count"],
                            }
                        ),
                    ),
                )
        return False

    def get(self, manifest_sha256: str) -> dict[str, object] | None:
        with self._connection() as connection:
            row = connection.execute(
                "SELECT body FROM caplab_v0.study_registrations WHERE manifest_sha256 = %s",
                (manifest_sha256,),
            ).fetchone()
        return None if row is None else row[0]
