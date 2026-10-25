"""CRUD: создать и получить, чужая запись 403, несуществующая 404, невалидное тело через parametrize; дубль кода и имени 409, деактивация"""
import pytest
from sqlalchemy import func, select

from app.models.achievement import Achievement

pytestmark = pytest.mark.integration
from app.main import app
BASE = "/api/v1/achievements"
COLLECTION = f"{BASE}/"   # маршруты объявлены как "/", слэш обязателен
NO_AUTH = (401, 403)      # код зависит от версии FastAPI (HTTPBearer)
VALID = {"name": "Первая тренировка", "code": "first_workout"}


def item_url(achievement_id: int) -> str:
    return f"{BASE}/{achievement_id}"


async def count_by_code(session, code: str) -> int:
    return await session.scalar(
        select(func.count()).select_from(Achievement).where(Achievement.code == code)
    )


# ---------------------------------------------------------------- чтение

async def test_list_is_public_and_empty_by_default(client):
    r = await client.get(COLLECTION)

    assert r.status_code == 200
    assert r.json() == []


async def test_list_returns_only_active(client, make_achievement):
    active = await make_achievement()
    await make_achievement(is_active=False)

    r = await client.get(COLLECTION)

    assert r.status_code == 200
    assert [a["id"] for a in r.json()] == [active.id]


async def test_list_pagination(client, make_achievement):
    for _ in range(3):
        await make_achievement()

    first = (await client.get(COLLECTION, params={"limit": 2})).json()
    second = (await client.get(COLLECTION, params={"skip": 2, "limit": 2})).json()

    assert len(first) == 2
    assert len(second) == 1
    assert len({a["id"] for a in first + second}) == 3   # страницы не пересекаются


@pytest.mark.parametrize(
    "params",
    [
        pytest.param({"skip": -1}, id="negative-skip"),
        pytest.param({"limit": 0}, id="zero-limit"),
        pytest.param({"limit": 101}, id="huge-limit"),
    ],
)
async def test_list_rejects_invalid_pagination(client, params):
    r = await client.get(COLLECTION, params=params)

    assert r.status_code == 422


async def test_get_by_id_returns_achievement(client, make_achievement):
    achievement = await make_achievement(
        description="Первая тренировка",
        icon_url="https://cdn.example.com/a.png",
    )

    r = await client.get(item_url(achievement.id))

    assert r.status_code == 200
    body = r.json()
    assert body["id"] == achievement.id
    assert body["name"] == achievement.name
    assert body["code"] == achievement.code
    assert body["description"] == "Первая тренировка"
    assert body["icon_url"] == "https://cdn.example.com/a.png"
    assert body["is_active"] is True
    assert "created_at" in body


async def test_get_missing_returns_404(client):
    r = await client.get(item_url(999_999))

    assert r.status_code == 404


async def test_get_with_non_integer_id_returns_422(client):
    r = await client.get(f"{BASE}/abc")

    assert r.status_code == 422


# -------------------------------------------------------------- создание

@pytest.mark.critical
async def test_create_as_admin(client, admin, auth_headers, session):
    payload = {
        "name": "Первая тренировка",
        "code": "first_workout",
        "description": "Завершите первую тренировку",
        "icon_url": "https://cdn.example.com/first.png",
    }

    r = await client.post(COLLECTION, json=payload, headers=auth_headers(admin))

    assert r.status_code == 201
    body = r.json()
    assert body["id"] > 0
    for key, value in payload.items():
        assert body[key] == value
    assert body["is_active"] is True
    assert "created_at" in body
    assert await count_by_code(session, "first_workout") == 1


@pytest.mark.critical
async def test_create_requires_admin(client, make_user, auth_headers, session):
    regular = await make_user()

    r = await client.post(COLLECTION, json=VALID, headers=auth_headers(regular))

    assert r.status_code == 403
    assert await count_by_code(session, VALID["code"]) == 0


@pytest.mark.critical
async def test_create_without_token(client):
    r = await client.post(COLLECTION, json=VALID)

    assert r.status_code in NO_AUTH


