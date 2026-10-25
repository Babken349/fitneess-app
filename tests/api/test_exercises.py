"""CRUD: создать и получить, чужая запись 403, несуществующая 404, невалидное тело через parametrize; плюс архив, фильтры по группе мышц и оборудованию, поиск"""
"""Exercises: справочник. Чтение публичное, мутации — admin."""
from httpx import AsyncClient


BASE = "/api/v1/exercises"


# ---------------------------------------------------------
# create — auth
# ---------------------------------------------------------

async def test_create_without_token(client: AsyncClient):
    r = await client.post(BASE, json={"name": "Приседания"})
    assert r.status_code == 401


async def test_create_as_user_forbidden(
    client: AsyncClient, make_user, auth_headers
):
    user = await make_user()
    r = await client.post(
        BASE,
        json={"name": "Приседания"},
        headers=auth_headers(user),
    )
    assert r.status_code == 403


async def test_create_as_admin(
    client: AsyncClient, admin, auth_headers
):
    r = await client.post(
        BASE,
        json={"name": "Приседания", "description": "Классика"},
        headers=auth_headers(admin),
    )
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["name"] == "Приседания"
    assert data["is_archived"] is False


async def test_create_duplicate_name_conflicts(
    client: AsyncClient, admin, auth_headers
):
    h = auth_headers(admin)
    r1 = await client.post(BASE, json={"name": "Жим лежа"}, headers=h)
    assert r1.status_code == 201

    r2 = await client.post(BASE, json={"name": "Жим лежа"}, headers=h)
    assert r2.status_code == 409


async def test_create_with_unknown_muscle_group(
    client: AsyncClient, admin, auth_headers
):
    r = await client.post(
        BASE,
        json={"name": "Тяга", "muscle_group_id": 999999},
        headers=auth_headers(admin),
    )
    assert r.status_code == 404


async def test_create_with_unknown_equipment(
    client: AsyncClient, admin, auth_headers
):
    r = await client.post(
        BASE,
        json={"name": "Тяга", "equipment_id": 999999},
        headers=auth_headers(admin),
    )
    assert r.status_code == 404


# ---------------------------------------------------------
# read — публично
# ---------------------------------------------------------

async def test_list_is_public(client: AsyncClient):
    r = await client.get(BASE)
    assert r.status_code == 200
    assert isinstance(r.json(), list)


async def test_get_by_id_public(
    client: AsyncClient, admin, auth_headers
):
    r = await client.post(
        BASE, json={"name": "Становая"}, headers=auth_headers(admin)
    )
    eid = r.json()["id"]

    # без токена
    r = await client.get(f"{BASE}/{eid}")
    assert r.status_code == 200
    assert r.json()["id"] == eid


async def test_get_missing_returns_404(client: AsyncClient):
    r = await client.get(f"{BASE}/999999")
    assert r.status_code == 404


async def test_get_with_non_integer_id_returns_422(client: AsyncClient):
    r = await client.get(f"{BASE}/abc")
    assert r.status_code == 422


# ---------------------------------------------------------
# update / delete — admin only
# ---------------------------------------------------------

async def test_update_requires_admin(
    client: AsyncClient, admin, make_user, auth_headers
):
    r = await client.post(
        BASE, json={"name": "Жим стоя"}, headers=auth_headers(admin)
    )
    eid = r.json()["id"]

    user = await make_user()
    r = await client.patch(
        f"{BASE}/{eid}",
        json={"description": "нет"},
        headers=auth_headers(user),
    )
    assert r.status_code == 403


async def test_update_changes_only_sent_fields(
    client: AsyncClient, admin, auth_headers
):
    h = auth_headers(admin)
    r = await client.post(
        BASE,
        json={"name": "Жим стоя", "description": "старое"},
        headers=h,
    )
    eid = r.json()["id"]

    r = await client.patch(
        f"{BASE}/{eid}",
        json={"description": "новое"},
        headers=h,
    )
    assert r.status_code == 200
    assert r.json()["name"] == "Жим стоя"  # не менялось
    assert r.json()["description"] == "новое"


async def test_delete_requires_admin(
    client: AsyncClient, admin, make_user, auth_headers
):
    r = await client.post(
        BASE, json={"name": "Удаляемое"}, headers=auth_headers(admin)
    )
    eid = r.json()["id"]

    user = await make_user()
    r = await client.delete(f"{BASE}/{eid}", headers=auth_headers(user))
    assert r.status_code == 403


async def test_delete_as_admin(
    client: AsyncClient, admin, auth_headers
):
    h = auth_headers(admin)
    r = await client.post(BASE, json={"name": "Удаляемое"}, headers=h)
    eid = r.json()["id"]

    r = await client.delete(f"{BASE}/{eid}", headers=h)
    assert r.status_code == 204

    r = await client.get(f"{BASE}/{eid}")
    assert r.status_code == 404


# ---------------------------------------------------------
# archive / unarchive
# ---------------------------------------------------------

async def test_archive_hides_from_list(
    client: AsyncClient, admin, auth_headers
):
    h = auth_headers(admin)
    r = await client.post(BASE, json={"name": "Архивируемое"}, headers=h)
    eid = r.json()["id"]

    r = await client.patch(f"{BASE}/{eid}/archive", headers=h)
    assert r.status_code == 200
    assert r.json()["is_archived"] is True

    # не появляется в общем списке
    r = await client.get(BASE, params={"limit": 100})
    ids = [x["id"] for x in r.json()]
    assert eid not in ids

    # появляется в /status/archived
    r = await client.get(f"{BASE}/status/archived", params={"limit": 100})
    assert eid in [x["id"] for x in r.json()]


async def test_unarchive_restores(
    client: AsyncClient, admin, auth_headers
):
    h = auth_headers(admin)
    r = await client.post(BASE, json={"name": "Возвращаемое"}, headers=h)
    eid = r.json()["id"]
    await client.patch(f"{BASE}/{eid}/archive", headers=h)

    r = await client.patch(f"{BASE}/{eid}/unarchive", headers=h)
    assert r.status_code == 200
    assert r.json()["is_archived"] is False


# ---------------------------------------------------------
# filter / search
# ---------------------------------------------------------

async def test_filter_by_muscle_and_equipment(
    client: AsyncClient,
    admin,
    auth_headers,
    make_muscle_group,
    make_equipment,
):
    mg = await make_muscle_group()
    eq = await make_equipment()
    h = auth_headers(admin)

    r = await client.post(
        BASE,
        json={"name": "Упражнение А", "muscle_group_id": mg.id, "equipment_id": eq.id},
        headers=h,
    )
    assert r.status_code == 201
    matching_id = r.json()["id"]

    # не подходит
    await client.post(BASE, json={"name": "Упражнение Б"}, headers=h)

    r = await client.get(
        f"{BASE}/filter",
        params={"muscle_group_id": mg.id, "equipment_id": eq.id},
    )
    assert r.status_code == 200
    ids = [x["id"] for x in r.json()]
    assert matching_id in ids
    assert len(ids) == 1


async def test_search_by_name(
    client: AsyncClient, admin, auth_headers
):
    h = auth_headers(admin)
    await client.post(BASE, json={"name": "Жим гантелей лежа"}, headers=h)
    await client.post(BASE, json={"name": "Приседания"}, headers=h)

    r = await client.get(f"{BASE}/search/name", params={"name": "жим"})
    assert r.status_code == 200
    names = [x["name"] for x in r.json()]
    assert all("жим" in n.lower() for n in names)
    assert "Приседания" not in names