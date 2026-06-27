"""测试公共 fixture：每个用例隔离的临时 DB。"""

import pytest
from fastapi.testclient import TestClient

from app.data import connection


@pytest.fixture()
def isolated_db(tmp_path, monkeypatch):
    """把 DB_PATH 重定向到临时文件并建表。"""
    monkeypatch.setattr(connection, "DB_PATH", tmp_path / "test.db")
    connection.init_db()
    return tmp_path / "test.db"


@pytest.fixture()
def client(isolated_db):
    """带隔离 DB 的 TestClient（lifespan 在 patched 路径建表）。"""
    from app.main import app

    with TestClient(app) as c:
        yield c
