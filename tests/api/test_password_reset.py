"""КРИТИЧНОЕ: запрос сброса (одинаковый ответ для любого email), сброс по токену, одноразовость"""
"""Password reset: forgot → reset, все состояния токена."""
from datetime import datetime, timedelta, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.password_reset_token import PasswordResetToken


BASE = "/api/v1/password-reset"


@pytest.fixture
def mail_capture(monkeypatch):
    """Мокаем EmailService.send_email, чтобы не ходить в Resend."""
    sent: list[dict] = []

    async def fake_send(self, *, to, subject, html):
        sent.append({"to": to, "subject": subject, "html": html})

    monkeypatch.setattr(
        "app.services.email.EmailService.send_email",
        fake_send,
    )
    return sent


# ---------------------------------------------------------
# /forgot-password
# ---------------------------------------------------------

async def test_forgot_password_creates_token_and_sends_email(
    client: AsyncClient,
    make_user,
    session: AsyncSession,
    mail_capture,
):
    user = await make_user()

    r = await client.post(
        f"{BASE}/forgot-password",
        json={"email": user.email},
    )
    assert r.status_code == 202, r.text
    assert "Если почта верна" in r.json()["message"]

    # письмо ушло
    assert len(mail_capture) == 1
    assert mail_capture[0]["to"] == user.email
    assert "token=" in mail_capture[0]["html"]

    # токен в БД
    stmt = select(PasswordResetToken).where(
        PasswordResetToken.user_id == user.id,
        PasswordResetToken.used.is_(False),
    )
    tokens = (await session.execute(stmt)).scalars().all()
    assert len(tokens) == 1


async def test_forgot_password_unknown_email_returns_same_message(
    client: AsyncClient,
    mail_capture,
):
    """Не палим существование email — одинаковый ответ."""
    r = await client.post(
        f"{BASE}/forgot-password",
        json={"email": "nobody@example.com"},
    )
    assert r.status_code == 202
    assert "Если почта верна" in r.json()["message"]
    assert len(mail_capture) == 0  # письмо не отправлено


async def test_forgot_password_replaces_old_token(
    client: AsyncClient,
    make_user,
    session: AsyncSession,
    mail_capture,
):
    """Повторный запрос удаляет старый неиспользованный токен."""
    user = await make_user()

    await client.post(f"{BASE}/forgot-password", json={"email": user.email})
    await client.post(f"{BASE}/forgot-password", json={"email": user.email})

    stmt = select(PasswordResetToken).where(
        PasswordResetToken.user_id == user.id,
    )
    tokens = (await session.execute(stmt)).scalars().all()
    assert len(tokens) == 1  # старый удалён


# ---------------------------------------------------------
# /reset-password
# ---------------------------------------------------------

async def test_reset_password_success(
    client: AsyncClient,
    make_user,
    session: AsyncSession,
    mail_capture,
):
    user = await make_user()

    await client.post(f"{BASE}/forgot-password", json={"email": user.email})
    html = mail_capture[0]["html"]
    token = html.split("token=")[1].split('"')[0].split("<")[0].strip()

    r = await client.post(
        f"{BASE}/reset-password",
        json={"token": token, "new_password": "NewTractor-Blue-99x"},
    )
    assert r.status_code == 200, r.text
    assert "успешно" in r.json()["message"].lower()

    # токен помечен used
    stmt = select(PasswordResetToken).where(
        PasswordResetToken.reset_token == token,
    )
    tok = (await session.execute(stmt)).scalar_one()
    assert tok.used is True


async def test_reset_password_then_login_with_new(
    client: AsyncClient,
    make_user,
    session: AsyncSession,
    mail_capture,
):
    """После сброса новый пароль работает, старый — нет."""
    user = await make_user()  # пароль по умолчанию из conftest

    await client.post(f"{BASE}/forgot-password", json={"email": user.email})
    html = mail_capture[0]["html"]
    token = html.split("token=")[1].split('"')[0].split("<")[0].strip()

    NEW_PASSWORD = "NewTractor-Blue-99x"
    r = await client.post(
        f"{BASE}/reset-password",
        json={"token": token, "new_password": NEW_PASSWORD},
    )
    assert r.status_code == 200

    # старый пароль не работает
    from tests.api.test_auth import TEST_PASSWORD
    r = await client.post(
        "/api/v1/auth/login",
        json={"identifier": user.login, "password": TEST_PASSWORD},
    )
    assert r.status_code == 401

    # новый работает
    r = await client.post(
        "/api/v1/auth/login",
        json={"identifier": user.login, "password": NEW_PASSWORD},
    )
    assert r.status_code == 200


async def test_reset_password_revokes_refresh_tokens(
    client: AsyncClient,
    make_user,
    mail_capture,
):
    """Сброс пароля отзывает все refresh."""
    user = await make_user()
    from tests.api.test_auth import TEST_PASSWORD

    # логинимся — получаем refresh
    r = await client.post(
        "/api/v1/auth/login",
        json={"identifier": user.login, "password": TEST_PASSWORD},
    )
    refresh = r.json()["refresh_token"]

    # сбрасываем пароль
    await client.post(f"{BASE}/forgot-password", json={"email": user.email})
    html = mail_capture[0]["html"]
    token = html.split("token=")[1].split('"')[0].split("<")[0].strip()
    await client.post(
        f"{BASE}/reset-password",
        json={"token": token, "new_password": "NewTractor-Blue-99x"},
    )

    # старый refresh мёртв
    r = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh},
    )
    assert r.status_code == 401


async def test_reset_password_unknown_token(
    client: AsyncClient,
):
    r = await client.post(
        f"{BASE}/reset-password",
        json={"token": "does-not-exist", "new_password": "ValidPass-1234"},
    )
    assert r.status_code == 401


async def test_reset_password_used_token(
    client: AsyncClient,
    make_user,
    session: AsyncSession,
):
    user = await make_user()
    token = PasswordResetToken(
        user_id=user.id,
        reset_token="already-used",
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        used=True,
    )
    session.add(token)
    await session.flush()

    r = await client.post(
        f"{BASE}/reset-password",
        json={"token": "already-used", "new_password": "ValidPass-1234"},
    )
    assert r.status_code == 401


async def test_reset_password_expired_token(
    client: AsyncClient,
    make_user,
    session: AsyncSession,
):
    """Протухший токен → 401 (не 500 от naive/aware)."""
    user = await make_user()
    token = PasswordResetToken(
        user_id=user.id,
        reset_token="expired-token",
        expires_at=datetime.now(timezone.utc) - timedelta(hours=2),
        used=False,
    )
    session.add(token)
    await session.flush()

    r = await client.post(
        f"{BASE}/reset-password",
        json={"token": "expired-token", "new_password": "ValidPass-1234"},
    )
    assert r.status_code == 401


async def test_reset_password_weak_password_422(
    client: AsyncClient,
    make_user,
    mail_capture,
):
    """Слабый пароль не пройдёт Pydantic-валидатор (schemas/auth.py)."""
    user = await make_user()
    await client.post(f"{BASE}/forgot-password", json={"email": user.email})
    html = mail_capture[0]["html"]
    token = html.split("token=")[1].split('"')[0].split("<")[0].strip()

    r = await client.post(
        f"{BASE}/reset-password",
        json={"token": token, "new_password": "short"},
    )
    assert r.status_code == 422