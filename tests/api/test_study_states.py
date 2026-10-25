"""CRUD: создать и получить, чужая запись 403, несуществующая 404, невалидное тело через parametrize"""
"""Study states: create, get, list, delete, ownership, валидация 1..10."""
from httpx import AsyncClient


BASE = "/api/v1/study-states"


def _payload(**overrides):
    data = {
        "concentration": 3,
        "energy": 4,
        "fatigue": 5,
        "motivation": 6,
    }
    data.update(overrides)
    return data


# ---------------------------------------------------------
# create
# ---------------------------------------------------------

async def test_create_requires_auth(client: AsyncClient):
    r = await client.post(BASE, json=_payload())
    assert r.status_code == 401


async def test_create_success(client: AsyncClient, make_user, auth_headers):
    user = await make_user()
    r = await client.post(
        BASE,
        json=_payload(notes="после обеда"),
        headers=auth_headers(user),
    )
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["user_id"] == user.id
    assert data["concentration"] == 3
    assert data["energy"] == 4
    assert data["fatigue"] == 5
    assert data["motivation"] == 6
    assert data["notes"] == "после обеда"
    assert "recorded_at" in data


async def test_create_missing_required_fields(
    client: AsyncClient, make_user, auth_headers
):
    user = await make_user()
    r = await client.post(
        BASE,
        json={"concentration": 3},
        headers=auth_headers(user),
    )
    assert r.status_code == 422


async def test_create_notes_nullable(
    client: AsyncClient, make_user, auth_headers
):
    user = await make_user()
    r = await client.post(
        BASE,
        json=_payload(notes=None),
        headers=auth_headers(user),
    )
    assert r.status_code == 201
    assert r.json()["notes"] is None


async def test_create_notes_too_long_422(
    client: AsyncClient, make_user, auth_headers
):
    user = await make_user()
    r = await client.post(
        BASE,
        json=_payload(notes="a" * 1001),
        headers=auth_headers(user),
    )
    assert r.status_code == 422


async def test_create_concentration_out_of_range_422(
    client: AsyncClient, make_user, auth_headers
):
    """ge=1, le=10."""
    user = await make_user()
    for bad in (0, 11, -1, 100):
        r = await client.post(
            BASE,
            json=_payload(concentration=bad),
            headers=auth_headers(user),
        )
        assert r.status_code == 422, f"concentration={bad} should be 422"


async def test_create_boundary_values_ok(
    client: AsyncClient, make_user, auth_headers
):
    """1 и 10 — валидные границы."""
    user = await make_user()
    h = auth_headers(user)
    for v in (1, 10):
        r = await client.post(
            BASE,
            json={
                "concentration": v,
                "energy": v,
                "fatigue": v,
                "motivation": v,
            },
            headers=h,
        )
        assert r.status_code == 201, r.text


# ---------------------------------------------------------
# read
# ---------------------------------------------------------

async def test_get_by_id(client: AsyncClient, make_user, auth_headers):
    user = await make_user()
    h = auth_headers(user)

    r = await client.post(BASE, json=_payload(), headers=h)
    sid = r.json()["id"]

    r = await client.get(f"{BASE}/{sid}", headers=h)
    assert r.status_code == 200
    assert r.json()["id"] == sid


async def test_get_missing_returns_404(
    client: AsyncClient, make_user, auth_headers
):
    user = await make_user()
    r = await client.get(f"{BASE}/999999", headers=auth_headers(user))
    assert r.status_code == 404


async def test_get_foreign_forbidden(
    client: AsyncClient, make_user, auth_headers
):
    user_a = await make_user()
    user_b = await make_user()

    r = await client.post(BASE, json=_payload(), headers=auth_headers(user_a))
    sid = r.json()["id"]

    r = await client.get(f"{BASE}/{sid}", headers=auth_headers(user_b))
    assert r.status_code == 403


# ---------------------------------------------------------
# list
# ---------------------------------------------------------

async def test_list_empty(client: AsyncClient, make_user, auth_headers):
    user = await make_user()
    r = await client.get(BASE, headers=auth_headers(user))
    assert r.status_code == 200
    assert r.json() == []


