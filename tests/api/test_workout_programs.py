from httpx import AsyncClient


BASE = "/api/v1/workout-programs"


def _payload(**overrides):
    data = {"name": "Базовая", "description": "Описание"}
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
        json=_payload(name="Базовая", description="Для новичков"),
        headers=auth_headers(user),
    )
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["user_id"] == user.id
    assert data["name"] == "Базовая"
    assert data["description"] == "Для новичков"
    assert data["is_public"] is False
    assert data["is_archived"] is False


async def test_create_duplicate_name_same_user_409(
    client, make_user, auth_headers
):
    user = await make_user()
    h = auth_headers(user)
    r1 = await client.post(BASE, json=_payload(name="Пуш"), headers=h)
    assert r1.status_code == 201
    r2 = await client.post(BASE, json=_payload(name="Пуш"), headers=h)
    assert r2.status_code == 409


async def test_create_same_name_different_user_ok(
    client, make_user, auth_headers
):
    """UNIQUE(user_id, name) — не глобально."""
    user_a = await make_user()
    user_b = await make_user()
    r1 = await client.post(
        BASE, json=_payload(name="Пуш"), headers=auth_headers(user_a)
    )
    r2 = await client.post(
        BASE, json=_payload(name="Пуш"), headers=auth_headers(user_b)
    )
    assert r1.status_code == 201
    assert r2.status_code == 201


# ---------------------------------------------------------
# read /me (paginated)
# ---------------------------------------------------------

async def test_get_my_programs_requires_auth(client: AsyncClient):
    r = await client.get(f"{BASE}/me")
    assert r.status_code == 401


async def test_get_my_programs_empty(client, make_user, auth_headers):
    user = await make_user()
    r = await client.get(f"{BASE}/me", headers=auth_headers(user))
    assert r.status_code == 200
    data = r.json()
    assert data["items"] == []
    assert data["total"] == 0
    assert data["skip"] == 0
    assert data["limit"] == 20


async def test_get_my_programs_only_own(
    client, make_user, auth_headers
):
    user_a = await make_user()
    user_b = await make_user()
    await client.post(BASE, json=_payload(name="A"), headers=auth_headers(user_a))
    await client.post(BASE, json=_payload(name="B"), headers=auth_headers(user_b))
    r = await client.get(f"{BASE}/me", headers=auth_headers(user_a))
    data = r.json()
    assert data["total"] == 1
    assert data["items"][0]["user_id"] == user_a.id


async def test_get_my_programs_pagination(
    client, make_user, auth_headers
):
    user = await make_user()
    h = auth_headers(user)
    for i in range(5):
        await client.post(BASE, json=_payload(name=f"Программа {i}"), headers=h)
    r = await client.get(f"{BASE}/me?skip=1&limit=2", headers=h)
    data = r.json()
    assert data["total"] == 5
    assert len(data["items"]) == 2
    assert data["skip"] == 1
    assert data["limit"] == 2


# ---------------------------------------------------------
# read /public (paginated, no auth)
# ---------------------------------------------------------

async def test_get_public_programs_no_auth(client: AsyncClient):
    r = await client.get(f"{BASE}/public")
    assert r.status_code == 200


async def test_get_public_programs_only_public(
    client, make_user, auth_headers
):
    user = await make_user()
    h = auth_headers(user)
    # приватная — не должна попасть
    await client.post(BASE, json=_payload(name="Секрет"), headers=h)
    # публичная — должна
    await client.post(
        BASE, json=_payload(name="Открытая", is_public=True), headers=h
    )
    # публичная + архивная — не должна
    r = await client.post(
        BASE, json=_payload(name="Архив", is_public=True), headers=h
    )
    pid = r.json()["id"]
    await client.patch(f"{BASE}/{pid}/archive", headers=h)

    r = await client.get(f"{BASE}/public")
    data = r.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "Открытая"


async def test_get_public_programs_pagination(
    client, make_user, auth_headers
):
    user = await make_user()
    h = auth_headers(user)
    for i in range(4):
        await client.post(
            BASE,
            json=_payload(name=f"Public {i}", is_public=True),
            headers=h,
        )
    r = await client.get(f"{BASE}/public?skip=1&limit=2")
    data = r.json()
    assert data["total"] == 4
    assert len(data["items"]) == 2


# ---------------------------------------------------------
# read /me/{id} — ownership
# ---------------------------------------------------------

async def test_get_my_program_by_id(client, make_user, auth_headers):
    user = await make_user()
    h = auth_headers(user)
    r = await client.post(BASE, json=_payload(), headers=h)
    pid = r.json()["id"]
    r = await client.get(f"{BASE}/me/{pid}", headers=h)
    assert r.status_code == 200
    assert r.json()["id"] == pid


