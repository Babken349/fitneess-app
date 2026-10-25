from datetime import datetime, timezone
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.refresh_token import RefreshToken


def create_refresh_token(
    db: AsyncSession,
    user_id: int,
    jti: str,
    expires_at: datetime,
) -> RefreshToken:
    db_token = RefreshToken(
        user_id=user_id,
        jti=jti,
        expires_at=expires_at,
    )
    db.add(db_token)
    # Никаких commit и refresh!
    return db_token


async def get_by_jti(db: AsyncSession, jti: str) -> RefreshToken | None:
    stmt = select(RefreshToken).where(RefreshToken.jti == jti)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def revoke(db: AsyncSession, token_db: RefreshToken) -> int:
    """Атомарно отзывает токен. Возвращает rowcount:
    1 — отозвали мы, 0 — уже был отозван кем-то другим (гонка)."""
    stmt = (
        update(RefreshToken)
        .where(RefreshToken.id == token_db.id, RefreshToken.revoked.is_(False))
        .values(revoked=True)
    )
    result = await db.execute(stmt)
    return result.rowcount or 0


async def revoke_all_for_user(db: AsyncSession, user_id: int) -> None:
    stmt = select(RefreshToken).where(
        RefreshToken.user_id == user_id,
        RefreshToken.revoked.is_(False),
    )
    tokens = (await db.execute(stmt)).scalars().all()

    for token in tokens:
        token.revoked = True
    # Никаких commit!


async def delete_by_jti(db: AsyncSession, jti: str) -> None:

    stmt = delete(RefreshToken).where(RefreshToken.jti == jti)
    await db.execute(stmt)



async def delete_expired_tokens(db: AsyncSession) -> int:

    stmt = delete(RefreshToken).where(
        RefreshToken.expires_at < datetime.now(timezone.utc),
    )

    result = await db.execute(stmt)

    return result.rowcount or 0