@pytest.mark.critical
async def test_create_with_garbage_token(client):
    r = await client.post(
        COLLECTION, json=VALID, headers={"Authorization": "Bearer not-a-jwt"}
    )

    assert r.status_code == 401


async def test_create_duplicate_code_conflicts(
    client, admin, auth_headers, make_achievement, session
):
    await make_achievement(code="streak_7")

    r = await client.post(
        COLLECTION,
        json={"name": "Другое имя", "code": "streak_7"},
        headers=auth_headers(admin),
    )

    assert r.status_code == 409
    assert "streak_7" in r.json()["detail"]
    assert await count_by_code(session, "streak_7") == 1


async def test_create_duplicate_name_conflicts(
    client, admin, auth_headers, make_achievement, session
):
    await make_achievement(name="Марафонец")

    r = await client.post(
        COLLECTION,
        json={"name": "Марафонец", "code": "marathon"},
        headers=auth_headers(admin),
    )

    assert r.status_code == 409
    assert "Марафонец" in r.json()["detail"]
    assert await count_by_code(session, "marathon") == 0


@pytest.mark.parametrize(
    "payload",
    [
        pytest.param({"code": "x"}, id="no-name"),
        pytest.param({"name": "X"}, id="no-code"),
        pytest.param({"name": "", "code": "x"}, id="empty-name"),
        pytest.param({"name": "   ", "code": "x"}, id="blank-name"),
        pytest.param({"name": "X", "code": ""}, id="empty-code"),
        pytest.param({"name": "n" * 101, "code": "x"}, id="name-too-long"),
        pytest.param({"name": "X", "code": "c" * 101}, id="code-too-long"),
        pytest.param(
            {"name": "X", "code": "x", "description": "d" * 501},
            id="description-too-long",
        ),
        pytest.param({"name": 123, "code": "x"}, id="name-wrong-type"),
    ],
)
async def test_create_rejects_invalid_body(client, admin, auth_headers, payload):
    r = await client.post(COLLECTION, json=payload, headers=auth_headers(admin))

    assert r.status_code == 422


async def test_create_trims_whitespace(client, admin, auth_headers):
    r = await client.post(
        COLLECTION,
        json={"name": "  Бегун  ", "code": "  runner  "},
        headers=auth_headers(admin),
    )

    assert r.status_code == 201
    assert r.json()["name"] == "Бегун"
    assert r.json()["code"] == "runner"


@pytest.mark.parametrize(
    "icon_url",
    [
        pytest.param("https://e.com/" + "a" * 500, id="too-long"),
        pytest.param("javascript:alert(1)", id="js-scheme"),
        pytest.param("не ссылка", id="not-a-url"),
    ],
)
async def test_create_rejects_bad_icon_url(client, admin, auth_headers, icon_url):
    payload = {"name": "X", "code": "x", "icon_url": icon_url}

    r = await client.post(COLLECTION, json=payload, headers=auth_headers(admin))

    assert r.status_code == 422


# ----------------------------------------------------------- обновление

async def test_update_changes_only_sent_fields(
    client, admin, auth_headers, make_achievement
):
    achievement = await make_achievement(
        name="Старое", code="old_code", description="Описание"
    )

    r = await client.patch(
        item_url(achievement.id), json={"name": "Новое"}, headers=auth_headers(admin)
    )

    assert r.status_code == 200
    body = r.json()
    assert body["name"] == "Новое"
    assert body["code"] == "old_code"
    assert body["description"] == "Описание"


async def test_update_can_clear_description(
    client, admin, auth_headers, make_achievement
):
    achievement = await make_achievement(description="Описание")

    r = await client.patch(
        item_url(achievement.id),
        json={"description": None},
        headers=auth_headers(admin),
    )

    assert r.status_code == 200
    assert r.json()["description"] is None


@pytest.mark.critical
async def test_update_requires_admin(client, make_user, auth_headers, make_achievement):
    achievement = await make_achievement(name="Имя")
    regular = await make_user()

    r = await client.patch(
        item_url(achievement.id), json={"name": "Взлом"}, headers=auth_headers(regular)
    )

    assert r.status_code == 403
    assert (await client.get(item_url(achievement.id))).json()["name"] == "Имя"


