"""КРИТИЧНОЕ (чужие данные): создание, дубль упражнения и порядка 409, чужая сессия 403"""
"""Exercise logs: create, get, list, update, delete, ownership, уникальность."""
from httpx import AsyncClient


BASE = "/api/v1"


# ---------------------------------------------------------
# create
# ---------------------------------------------------------

async def test_create_exercise_log(
    client: AsyncClient,
    make_user,
    make_exercise,
    make_workout_session,
    auth_headers,
):
    user = await make_user()
    exercise = await make_exercise()
    session = await make_workout_session(user=user)

    r = await client.post(
        f"{BASE}/workout-sessions/{session.id}/exercises",
        json={"exercise_id": exercise.id, "exercise_order": 1, "notes": "разминка"},
        headers=auth_headers(user),
    )
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["workout_session_id"] == session.id
    assert data["exercise_id"] == exercise.id
    assert data["exercise_order"] == 1
    assert data["notes"] == "разминка"


async def test_create_exercise_log_missing_session(
    client: AsyncClient,
    make_user,
    make_exercise,
    auth_headers,
):
    user = await make_user()
    exercise = await make_exercise()

    r = await client.post(
        f"{BASE}/workout-sessions/999999/exercises",
        json={"exercise_id": exercise.id, "exercise_order": 1},
        headers=auth_headers(user),
    )
    assert r.status_code == 404


async def test_create_exercise_log_missing_exercise(
    client: AsyncClient,
    make_user,
    make_workout_session,
    auth_headers,
):
    user = await make_user()
    session = await make_workout_session(user=user)

    r = await client.post(
        f"{BASE}/workout-sessions/{session.id}/exercises",
        json={"exercise_id": 999999, "exercise_order": 1},
        headers=auth_headers(user),
    )
    assert r.status_code == 404


async def test_create_exercise_log_duplicate_exercise(
    client: AsyncClient,
    make_user,
    make_exercise,
    make_workout_session,
    auth_headers,
):
    """UNIQUE (workout_session_id, exercise_id) → 409."""
    user = await make_user()
    exercise = await make_exercise()
    session = await make_workout_session(user=user)
    h = auth_headers(user)

    r1 = await client.post(
        f"{BASE}/workout-sessions/{session.id}/exercises",
        json={"exercise_id": exercise.id, "exercise_order": 1},
        headers=h,
    )
    assert r1.status_code == 201

    r2 = await client.post(
        f"{BASE}/workout-sessions/{session.id}/exercises",
        json={"exercise_id": exercise.id, "exercise_order": 2},
        headers=h,
    )
    assert r2.status_code == 409


async def test_create_exercise_log_duplicate_order(
    client: AsyncClient,
    make_user,
    make_exercise,
    make_workout_session,
    auth_headers,
):
    """UNIQUE (workout_session_id, exercise_order) → 409."""
    user = await make_user()
    ex1 = await make_exercise()
    ex2 = await make_exercise()
    session = await make_workout_session(user=user)
    h = auth_headers(user)

    r1 = await client.post(
        f"{BASE}/workout-sessions/{session.id}/exercises",
        json={"exercise_id": ex1.id, "exercise_order": 1},
        headers=h,
    )
    assert r1.status_code == 201

    r2 = await client.post(
        f"{BASE}/workout-sessions/{session.id}/exercises",
        json={"exercise_id": ex2.id, "exercise_order": 1},
        headers=h,
    )
    assert r2.status_code == 409


async def test_create_exercise_log_foreign_session(
    client: AsyncClient,
    make_user,
    make_exercise,
    make_workout_session,
    auth_headers,
):
    """Чужая сессия → 403."""
    user_a = await make_user()
    user_b = await make_user()
    exercise = await make_exercise()
    session_a = await make_workout_session(user=user_a)

    r = await client.post(
        f"{BASE}/workout-sessions/{session_a.id}/exercises",
        json={"exercise_id": exercise.id, "exercise_order": 1},
        headers=auth_headers(user_b),
    )
    assert r.status_code == 403


# ---------------------------------------------------------
# read
# ---------------------------------------------------------

async def test_get_exercise_log(
    client: AsyncClient,
    make_user,
    make_exercise,
    make_workout_session,
    auth_headers,
):
    user = await make_user()
    exercise = await make_exercise()
    session = await make_workout_session(user=user)
    h = auth_headers(user)

    r = await client.post(
        f"{BASE}/workout-sessions/{session.id}/exercises",
        json={"exercise_id": exercise.id, "exercise_order": 1},
        headers=h,
    )
    log_id = r.json()["id"]

    r = await client.get(f"{BASE}/exercise-logs/{log_id}", headers=h)
    assert r.status_code == 200
    assert r.json()["id"] == log_id


