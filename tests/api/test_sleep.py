"""CRUD: создать и получить, чужая запись 403, несуществующая 404, невалидное тело через parametrize; дубль за дату 409, диапазон дат, переход через полночь"""
"""Sleep: CRUD, длительность (через полночь, 0, >18h), 409, фильтры, ownership."""
from datetime import date

from httpx import AsyncClient


BASE = "/api/v1/sleep"


# ---------------------------------------------------------
# create
# ---------------------------------------------------------

async def test_create_requires_auth(client: AsyncClient):
    r = await client.post(
        BASE + "/",
        json={
            "sleep_date": "2026-10-15",
            "bedtime": "23:00:00",
            "wake_time": "07:00:00",
        },
    )
    assert r.status_code == 401


async def test_create_success_cross_midnight(
    client: AsyncClient, make_user, auth_headers
):
    """23:00 → 07:00 = 480 мин (8ч)."""
    user = await make_user()
    r = await client.post(
        BASE + "/",
        json={
            "sleep_date": "2026-10-15",
            "bedtime": "23:00:00",
            "wake_time": "07:00:00",
            "note": "хорошо выспался",
        },
        headers=auth_headers(user),
    )
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["user_id"] == user.id
    assert data["sleep_date"] == "2026-10-15"
    assert data["duration_minutes"] == 480
    assert data["duration_hours"] == 8.0
    assert data["note"] == "хорошо выспался"


async def test_create_same_day_sleep(
    client: AsyncClient, make_user, auth_headers
):
    """01:00 → 08:00 = 420 мин (без перехода через полночь)."""
    user = await make_user()
    r = await client.post(
        BASE + "/",
        json={
            "sleep_date": "2026-10-15",
            "bedtime": "01:00:00",
            "wake_time": "08:00:00",
        },
        headers=auth_headers(user),
    )
    assert r.status_code == 201
    assert r.json()["duration_minutes"] == 420


async def test_create_equal_times_422(
    client: AsyncClient, make_user, auth_headers
):
    """bedtime == wake_time → 422."""
    user = await make_user()
    r = await client.post(
        BASE + "/",
        json={
            "sleep_date": "2026-10-15",
            "bedtime": "22:00:00",
            "wake_time": "22:00:00",
        },
        headers=auth_headers(user),
    )
    assert r.status_code == 422


async def test_create_over_18h_422(
    client: AsyncClient, make_user, auth_headers
):
    """00:00 → 18:30 = 1110 мин (>18ч) → 422."""
    user = await make_user()
    r = await client.post(
        BASE + "/",
        json={
            "sleep_date": "2026-10-15",
            "bedtime": "00:00:00",
            "wake_time": "18:30:00",
        },
        headers=auth_headers(user),
    )
    assert r.status_code == 422


async def test_create_duplicate_date_conflicts(
    client: AsyncClient, make_user, auth_headers
):
    """UNIQUE(user_id, sleep_date) → 409."""
    user = await make_user()
    h = auth_headers(user)
    body = {
        "sleep_date": "2026-10-15",
        "bedtime": "23:00:00",
        "wake_time": "07:00:00",
    }

    r1 = await client.post(BASE + "/", json=body, headers=h)
    assert r1.status_code == 201

    r2 = await client.post(BASE + "/", json=body, headers=h)
    assert r2.status_code == 409


async def test_two_users_same_date_ok(
    client: AsyncClient, make_user, auth_headers
):
    """UNIQUE только в паре с user_id — разные юзеры могут иметь одну дату."""
    user_a = await make_user()
    user_b = await make_user()
    body = {
        "sleep_date": "2026-10-15",
        "bedtime": "23:00:00",
        "wake_time": "07:00:00",
    }

    r1 = await client.post(BASE + "/", json=body, headers=auth_headers(user_a))
    assert r1.status_code == 201
    r2 = await client.post(BASE + "/", json=body, headers=auth_headers(user_b))
    assert r2.status_code == 201


# ---------------------------------------------------------
# read
# ---------------------------------------------------------

async def test_get_by_id(
    client: AsyncClient, make_user, auth_headers
):
    user = await make_user()
    h = auth_headers(user)

    r = await client.post(
        BASE + "/",
        json={
            "sleep_date": "2026-10-15",
            "bedtime": "23:00:00",
            "wake_time": "07:00:00",
        },
        headers=h,
    )
    sid = r.json()["id"]

    r = await client.get(f"{BASE}/{sid}", headers=h)
    assert r.status_code == 200
    assert r.json()["id"] == sid
    assert r.json()["duration_minutes"] == 480


