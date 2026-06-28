"""项目/快照 repository 测试：用户隔离、CASCADE、restore/fork。"""

from app.auth.repository import create_user
from app.data import connection
from app.data.project_repository import (
    create_project,
    create_snapshot,
    delete_project,
    fork_snapshot,
    get_project,
    list_projects,
    list_snapshots,
    restore_snapshot,
    update_project,
)


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
    monkeypatch.setattr(connection, "DB_PATH", tmp_path / "t.db")
    connection.init_db()
    return create_user(name, "secret1")


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


def test_project_isolation_between_users(tmp_path, monkeypatch):
    alice = _seed_user(tmp_path, monkeypatch, "alice")
    # 直接给 bob 建号（不重置 DB）
    from app.auth.repository import create_user as _cu
    bob = _cu("bob", "secret1")

    pa = create_project(alice["id"], "alice-proj")
    create_project(bob["id"], "bob-proj")

    # alice 列表里只有自己的
    assert [p["name"] for p in list_projects(alice["id"])] == ["alice-proj"]
    # bob 取不到 alice 的项目
    assert get_project(bob["id"], pa["id"]) is None
    # bob 删不掉 alice 的项目
    assert delete_project(bob["id"], pa["id"]) is False
    assert get_project(alice["id"], pa["id"]) is not None


def test_update_project_data_and_name(tmp_path, monkeypatch):
    u = _seed_user(tmp_path, monkeypatch)
    p = create_project(u["id"], "p1")

    updated = update_project(u["id"], p["id"], data={"x": 1}, name="p2")
    assert updated["name"] == "p2"
    assert updated["data"] == {"x": 1}
    again = get_project(u["id"], p["id"])
    assert again["name"] == "p2" and again["data"] == {"x": 1}


def test_restore_snapshot_overwrites_working_state(tmp_path, monkeypatch):
    u = _seed_user(tmp_path, monkeypatch)
    p = create_project(u["id"], "p1")

    update_project(u["id"], p["id"], data={"v": 1})
    snap = create_snapshot(u["id"], p["id"], "s1")
    update_project(u["id"], p["id"], data={"v": 2})  # 工作态前进

    restore_snapshot(u["id"], p["id"], snap["id"])
    assert get_project(u["id"], p["id"])["data"] == {"v": 1}
    # 快照本身不变
    assert list_snapshots(u["id"], p["id"])[0]["data"] == {"v": 1}


def test_fork_snapshot_creates_independent_project(tmp_path, monkeypatch):
    u = _seed_user(tmp_path, monkeypatch)
    p = create_project(u["id"], "p1")

    update_project(u["id"], p["id"], data={"v": 1})
    snap = create_snapshot(u["id"], p["id"], "s1")
    update_project(u["id"], p["id"], data={"v": 99})

    forked = fork_snapshot(u["id"], p["id"], snap["id"], "fork-1")
    assert forked["id"] != p["id"]
    assert forked["name"] == "fork-1"
    assert forked["data"] == {"v": 1}  # 来自快照
    # 源项目不受影响
    assert get_project(u["id"], p["id"])["data"] == {"v": 99}
