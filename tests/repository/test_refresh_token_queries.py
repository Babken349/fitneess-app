"""revoke_all_for_user, delete_expired_tokens"""
async def test_revoke_atomic_second_call_returns_zero(session, make_user):
    """Первый revoke — 1, второй на том же jti — 0."""
    from datetime import datetime, timedelta, timezone

    from app.models.refresh_token import RefreshToken
    from app.repository import refresh_tokens as refresh_repository

    user = await make_user()
    token = RefreshToken(
        user_id=user.id,
        jti="atomic-test-jti",
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )
    session.add(token)
    await session.flush()

    n1 = await refresh_repository.revoke(session, token)
    assert n1 == 1

    n2 = await refresh_repository.revoke(session, token)
    assert n2 == 0