"""КРИТИЧНОЕ: профиль, смена пароля, email, логина (неверный пароль даёт отказ), удаление аккаунта"""
"""Users: register, /me, admin-panel, premium-content, get by id."""
from datetime import datetime, timedelta, timezone

import pytest
from httpx import AsyncClient

from app.models.users import User


BASE = "/api/v1/users"
TEST_PASSWORD = "Tractor-Blue-42x"


# ---------------------------------------------------------
# register
# ---------------------------------------------------------

async def test_register_success(client: AsyncClient):
    r = await client.post(
        f"{BASE}/register",
        json={
            "login": "newuser123",
            "email": "newuser123@example.com",
            "password": TEST_PASSWORD,
        },
    )
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["login"] == "newuser123"
    assert data["email"] == "newuser123@example.com"
    assert data["is_active"] is True
    assert data["is_verified"] is False
    assert "id" in data


async def test_register_does_not_leak_password(client: AsyncClient):
    """Ни в каком виде hashed_password не уходит в ответ."""
    r = await client.post(
        f"{BASE}/register",
        json={
            "login": "leaktest",
            "email": "leaktest@example.com",
            "password": TEST_PASSWORD,
        },
    )
    assert r.status_code == 201
    body = r.text.lower()
    assert "password" not in body
    assert "hashed" not in body
    assert TEST_PASSWORD not in r.text


async def test_register_duplicate_email(client: AsyncClient, make_user):
    existing = await make_user()
    r = await client.post(
        f"{BASE}/register",
        json={
            "login": "unique_login",
            "email": existing.email,
            "password": TEST_PASSWORD,
        },
    )
    assert r.status_code == 409


async def test_register_duplicate_login(client: AsyncClient, make_user):
    existing = await make_user()
    r = await client.post(
        f"{BASE}/register",
        json={
            "login": existing.login,
            "email": "unique_email@example.com",
            "password": TEST_PASSWORD,
        },
    )
    assert r.status_code == 409


async def test_register_weak_password_422(client: AsyncClient):
    """Пароль <10 символов не пройдёт валидатор."""
    r = await client.post(
        f"{BASE}/register",
        json={
            "login": "weakpwduser",
            "email": "weakpwd@example.com",
            "password": "short",
        },
    )
    assert r.status_code == 422


async def test_register_invalid_email_422(client: AsyncClient):
    r = await client.post(
        f"{BASE}/register",
        json={
            "login": "invalidemail",
            "email": "not-an-email",
            "password": TEST_PASSWORD,
        },
    )
    assert r.status_code == 422


async def test_register_can_login_after(client: AsyncClient):
    """Косвенная проверка: пароль захэширован правильно и verify работает."""
    r = await client.post(
        f"{BASE}/register",
        json={
            "login": "loginafter",
            "email": "loginafter@example.com",
            "password": TEST_PASSWORD,
        },
    )
    assert r.status_code == 201

    r = await client.post(
        "/api/v1/auth/login",
        json={"identifier": "loginafter", "password": TEST_PASSWORD},
    )
    assert r.status_code == 200


# ---------------------------------------------------------
# /me
# ---------------------------------------------------------

async def test_me_requires_auth(client: AsyncClient):
    r = await client.get(f"{BASE}/me")
    assert r.status_code == 401


async def test_me_returns_current_user(
    client: AsyncClient, make_user, auth_headers
):
    user = await make_user()
    r = await client.get(f"{BASE}/me", headers=auth_headers(user))
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == user.id
    assert data["login"] == user.login


async def test_me_does_not_leak_password(
    client: AsyncClient, make_user, auth_headers
):
    user = await make_user()
    r = await client.get(f"{BASE}/me", headers=auth_headers(user))
    assert r.status_code == 200
    body = r.text.lower()
    assert "password" not in body
    assert "hashed" not in body


# ---------------------------------------------------------
# admin-panel
# ---------------------------------------------------------

async def test_admin_panel_forbidden_for_user(
    client: AsyncClient, make_user, auth_headers
):
    user = await make_user()  # role="user"
    r = await client.get(
        f"{BASE}/admin-panel", headers=auth_headers(user)
    )
    assert r.status_code == 403


async def test_admin_panel_allowed_for_admin(
    client: AsyncClient, admin, auth_headers
):
    r = await client.get(
        f"{BASE}/admin-panel", headers=auth_headers(admin)
    )
    assert r.status_code == 200
    assert r.json()["id"] == admin.id


async def test_admin_panel_requires_auth(client: AsyncClient):
    r = await client.get(f"{BASE}/admin-panel")
    assert r.status_code == 401


# ---------------------------------------------------------
# premium-content
# ---------------------------------------------------------

async def test_premium_forbidden_without_premium(
    client: AsyncClient, make_user, auth_headers
):
    """premium_until=None → 403."""
    user = await make_user(premium_until=None)
    r = await client.get(
        f"{BASE}/premium-content", headers=auth_headers(user)
    )
    assert r.status_code == 403


async def test_premium_allowed_with_future_premium(
    client: AsyncClient, make_user, auth_headers
):
    future = datetime.now(timezone.utc) + timedelta(days=30)
    user = await make_user(premium_until=future)
    r = await client.get(
        f"{BASE}/premium-content", headers=auth_headers(user)
    )
    assert r.status_code == 200


async def test_premium_forbidden_with_expired_premium(
    client: AsyncClient, make_user, auth_headers
):
    """premium_until в прошлом → 403 (регрессия К3: timestamptz + require_premium)."""
    past = datetime.now(timezone.utc) - timedelta(days=1)
    user = await make_user(premium_until=past)
    r = await client.get(
        f"{BASE}/premium-content", headers=auth_headers(user)
    )
    assert r.status_code == 403


async def test_premium_requires_auth(client: AsyncClient):
    r = await client.get(f"{BASE}/premium-content")
    assert r.status_code == 401


# ---------------------------------------------------------
# get user by id — публичный endpoint
# ---------------------------------------------------------

async def test_get_user_by_id_public(
    client: AsyncClient, make_user
):
    """Endpoint без Depends(get_current_user) — публичный."""
    user = await make_user()
    r = await client.get(f"{BASE}/{user.id}")
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == user.id
    assert data["login"] == user.login


async def test_get_user_by_id_not_found(client: AsyncClient):
    r = await client.get(f"{BASE}/999999")
    assert r.status_code == 404


async def test_get_user_by_id_no_password_leak(
    client: AsyncClient, make_user
):
    user = await make_user()
    r = await client.get(f"{BASE}/{user.id}")
    assert r.status_code == 200
    body = r.text.lower()
    assert "password" not in body
    assert "hashed" not in body