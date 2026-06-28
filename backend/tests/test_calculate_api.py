"""/calculate 板（门禁 + 超筋处理）与 /checks 板。"""

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


MATERIALS = {"fc": 9.6, "fy_slab": 270, "fy_beam": 300, "gamma_d": 1.2}

SLAB_INPUT = {
    "length": 6.0, "width": 6.0, "thickness": 80, "support_width": 200, "spans": 3,
    "reinforced_concrete_weight": 25.0, "terrazzo_surface": 0.65,
    "plaster_thickness": 20, "plaster_weight": 17.0, "live_load": 2.0,
}


def _save_slab_input(client, token, pid):
    client.patch(
        f"/api/projects/{pid}",
        json={"data": {"materials": MATERIALS, "slab": {"input": SLAB_INPUT}}},
        headers=_auth(token),
    )


def test_calculate_slab_success(client, token):
    pid = _project(client, token)
    _save_slab_input(client, token, pid)

    res = client.post(f"/api/projects/{pid}/calculate", json={"page": "slab"}, headers=_auth(token))
    assert res.status_code == 200
    body = res.json()
    assert body["load"]["dead_load_standard"] == pytest.approx(2.99, abs=0.01)
    assert len(body["reinforcement"]["sections"]) == 5  # 3 跨 → 5 截面


def test_calculate_gating_missing_materials(client, token):
    pid = _project(client, token)
    client.patch(
        f"/api/projects/{pid}",
        json={"data": {"slab": {"input": SLAB_INPUT}}},
        headers=_auth(token),
    )
    res = client.post(f"/api/projects/{pid}/calculate", json={"page": "slab"}, headers=_auth(token))
    assert res.status_code == 400
    missing = res.json()["detail"]["missing"]
    assert "fc" in missing and "fy_slab" in missing


def test_calculate_gating_missing_slab_input(client, token):
    pid = _project(client, token)
    client.patch(
        f"/api/projects/{pid}",
        json={"data": {"materials": MATERIALS, "slab": {"input": {"length": 6.0}}}},
        headers=_auth(token),
    )
    res = client.post(f"/api/projects/{pid}/calculate", json={"page": "slab"}, headers=_auth(token))
    assert res.status_code == 400
    missing = res.json()["detail"]["missing"]
    assert "thickness" in missing and "live_load" in missing


def test_calculate_overreinforcement_returns_400(client, token):
    """超大跨度/超薄板 → αs>0.5 超筋 → 端点返 400，不 500。"""
    pid = _project(client, token)
    bad = dict(SLAB_INPUT, length=30.0)  # 30m/3跨=10m l0，80mm 板严重超筋
    client.patch(
        f"/api/projects/{pid}",
        json={"data": {"materials": MATERIALS, "slab": {"input": bad}}},
        headers=_auth(token),
    )
    res = client.post(f"/api/projects/{pid}/calculate", json={"page": "slab"}, headers=_auth(token))
    assert res.status_code == 400


def test_calculate_beam_page_not_implemented(client, token):
    pid = _project(client, token)
    res = client.post(f"/api/projects/{pid}/calculate", json={"page": "beam"}, headers=_auth(token))
    assert res.status_code == 501


def test_checks_endpoint_after_calculate(client, token):
    pid = _project(client, token)
    _save_slab_input(client, token, pid)
    client.post(f"/api/projects/{pid}/calculate", json={"page": "slab"}, headers=_auth(token))

    res = client.get(f"/api/projects/{pid}/checks", headers=_auth(token))
    assert res.status_code == 200
    body = res.json()
    assert "slab" in body
    assert len(body["slab"]) > 0
    names = [i["name"] for i in body["slab"]]
    assert any("ξ" in n for n in names)


def test_checks_empty_before_calculate(client, token):
    pid = _project(client, token)
    res = client.get(f"/api/projects/{pid}/checks", headers=_auth(token))
    assert res.status_code == 200
    assert res.json()["slab"] == []
