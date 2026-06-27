"""用户数据访问（raw sqlite3）。"""

import sqlite3

from app.data.connection import get_connection
from app.security import hash_password


class UsernameAlreadyExists(Exception):
    """用户名已被占用。"""


def _row_to_dict(row) -> dict:
    return {
        "id": row["id"],
        "username": row["username"],
        "created_at": row["created_at"],
    }


def create_user(username: str, password: str) -> dict:
    conn = get_connection()
    try:
        cur = conn.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, hash_password(password)),
        )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM users WHERE id = ?", (cur.lastrowid,)
        ).fetchone()
    except sqlite3.IntegrityError as exc:
        conn.close()
        raise UsernameAlreadyExists(username) from exc
    conn.close()
    return _row_to_dict(row)


def get_by_username(username: str):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM users WHERE username = ?", (username,)
    ).fetchone()
    conn.close()
    return row


def get_by_id(user_id: int):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM users WHERE id = ?", (user_id,)
    ).fetchone()
    conn.close()
    return row
