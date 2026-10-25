"""КРИТИЧНОЕ: свой календарь, календарь друга только при accepted, чужая запись 403"""
"""Calendar availability: create/upsert, my range, ownership, friendship."""
from datetime import date, timedelta

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.friendship import Friendship


async def test_calendar_create_returns_201(
    client: AsyncClient, make_user, auth_headers
):
    user = await make_user()
    today = date.today().isoformat()

    r = await client.post(
        "/api/v1/calendar/availability",
        json={"date": today, "is_available": True, "note": "зал"},
        headers=auth_headers(user),
    )
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["user_id"] == user.id
    assert data["date"] == today
    assert data["is_available"] is True
    assert data["note"] == "зал"


async def test_calendar_post_same_date_upserts(
    client: AsyncClient, make_user, auth_headers
):
    """POST на ту же дату обновляет запись, не создаёт новую."""
    user = await make_user()
    today = date.today().isoformat()
    h = auth_headers(user)

    r1 = await client.post(
        "/api/v1/calendar/availability",
        json={"date": today, "is_available": True, "note": "зал"},
        headers=h,
    )
    assert r1.status_code == 201
    id1 = r1.json()["id"]

    r2 = await client.post(
        "/api/v1/calendar/availability",
        json={"date": today, "is_available": False, "note": "отдых"},
        headers=h,
    )
    assert r2.status_code == 201
    assert r2.json()["id"] == id1
    assert r2.json()["is_available"] is False
    assert r2.json()["note"] == "отдых"


async def test_calendar_my_range(
    client: AsyncClient, make_user, auth_headers
):
    user = await make_user()
    h = auth_headers(user)
    today = date.today()

    for delta in (-1, 0, 1):
        d = (today + timedelta(days=delta)).isoformat()
        r = await client.post(
            "/api/v1/calendar/availability",
            json={"date": d, "is_available": True},
            headers=h,
        )
        assert r.status_code == 201

    r = await client.get(
        "/api/v1/calendar/availability/me",
        params={
            "start_date": today.isoformat(),
            "end_date": (today + timedelta(days=1)).isoformat(),
        },
        headers=h,
    )
    assert r.status_code == 200
    dates = [x["date"] for x in r.json()]
    assert len(dates) == 2
    assert today.isoformat() in dates
    assert (today + timedelta(days=1)).isoformat() in dates
    assert (today - timedelta(days=1)).isoformat() not in dates


async def test_calendar_ownership(
    client: AsyncClient, make_user, auth_headers
):
    user_a = await make_user()
    user_b = await make_user()
    today = date.today().isoformat()

    r = await client.post(
        "/api/v1/calendar/availability",
        json={"date": today, "is_available": True},
        headers=auth_headers(user_a),
    )
    aid = r.json()["id"]

    r = await client.patch(
        f"/api/v1/calendar/availability/{aid}",
        json={"is_available": False},
        headers=auth_headers(user_b),
    )
    assert r.status_code in (403, 404)

    r = await client.delete(
        f"/api/v1/calendar/availability/{aid}",
        headers=auth_headers(user_b),
    )
    assert r.status_code in (403, 404)

    # исходная цела
    r = await client.patch(
        f"/api/v1/calendar/availability/{aid}",
        json={"note": "ok"},
        headers=auth_headers(user_a),
    )
    assert r.status_code == 200


async def test_calendar_friend_without_friendship_403(
    client: AsyncClient, make_user, auth_headers
):
    user_a = await make_user()
    user_b = await make_user()
    today = date.today().isoformat()

    r = await client.get(
        f"/api/v1/calendar/availability/friend/{user_b.id}",
        params={"start_date": today, "end_date": today},
        headers=auth_headers(user_a),
    )
    assert r.status_code == 403


async def test_calendar_friend_with_accepted_friendship(
    client: AsyncClient,
    make_user,
    auth_headers,
    session: AsyncSession,
):
    user_a = await make_user()
    user_b = await make_user()
    today = date.today()

    # принимаем дружбу
    session.add(
        Friendship(
            requester_id=user_a.id,
            addressee_id=user_b.id,
            status="accepted",
        )
    )
    await session.flush()

    # user_b создаёт запись
    r = await client.post(
        "/api/v1/calendar/availability",
        json={"date": today.isoformat(), "is_available": True},
        headers=auth_headers(user_b),
    )
    assert r.status_code == 201

    # user_a читает календарь друга
    r = await client.get(
        f"/api/v1/calendar/availability/friend/{user_b.id}",
        params={
            "start_date": today.isoformat(),
            "end_date": today.isoformat(),
        },
        headers=auth_headers(user_a),
    )
    assert r.status_code == 200
    rows = r.json()
    assert len(rows) == 1
    assert rows[0]["user_id"] == user_b.id