async def test_get_exercise_log_foreign(
    client: AsyncClient,
    make_user,
    make_exercise,
    make_workout_session,
    auth_headers,
):
    user_a = await make_user()
    user_b = await make_user()
    exercise = await make_exercise()
    session = await make_workout_session(user=user_a)

    r = await client.post(
        f"{BASE}/workout-sessions/{session.id}/exercises",
        json={"exercise_id": exercise.id, "exercise_order": 1},
        headers=auth_headers(user_a),
    )
    log_id = r.json()["id"]

    r = await client.get(
        f"{BASE}/exercise-logs/{log_id}",
        headers=auth_headers(user_b),
    )
    assert r.status_code == 403


async def test_list_session_exercises(
    client: AsyncClient,
    make_user,
    make_exercise,
    make_workout_session,
    auth_headers,
):
    user = await make_user()
    session = await make_workout_session(user=user)
    h = auth_headers(user)

    for i in range(1, 4):
        ex = await make_exercise()
        r = await client.post(
            f"{BASE}/workout-sessions/{session.id}/exercises",
            json={"exercise_id": ex.id, "exercise_order": i},
            headers=h,
        )
        assert r.status_code == 201

    r = await client.get(
        f"{BASE}/workout-sessions/{session.id}/exercises",
        headers=h,
    )
    assert r.status_code == 200
    rows = r.json()
    assert len(rows) == 3
    # порядок по exercise_order
    assert [x["exercise_order"] for x in rows] == [1, 2, 3]


# ---------------------------------------------------------
# update
# ---------------------------------------------------------

async def test_update_exercise_log_notes(
    client: AsyncClient,
    make_user,
    make_exercise,
    make_workout_session,
    auth_headers,
):
    user = await make_user()
    exercise = await make_exercise()
    session = await make_workout_session(user=user)
    h = auth_headers(user)

    r = await client.post(
        f"{BASE}/workout-sessions/{session.id}/exercises",
        json={"exercise_id": exercise.id, "exercise_order": 1, "notes": "старое"},
        headers=h,
    )
    log_id = r.json()["id"]

    r = await client.patch(
        f"{BASE}/exercise-logs/{log_id}",
        json={"notes": "новое"},
        headers=h,
    )
    assert r.status_code == 200
    assert r.json()["notes"] == "новое"


async def test_update_exercise_order_conflict(
    client: AsyncClient,
    make_user,
    make_exercise,
    make_workout_session,
    auth_headers,
):
    user = await make_user()
    ex1 = await make_exercise()
    ex2 = await make_exercise()
    session = await make_workout_session(user=user)
    h = auth_headers(user)

    r1 = await client.post(
        f"{BASE}/workout-sessions/{session.id}/exercises",
        json={"exercise_id": ex1.id, "exercise_order": 1},
        headers=h,
    )
    log1 = r1.json()["id"]

    r2 = await client.post(
        f"{BASE}/workout-sessions/{session.id}/exercises",
        json={"exercise_id": ex2.id, "exercise_order": 2},
        headers=h,
    )
    assert r2.status_code == 201

    # пытаемся сделать order=2 у log1 → конфликт
    r = await client.patch(
        f"{BASE}/exercise-logs/{log1}",
        json={"exercise_order": 2},
        headers=h,
    )
    assert r.status_code == 409


# ---------------------------------------------------------
# delete
# ---------------------------------------------------------

async def test_delete_exercise_log(
    client: AsyncClient,
    make_user,
    make_exercise,
    make_workout_session,
    auth_headers,
):
    user = await make_user()
    exercise = await make_exercise()
    session = await make_workout_session(user=user)
    h = auth_headers(user)

    r = await client.post(
        f"{BASE}/workout-sessions/{session.id}/exercises",
        json={"exercise_id": exercise.id, "exercise_order": 1},
        headers=h,
    )
    log_id = r.json()["id"]

    r = await client.delete(f"{BASE}/exercise-logs/{log_id}", headers=h)
    assert r.status_code == 204

    r = await client.get(f"{BASE}/exercise-logs/{log_id}", headers=h)
    assert r.status_code == 404


async def test_delete_exercise_log_foreign(
    client: AsyncClient,
    make_user,
    make_exercise,
    make_workout_session,
    auth_headers,
):
    user_a = await make_user()
    user_b = await make_user()
    exercise = await make_exercise()
    session = await make_workout_session(user=user_a)

    r = await client.post(
        f"{BASE}/workout-sessions/{session.id}/exercises",
        json={"exercise_id": exercise.id, "exercise_order": 1},
        headers=auth_headers(user_a),
    )
    log_id = r.json()["id"]

    r = await client.delete(
        f"{BASE}/exercise-logs/{log_id}",
        headers=auth_headers(user_b),
    )
    assert r.status_code == 403


# ---------------------------------------------------------
# auth
# ---------------------------------------------------------

async def test_exercise_logs_require_auth(client: AsyncClient):
    r = await client.get(f"{BASE}/exercise-logs/1")
    assert r.status_code == 401