@pytest.mark.critical
async def test_update_without_token(client, make_achievement):
    achievement = await make_achievement()

    r = await client.patch(item_url(achievement.id), json={"name": "X"})

    assert r.status_code in NO_AUTH


async def test_update_missing_returns_404(client, admin, auth_headers):
    r = await client.patch(
        item_url(999_999), json={"name": "X"}, headers=auth_headers(admin)
    )

    assert r.status_code == 404


async def test_update_code_conflicts_with_other(
    client, admin, auth_headers, make_achievement
):
    await make_achievement(code="taken")
    target = await make_achievement(code="mine")

    r = await client.patch(
        item_url(target.id), json={"code": "taken"}, headers=auth_headers(admin)
    )

    assert r.status_code == 409


async def test_update_name_conflicts_with_other(
    client, admin, auth_headers, make_achievement
):
    await make_achievement(name="Занято")
    target = await make_achievement(name="Моё")

    r = await client.patch(
        item_url(target.id), json={"name": "Занято"}, headers=auth_headers(admin)
    )

    assert r.status_code == 409


async def test_update_with_own_values_is_ok(
    client, admin, auth_headers, make_achievement
):
    target = await make_achievement(name="Имя", code="code_a")

    r = await client.patch(
        item_url(target.id),
        json={"name": "Имя", "code": "code_a"},
        headers=auth_headers(admin),
    )

    assert r.status_code == 200


async def test_update_can_reactivate(client, admin, auth_headers, make_achievement):
    target = await make_achievement(is_active=False)

    r = await client.patch(
        item_url(target.id), json={"is_active": True}, headers=auth_headers(admin)
    )

    assert r.status_code == 200
    assert r.json()["is_active"] is True
    listing = (await client.get(COLLECTION)).json()
    assert [a["id"] for a in listing] == [target.id]


@pytest.mark.parametrize(
    "payload",
    [
        pytest.param({"name": ""}, id="empty-name"),
        pytest.param({"name": "n" * 101}, id="name-too-long"),
        pytest.param({"code": "c" * 101}, id="code-too-long"),
        pytest.param({"description": "d" * 501}, id="description-too-long"),
    ],
)
async def test_update_rejects_invalid_body(
    client, admin, auth_headers, make_achievement, payload
):
    target = await make_achievement()

    r = await client.patch(
        item_url(target.id), json=payload, headers=auth_headers(admin)
    )

    assert r.status_code == 422


@pytest.mark.parametrize("field", ["name", "code", "is_active"])
async def test_update_rejects_null_for_required_fields(
    client, admin, auth_headers, make_achievement, field
):
    target = await make_achievement()

    r = await client.patch(
        item_url(target.id), json={field: None}, headers=auth_headers(admin)
    )

    assert r.status_code == 422


# ---------------------------------------------------------- деактивация

@pytest.mark.critical
async def test_deactivate_as_admin_hides_from_list(
    client, admin, auth_headers, make_achievement
):
    target = await make_achievement()

    r = await client.delete(item_url(target.id), headers=auth_headers(admin))

    assert r.status_code == 200
    assert r.json()["is_active"] is False
    assert (await client.get(COLLECTION)).json() == []


@pytest.mark.critical
async def test_deactivate_requires_admin(
    client, make_user, auth_headers, make_achievement
):
    target = await make_achievement()
    regular = await make_user()

    r = await client.delete(item_url(target.id), headers=auth_headers(regular))

    assert r.status_code == 403
    assert [a["id"] for a in (await client.get(COLLECTION)).json()] == [target.id]


@pytest.mark.critical
async def test_deactivate_without_token(client, make_achievement):
    target = await make_achievement()

    r = await client.delete(item_url(target.id))

    assert r.status_code in NO_AUTH


async def test_deactivate_missing_returns_404(client, admin, auth_headers):
    r = await client.delete(item_url(999_999), headers=auth_headers(admin))

    assert r.status_code == 404


async def test_deactivate_is_idempotent(client, admin, auth_headers, make_achievement):
    target = await make_achievement()
    headers = auth_headers(admin)

    first = await client.delete(item_url(target.id), headers=headers)
    second = await client.delete(item_url(target.id), headers=headers)

    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json()["is_active"] is False