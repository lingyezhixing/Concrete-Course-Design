"""快照端点测试：归档、恢复、fork、隔离。"""


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def _make_project(client, token, name="p1"):
    return client.post("/api/projects", json={"name": name}, headers=_auth(token)).json()["id"]


def test_archive_creates_snapshot(client, alice_token):
    pid = _make_project(client, alice_token)
    client.patch(f"/api/projects/{pid}", json={"data": {"v": 1}}, headers=_auth(alice_token))

    res = client.post(f"/api/projects/{pid}/snapshots", json={"name": "s1"}, headers=_auth(alice_token))
    assert res.status_code == 201
    snap = res.json()
    assert snap["name"] == "s1"
    assert snap["data"] == {"v": 1}

    lst = client.get(f"/api/projects/{pid}/snapshots", headers=_auth(alice_token))
    assert len(lst.json()) == 1


def test_has_uncommitted_false_after_archive(client, alice_token):
    pid = _make_project(client, alice_token)
    client.patch(f"/api/projects/{pid}", json={"data": {"v": 1}}, headers=_auth(alice_token))
    client.post(f"/api/projects/{pid}/snapshots", json={"name": "s1"}, headers=_auth(alice_token))

    got = client.get(f"/api/projects/{pid}", headers=_auth(alice_token)).json()
    assert got["has_uncommitted"] is False  # 归档后无新改动


def test_restore_overwrites_working_state(client, alice_token):
    pid = _make_project(client, alice_token)
    client.patch(f"/api/projects/{pid}", json={"data": {"v": 1}}, headers=_auth(alice_token))
    sid = client.post(f"/api/projects/{pid}/snapshots", json={"name": "s1"}, headers=_auth(alice_token)).json()["id"]
    client.patch(f"/api/projects/{pid}", json={"data": {"v": 2}}, headers=_auth(alice_token))

    res = client.post(f"/api/projects/{pid}/snapshots/{sid}/restore", headers=_auth(alice_token))
    assert res.status_code == 200
    assert res.json()["data"] == {"v": 1}


def test_fork_creates_new_project(client, alice_token):
    pid = _make_project(client, alice_token)
    client.patch(f"/api/projects/{pid}", json={"data": {"v": 1}}, headers=_auth(alice_token))
    sid = client.post(f"/api/projects/{pid}/snapshots", json={"name": "s1"}, headers=_auth(alice_token)).json()["id"]

    res = client.post(
        f"/api/projects/{pid}/snapshots/{sid}/fork", json={"name": "fork-1"}, headers=_auth(alice_token)
    )
    assert res.status_code == 201
    forked = res.json()
    assert forked["id"] != pid
    assert forked["name"] == "fork-1"
    assert forked["data"] == {"v": 1}


def test_snapshot_isolation(client, alice_token, bob_token):
    pid = _make_project(client, alice_token)
    sid = client.post(f"/api/projects/{pid}/snapshots", json={"name": "s1"}, headers=_auth(alice_token)).json()["id"]

    # bob 对 alice 的项目/快照一律 404
    assert client.get(f"/api/projects/{pid}/snapshots", headers=_auth(bob_token)).status_code == 404
    assert client.post(f"/api/projects/{pid}/snapshots/{sid}/restore", headers=_auth(bob_token)).status_code == 404
    assert client.delete(f"/api/snapshots/{sid}", headers=_auth(bob_token)).status_code == 404


def test_delete_snapshot(client, alice_token):
    pid = _make_project(client, alice_token)
    sid = client.post(f"/api/projects/{pid}/snapshots", json={"name": "s1"}, headers=_auth(alice_token)).json()["id"]
    assert client.delete(f"/api/snapshots/{sid}", headers=_auth(alice_token)).status_code == 204
    lst = client.get(f"/api/projects/{pid}/snapshots", headers=_auth(alice_token))
    assert len(lst.json()) == 0
