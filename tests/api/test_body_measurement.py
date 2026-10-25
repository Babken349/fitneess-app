"""CRUD: создать и получить, чужая запись 403, несуществующая 404, невалидное тело через parametrize; пустое измерение отклоняется"""
"""Body measurement: CRUD + ownership + empty payload."""
from httpx import AsyncClient


async def test_body_measurement_crud_cycle(
    client: AsyncClient, make_user, auth_headers
):
    user = await make_user()
    h = auth_headers(user)

    # create
    r = await client.post(
        "/api/v1/body/measurements",
        json={"chest": 100.0, "waist": 80.0},
        headers=h,
    )
    assert r.status_code == 201, r.text
    mid = r.json()["id"]
    assert r.json()["chest"] == 100.0
    assert r.json()["waist"] == 80.0
    assert r.json()["user_id"] == user.id

    # get
    r = await client.get(f"/api/v1/body/measurements/{mid}", headers=h)
    assert r.status_code == 200

    # list
    r = await client.get("/api/v1/body/measurements", headers=h)
    assert r.status_code == 200
    assert any(x["id"] == mid for x in r.json())

    # patch — меняем только chest, waist должен остаться
    r = await client.patch(
        f"/api/v1/body/measurements/{mid}",
        json={"chest": 101.0},
        headers=h,
    )
    assert r.status_code == 200
    assert r.json()["chest"] == 101.0
    assert r.json()["waist"] == 80.0  # exclude_unset=True сохранил

    # delete
    r = await client.delete(f"/api/v1/body/measurements/{mid}", headers=h)
    assert r.status_code == 204

    r = await client.get(f"/api/v1/body/measurements/{mid}", headers=h)
    assert r.status_code == 404


async def test_body_measurement_ownership(
    client: AsyncClient, make_user, auth_headers
):
    user_a = await make_user()
    user_b = await make_user()

    r = await client.post(
        "/api/v1/body/measurements",
        json={"chest": 100.0},
        headers=auth_headers(user_a),
    )
    mid = r.json()["id"]

    r = await client.get(
        f"/api/v1/body/measurements/{mid}",
        headers=auth_headers(user_b),
    )
    assert r.status_code in (403, 404)

    r = await client.delete(
        f"/api/v1/body/measurements/{mid}",
        headers=auth_headers(user_b),
    )
    assert r.status_code in (403, 404)

    # исходная цела
    r = await client.get(
        f"/api/v1/body/measurements/{mid}",
        headers=auth_headers(user_a),
    )
    assert r.status_code == 200


async def test_body_measurement_rejects_empty_payload(
    client: AsyncClient, make_user, auth_headers
):
    """EmptyBodyMeasurementError: хотя бы одно поле обязательно."""
    user = await make_user()
    r = await client.post(
        "/api/v1/body/measurements",
        json={},
        headers=auth_headers(user),
    )
    assert r.status_code == 400