async def test_get_my_program_foreign_403(
    client, make_user, auth_headers
):
    user_a = await make_user()
    user_b = await make_user()
    r = await client.post(
        BASE, json=_payload(), headers=auth_headers(user_a)
    )
    pid = r.json()["id"]
    r = await client.get(f"{BASE}/me/{pid}", headers=auth_headers(user_b))
    assert r.status_code == 403


async def test_get_my_program_missing_404(
    client, make_user, auth_headers
):
    user = await make_user()
    r = await client.get(f"{BASE}/me/999999", headers=auth_headers(user))
    assert r.status_code == 404


# ---------------------------------------------------------
# read /{id} — accessible (own OR public)
# ---------------------------------------------------------

async def test_get_accessible_own_private(
    client, make_user, auth_headers
):
    user = await make_user()
    h = auth_headers(user)
    r = await client.post(BASE, json=_payload(is_public=False), headers=h)
    pid = r.json()["id"]
    r = await client.get(f"{BASE}/{pid}", headers=h)
    assert r.status_code == 200


async def test_get_accessible_foreign_public_ok(
    client, make_user, auth_headers
):
    user_a = await make_user()
    user_b = await make_user()
    r = await client.post(
        BASE, json=_payload(is_public=True), headers=auth_headers(user_a)
    )
    pid = r.json()["id"]
    r = await client.get(f"{BASE}/{pid}", headers=auth_headers(user_b))
    assert r.status_code == 200


async def test_get_accessible_foreign_private_403(
    client, make_user, auth_headers
):
    user_a = await make_user()
    user_b = await make_user()
    r = await client.post(
        BASE, json=_payload(is_public=False), headers=auth_headers(user_a)
    )
    pid = r.json()["id"]
    r = await client.get(f"{BASE}/{pid}", headers=auth_headers(user_b))
    assert r.status_code == 403


# ---------------------------------------------------------
# update
# ---------------------------------------------------------

async def test_update_only_sent_fields(
    client, make_user, auth_headers
):
    user = await make_user()
    h = auth_headers(user)
    r = await client.post(
        BASE,
        json=_payload(name="Старое", description="Старое описание"),
        headers=h,
    )
    pid = r.json()["id"]

    # меняем только description
    r = await client.patch(
        f"{BASE}/{pid}", json={"description": "Новое"}, headers=h
    )
    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "Старое"
    assert data["description"] == "Новое"
    assert data["is_public"] is False


async def test_update_foreign_403(client, make_user, auth_headers):
    user_a = await make_user()
    user_b = await make_user()
    r = await client.post(
        BASE, json=_payload(), headers=auth_headers(user_a)
    )
    pid = r.json()["id"]
    r = await client.patch(
        f"{BASE}/{pid}",
        json={"name": "Взлом"},
        headers=auth_headers(user_b),
    )
    assert r.status_code == 403


async def test_update_duplicate_name_409(
    client, make_user, auth_headers
):
    user = await make_user()
    h = auth_headers(user)
    await client.post(BASE, json=_payload(name="A"), headers=h)
    r = await client.post(BASE, json=_payload(name="B"), headers=h)
    pid = r.json()["id"]
    r = await client.patch(f"{BASE}/{pid}", json={"name": "A"}, headers=h)
    assert r.status_code == 409


# ---------------------------------------------------------
# archive / unarchive
# ---------------------------------------------------------

async def test_archive_then_unarchive(
    client, make_user, auth_headers
):
    user = await make_user()
    h = auth_headers(user)
    r = await client.post(BASE, json=_payload(), headers=h)
    pid = r.json()["id"]

    r = await client.patch(f"{BASE}/{pid}/archive", headers=h)
    assert r.status_code == 200
    assert r.json()["is_archived"] is True

    r = await client.patch(f"{BASE}/{pid}/unarchive", headers=h)
    assert r.status_code == 200
    assert r.json()["is_archived"] is False


async def test_archive_twice_400(client, make_user, auth_headers):
    user = await make_user()
    h = auth_headers(user)
    r = await client.post(BASE, json=_payload(), headers=h)
    pid = r.json()["id"]
    await client.patch(f"{BASE}/{pid}/archive", headers=h)
    r = await client.patch(f"{BASE}/{pid}/archive", headers=h)
    assert r.status_code == 400


