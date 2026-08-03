from datetime import datetime, timezone
from sqlalchemy import delete, select
from sqlalchemy.orm import Session
from app.models.refresh_token import RefreshToken


def create_refresh_token(
    db: Session,
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


def get_by_jti(db: Session, jti: str) -> RefreshToken | None:
    stmt = select(RefreshToken).where(RefreshToken.jti == jti)
    result = db.execute(stmt)
    return result.scalar_one_or_none()


def revoke(db: Session, token_db: RefreshToken) -> RefreshToken:
    token_db.revoked = True
    # Только меняем поле!
    return token_db


def revoke_all_for_user(db: Session, user_id: int) -> None:
    stmt = select(RefreshToken).where(
        RefreshToken.user_id == user_id,
        RefreshToken.revoked.is_(False),
    )
    tokens = db.execute(stmt).scalars().all()

    for token in tokens:
        token.revoked = True
    # Никаких commit!


def delete_by_jti(db: Session, jti: str) -> None:

    stmt = delete(RefreshToken).where(RefreshToken.jti == jti)
    db.execute(stmt)



def delete_expired_tokens(db: Session) -> int:

    stmt = delete(RefreshToken).where(
        RefreshToken.expires_at < datetime.now(timezone.utc),
    )

    result = db.execute(stmt)

    return result.rowcount or 0