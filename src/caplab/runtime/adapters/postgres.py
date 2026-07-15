"""PostgreSQL authority for durable operation and registration metadata."""

from __future__ import annotations

import json
from collections.abc import Callable, Iterator, Mapping
from contextlib import contextmanager
from typing import Any

from ..canonical import canonical_json
from ..errors import ObjectMismatch, OperationConflict
from ..migrations import Migration, discover_migrations, pending_migrations
from ..models import RegistrationIntent


def _plain(value: Mapping[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_json(value).decode("utf-8"))


def _advisory_key(content_sha256: str) -> int:
    unsigned = int(content_sha256[:16], 16)
    return unsigned if unsigned < 2**63 else unsigned - 2**64


class PostgresMetadataStore:
    def __init__(self, conninfo: str, *, connect: Callable[..., Any] | None = None) -> None:
        if connect is None:
            import psycopg

            connect = psycopg.connect
        self.conninfo = conninfo
        self._connect = connect

    def _jsonb(self, value: Mapping[str, Any]) -> Any:
        from psycopg.types.json import Jsonb

        return Jsonb(_plain(value))

    @contextmanager
    def _connection(self, *, autocommit: bool = False) -> Iterator[Any]:
        connection = self._connect(self.conninfo, autocommit=autocommit)
        try:
            yield connection
        finally:
            connection.close()

    def claim_operation(self, intent: RegistrationIntent) -> bool:
        request_body = intent.registration_record()
        with self._connection() as connection:
            with connection.transaction():
                connection.execute(
                    "SELECT pg_advisory_xact_lock(hashtextextended(%s, 0))",
                    (f"caplab-operation:{intent.operation_id}",),
                )
                inserted = connection.execute(
                    """
                    INSERT INTO caplab_v0.operation_requests
                        (operation_id, request_sha256, campaign_id, request_body)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (operation_id) DO NOTHING
                    RETURNING operation_id
                    """,
                    (
                        intent.operation_id,
                        intent.request_sha256,
                        intent.campaign_id,
                        self._jsonb(request_body),
                    ),
                ).fetchone()
                existing = connection.execute(
                    """
                    SELECT request_sha256, campaign_id
                    FROM caplab_v0.operation_requests
                    WHERE operation_id = %s
                    """,
                    (intent.operation_id,),
                ).fetchone()
                if existing is None:
                    raise RuntimeError("operation claim disappeared inside its transaction")
                if existing[0] != intent.request_sha256 or existing[1] != intent.campaign_id:
                    raise OperationConflict(
                        f"operation {intent.operation_id!r} already has a different request"
                    )
                if inserted is not None:
                    connection.execute(
                        """
                        INSERT INTO caplab_v0.operation_events (operation_id, event_type)
                        VALUES (%s, 'requested')
                        """,
                        (intent.operation_id,),
                    )
                return inserted is None

    @contextmanager
    def object_guard(self, content_sha256: str) -> Iterator[None]:
        key = _advisory_key(content_sha256)
        with self._connection(autocommit=True) as connection:
            connection.execute("SELECT pg_advisory_lock(%s)", (key,))
            try:
                yield
            finally:
                unlocked = connection.execute("SELECT pg_advisory_unlock(%s)", (key,)).fetchone()
                if unlocked is None or unlocked[0] is not True:
                    raise RuntimeError("CAPLAB object advisory lock was not held at release")

    def append_event(self, operation_id: str, event_type: str) -> None:
        with self._connection() as connection:
            with connection.transaction():
                connection.execute(
                    """
                    INSERT INTO caplab_v0.operation_events (operation_id, event_type)
                    VALUES (%s, %s)
                    """,
                    (operation_id, event_type),
                )

    def _insert_json_identity(
        self,
        connection: Any,
        table: str,
        identity_sha256: str,
        body: Mapping[str, Any],
    ) -> None:
        allowed = {
            "model_identities",
            "agent_configurations",
            "administrations",
            "trial_contexts",
            "trial_assignments",
        }
        if table not in allowed:
            raise ValueError(f"unsupported identity table: {table}")
        connection.execute(
            f"""
            INSERT INTO caplab_v0.{table} (identity_sha256, body)
            VALUES (%s, %s)
            ON CONFLICT (identity_sha256) DO NOTHING
            """,
            (identity_sha256, self._jsonb(body)),
        )
        retained = connection.execute(
            f"SELECT body FROM caplab_v0.{table} WHERE identity_sha256 = %s",
            (identity_sha256,),
        ).fetchone()
        if retained is None or retained[0] != _plain(body):
            raise OperationConflict(f"identity collision in {table}")

    def finalize_registration(self, intent: RegistrationIntent) -> dict[str, Any]:
        identities = intent.identity_sha256
        layers = intent.identity_layers
        attempt_number = layers["attempt"].get("attempt")
        if isinstance(attempt_number, bool) or not isinstance(attempt_number, int) or attempt_number < 1:
            raise ValueError("attempt identity requires a positive integer attempt field")

        with self._connection() as connection:
            with connection.transaction():
                operation = connection.execute(
                    """
                    SELECT request_sha256 FROM caplab_v0.operation_requests
                    WHERE operation_id = %s
                    """,
                    (intent.operation_id,),
                ).fetchone()
                if operation is None or operation[0] != intent.request_sha256:
                    raise OperationConflict("operation request changed before finalization")

                for table, layer in (
                    ("model_identities", "model"),
                    ("agent_configurations", "agent_configuration"),
                    ("administrations", "administration"),
                    ("trial_contexts", "trial_context"),
                    ("trial_assignments", "trial_assignment"),
                ):
                    self._insert_json_identity(
                        connection, table, identities[layer], layers[layer]
                    )

                connection.execute(
                    """
                    INSERT INTO caplab_v0.attempts
                        (identity_sha256, assignment_sha256, attempt_number, body)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (identity_sha256) DO NOTHING
                    """,
                    (
                        identities["attempt"],
                        identities["trial_assignment"],
                        attempt_number,
                        self._jsonb(layers["attempt"]),
                    ),
                )
                retained_attempt = connection.execute(
                    """
                    SELECT assignment_sha256, attempt_number, body
                    FROM caplab_v0.attempts WHERE identity_sha256 = %s
                    """,
                    (identities["attempt"],),
                ).fetchone()
                if retained_attempt != (
                    identities["trial_assignment"],
                    attempt_number,
                    _plain(layers["attempt"]),
                ):
                    raise OperationConflict("attempt identity collision")

                connection.execute(
                    """
                    INSERT INTO caplab_v0.artifacts
                        (content_sha256, object_key, local_copy_key, media_type, byte_count)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (content_sha256) DO NOTHING
                    """,
                    (
                        intent.content_sha256,
                        intent.object_key,
                        intent.object_key,
                        intent.media_type,
                        len(intent.payload),
                    ),
                )
                retained_artifact = connection.execute(
                    """
                    SELECT object_key, local_copy_key, media_type, byte_count
                    FROM caplab_v0.artifacts WHERE content_sha256 = %s
                    """,
                    (intent.content_sha256,),
                ).fetchone()
                if retained_artifact != (
                    intent.object_key,
                    intent.object_key,
                    intent.media_type,
                    len(intent.payload),
                ):
                    raise ObjectMismatch("artifact identity or locator collision")

                connection.execute(
                    """
                    INSERT INTO caplab_v0.attempt_artifacts
                        (attempt_sha256, content_sha256, artifact_kind)
                    VALUES (%s, %s, %s)
                    ON CONFLICT DO NOTHING
                    """,
                    (identities["attempt"], intent.content_sha256, intent.artifact_kind),
                )
                connection.execute(
                    """
                    INSERT INTO caplab_v0.manifests (manifest_sha256, body)
                    VALUES (%s, %s)
                    ON CONFLICT (manifest_sha256) DO NOTHING
                    """,
                    (intent.manifest_sha256, self._jsonb(intent.manifest)),
                )
                retained_manifest = connection.execute(
                    """
                    SELECT body FROM caplab_v0.manifests WHERE manifest_sha256 = %s
                    """,
                    (intent.manifest_sha256,),
                ).fetchone()
                if retained_manifest is None or retained_manifest[0] != _plain(intent.manifest):
                    raise OperationConflict("manifest identity collision")

                inserted = connection.execute(
                    """
                    INSERT INTO caplab_v0.registrations (
                        operation_id, campaign_id, content_sha256, manifest_sha256,
                        model_sha256, agent_configuration_sha256, administration_sha256,
                        trial_context_sha256, trial_assignment_sha256, attempt_sha256,
                        analysis_sha256
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (operation_id) DO NOTHING
                    RETURNING registration_id
                    """,
                    (
                        intent.operation_id,
                        intent.campaign_id,
                        intent.content_sha256,
                        intent.manifest_sha256,
                        identities["model"],
                        identities["agent_configuration"],
                        identities["administration"],
                        identities["trial_context"],
                        identities["trial_assignment"],
                        identities["attempt"],
                        identities["analysis"],
                    ),
                ).fetchone()
                if inserted is not None:
                    connection.execute(
                        """
                        INSERT INTO caplab_v0.operation_events (operation_id, event_type)
                        VALUES (%s, 'registered')
                        """,
                        (intent.operation_id,),
                    )
                    connection.execute(
                        """
                        INSERT INTO caplab_v0.audit_events
                            (operation_id, event_type, event_body)
                        VALUES (%s, 'registration-completed', %s)
                        """,
                        (
                            intent.operation_id,
                            self._jsonb(
                                {
                                    "content_sha256": intent.content_sha256,
                                    "manifest_sha256": intent.manifest_sha256,
                                }
                            ),
                        ),
                    )

        record = self.registration_for_operation(intent.operation_id)
        if record is None:
            raise RuntimeError("registration disappeared after finalization")
        expected = intent.registration_record()
        for field in (
            "campaign_id",
            "request_sha256",
            "content_sha256",
            "object_key",
            "local_copy_key",
            "manifest_sha256",
            "identity_sha256",
        ):
            if record[field] != expected[field]:
                raise OperationConflict(f"completed registration differs at {field}")
        return record

    def registration_for_operation(self, operation_id: str) -> dict[str, Any] | None:
        with self._connection() as connection:
            row = connection.execute(
                """
                SELECT
                    registration.operation_id,
                    registration.campaign_id,
                    request.request_sha256,
                    artifact.content_sha256,
                    artifact.object_key,
                    artifact.local_copy_key,
                    artifact.media_type,
                    artifact.byte_count,
                    registration.manifest_sha256,
                    registration.model_sha256,
                    registration.agent_configuration_sha256,
                    registration.administration_sha256,
                    registration.trial_context_sha256,
                    registration.trial_assignment_sha256,
                    registration.attempt_sha256,
                    registration.analysis_sha256,
                    manifest.body
                FROM caplab_v0.registrations AS registration
                JOIN caplab_v0.operation_requests AS request USING (operation_id)
                JOIN caplab_v0.artifacts AS artifact USING (content_sha256)
                JOIN caplab_v0.manifests AS manifest USING (manifest_sha256)
                WHERE registration.operation_id = %s
                """,
                (operation_id,),
            ).fetchone()
            migration_rows = connection.execute(
                """
                SELECT filename, file_sha256, runtime_commit
                FROM caplab_v0.schema_migrations ORDER BY filename
                """
            ).fetchall()
        if row is None:
            return None
        return {
            "operation_id": row[0],
            "campaign_id": row[1],
            "request_sha256": row[2],
            "content_sha256": row[3],
            "object_key": row[4],
            "local_copy_key": row[5],
            "media_type": row[6],
            "byte_count": row[7],
            "manifest_sha256": row[8],
            "identity_sha256": {
                "model": row[9],
                "agent_configuration": row[10],
                "administration": row[11],
                "trial_context": row[12],
                "trial_assignment": row[13],
                "attempt": row[14],
                "analysis": row[15],
            },
            "manifest": row[16],
            "migration_state": [
                {"filename": item[0], "sha256": item[1], "runtime_commit": item[2]}
                for item in migration_rows
            ],
        }

    def operation_for_operation(self, operation_id: str) -> dict[str, Any] | None:
        with self._connection() as connection:
            row = connection.execute(
                """
                SELECT request_body
                FROM caplab_v0.operation_requests
                WHERE operation_id = %s
                """,
                (operation_id,),
            ).fetchone()
            migration_rows = connection.execute(
                """
                SELECT filename, file_sha256, runtime_commit
                FROM caplab_v0.schema_migrations ORDER BY filename
                """
            ).fetchall()
        if row is None:
            return None
        record = dict(row[0])
        record["migration_state"] = [
            {"filename": item[0], "sha256": item[1], "runtime_commit": item[2]}
            for item in migration_rows
        ]
        return record


class PostgresMigrator:
    def __init__(
        self,
        conninfo: str,
        migrations_root: Any,
        runtime_commit: str,
        *,
        connect: Callable[..., Any] | None = None,
    ) -> None:
        if connect is None:
            import psycopg

            connect = psycopg.connect
        if len(runtime_commit) != 40 or any(character not in "0123456789abcdef" for character in runtime_commit):
            raise ValueError("runtime commit must be a full lowercase Git identity")
        self.conninfo = conninfo
        self.migrations_root = migrations_root
        self.runtime_commit = runtime_commit
        self._connect = connect

    @contextmanager
    def _connection(self) -> Iterator[Any]:
        connection = self._connect(self.conninfo, autocommit=True)
        try:
            yield connection
        finally:
            connection.close()

    @staticmethod
    def _applied(connection: Any) -> dict[str, str]:
        exists = connection.execute(
            "SELECT to_regclass('caplab_v0.schema_migrations')"
        ).fetchone()
        if exists is None or exists[0] is None:
            return {}
        return dict(
            connection.execute(
                "SELECT filename, file_sha256 FROM caplab_v0.schema_migrations"
            ).fetchall()
        )

    def apply(self) -> list[Migration]:
        migrations = discover_migrations(self.migrations_root)
        with self._connection() as connection:
            connection.execute(
                "SELECT pg_advisory_lock(hashtextextended('caplab_v0:migrator', 0))"
            )
            try:
                pending = pending_migrations(migrations, self._applied(connection))
                applied: list[Migration] = []
                for migration in pending:
                    with connection.transaction():
                        connection.execute("SET LOCAL ROLE caplab_owner")
                        connection.execute(migration.sql)
                        connection.execute(
                            """
                            INSERT INTO caplab_v0.schema_migrations
                                (filename, file_sha256, runtime_commit)
                            VALUES (%s, %s, %s)
                            """,
                            (migration.filename, migration.sha256, self.runtime_commit),
                        )
                    applied.append(migration)
                pending_migrations(migrations, self._applied(connection))
                return applied
            finally:
                unlocked = connection.execute(
                    "SELECT pg_advisory_unlock(hashtextextended('caplab_v0:migrator', 0))"
                ).fetchone()
                if unlocked is None or unlocked[0] is not True:
                    raise RuntimeError("CAPLAB migration advisory lock was not held at release")
