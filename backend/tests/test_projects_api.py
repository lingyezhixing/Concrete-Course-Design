"""项目 CRUD 端点测试（隔离、has_uncommitted、门禁）。"""

import pytest

from app.models.project import (
    LOADS_REQUIRED,
    STRUCTURE_REQUIRED,
    ProjectCreate,
    ProjectPatch,
)


def test_project_create_validates_name():
    from pydantic import ValidationError

    ProjectCreate(name="p1")  # ok
    try:
        ProjectCreate(name="")
        raise AssertionError("空名应拒绝")
    except ValidationError:
        pass


def test_required_field_constants():
    assert "L1" in STRUCTURE_REQUIRED and "slab_thickness" in STRUCTURE_REQUIRED
    assert "live_load" in LOADS_REQUIRED
    # 分项系数已固定在后端，不计入 LOADS_REQUIRED
    assert "dead_load_factor" not in LOADS_REQUIRED


def test_project_patch_all_optional():
    p = ProjectPatch()
    assert p.name is None and p.data is None
    p2 = ProjectPatch(name="x")
    assert p2.name == "x"


@pytest.fixture()
def alice_token(client):
    res = client.post("/api/auth/register", json={"username": "alice", "password": "secret1"})
    return res.json()["access_token"]


@pytest.fixture()
def bob_token(client):
    res = client.post("/api/auth/register", json={"username": "bob", "password": "secret1"})
    return res.json()["access_token"]


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def test_create_and_list_project(client, alice_token):
    res = client.post("/api/projects", json={"name": "p1"}, headers=_auth(alice_token))
    assert res.status_code == 201
    body = res.json()
    assert body["name"] == "p1"
    assert body["data"]["slab"]["initialized"] is False
    assert body["has_uncommitted"] is False  # 新建且无快照

    lst = client.get("/api/projects", headers=_auth(alice_token))
    assert lst.status_code == 200
    assert len(lst.json()) == 1


def test_get_project_updates_last_opened_and_has_uncommitted(client, alice_token):
    pid = client.post("/api/projects", json={"name": "p1"}, headers=_auth(alice_token)).json()["id"]
    # 改 data（updated_at 推进）
    client.patch(f"/api/projects/{pid}", json={"data": {"x": 1}}, headers=_auth(alice_token))
    got = client.get(f"/api/projects/{pid}", headers=_auth(alice_token))
    assert got.status_code == 200
    assert got.json()["has_uncommitted"] is True  # 有改动且无快照
    assert got.json()["data"] == {"x": 1}


def test_isolation_other_user_gets_404(client, alice_token, bob_token):
    pid = client.post("/api/projects", json={"name": "alice-p"}, headers=_auth(alice_token)).json()["id"]
    # bob 看不到 alice 的项目
    assert client.get(f"/api/projects/{pid}", headers=_auth(bob_token)).status_code == 404
    assert client.patch(f"/api/projects/{pid}", json={"data": {}}, headers=_auth(bob_token)).status_code == 404
    assert client.delete(f"/api/projects/{pid}", headers=_auth(bob_token)).status_code == 404


def test_endpoints_require_auth(client):
    assert client.get("/api/projects").status_code == 401
    assert client.post("/api/projects", json={"name": "x"}).status_code == 401


def test_delete_project(client, alice_token):
    pid = client.post("/api/projects", json={"name": "p1"}, headers=_auth(alice_token)).json()["id"]
    assert client.delete(f"/api/projects/{pid}", headers=_auth(alice_token)).status_code == 204
    assert client.get(f"/api/projects/{pid}", headers=_auth(alice_token)).status_code == 404


def test_fresh_project_has_uncommitted_consistently_false(client, alice_token):
    # 新建、未编辑的项目：POST / GET / LIST 三处 has_uncommitted 必须一致为 False
    pid = client.post("/api/projects", json={"name": "p1"}, headers=_auth(alice_token)).json()["id"]

    assert client.get(f"/api/projects/{pid}", headers=_auth(alice_token)).json()["has_uncommitted"] is False

    lst = client.get("/api/projects", headers=_auth(alice_token)).json()
    assert all(p["has_uncommitted"] is False for p in lst), lst
