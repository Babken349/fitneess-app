"""КРИТИЧНОЕ (чужие данные): подходы, дубль номера 409, чужой лог 403"""
"""Set logs: create, get, list, update, delete, ownership, дубль set_number."""
from httpx import AsyncClient


BASE = "/api/v1"


# ---------------------------------------------------------
# create
# ---------------------------------------------------------

async def test_create_set_requires_auth(
    client: AsyncClient, setup_exercise_log
):
    _, log = await setup_exercise_log()
    r = await client.post(
        f"{BASE}/exercise-logs/{log['id']}/sets",
        json={"set_number": 1, "actual_reps": 10, "actual_weight": 50},
    )
    assert r.status_code == 401


async def test_create_set_success(
    client: AsyncClient, setup_exercise_log, auth_headers
):
    user, log = await setup_exercise_log()
    r = await client.post(
        f"{BASE}/exercise-logs/{log['id']}/sets",
        json={
            "set_number": 1,
            "actual_reps": 12,
            "actual_weight": 50.5,
            "rir": 2,
            "completed": True,
        },
        headers=auth_headers(user),
    )
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["exercise_log_id"] == log["id"]
    assert data["set_number"] == 1
    assert data["actual_reps"] == 12
    assert data["actual_weight"] == 50.5
    assert data["rir"] == 2
    assert data["completed"] is True


async def test_create_set_missing_exercise_log(
    client: AsyncClient, make_user, auth_headers
):
    user = await make_user()
    r = await client.post(
        f"{BASE}/exercise-logs/999999/sets",
        json={"set_number": 1, "actual_reps": 10, "actual_weight": 50},
        headers=auth_headers(user),
    )
    assert r.status_code == 404


async def test_create_set_foreign_exercise_log(
    client: AsyncClient,
    make_user,
    auth_headers,
    setup_exercise_log,
):
    _, log_a = await setup_exercise_log()
    user_b = await make_user()

    r = await client.post(
        f"{BASE}/exercise-logs/{log_a['id']}/sets",
        json={"set_number": 1, "actual_reps": 10, "actual_weight": 50},
        headers=auth_headers(user_b),
    )
    assert r.status_code == 403


async def test_create_set_duplicate_number_conflicts(
    client: AsyncClient, setup_exercise_log, auth_headers
):
    user, log = await setup_exercise_log()
    h = auth_headers(user)

    r1 = await client.post(
        f"{BASE}/exercise-logs/{log['id']}/sets",
        json={"set_number": 1, "actual_reps": 10, "actual_weight": 50},
        headers=h,
    )
    assert r1.status_code == 201

    r2 = await client.post(
        f"{BASE}/exercise-logs/{log['id']}/sets",
        json={"set_number": 1, "actual_reps": 8, "actual_weight": 55},
        headers=h,
    )
    assert r2.status_code == 409


async def test_create_set_invalid_reps_422(
    client: AsyncClient, setup_exercise_log, auth_headers
):
    user, log = await setup_exercise_log()
    r = await client.post(
        f"{BASE}/exercise-logs/{log['id']}/sets",
        json={"set_number": 1, "actual_reps": -1, "actual_weight": 50},
        headers=auth_headers(user),
    )
    assert r.status_code == 422


async def test_create_set_invalid_weight_422(
    client: AsyncClient, setup_exercise_log, auth_headers
):
    user, log = await setup_exercise_log()
    r = await client.post(
        f"{BASE}/exercise-logs/{log['id']}/sets",
        json={"set_number": 1, "actual_reps": 10, "actual_weight": -5},
        headers=auth_headers(user),
    )
    assert r.status_code == 422


async def test_create_set_invalid_number_422(
    client: AsyncClient, setup_exercise_log, auth_headers
):
    user, log = await setup_exercise_log()
    r = await client.post(
        f"{BASE}/exercise-logs/{log['id']}/sets",
        json={"set_number": 0, "actual_reps": 10, "actual_weight": 50},
        headers=auth_headers(user),
    )
    assert r.status_code == 422


# ---------------------------------------------------------
# read
# ---------------------------------------------------------

async def test_get_set_by_id(
    client: AsyncClient, setup_exercise_log, auth_headers
):
    user, log = await setup_exercise_log()
    h = auth_headers(user)

    r = await client.post(
        f"{BASE}/exercise-logs/{log['id']}/sets",
        json={"set_number": 1, "actual_reps": 10, "actual_weight": 50},
        headers=h,
    )
    sid = r.json()["id"]

    r = await client.get(f"{BASE}/sets/{sid}", headers=h)
    assert r.status_code == 200
    assert r.json()["id"] == sid


async def test_get_set_missing_returns_404(
    client: AsyncClient, make_user, auth_headers
):
    user = await make_user()
    r = await client.get(
        f"{BASE}/sets/999999", headers=auth_headers(user)
    )
    assert r.status_code == 404


async def test_get_set_foreign_forbidden(
    client: AsyncClient,
    make_user,
    auth_headers,
    setup_exercise_log,
):
    _, log = await setup_exercise_log()
    user_b = await make_user()

    # создаём set у user_a
    user_a = (await setup_exercise_log())[0]  # это создаст новый log, но сути не меняет
    # Проще: создадим напрямую через log из первого setup
    # Перепишем правильно: