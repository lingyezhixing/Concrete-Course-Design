"""鉴权模块测试。"""

import pytest
from pydantic import ValidationError

from app.data import connection


def test_init_db_creates_users_table(tmp_path, monkeypatch):
    monkeypatch.setattr(connection, "DB_PATH", tmp_path / "t.db")
    connection.init_db()
    conn = connection.get_connection()
    cols = {row["name"] for row in conn.execute("PRAGMA table_info(users)").fetchall()}
    conn.close()
    assert {"id", "username", "password_hash", "created_at"} <= cols


# ── security ──────────────────────────────────────────────
from app.security import (  # noqa: E402
    create_access_token,
    decode_token,
    hash_password,
    verify_password,
)


class TestPasswordHash:
    def test_hash_and_verify(self):
        h = hash_password("secret1")
        assert h != "secret1"
        assert verify_password("secret1", h) is True
        assert verify_password("wrong", h) is False

    def test_unique_salt(self):
        assert hash_password("secret1") != hash_password("secret1")


class TestJwt:
    def test_roundtrip(self):
        payload = decode_token(create_access_token(42))
        assert payload is not None
        assert payload["sub"] == "42"
        assert "exp" in payload and "iat" in payload

    def test_invalid_token_returns_none(self):
        assert decode_token("garbage") is None

    def test_tampered_token_returns_none(self):
        token = create_access_token(42)
        assert decode_token(token + "x") is None


# ── models ────────────────────────────────────────────────
from app.models.user import UserCreate  # noqa: E402


class TestUserCreate:
    def test_valid(self):
        u = UserCreate(username="alice", password="secret1")
        assert u.username == "alice"

    def test_short_username(self):
        with pytest.raises(ValidationError):
            UserCreate(username="ab", password="secret1")

    def test_invalid_chars(self):
        with pytest.raises(ValidationError):
            UserCreate(username="ali ce", password="secret1")

    def test_short_password(self):
        with pytest.raises(ValidationError):
            UserCreate(username="alice", password="123")


# ── repository ────────────────────────────────────────────
from app.auth.repository import (  # noqa: E402
    UsernameAlreadyExists,
    create_user,
    get_by_id,
    get_by_username,
)


class TestRepository:
    def test_create_user_returns_public(self, isolated_db):
        u = create_user("alice", "secret1")
        assert u["username"] == "alice"
        assert isinstance(u["id"], int)
        assert u["created_at"]

    def test_duplicate_raises(self, isolated_db):
        create_user("alice", "secret1")
        with pytest.raises(UsernameAlreadyExists):
            create_user("alice", "other12")

    def test_password_is_hashed(self, isolated_db):
        u = create_user("alice", "secret1")
        row = get_by_id(u["id"])
        assert row["password_hash"] != "secret1"
        assert "secret1" not in row["password_hash"]

    def test_get_by_username(self, isolated_db):
        create_user("alice", "secret1")
        assert get_by_username("alice") is not None
        assert get_by_username("ghost") is None


# ── dependencies ──────────────────────────────────────────
from fastapi import HTTPException  # noqa: E402

from app.auth.dependencies import get_current_user  # noqa: E402


class TestGetCurrentUser:
    def test_valid_token(self, isolated_db):
        u = create_user("dave", "secret1")
        cu = get_current_user(create_access_token(u["id"]))
        assert cu["username"] == "dave"
        assert cu["id"] == u["id"]

    def test_invalid_token(self, isolated_db):
        with pytest.raises(HTTPException) as exc:
            get_current_user("garbage")
        assert exc.value.status_code == 401

    def test_unknown_user(self, isolated_db):
        token = create_access_token(99999)
        with pytest.raises(HTTPException) as exc:
            get_current_user(token)
        assert exc.value.status_code == 401


# ── routes ────────────────────────────────────────────────
class TestAuthRoutes:
    def test_register_returns_token(self, client):
        res = client.post(
            "/api/auth/register", json={"username": "alice", "password": "secret1"}
        )
        assert res.status_code == 200
        data = res.json()
        assert data["token_type"] == "bearer"
        assert data["access_token"]
        assert data["expires_in"] == 7 * 86400
        assert data["user"]["username"] == "alice"

    def test_register_duplicate_409(self, client):
        client.post(
            "/api/auth/register", json={"username": "alice", "password": "secret1"}
        )
        res = client.post(
            "/api/auth/register", json={"username": "alice", "password": "other12"}
        )
        assert res.status_code == 409

    def test_register_invalid_username_422(self, client):
        res = client.post(
            "/api/auth/register", json={"username": "ab", "password": "secret1"}
        )
        assert res.status_code == 422

    def test_register_short_password_422(self, client):
        res = client.post(
            "/api/auth/register", json={"username": "alice", "password": "123"}
        )
        assert res.status_code == 422

    def test_login_success(self, client):
        client.post(
            "/api/auth/register", json={"username": "bob", "password": "secret1"}
        )
        res = client.post(
            "/api/auth/login", json={"username": "bob", "password": "secret1"}
        )
        assert res.status_code == 200
        assert res.json()["access_token"]

    def test_login_wrong_password_401(self, client):
        client.post(
            "/api/auth/register", json={"username": "bob", "password": "secret1"}
        )
        res = client.post(
            "/api/auth/login", json={"username": "bob", "password": "wrong"}
        )
        assert res.status_code == 401

    def test_login_unknown_user_401(self, client):
        res = client.post(
            "/api/auth/login", json={"username": "ghost", "password": "x"}
        )
        assert res.status_code == 401

    def test_me_with_token(self, client):
        reg = client.post(
            "/api/auth/register", json={"username": "carol", "password": "secret1"}
        ).json()
        res = client.get(
            "/api/auth/me", headers={"Authorization": f"Bearer {reg['access_token']}"}
        )
        assert res.status_code == 200
        assert res.json()["username"] == "carol"

    def test_me_without_token_401(self, client):
        assert client.get("/api/auth/me").status_code == 401

    def test_me_bad_token_401(self, client):
        res = client.get(
            "/api/auth/me", headers={"Authorization": "Bearer not.a.jwt"}
        )
        assert res.status_code == 401

    def test_delete_account(self, client):
        reg = client.post(
            "/api/auth/register", json={"username": "del", "password": "secret1"}
        ).json()
        token = reg["access_token"]
        res = client.delete(
            "/api/auth/account", headers={"Authorization": f"Bearer {token}"}
        )
        assert res.status_code == 204
        # 账户已删除，原 token 立即失效
        me = client.get(
            "/api/auth/me", headers={"Authorization": f"Bearer {token}"}
        )
        assert me.status_code == 401

    def test_delete_account_requires_auth(self, client):
        assert client.delete("/api/auth/account").status_code == 401
