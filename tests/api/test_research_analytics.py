"""SMOKE: обычный пользователь 403, роль с доступом 200, date_from позже date_to 400"""
"""Research analytics: доступ по роли, валидация, корреляции."""
from datetime import date, datetime

from httpx import AsyncClient


BASE = "/api/v1/research/analytics/sleep"


def _params(from_="2026-10-01", to="2026-10-31"):
    return {"date_from": from_, "date_to": to}


# ---------------------------------------------------------
# доступ
# ---------------------------------------------------------

async def test_requires_auth(client: AsyncClient):
    r = await client.get(BASE, params=_params())
    assert r.status_code == 401


async def test_user_forbidden(
    client: AsyncClient, make_user, auth_headers
):
    user = await make_user()  # role="user"
    r = await client.get(
        BASE, params=_params(), headers=auth_headers(user)
    )
    assert r.status_code == 403


async def test_moderator_forbidden(
    client: AsyncClient, make_user, auth_headers
):
    mod = await make_user(role="moderator")
    r = await client.get(
        BASE, params=_params(), headers=auth_headers(mod)
    )
    assert r.status_code == 403


async def test_admin_allowed(
    client: AsyncClient, admin, auth_headers
):
    r = await client.get(
        BASE, params=_params(), headers=auth_headers(admin)
    )
    assert r.status_code == 200, r.text


async def test_researcher_allowed(
    client: AsyncClient, make_user, auth_headers
):
    researcher = await make_user(role="researcher")
    r = await client.get(
        BASE, params=_params(), headers=auth_headers(researcher)
    )
    assert r.status_code == 200, r.text


# ---------------------------------------------------------
# валидация
# ---------------------------------------------------------

async def test_missing_params_422(
    client: AsyncClient, admin, auth_headers
):
    r = await client.get(BASE, headers=auth_headers(admin))
    assert r.status_code == 422


async def test_date_from_after_date_to_422(
    client: AsyncClient, admin, auth_headers
):
    r = await client.get(
        BASE,
        params=_params(from_="2026-10-31", to="2026-10-01"),
        headers=auth_headers(admin),
    )
    assert r.status_code == 422


# ---------------------------------------------------------
# пустые данные
# ---------------------------------------------------------

async def test_empty_data(
    client: AsyncClient, admin, auth_headers
):
    r = await client.get(
        BASE,
        params=_params(from_="2020-01-01", to="2020-01-02"),
        headers=auth_headers(admin),
    )
    assert r.status_code == 200
    data = r.json()
    assert data["sleep_entries"] == 0
    assert data["participants_with_sleep"] == 0
    assert data["average_sleep_minutes"] is None
    assert data["concentration_pairs"] == 0
    assert data["test_score_pairs"] == 0
    assert data["sleep_concentration"]["rho"] is None
    assert data["sleep_concentration"]["p_value"] is None
    assert data["sleep_test_score"]["rho"] is None


# ---------------------------------------------------------
# агрегаты по sleep
# ---------------------------------------------------------

async def test_single_sleep_entry_average(
    client: AsyncClient,
    admin,
    auth_headers,
    make_user,
    make_sleep_entry,
):
    user = await make_user()
    await make_sleep_entry(
        user=user, sleep_date=date(2026, 10, 15), duration_minutes=450,
    )

    r = await client.get(
        BASE, params=_params(), headers=auth_headers(admin)
    )
    assert r.status_code == 200
    data = r.json()
    assert data["sleep_entries"] == 1
    assert data["participants_with_sleep"] == 1
    assert data["average_sleep_minutes"] == 450.0


async def test_multiple_entries_average(
    client: AsyncClient,
    admin,
    auth_headers,
    make_user,
    make_sleep_entry,
):
    """Средняя продолжительность по всем записям."""
    user_a = await make_user()
    user_b = await make_user()

    await make_sleep_entry(
        user=user_a, sleep_date=date(2026, 10, 15), duration_minutes=400,
    )
    await make_sleep_entry(
        user=user_b, sleep_date=date(2026, 10, 15), duration_minutes=500,
    )

    r = await client.get(
        BASE, params=_params(), headers=auth_headers(admin)
    )
    data = r.json()
    assert data["sleep_entries"] == 2
    assert data["participants_with_sleep"] == 2
    assert data["average_sleep_minutes"] == 450.0


# ---------------------------------------------------------
# корреляция sleep × concentration
# ---------------------------------------------------------

