"""P0-тесты auth: login, refresh rotation, is_active, доменные ошибки токена."""
from datetime import datetime, timedelta, timezone

import jwt
import pytest
from httpx import AsyncClient

from app.auth.security import decode_token
from app.core.config import settings
from app.models.users import User


# Должно совпадать с TEST_PASSWORD в tests/conftest.py
TEST_PASSWORD = "Tractor-Blue-42x"


# ---------------------------------------------------------
# login
# ---------------------------------------------------------

@pytest.mark.smoke
async def test_login_success(client: AsyncClient, make_user):
    user = await make_user()

    r = await client.post(
        "/api/v1/auth/login",
        json={"identifier": user.login, "password": TEST_PASSWORD},
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

    me = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {data['access_token']}"},
    )
    assert me.status_code == 200, me.text
    assert me.json()["login"] == user.login
 

async def test_login_wrong_password(client: AsyncClient, make_user):
    user = await make_user()

    r = await client.post(
        "/api/v1/auth/login",
        json={"identifier": user.login, "password": "WrongPassword-42x"},
    )
    assert r.status_code == 401


async def test_login_unknown_user(client: AsyncClient):
    r = await client.post(
        "/api/v1/auth/login",
        json={"identifier": "nobody_exists", "password": TEST_PASSWORD},
    )
    assert r.status_code == 401


@pytest.mark.critical
async def test_login_wrong_and_unknown_have_same_body(
    client: AsyncClient, make_user
):
    """Не палим существование аккаунта: тело и статус одинаковые."""
    user = await make_user()

    r_wrong = await client.post(
        "/api/v1/auth/login",
        json={"identifier": user.login, "password": "WrongPassword-42x"},
    )
    r_unknown = await client.post(
        "/api/v1/auth/login",
        json={"identifier": "nobody_exists", "password": TEST_PASSWORD},
    )
    assert r_wrong.status_code == r_unknown.status_code == 401
    assert r_wrong.json() == r_unknown.json()


@pytest.mark.critical
async def test_login_inactive_user(client: AsyncClient, make_user):
    """К2: деактивированный пользователь не должен логиниться."""
    user = await make_user(is_active=False)

    r = await client.post(
        "/api/v1/auth/login",
        json={"identifier": user.login, "password": TEST_PASSWORD},
    )
    assert r.status_code == 401


# ---------------------------------------------------------
# /me и заголовки
# ---------------------------------------------------------

@pytest.mark.critical
async def test_me_without_token(client: AsyncClient):
    """В3: без заголовка Authorization — 401, не 403, с WWW-Authenticate."""
    r = await client.get("/api/v1/users/me")
    assert r.status_code == 401, r.text
    assert r.headers.get("www-authenticate") == "Bearer"


async def test_me_with_garbage_token(client: AsyncClient):
    r = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": "Bearer garbage"},
    )
    assert r.status_code == 401


@pytest.mark.critical
async def test_me_inactive_user_with_valid_token(
    client: AsyncClient, make_user, auth_headers
):
    """К2: access-токен, выданный до деактивации, не работает.

    auth_headers строит токен напрямую из user.id, минуя /login.
    get_current_user всё равно сходит в БД и проверит is_active.
    """
    user = await make_user(is_active=False)
    r = await client.get("/api/v1/users/me", headers=auth_headers(user))
    assert r.status_code == 401, r.text


# ---------------------------------------------------------
# подмена типов токенов
# ---------------------------------------------------------

@pytest.mark.critical
async def test_access_with_refresh_token(client: AsyncClient, make_user):
    """refresh не должен работать как access."""
    user = await make_user()
    r = await client.post(
        "/api/v1/auth/login",
        json={"identifier": user.login, "password": TEST_PASSWORD},
    )
    refresh = r.json()["refresh_token"]

    me = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {refresh}"},
    )
    assert me.status_code == 401


@pytest.mark.critical
async def test_refresh_with_access_token(client: AsyncClient, make_user):
    """access не должен работать как refresh."""
    user = await make_user()
    r = await client.post(
        "/api/v1/auth/login",
        json={"identifier": user.login, "password": TEST_PASSWORD},
    )
    access = r.json()["access_token"]

    r2 = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": access},
    )
    assert r2.status_code == 401


# ---------------------------------------------------------
# refresh rotation
# ---------------------------------------------------------

async def test_refresh_rotation(client: AsyncClient, make_user):
    """Успешная ротация: old → new, new работает. Старый не трогаем повторно —
    это уже negative-сценарий, покрыт test_refresh_reuse_revokes_all."""
    user = await make_user()
    r = await client.post(
        "/api/v1/auth/login",
        json={"identifier": user.login, "password": TEST_PASSWORD},
    )
    old_refresh = r.json()["refresh_token"]

    r2 = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": old_refresh},
    )
    assert r2.status_code == 200, r2.text
    new_refresh = r2.json()["refresh_token"]
    assert new_refresh != old_refresh

    # Новый работает
    r4 = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": new_refresh},
    )
    assert r4.status_code == 200, r4.text


