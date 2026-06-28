"""项目/快照 repository 测试：用户隔离、CASCADE、restore/fork。"""

from app.auth.repository import create_user
from app.data import connection


def test_init_db_creates_projects_and_snapshots_tables(tmp_path, monkeypatch):
    monkeypatch.setattr(connection, "DB_PATH", tmp_path / "t.db")
    connection.init_db()
    conn = connection.get_connection()

    proj_cols = {r["name"] for r in conn.execute("PRAGMA table_info(projects)").fetchall()}
    snap_cols = {r["name"] for r in conn.execute("PRAGMA table_info(snapshots)").fetchall()}
    conn.close()

    assert {"id", "user_id", "name", "data", "created_at", "updated_at", "last_opened_at"} <= proj_cols
    assert {"id", "project_id", "user_id", "name", "data", "created_at"} <= snap_cols


def _seed_user(tmp_path, monkeypatch, name="alice"):
    from app.auth.repository import create_user as _cu  # noqa
    monkeypatch.setattr(connection, "DB_PATH", tmp_path / "t.db")
    connection.init_db()
    return _cu(name, "secret1")


def test_delete_user_cascades_to_projects_and_snapshots(tmp_path, monkeypatch):
    from app.auth.repository import delete_user
    from app.data.project_repository import create_project, create_snapshot  # Task 2 提供

    u = _seed_user(tmp_path, monkeypatch)
    p = create_project(u["id"], "p1")
    create_snapshot(u["id"], p["id"], "s1")

    delete_user(u["id"])

    conn = connection.get_connection()
    n_proj = conn.execute("SELECT COUNT(*) c FROM projects WHERE user_id=?", (u["id"],)).fetchone()["c"]
    n_snap = conn.execute("SELECT COUNT(*) c FROM snapshots WHERE user_id=?", (u["id"],)).fetchone()["c"]
    conn.close()
    assert n_proj == 0
    assert n_snap == 0