async def test_get_missing_returns_404(
    client: AsyncClient, make_user, auth_headers
):
    user = await make_user()
    r = await client.get(f"{BASE}/999999", headers=auth_headers(user))
    assert r.status_code == 404


async def test_get_foreign_returns_404(
    client: AsyncClient, make_user, auth_headers
):
    """Чужая запись неотличима от несуществующей (репозиторий фильтрует по user_id)."""
    user_a = await make_user()
    user_b = await make_user()

    r = await client.post(
        BASE + "/",
        json={
            "sleep_date": "2026-10-15",
            "bedtime": "23:00:00",
            "wake_time": "07:00:00",
        },
        headers=auth_headers(user_a),
    )
    sid = r.json()["id"]

    r = await client.get(f"{BASE}/{sid}", headers=auth_headers(user_b))
    assert r.status_code == 404


async def test_list_empty(client: AsyncClient, make_user, auth_headers):
    user = await make_user()
    r = await client.get(BASE + "/", headers=auth_headers(user))
    assert r.status_code == 200
    data = r.json()
    assert data["items"] == []
    assert data["total"] == 0
    assert data["skip"] == 0
    assert data["limit"] == 20


async def test_list_returns_only_own(
    client: AsyncClient, make_user, auth_headers
):
    user_a = await make_user()
    user_b = await make_user()

    r = await client.post(
        BASE + "/",
        json={
            "sleep_date": "2026-10-15",
            "bedtime": "23:00:00",
            "wake_time": "07:00:00",
        },
        headers=auth_headers(user_a),
    )
    assert r.status_code == 201
    r = await client.post(
        BASE + "/",
        json={
            "sleep_date": "2026-10-15",
            "bedtime": "23:00:00",
            "wake_time": "07:00:00",
        },
        headers=auth_headers(user_b),
    )
    assert r.status_code == 201

    r = await client.get(BASE + "/", headers=auth_headers(user_a))
    assert r.status_code == 200
    data = r.json()
    assert len(data["items"]) == 1
    assert data["total"] == 1
    assert data["items"][0]["user_id"] == user_a.id


async def test_list_date_filter(
    client: AsyncClient, make_user, auth_headers
):
    user = await make_user()
    h = auth_headers(user)

    for d in ("2026-10-10", "2026-10-15", "2026-10-20"):
        r = await client.post(
            BASE + "/",
            json={
                "sleep_date": d,
                "bedtime": "23:00:00",
                "wake_time": "07:00:00",
            },
            headers=h,
        )
        assert r.status_code == 201

    r = await client.get(
        BASE + "/",
        params={"date_from": "2026-10-12", "date_to": "2026-10-18"},
        headers=h,
    )
    assert r.status_code == 200
    data = r.json()
    dates = [x["sleep_date"] for x in data["items"]]
    assert dates == ["2026-10-15"]
    assert data["total"] == 1

async def test_list_invalid_range_422(
    client: AsyncClient, make_user, auth_headers
):
    user = await make_user()
    r = await client.get(
        BASE + "/",
        params={"date_from": "2026-10-20", "date_to": "2026-10-10"},
        headers=auth_headers(user),
    )
    assert r.status_code == 422


# ---------------------------------------------------------
# update
# ---------------------------------------------------------

async def test_update_recalculates_duration(
    client: AsyncClient, make_user, auth_headers
):
    """PATCH wake_time → duration пересчитывается."""
    user = await make_user()
    h = auth_headers(user)

    r = await client.post(
        BASE + "/",
        json={
            "sleep_date": "2026-10-15",
            "bedtime": "23:00:00",
            "wake_time": "07:00:00",
        },
        headers=h,
    )
    sid = r.json()["id"]
    assert r.json()["duration_minutes"] == 480

    r = await client.patch(
        f"{BASE}/{sid}",
        json={"wake_time": "06:00:00"},  # 7 часов
        headers=h,
    )
    assert r.status_code == 200
    assert r.json()["duration_minutes"] == 420


async def test_update_note_only_keeps_duration(
    client: AsyncClient, make_user, auth_headers
):
    user = await make_user()
    h = auth_headers(user)

    r = await client.post(
        BASE + "/",
        json={
            "sleep_date": "2026-10-15",
            "bedtime": "23:00:00",
            "wake_time": "07:00:00",
            "note": "старое",
        },
        headers=h,
    )
    sid = r.json()["id"]

    r = await client.patch(
        f"{BASE}/{sid}",
        json={"note": "новое"},
        headers=h,
    )
    assert r.status_code == 200
    assert r.json()["note"] == "новое"
    assert r.json()["duration_minutes"] == 480