async def test_list_returns_only_own(
    client: AsyncClient, make_user, auth_headers
):
    user_a = await make_user()
    user_b = await make_user()

    for _ in range(2):
        await client.post(BASE, json=_payload(), headers=auth_headers(user_a))
    await client.post(BASE, json=_payload(), headers=auth_headers(user_b))

    r = await client.get(BASE, headers=auth_headers(user_a))
    assert r.status_code == 200
    rows = r.json()
    assert len(rows) == 2
    assert all(x["user_id"] == user_a.id for x in rows)


async def test_list_skip_limit(
    client: AsyncClient, make_user, auth_headers
):
    user = await make_user()
    h = auth_headers(user)
    for _ in range(3):
        await client.post(BASE, json=_payload(), headers=h)

    r = await client.get(BASE, params={"skip": 1, "limit": 1}, headers=h)
    assert r.status_code == 200
    assert len(r.json()) == 1


async def test_list_negative_skip_422(
    client: AsyncClient, make_user, auth_headers
):
    user = await make_user()
    r = await client.get(
        BASE, params={"skip": -1}, headers=auth_headers(user)
    )
    assert r.status_code == 422


async def test_list_limit_over_100_422(
    client: AsyncClient, make_user, auth_headers
):
    user = await make_user()
    r = await client.get(
        BASE, params={"limit": 101}, headers=auth_headers(user)
    )
    assert r.status_code == 422


# ---------------------------------------------------------
# delete
# ---------------------------------------------------------

async def test_delete(client: AsyncClient, make_user, auth_headers):
    user = await make_user()
    h = auth_headers(user)

    r = await client.post(BASE, json=_payload(), headers=h)
    sid = r.json()["id"]

    r = await client.delete(f"{BASE}/{sid}", headers=h)
    assert r.status_code == 204

    r = await client.get(f"{BASE}/{sid}", headers=h)
    assert r.status_code == 404


async def test_delete_missing_returns_404(
    client: AsyncClient, make_user, auth_headers
):
    user = await make_user()
    r = await client.delete(f"{BASE}/999999", headers=auth_headers(user))
    assert r.status_code == 404


async def test_delete_foreign_forbidden(
    client: AsyncClient, make_user, auth_headers
):
    user_a = await make_user()
    user_b = await make_user()

    r = await client.post(BASE, json=_payload(), headers=auth_headers(user_a))
    sid = r.json()["id"]

    r = await client.delete(f"{BASE}/{sid}", headers=auth_headers(user_b))
    assert r.status_code == 403

    # исходная цела
    r = await client.get(f"{BASE}/{sid}", headers=auth_headers(user_a))
    assert r.status_code == 200
    
# ---------------------------------------------------------
# subject + duration_minutes (после расширения модели)
# ---------------------------------------------------------

async def test_create_with_subject_and_duration(
    client: AsyncClient, make_user, auth_headers
):
    user = await make_user()
    r = await client.post(
        BASE,
        json=_payload(subject="Математика", duration_minutes=45),
        headers=auth_headers(user),
    )
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["subject"] == "Математика"
    assert data["duration_minutes"] == 45


async def test_create_subject_defaults_to_empty(
    client: AsyncClient, make_user, auth_headers
):
    """Если subject не передан — server_default=''."""
    user = await make_user()
    r = await client.post(
        BASE, json=_payload(), headers=auth_headers(user)
    )
    assert r.status_code == 201
    data = r.json()
    assert data["subject"] == ""
    assert data["duration_minutes"] is None


async def test_create_duration_zero_422(
    client: AsyncClient, make_user, auth_headers
):
    """ge=1."""
    user = await make_user()
    r = await client.post(
        BASE,
        json=_payload(duration_minutes=0),
        headers=auth_headers(user),
    )
    assert r.status_code == 422


async def test_create_duration_over_720_422(
    client: AsyncClient, make_user, auth_headers
):
    """le=720."""
    user = await make_user()
    r = await client.post(
        BASE,
        json=_payload(duration_minutes=721),
        headers=auth_headers(user),
    )
    assert r.status_code == 422


async def test_create_duration_boundary_ok(
    client: AsyncClient, make_user, auth_headers
):
    """1 и 720 — валидные границы."""
    user = await make_user()
    h = auth_headers(user)
    for v in (1, 720):
        r = await client.post(
            BASE,
            json=_payload(duration_minutes=v),
            headers=h,
        )
        assert r.status_code == 201, r.text
        assert r.json()["duration_minutes"] == v