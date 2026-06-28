"""项目与快照数据访问（raw sqlite3）。

所有函数都带 user_id 隔离：非本人资源返回 None / False，绝不跨用户读写。
"""

import json

from app.data.connection import get_connection


def empty_data() -> dict:
    """新建项目的空数据骨架（与 spec §3.2 一致）。"""
    return {
        "materials": {"fc": None, "fy_slab": None, "fy_beam": None, "gamma_d": None},
        "slab": {"input": {}, "result": {}, "initialized": False},
        "beam": {"input": {}, "result": {}, "initialized": False},
        "main_beam": {"input": {}, "result": {}, "initialized": False},
    }


# ── projects ──────────────────────────────────────────────

def _project_row_to_dict(row) -> dict:
    return {
        "id": row["id"],
        "user_id": row["user_id"],
        "name": row["name"],
        "data": json.loads(row["data"]),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "last_opened_at": row["last_opened_at"],
    }


def list_projects(user_id: int) -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM projects WHERE user_id = ? "
        "ORDER BY COALESCE(last_opened_at, created_at) DESC",
        (user_id,),
    ).fetchall()
    conn.close()
    return [_project_row_to_dict(r) for r in rows]


def create_project(user_id: int, name: str) -> dict:
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO projects (user_id, name, data) VALUES (?, ?, ?)",
        (user_id, name, json.dumps(empty_data())),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM projects WHERE id = ?", (cur.lastrowid,)).fetchone()
    conn.close()
    return _project_row_to_dict(row)


def get_project(user_id: int, project_id: int) -> dict | None:
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM projects WHERE id = ? AND user_id = ?", (project_id, user_id)
    ).fetchone()
    conn.close()
    return _project_row_to_dict(row) if row else None


def update_project(
    user_id: int, project_id: int, *, data: dict | None = None, name: str | None = None
) -> dict | None:
    """更新项目 data 和/或 name；非自有返回 None。data 为 None 时不变。"""
    existing = get_project(user_id, project_id)
    if existing is None:
        return None
    new_data = json.dumps(data) if data is not None else json.dumps(existing["data"])
    conn = get_connection()
    if name is not None:
        conn.execute(
            "UPDATE projects SET name = ?, data = ?, updated_at = datetime('now') "
            "WHERE id = ? AND user_id = ?",
            (name, new_data, project_id, user_id),
        )
    else:
        conn.execute(
            "UPDATE projects SET data = ?, updated_at = datetime('now') "
            "WHERE id = ? AND user_id = ?",
            (new_data, project_id, user_id),
        )
    conn.commit()
    conn.close()
    return get_project(user_id, project_id)


def delete_project(user_id: int, project_id: int) -> bool:
    conn = get_connection()
    cur = conn.execute(
        "DELETE FROM projects WHERE id = ? AND user_id = ?", (project_id, user_id)
    )
    conn.commit()
    conn.close()
    return cur.rowcount > 0


def touch_opened(user_id: int, project_id: int) -> None:
    """打开项目时更新 last_opened_at。"""
    conn = get_connection()
    conn.execute(
        "UPDATE projects SET last_opened_at = datetime('now') WHERE id = ? AND user_id = ?",
        (project_id, user_id),
    )
    conn.commit()
    conn.close()


# ── snapshots ─────────────────────────────────────────────

def _snapshot_row_to_dict(row) -> dict:
    return {
        "id": row["id"],
        "project_id": row["project_id"],
        "user_id": row["user_id"],
        "name": row["name"],
        "data": json.loads(row["data"]),
        "created_at": row["created_at"],
    }


def list_snapshots(user_id: int, project_id: int) -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM snapshots WHERE project_id = ? AND user_id = ? "
        "ORDER BY created_at DESC",
        (project_id, user_id),
    ).fetchall()
    conn.close()
    return [_snapshot_row_to_dict(r) for r in rows]


def create_snapshot(user_id: int, project_id: int, name: str) -> dict | None:
    """归档：把项目当前 data 复制成不可变快照。项目不存在(或非自有)返回 None。"""
    project = get_project(user_id, project_id)
    if project is None:
        return None
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO snapshots (project_id, user_id, name, data) VALUES (?, ?, ?, ?)",
        (project_id, user_id, name, json.dumps(project["data"])),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM snapshots WHERE id = ?", (cur.lastrowid,)).fetchone()
    conn.close()
    return _snapshot_row_to_dict(row)


def get_snapshot(user_id: int, snapshot_id: int) -> dict | None:
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM snapshots WHERE id = ? AND user_id = ?", (snapshot_id, user_id)
    ).fetchone()
    conn.close()
    return _snapshot_row_to_dict(row) if row else None


def delete_snapshot(user_id: int, snapshot_id: int) -> bool:
    conn = get_connection()
    cur = conn.execute(
        "DELETE FROM snapshots WHERE id = ? AND user_id = ?", (snapshot_id, user_id)
    )
    conn.commit()
    conn.close()
    return cur.rowcount > 0


def restore_snapshot(user_id: int, project_id: int, snapshot_id: int) -> dict | None:
    """恢复：把快照 data 写回所属项目的工作态（覆盖）。"""
    snap = get_snapshot(user_id, snapshot_id)
    if snap is None or snap["project_id"] != project_id:
        return None
    return update_project(user_id, project_id, data=snap["data"])


def fork_snapshot(
    user_id: int, project_id: int, snapshot_id: int, name: str
) -> dict | None:
    """fork：用快照 data 创建一个新项目（源项目不动）。"""
    snap = get_snapshot(user_id, snapshot_id)
    if snap is None or snap["project_id"] != project_id:
        return None
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO projects (user_id, name, data) VALUES (?, ?, ?)",
        (user_id, name, json.dumps(snap["data"])),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM projects WHERE id = ?", (cur.lastrowid,)).fetchone()
    conn.close()
    return _project_row_to_dict(row)
