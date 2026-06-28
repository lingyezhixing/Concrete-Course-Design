"""/calculate 三构件：派生计算 + 门禁 + 超筋处理。"""

import pytest


@pytest.fixture()
def token(client):
    return client.post(
        "/api/auth/register", json={"username": "alice", "password": "secret1"}
    ).json()["access_token"]


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def _project(client, token):
    return client.post("/api/projects", json={"name": "p1"}, headers=_auth(token)).json()["id"]


# 第 1 组方案 A 实测参数
STRUCTURE = {
    "L1": 30.0, "L2": 18.0, "slab_thickness": 120,
    "beam_width": 200, "beam_height": 500,
    "main_beam_width": 300, "main_beam_height": 600,
    "column_width": 350, "slab_spans": 9, "beam_spans": 5, "main_beam_spans": 3,
    "beam_stirrup_diameter": 6, "main_beam_stirrup_diameter": 10,
}
LOADS = {
    "reinforced_concrete_weight": 25.0, "terrazzo_surface": 0.65,
    "plaster_thickness": 15, "plaster_weight": 17.0, "live_load": 4.0,
}


def _save_params(client, token, pid, **overrides):
    data = {"structure": STRUCTURE, "loads": LOADS}
    data.update(overrides)
    client.patch(f"/api/projects/{pid}", json={"data": data}, headers=_auth(token))


def test_calculate_slab_success(client, token):
    pid = _project(client, token)
    _save_params(client, token, pid)
    res = client.post(f"/api/projects/{pid}/calculate", json={"page": "slab"}, headers=_auth(token))
    assert res.status_code == 200
    body = res.json()
    assert body["load"]["dead_load_standard"] == pytest.approx(3.905, abs=0.01)
    assert len(body["reinforcement"]["sections"]) == 9  # 五跨连续板 → 2×5−1 截面


def test_calculate_beam_success(client, token):
    pid = _project(client, token)
    _save_params(client, token, pid)
    res = client.post(f"/api/projects/{pid}/calculate", json={"page": "beam"}, headers=_auth(token))
    assert res.status_code == 200
    body = res.json()
    assert body["load"]["dead_load_standard"] == pytest.approx(9.9038, abs=0.01)
    assert len(body["internal_forces"]["moments"]) == 9  # 五跨次梁 → 9 截面


def test_calculate_main_beam_success(client, token):
    pid = _project(client, token)
    _save_params(client, token, pid)
    res = client.post(f"/api/projects/{pid}/calculate", json={"page": "main_beam"}, headers=_auth(token))
    assert res.status_code == 200
    body = res.json()
    assert body["load"]["dead_load_design"] == pytest.approx(70.468, abs=0.01)
    assert body["load"]["live_load_design"] == pytest.approx(57.6, abs=0.01)


def test_calculate_gating_missing_structure(client, token):
    pid = _project(client, token)
    client.patch(
        f"/api/projects/{pid}",
        json={"data": {"loads": LOADS, "structure": {"L1": 30.0}}},
        headers=_auth(token),
    )
    res = client.post(f"/api/projects/{pid}/calculate", json={"page": "slab"}, headers=_auth(token))
    assert res.status_code == 400
    missing = res.json()["detail"]["missing"]
    assert "slab_thickness" in missing and "L2" in missing


def test_calculate_overreinforcement_returns_400(client, token):
    """超大跨 → αs>0.5 超筋 → 端点返 400，不 500。"""
    pid = _project(client, token)
    bad_structure = dict(STRUCTURE, slab_spans=2)  # 18/2=9m 板跨，120mm 板严重超筋
    _save_params(client, token, pid, structure=bad_structure)
    res = client.post(f"/api/projects/{pid}/calculate", json={"page": "slab"}, headers=_auth(token))
    assert res.status_code == 400
