"""Shared pytest fixtures.

Each test gets an isolated, temporary SQLite database by pointing the
storage module's default path at a tmp file via monkeypatch.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app import storage
from app.main import app


@pytest.fixture
def db_path(tmp_path, monkeypatch):
    path = str(tmp_path / "test.db")
    # Redirect every storage function's default db_path to the temp file.
    monkeypatch.setattr(storage, "DEFAULT_DB_PATH", path)
    storage.init_db(path)
    return path


@pytest.fixture
def client(db_path):
    with TestClient(app) as test_client:
        yield test_client
