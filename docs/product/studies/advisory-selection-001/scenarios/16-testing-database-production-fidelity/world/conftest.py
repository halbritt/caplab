"""Shared pytest harness for the trackd suite.

The whole suite runs against one in-memory SQLite database, created once per
session. Each test executes inside a transaction that is rolled back when the
test finishes, which keeps tests isolated from each other, keeps the suite
fast, and leaves nothing behind on disk.
"""

from __future__ import annotations

import sqlite3

import pytest

from trackd.schema import apply_schema
from trackd.service import TrackingService


class SuiteConnection:
    """Adapter that hands the service our shared in-memory connection.

    The service opens and closes a connection per call; here every call gets
    the same underlying connection. commit() and close() are no-ops so the
    end-of-test rollback can wipe whatever the test created.
    """

    def __init__(self, real: sqlite3.Connection) -> None:
        self._real = real

    def commit(self) -> None:  # rollback at teardown keeps the db clean
        pass

    def close(self) -> None:  # the shared connection must outlive each call
        pass

    def __getattr__(self, name: str):
        return getattr(self._real, name)


@pytest.fixture(scope="session")
def _suite_db() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    apply_schema(conn)
    yield conn
    conn.close()


@pytest.fixture()
def service(_suite_db: sqlite3.Connection) -> TrackingService:
    shared = SuiteConnection(_suite_db)
    yield TrackingService(connection_factory=lambda: shared)
    _suite_db.rollback()
