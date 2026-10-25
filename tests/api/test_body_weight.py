"""CRUD: создать и получить, чужая запись 403, несуществующая 404, невалидное тело через parametrize"""
"""Body weight: CRUD + ownership."""
from httpx import AsyncClient


async def test_body_weight_crud_cycle(
    client: AsyncClient, make_user, auth_headers
):
    user = await make_user()
    h = auth_headers(user)

    # create
    r = await client.post(
        "/api/v1/body/weights",
        json={"weight": 70.5},
        headers=h,
    )
    assert r.status_code == 201, r.text
    wid = r.json()["id"]
    assert r.json()["weight"] == 70.5
    assert r.json()["user_id"] == user.id

    # get by id
    r = await client.get(f"/api/v1/body/weights/{wid}", headers=h)
    assert r.status_code == 200
    assert r.json()["weight"] == 70.5

    # list
    r = await client.get("/api/v1/body/weights", headers=h)
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 1
    assert any(x["id"] == wid for x in data["items"])

    # patch
    r = await client.patch(
        f"/api/v1/body/weights/{wid}",
        json={"weight": 71.2},
        headers=h,
    )
    assert r.status_code == 200
    assert r.json()["weight"] == 71.2

    # delete
    r = await client.delete(f"/api/v1/body/weights/{wid}", headers=h)
    assert r.status_code == 204

    # get after delete → 404
    r = await client.get(f"/api/v1/body/weights/{wid}", headers=h)
    assert r.status_code == 404


async def test_body_weight_ownership(
    client: AsyncClient, make_user, auth_headers
):
    """Чужой пользователь не может читать, менять, удалять."""
    user_a = await make_user()
    user_b = await make_user()

    r = await client.post(
        "/api/v1/body/weights",
        json={"weight": 70.5},
        headers=auth_headers(user_a),
    )
    wid = r.json()["id"]

    # чужой читает
    r = await client.get(f"/api/v1/body/weights/{wid}", headers=auth_headers(user_b))
    assert r.status_code in (403, 404)

    # чужой меняет
    r = await client.patch(
        f"/api/v1/body/weights/{wid}",
        json={"weight": 80.0},
        headers=auth_headers(user_b),
    )
    assert r.status_code in (403, 404)

    # чужой удаляет
    r = await client.delete(f"/api/v1/body/weights/{wid}", headers=auth_headers(user_b))
    assert r.status_code in (403, 404)

    # исходная запись цела
    r = await client.get(f"/api/v1/body/weights/{wid}", headers=auth_headers(user_a))
    assert r.status_code == 200
    assert r.json()["weight"] == 70.5


async def test_body_weight_rejects_invalid_weight(
    client: AsyncClient, make_user, auth_headers
):
    user = await make_user()
    r = await client.post(
        "/api/v1/body/weights",
        json={"weight": -1},
        headers=auth_headers(user),
    )
    assert r.status_code == 422




async def test_body_weight_list_empty(
    client: AsyncClient, make_user, auth_headers
):
    user = await make_user()
    r = await client.get("/api/v1/body/weights", headers=auth_headers(user))
    assert r.status_code == 200
    data = r.json()
    assert data["items"] == []
    assert data["total"] == 0
    assert data["skip"] == 0
    assert data["limit"] == 20


async def test_body_weight_pagination(
    client: AsyncClient, make_user, auth_headers
):
    user = await make_user()
    h = auth_headers(user)
    for w in (70.0, 71.0, 72.0, 73.0, 74.0):
        r = await client.post(
            "/api/v1/body/weights",
            json={"weight": w},
            headers=h,
        )
        assert r.status_code == 201

    r = await client.get(
        "/api/v1/body/weights", params={"skip": 1, "limit": 2}, headers=h
    )
    data = r.json()
    assert data["total"] == 5
    assert len(data["items"]) == 2
    assert data["skip"] == 1
    assert data["limit"] == 2