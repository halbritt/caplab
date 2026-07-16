"""PostgreSQL adapter for the narrow P5 custody tables and purge function."""

from __future__ import annotations

from collections.abc import Callable, Iterator
from contextlib import contextmanager
from datetime import datetime
from typing import Any

from ..errors import (
    AuthorizationExpired,
    AuthorizationMismatch,
    DependencyRetained,
    UnknownPurgeIdentity,
)
from ..models import InvalidAttemptObservation, PurgeRequest, PurgeTombstone


class PostgresCustodyStore:
    def __init__(
        self, conninfo: str, *, connect: Callable[..., Any] | None = None
    ) -> None:
        if connect is None:
            import psycopg

            connect = psycopg.connect
        self.conninfo = conninfo
        self._connect = connect

    @contextmanager
    def _connection(self) -> Iterator[Any]:
        connection = self._connect(self.conninfo)
        try:
            yield connection
        finally:
            connection.close()

    @staticmethod
    def _jsonb(value: object) -> Any:
        from psycopg.types.json import Jsonb

        return Jsonb(value)

    def record_invalid_observation(
        self, observation: InvalidAttemptObservation
    ) -> None:
        record = observation.to_record()
        with self._connection() as connection:
            with connection.transaction():
                connection.execute(
                    """
                    INSERT INTO caplab_v0.invalid_attempt_observations (
                        observation_id,
                        campaign_id,
                        fixture_sha256,
                        fixture_byte_count,
                        disposition,
                        reason_codes
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        record["observation_id"],
                        record["campaign_id"],
                        record["fixture_sha256"],
                        record["fixture_byte_count"],
                        record["disposition"],
                        self._jsonb(record["reason_codes"]),
                    ),
                )

    def request_purge(self, request: PurgeRequest) -> None:
        with self._connection() as connection:
            with connection.transaction():
                connection.execute(
                    """
                    INSERT INTO caplab_v0.custody_requests (
                        custody_request_id,
                        operation_id,
                        campaign_id,
                        request_sha256,
                        content_sha256,
                        manifest_sha256,
                        authorization_sha256,
                        expires_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        request.custody_request_id,
                        request.operation_id,
                        request.campaign_id,
                        request.request_sha256,
                        request.content_sha256,
                        request.manifest_sha256,
                        request.authorization_sha256,
                        request.expires_at,
                    ),
                )

    def record_dependency(
        self,
        *,
        operation_id: str,
        dependency_kind: str,
        dependency_identity: str,
        event_type: str,
    ) -> None:
        if dependency_kind not in {
            "registration",
            "result",
            "claim",
            "dataset",
            "campaign",
        }:
            raise ValueError("unsupported custody dependency kind")
        if event_type not in {"retained", "released"}:
            raise ValueError("unsupported custody dependency event")
        if not dependency_identity:
            raise ValueError("dependency identity must not be empty")
        with self._connection() as connection:
            with connection.transaction():
                connection.execute(
                    """
                    INSERT INTO caplab_v0.custody_dependency_events (
                        operation_id, dependency_kind, dependency_identity, event_type
                    ) VALUES (%s, %s, %s, %s)
                    """,
                    (operation_id, dependency_kind, dependency_identity, event_type),
                )

    def inventory_state(
        self,
    ) -> tuple[
        dict[str, dict[str, Any]],
        dict[str, dict[str, Any]],
        dict[str, tuple[str, ...]],
        tuple[str, ...],
    ]:
        with self._connection() as connection:
            operations = {
                row[0]: dict(row[1])
                for row in connection.execute(
                    """
                    SELECT operation_id, request_body
                    FROM caplab_v0.operation_requests
                    ORDER BY operation_id
                    """
                )
            }
            registrations = {
                row[0]: {
                    "operation_id": row[0],
                    "campaign_id": row[1],
                    "content_sha256": row[2],
                    "object_key": row[3],
                    "local_copy_key": row[4],
                    "manifest_sha256": row[5],
                }
                for row in connection.execute(
                    """
                    SELECT
                        registration.operation_id,
                        registration.campaign_id,
                        registration.content_sha256,
                        artifact.object_key,
                        artifact.local_copy_key,
                        registration.manifest_sha256
                    FROM caplab_v0.registrations AS registration
                    JOIN caplab_v0.artifacts AS artifact USING (content_sha256)
                    ORDER BY registration.operation_id
                    """
                )
            }
            dependency_rows = connection.execute(
                """
                SELECT operation_id, dependency_kind, dependency_identity
                FROM caplab_v0.current_custody_dependencies
                ORDER BY operation_id, dependency_kind, dependency_identity
                """
            ).fetchall()
            tombstones = tuple(
                row[0]
                for row in connection.execute(
                    """
                    SELECT operation_id
                    FROM caplab_v0.purge_tombstones
                    ORDER BY operation_id
                    """
                )
            )
        dependencies: dict[str, list[str]] = {}
        for operation_id, kind, identity in dependency_rows:
            dependencies.setdefault(operation_id, []).append(f"{kind}:{identity}")
        return (
            operations,
            registrations,
            {
                operation_id: tuple(entries)
                for operation_id, entries in dependencies.items()
            },
            tombstones,
        )

    def purge(self, request: PurgeRequest, *, purged_at: datetime) -> PurgeTombstone:
        try:
            with self._connection() as connection:
                with connection.transaction():
                    row = connection.execute(
                        "SELECT * FROM caplab_v0.purge_p5_operation(%s)",
                        (request.custody_request_id,),
                    ).fetchone()
        except Exception as error:
            sqlstate = getattr(error, "sqlstate", None)
            mapped = {
                "P5001": UnknownPurgeIdentity,
                "P5002": AuthorizationMismatch,
                "P5003": AuthorizationExpired,
                "P5004": DependencyRetained,
            }.get(sqlstate)
            if mapped is None:
                raise
            raise mapped(str(error).strip()) from error
        if row is None:
            raise RuntimeError("guarded P5 purge returned no tombstone")
        if row[11] < purged_at:
            raise RuntimeError(
                "guarded P5 purge tombstone predates the requested effect"
            )
        return PurgeTombstone(
            custody_request_id=row[0],
            operation_id=row[1],
            campaign_id=row[2],
            request_sha256=row[3],
            content_sha256=row[4],
            manifest_sha256=row[7],
            authorization_sha256=row[9],
            purged_at=row[11],
        )