async def test_update_invalid_duration_422(
    client: AsyncClient, make_user, auth_headers
):
    user = await make_user()
    h = auth_headers(user)

    r = await client.post(
        BASE + "/",
        json={
            "sleep_date": "2026-10-15",
            "bedtime": "23:00:00",
            "wake_time": "07:00:00",
        },
        headers=h,
    )
    sid = r.json()["id"]

    r = await client.patch(
        f"{BASE}/{sid}",
        json={"wake_time": "23:00:00"},  # == bedtime → InvalidSleepDuration
        headers=h,
    )
    assert r.status_code == 422


async def test_update_missing_returns_404(
    client: AsyncClient, make_user, auth_headers
):
    user = await make_user()
    r = await client.patch(
        f"{BASE}/999999",
        json={"wake_time": "06:00:00"},
        headers=auth_headers(user),
    )
    assert r.status_code == 404


async def test_update_foreign_returns_404(
    client: AsyncClient, make_user, auth_headers
):
    user_a = await make_user()
    user_b = await make_user()

    r = await client.post(
        BASE + "/",
        json={
            "sleep_date": "2026-10-15",
            "bedtime": "23:00:00",
            "wake_time": "07:00:00",
        },
        headers=auth_headers(user_a),
    )
    sid = r.json()["id"]

    r = await client.patch(
        f"{BASE}/{sid}",
        json={"wake_time": "06:00:00"},
        headers=auth_headers(user_b),
    )
    assert r.status_code == 404


# ---------------------------------------------------------
# delete
# ---------------------------------------------------------

async def test_delete(client: AsyncClient, make_user, auth_headers):
    user = await make_user()
    h = auth_headers(user)

    r = await client.post(
        BASE + "/",
        json={
            "sleep_date": "2026-10-15",
            "bedtime": "23:00:00",
            "wake_time": "07:00:00",
        },
        headers=h,
    )
    sid = r.json()["id"]

    r = await client.delete(f"{BASE}/{sid}", headers=h)
    assert r.status_code == 204

    r = await client.get(f"{BASE}/{sid}", headers=h)
    assert r.status_code == 404


async def test_delete_foreign_returns_404(
    client: AsyncClient, make_user, auth_headers
):
    user_a = await make_user()
    user_b = await make_user()

    r = await client.post(
        BASE + "/",
        json={
            "sleep_date": "2026-10-15",
            "bedtime": "23:00:00",
            "wake_time": "07:00:00",
        },
        headers=auth_headers(user_a),
    )
    sid = r.json()["id"]

    r = await client.delete(f"{BASE}/{sid}", headers=auth_headers(user_b))
    assert r.status_code == 404

    # у user_a цела
    r = await client.get(f"{BASE}/{sid}", headers=auth_headers(user_a))
    assert r.status_code == 200


    async def test_list_pagination_skip_limit(
    client: AsyncClient, make_user, auth_headers
    ):
        user = await make_user()
        h = auth_headers(user)
        for d in ("2026-10-10", "2026-10-11", "2026-10-12"):
            await client.post(
                BASE + "/",
                json={
                    "sleep_date": d,
                    "bedtime": "23:00:00",
                    "wake_time": "07:00:00",
                },
                headers=h,
            )

        r = await client.get(BASE + "/", params={"skip": 1, "limit": 1}, headers=h)
        data = r.json()
        assert data["total"] == 3
        assert len(data["items"]) == 1
        assert data["skip"] == 1
        assert data["limit"] == 1


async def test_list_total_independent_of_limit(client, make_user, auth_headers):
    user = await make_user()
    h = auth_headers(user)
    for d in ("2026-10-10", "2026-10-11", "2026-10-12", "2026-10-13", "2026-10-14"):
        await client.post(
            BASE + "/",
            json={"sleep_date": d, "bedtime": "23:00:00", "wake_time": "07:00:00"},
            headers=h,
        )

    r = await client.get(BASE + "/", params={"limit": 2}, headers=h)
    data = r.json()
    assert data["total"] == 5
    assert len(data["items"]) == 2
    # ↑ упадёт на UNIQUE(user_id, sleep_date) со 2-го раза, поэтому: