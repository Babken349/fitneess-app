"""КРИТИЧНОЕ: отправка (почта подменена), verify, повторное использование и просроченный токен"""
"""Email verification: send + verify, все состояния токена."""
from datetime import datetime, timedelta, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.email_verification_token import EmailVerificationToken


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
# POST /send
# ---------------------------------------------------------

async def test_send_requires_auth(client: AsyncClient):
    r = await client.post("/api/v1/email-verification/send")
    assert r.status_code == 401


async def test_send_creates_token_and_sends_email(
    client: AsyncClient,
    make_user,
    auth_headers,
    session: AsyncSession,
    mail_capture,
):
    user = await make_user(is_verified=False)

    r = await client.post(
        "/api/v1/email-verification/send",
        headers=auth_headers(user),
    )
    assert r.status_code == 202, r.text
    assert r.json()["message"] == "Verification email sent"

    # письмо отправлено
    assert len(mail_capture) == 1
    assert mail_capture[0]["to"] == user.email
    assert "verify?token=" in mail_capture[0]["html"]

    # токен создан в БД
    stmt = select(EmailVerificationToken).where(
        EmailVerificationToken.user_id == user.id,
        EmailVerificationToken.used.is_(False),
    )
    tokens = (await session.execute(stmt)).scalars().all()
    assert len(tokens) == 1


async def test_send_for_verified_user_returns_400(
    client: AsyncClient,
    make_user,
    auth_headers,
    mail_capture,
):
    user = await make_user(is_verified=True)

    r = await client.post(
        "/api/v1/email-verification/send",
        headers=auth_headers(user),
    )
    assert r.status_code == 400
    assert len(mail_capture) == 0


async def test_send_replaces_old_token(
    client: AsyncClient,
    make_user,
    auth_headers,
    session: AsyncSession,
    mail_capture,
):
    """Повторный /send удаляет старый активный токен."""
    user = await make_user(is_verified=False)
    h = auth_headers(user)

    await client.post("/api/v1/email-verification/send", headers=h)
    await client.post("/api/v1/email-verification/send", headers=h)

    stmt = select(EmailVerificationToken).where(
        EmailVerificationToken.user_id == user.id,
        EmailVerificationToken.used.is_(False),
    )
    tokens = (await session.execute(stmt)).scalars().all()
    assert len(tokens) == 1  # старый удалён


# ---------------------------------------------------------
# GET /verify
# ---------------------------------------------------------

async def test_verify_success(
    client: AsyncClient,
    make_user,
    auth_headers,
    session: AsyncSession,
    mail_capture,
):
    user = await make_user(is_verified=False)
    await client.post(
        "/api/v1/email-verification/send",
        headers=auth_headers(user),
    )
    # достаём токен из письма
    html = mail_capture[0]["html"]
    token = html.split("verify?token=")[1].split('"')[0].split("<")[0].strip()

    r = await client.get(
        "/api/v1/email-verification/verify",
        params={"token": token},
    )
    assert r.status_code == 200, r.text
    assert r.json()["message"] == "Email successfully verified"

    # user.is_verified = True
    await session.refresh(user)
    assert user.is_verified is True

    # токен помечен used
    stmt = select(EmailVerificationToken).where(
        EmailVerificationToken.token == token,
    )
    tok = (await session.execute(stmt)).scalar_one()
    assert tok.used is True


async def test_verify_unknown_token_returns_404(client: AsyncClient):
    r = await client.get(
        "/api/v1/email-verification/verify",
        params={"token": "does-not-exist"},
    )
    assert r.status_code == 404


async def test_verify_used_token_returns_400(
    client: AsyncClient,
    make_user,
    session: AsyncSession,
):
    """Уже использованный токен → 400."""
    user = await make_user(is_verified=False)

    token = EmailVerificationToken(
        user_id=user.id,
        token="already-used-token",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=30),
        used=True,
    )
    session.add(token)
    await session.flush()

    r = await client.get(
        "/api/v1/email-verification/verify",
        params={"token": "already-used-token"},
    )
    assert r.status_code == 400


async def test_verify_expired_token_returns_400(
    client: AsyncClient,
    make_user,
    session: AsyncSession,
):
    """Протухший токен → 400 (а не 500 от TypeError)."""
    user = await make_user(is_verified=False)

    token = EmailVerificationToken(
        user_id=user.id,
        token="expired-token-xxx",
        expires_at=datetime.now(timezone.utc) - timedelta(minutes=5),
        used=False,
    )
    session.add(token)
    await session.flush()

    r = await client.get(
        "/api/v1/email-verification/verify",
        params={"token": "expired-token-xxx"},
    )
    assert r.status_code == 400


async def test_verify_when_already_verified_returns_400(
    client: AsyncClient,
    make_user,
    session: AsyncSession,
):
    """Юзер уже verified, но токен не использован → 400."""
    user = await make_user(is_verified=True)

    token = EmailVerificationToken(
        user_id=user.id,
        token="valid-but-user-verified",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=30),
        used=False,
    )
    session.add(token)
    await session.flush()

    r = await client.get(
        "/api/v1/email-verification/verify",
        params={"token": "valid-but-user-verified"},
    )
    assert r.status_code == 400