async def test_concentration_insufficient_data(
    client: AsyncClient,
    admin,
    auth_headers,
    make_user,
    make_sleep_entry,
    make_study_state,
):
    """n < 3 → rho и p_value = None."""
    user = await make_user()
    await make_sleep_entry(
        user=user, sleep_date=date(2026, 10, 15), duration_minutes=400,
    )
    await make_study_state(
        user=user,
        recorded_at=datetime(2026, 10, 15, 12, 0),
        concentration=1,
    )

    r = await client.get(
        BASE, params=_params(), headers=auth_headers(admin)
    )
    data = r.json()
    assert data["concentration_pairs"] == 1
    assert data["sleep_concentration"]["sample_size"] == 1
    assert data["sleep_concentration"]["rho"] is None
    assert data["sleep_concentration"]["p_value"] is None


async def test_concentration_perfect_positive_correlation(
    client: AsyncClient,
    admin,
    auth_headers,
    make_user,
    make_sleep_entry,
    make_study_state,
):
    """3 пары монотонно растут → rho = 1.0."""
    user = await make_user()
    pairs = [
        (date(2026, 10, 15), 400, 1),
        (date(2026, 10, 16), 480, 2),
        (date(2026, 10, 17), 560, 3),
    ]
    for d, dur, conc in pairs:
        await make_sleep_entry(user=user, sleep_date=d, duration_minutes=dur)
        await make_study_state(
            user=user,
            recorded_at=datetime(d.year, d.month, d.day, 12, 0),
            concentration=conc,
        )

    r = await client.get(
        BASE, params=_params(), headers=auth_headers(admin)
    )
    data = r.json()
    assert data["concentration_pairs"] == 3
    assert data["sleep_concentration"]["sample_size"] == 3
    assert data["sleep_concentration"]["rho"] == 1.0


async def test_concentration_perfect_negative_correlation(
    client: AsyncClient,
    admin,
    auth_headers,
    make_user,
    make_sleep_entry,
    make_study_state,
):
    """3 пары монотонно убывают → rho = -1.0."""
    user = await make_user()
    pairs = [
        (date(2026, 10, 15), 400, 3),
        (date(2026, 10, 16), 480, 2),
        (date(2026, 10, 17), 560, 1),
    ]
    for d, dur, conc in pairs:
        await make_sleep_entry(user=user, sleep_date=d, duration_minutes=dur)
        await make_study_state(
            user=user,
            recorded_at=datetime(d.year, d.month, d.day, 12, 0),
            concentration=conc,
        )

    r = await client.get(
        BASE, params=_params(), headers=auth_headers(admin)
    )
    data = r.json()
    assert data["sleep_concentration"]["rho"] == -1.0


# ---------------------------------------------------------
# корреляция sleep × test_score
# ---------------------------------------------------------

async def test_test_score_perfect_positive_correlation(
    client: AsyncClient,
    admin,
    auth_headers,
    make_user,
    make_sleep_entry,
    make_study_test_result,
):
    """3 пары sleep/test_score растут монотонно → rho = 1.0."""
    user = await make_user()
    pairs = [
        (date(2026, 10, 15), 400, 50),
        (date(2026, 10, 16), 480, 70),
        (date(2026, 10, 17), 560, 90),
    ]
    for d, dur, score in pairs:
        await make_sleep_entry(user=user, sleep_date=d, duration_minutes=dur)
        await make_study_test_result(
            user=user,
            tested_at=datetime(d.year, d.month, d.day, 12, 0),
            score=score,
            max_score=100,
        )

    r = await client.get(
        BASE, params=_params(), headers=auth_headers(admin)
    )
    data = r.json()
    assert data["test_score_pairs"] == 3
    assert data["sleep_test_score"]["sample_size"] == 3
    assert data["sleep_test_score"]["rho"] == 1.0


# ---------------------------------------------------------
# фильтр по датам работает
# ---------------------------------------------------------

async def test_date_filter_excludes_out_of_range(
    client: AsyncClient,
    admin,
    auth_headers,
    make_user,
    make_sleep_entry,
):
    """Запись вне диапазона не попадает."""
    user = await make_user()
    await make_sleep_entry(
        user=user, sleep_date=date(2026, 9, 1), duration_minutes=400,
    )
    await make_sleep_entry(
        user=user, sleep_date=date(2026, 10, 15), duration_minutes=500,
    )

    r = await client.get(
        BASE,
        params={"date_from": "2026-10-01", "date_to": "2026-10-31"},
        headers=auth_headers(admin),
    )
    data = r.json()
    assert data["sleep_entries"] == 1
    assert data["average_sleep_minutes"] == 500.0