# ---------------------------------------------------------
# logout
# ---------------------------------------------------------

async def test_logout_revokes_refresh(client: AsyncClient, make_user):
    user = await make_user()
    r = await client.post(
        "/api/v1/auth/login",
        json={"identifier": user.login, "password": TEST_PASSWORD},
    )
    refresh = r.json()["refresh_token"]

    r_logout = await client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": refresh},
    )
    assert r_logout.status_code == 200, r_logout.text

    # После logout refresh не работает
    r_after = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh},
    )
    assert r_after.status_code == 401


async def test_logout_all_revokes_all_sessions(
    client: AsyncClient, make_user
):
    user = await make_user()

    # Две сессии (два логина)
    r1 = await client.post(
        "/api/v1/auth/login",
        json={"identifier": user.login, "password": TEST_PASSWORD},
    )
    r2 = await client.post(
        "/api/v1/auth/login",
        json={"identifier": user.login, "password": TEST_PASSWORD},
    )
    assert r1.status_code == r2.status_code == 200

    refresh_1 = r1.json()["refresh_token"]
    refresh_2 = r2.json()["refresh_token"]
    access_1 = r1.json()["access_token"]

    # logout-all
    r_la = await client.post(
        "/api/v1/auth/logout-all",
        headers={"Authorization": f"Bearer {access_1}"},
    )
    assert r_la.status_code == 200, r_la.text

    # Оба refresh теперь невалидны
    for refresh in (refresh_1, refresh_2):
        r_after = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh},
        )
        assert r_after.status_code == 401


# ---------------------------------------------------------
# В2: сверка владельца и типа токена
# ---------------------------------------------------------

def _forge_refresh(*, sub: str, jti: str, ttl_days: int = 1) -> str:
    """Собирает refresh-токен вручную — для тестов В2."""
    payload = {
        "sub": sub,
        "type": "refresh",
        "jti": jti,
        "exp": datetime.now(timezone.utc) + timedelta(days=ttl_days),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


@pytest.mark.critical
async def test_refresh_with_other_users_jti(client: AsyncClient, make_user):
    """Чужой jti при своём sub → 401, новые токены не выдаются."""
    user_a = await make_user()
    user_b = await make_user()

    r_b = await client.post(
        "/api/v1/auth/login",
        json={"identifier": user_b.login, "password": TEST_PASSWORD},
    )
    jti_b = decode_token(r_b.json()["refresh_token"])["jti"]

    forged = _forge_refresh(sub=str(user_a.id), jti=jti_b)
    r = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": forged},
    )
    assert r.status_code == 401, r.text


async def test_refresh_with_non_numeric_sub(client: AsyncClient, make_user):
    """sub='abc' → 401, а не 500 от int('abc')."""
    user = await make_user()
    r = await client.post(
        "/api/v1/auth/login",
        json={"identifier": user.login, "password": TEST_PASSWORD},
    )
    jti = decode_token(r.json()["refresh_token"])["jti"]

    forged = _forge_refresh(sub="abc", jti=jti)
    r2 = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": forged},
    )
    assert r2.status_code == 401, r2.text


@pytest.mark.critical
async def test_logout_with_access_token(client: AsyncClient, make_user):
    """logout принимает только refresh — access даёт 401."""
    user = await make_user()
    r = await client.post(
        "/api/v1/auth/login",
        json={"identifier": user.login, "password": TEST_PASSWORD},
    )
    access = r.json()["access_token"]

    r2 = await client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": access},
    )
    assert r2.status_code == 401, r2.text


@pytest.mark.critical
async def test_refresh_reuse_revokes_all(client: AsyncClient, make_user):
    user = await make_user()

    r1 = await client.post(
        "/api/v1/auth/login",
        json={"identifier": user.login, "password": TEST_PASSWORD},
    )
    r2 = await client.post(
        "/api/v1/auth/login",
        json={"identifier": user.login, "password": TEST_PASSWORD},
    )
    t1 = r1.json()["refresh_token"]
    t2 = r2.json()["refresh_token"]

    # Успешное обновление t1 → t1'
    r1_new = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": t1},
    )
    assert r1_new.status_code == 200, r1_new.text
    t1_prime = r1_new.json()["refresh_token"]

    # Reuse t1 → 401 + массовый отзыв
    r_reuse = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": t1},
    )
    assert r_reuse.status_code == 401, r_reuse.text

    # t1' и t2 тоже умерли
    for r in (t1_prime, t2):
        r_check = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": r},
        )
        assert r_check.status_code == 401, r_check.text