async def test_archive_foreign_403(client, make_user, auth_headers):
    user_a = await make_user()
    user_b = await make_user()
    r = await client.post(
        BASE, json=_payload(), headers=auth_headers(user_a)
    )
    pid = r.json()["id"]
    r = await client.patch(
        f"{BASE}/{pid}/archive", headers=auth_headers(user_b)
    )
    assert r.status_code == 403


# ---------------------------------------------------------
# public / private
# ---------------------------------------------------------

async def test_make_public_then_private(
    client, make_user, auth_headers
):
    user = await make_user()
    h = auth_headers(user)
    r = await client.post(BASE, json=_payload(), headers=h)
    pid = r.json()["id"]

    r = await client.patch(f"{BASE}/{pid}/public", headers=h)
    assert r.status_code == 200
    assert r.json()["is_public"] is True

    r = await client.patch(f"{BASE}/{pid}/private", headers=h)
    assert r.status_code == 200
    assert r.json()["is_public"] is False


async def test_make_public_foreign_403(
    client, make_user, auth_headers
):
    user_a = await make_user()
    user_b = await make_user()
    r = await client.post(
        BASE, json=_payload(), headers=auth_headers(user_a)
    )
    pid = r.json()["id"]
    r = await client.patch(
        f"{BASE}/{pid}/public", headers=auth_headers(user_b)
    )
    assert r.status_code == 403


# ---------------------------------------------------------
# delete
# ---------------------------------------------------------

async def test_delete_own(client, make_user, auth_headers):
    user = await make_user()
    h = auth_headers(user)
    r = await client.post(BASE, json=_payload(), headers=h)
    pid = r.json()["id"]
    r = await client.delete(f"{BASE}/{pid}", headers=h)
    assert r.status_code == 204
    r = await client.get(f"{BASE}/me/{pid}", headers=h)
    assert r.status_code == 404


async def test_delete_foreign_403(client, make_user, auth_headers):
    user_a = await make_user()
    user_b = await make_user()
    r = await client.post(
        BASE, json=_payload(), headers=auth_headers(user_a)
    )
    pid = r.json()["id"]
    r = await client.delete(
        f"{BASE}/{pid}", headers=auth_headers(user_b)
    )
    assert r.status_code == 403


# ---------------------------------------------------------
# search — только свои и публичные, не архивные
# ---------------------------------------------------------

async def test_search_finds_own_and_public(
    client, make_user, auth_headers
):
    user_a = await make_user()
    user_b = await make_user()
    h_a = auth_headers(user_a)
    h_b = auth_headers(user_b)

    await client.post(
        BASE, json=_payload(name="Своя private"), headers=h_a
    )
    await client.post(
        BASE,
        json=_payload(name="Чужая public", is_public=True),
        headers=h_b,
    )
    await client.post(
        BASE, json=_payload(name="Чужая private"), headers=h_b
    )

    # "я" есть в именах всех трёх — фильтр только по приватности
    r = await client.get(f"{BASE}/search?name=я", headers=h_a)
    names = sorted(x["name"] for x in r.json())
    assert "Своя private" in names
    assert "Чужая public" in names
    assert "Чужая private" not in names


async def test_search_excludes_archived(
    client, make_user, auth_headers
):
    user = await make_user()
    h = auth_headers(user)
    r = await client.post(
        BASE, json=_payload(name="Архивная"), headers=h
    )
    pid = r.json()["id"]
    await client.patch(f"{BASE}/{pid}/archive", headers=h)

    r = await client.get(f"{BASE}/search?name=я", headers=h)
    names = [x["name"] for x in r.json()]
    assert "Архивная" not in names


# ---------------------------------------------------------
# /me/active и /me/archived
# ---------------------------------------------------------

async def test_get_active_excludes_archived(
    client, make_user, auth_headers
):
    user = await make_user()
    h = auth_headers(user)
    await client.post(BASE, json=_payload(name="Активная"), headers=h)
    r = await client.post(BASE, json=_payload(name="Архивная"), headers=h)
    pid = r.json()["id"]
    await client.patch(f"{BASE}/{pid}/archive", headers=h)

    r = await client.get(f"{BASE}/me/active", headers=h)
    names = [x["name"] for x in r.json()]
    assert names == ["Активная"]


async def test_get_archived_only_archived(
    client, make_user, auth_headers
):
    user = await make_user()
    h = auth_headers(user)
    await client.post(BASE, json=_payload(name="Активная"), headers=h)
    r = await client.post(BASE, json=_payload(name="Архивная"), headers=h)
    pid = r.json()["id"]
    await client.patch(f"{BASE}/{pid}/archive", headers=h)

    r = await client.get(f"{BASE}/me/archived", headers=h)
    names = [x["name"] for x in r.json()]
    assert names == ["Архивная"]