from datetime import datetime, timezone
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.password_reset_token import PasswordResetToken


def create_reset_token(db: AsyncSession, token_model: PasswordResetToken) -> PasswordResetToken:
    # Просто добавляем объект в сессию. Коммитить будет Сервис!
    db.add(token_model)
    # db.flush() можно вызвать, если нам сразу нужен token_model.id, 
    # но так как мы возвращаем сам объект, достаточно просто add.
    return token_model


async def get_by_token(db: AsyncSession, token_string: str) -> PasswordResetToken | None:
    stmt = select(PasswordResetToken).where(
        PasswordResetToken.reset_token == token_string
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def delete_user_tokens(db: AsyncSession, user_id: int) -> None:
    # Просто выполняем DELETE-запрос. Коммитит Сервис!
    stmt = delete(PasswordResetToken).where(
        PasswordResetToken.user_id == user_id
    )
    await db.execute(stmt)


def mark_used(db: AsyncSession, token_db: PasswordResetToken) -> PasswordResetToken:
    # Меняем поле объекта. Коммитит Сервис!
    token_db.used = True
    return token_db


async def delete_expired_tokens(db: AsyncSession) -> None:

    # Просто выполняем DELETE-запрос.
    
    stmt = delete(PasswordResetToken).where(
        PasswordResetToken.expires_at < datetime.now(timezone.utc)
    )
    await db.execute(stmt)