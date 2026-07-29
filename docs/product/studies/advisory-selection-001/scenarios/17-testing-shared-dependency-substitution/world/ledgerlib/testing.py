"""Pytest fixtures for ledgerlib's own suite (and for downstream projects).

Loaded through the repository-root conftest.py via ``pytest_plugins``.
"""

from __future__ import annotations

import pytest

from ledgerlib.ledger import Ledger
from ledgerlib.store import SqliteStore


@pytest.fixture(scope="session")
def store(tmp_path_factory):
    # One migrated database for the whole run: connecting and applying the
    # schema once keeps that startup cost out of every individual test.
    db_path = tmp_path_factory.mktemp("ledgerlib") / "suite.db"
    store = SqliteStore(db_path)
    store.migrate()
    yield store
    store.close()


@pytest.fixture
def ledger(store):
    return Ledger(store)