@pytest.mark.critical
async def test_refresh_reuse_does_not_affect_other_users(
    client: AsyncClient, make_user
):
    """Reuse у user_a не должен отзывать токены user_b."""
    user_a = await make_user()
    user_b = await make_user()

    ra = await client.post(
        "/api/v1/auth/login",
        json={"identifier": user_a.login, "password": TEST_PASSWORD},
    )
    ta = ra.json()["refresh_token"]

    rb = await client.post(
        "/api/v1/auth/login",
        json={"identifier": user_b.login, "password": TEST_PASSWORD},
    )
    tb = rb.json()["refresh_token"]

    # Обновляем ta
    await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": ta},
    )

    # Reuse ta → массовый отзыв только у user_a
    r_reuse = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": ta},
    )
    assert r_reuse.status_code == 401

    # tb у user_b работает
    r_tb = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": tb},
    )
    assert r_tb.status_code == 200, r_tb.text


@pytest.mark.critical
async def test_refresh_unknown_jti_does_not_revoke(
    client: AsyncClient, make_user
):
    """Неизвестный jti → 401, но не отзывает чужие токены."""
    user = await make_user()

    r1 = await client.post(
        "/api/v1/auth/login",
        json={"identifier": user.login, "password": TEST_PASSWORD},
    )
    t1 = r1.json()["refresh_token"]

    forged = _forge_refresh(sub=str(user.id), jti="nonexistent-jti-xyz")
    r_forged = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": forged},
    )
    assert r_forged.status_code == 401

    # t1 всё ещё работает
    r_t1 = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": t1},
    )
    assert r_t1.status_code == 200, r_t1.text


async def test_logout_idempotent(client: AsyncClient, make_user):
    """Повторный logout не отзывает остальные токены."""
    user = await make_user()

    r1 = await client.post(
        "/api/v1/auth/login",
        json={"identifier": user.login, "password": TEST_PASSWORD},
    )
    r2 = await client.post(
        "/api/v1/auth/login",
        json={"identifier": user.login, "password": TEST_PASSWORD},
    )
    t1 = r1.json()["refresh_token"]
    t2 = r2.json()["refresh_token"]

    # Первый logout
    r_out1 = await client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": t1},
    )
    assert r_out1.status_code == 200, r_out1.text

    # Второй logout с тем же t1 — тоже 200, без mass-revoke
    r_out2 = await client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": t1},
    )
    assert r_out2.status_code == 200, r_out2.text

    # t2 всё ещё работает
    r_t2 = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": t2},
    )
    assert r_t2.status_code == 200, r_t2.text


# ---------------------------------------------------------
# В4: max_length и timing
# ---------------------------------------------------------

async def test_login_password_too_long(client: AsyncClient):
    """Без max_length bcrypt будет доедать CPU на мегабайтном пароле."""
    r = await client.post(
        "/api/v1/auth/login",
        json={"identifier": "anyone", "password": "a" * 200},
    )
    assert r.status_code == 422


@pytest.mark.critical
async def test_login_wrong_password_and_unknown_same_timing_status(
    client: AsyncClient, make_user
):
    """Дополнительная (не временная) страховка: оба пути дают 401 + одинаковое тело.
    Точный timing assert в CI не пишем — флейки."""
    user = await make_user()

    r_wrong = await client.post(
        "/api/v1/auth/login",
        json={"identifier": user.login, "password": "WrongPassword-42x"},
    )
    r_unknown = await client.post(
        "/api/v1/auth/login",
        json={"identifier": "nobody_exists", "password": TEST_PASSWORD},
    )
    assert r_wrong.status_code == r_unknown.status_code == 401
    assert r_wrong.json() == r_unknown.json()


# ---------------------------------------------------------
# В5: каскад при удалении пользователя
# ---------------------------------------------------------

@pytest.mark.integration
async def test_delete_account_cascades_tokens(
    client: AsyncClient, session, make_user
):
    """Удаление юзера не падает + refresh-токены уходят каскадом."""
    from sqlalchemy import select, func
    from app.models.refresh_token import RefreshToken

    user = await make_user()
    r = await client.post(
        "/api/v1/auth/login",
        json={"identifier": user.login, "password": TEST_PASSWORD},
    )
    assert r.status_code == 200

    # Сколько токенов до
    before = (await session.execute(
        select(func.count()).select_from(RefreshToken)
        .where(RefreshToken.user_id == user.id)
    )).scalar()
    assert before >= 1

    # Удаляем юзера (как delete_account)
    await session.delete(user)
    await session.flush()

    after = (await session.execute(
        select(func.count()).select_from(RefreshToken)
        .where(RefreshToken.user_id == user.id)
    )).scalar()
    assert after == 0