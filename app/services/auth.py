from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import InvalidCredentialsError
from app.models.users import User

from app.schemas.auth import Token, RefreshTokenRequest
from app.schemas.users import UserLogin
from app.repository import users as users_repository
from app.repository import refresh_tokens as refresh_repository
from app.auth.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.utils.password import password_manager
_DUMMY_HASH = "$2b$12$s9HbiDiRmWPUOrTRhtvAhut.ZC5Gn31wC7qU4PfWWfVyVNjIsiUlO"

async def login(db: AsyncSession, credentials: UserLogin) -> Token:
    user = await users_repository.get_user_by_identifier(db, credentials.identifier)

    hashed = user.hashed_password if user is not None else _DUMMY_HASH
    ok = await password_manager.verify(credentials.password, hashed)

    if user is None or not ok:
        raise InvalidCredentialsError()

    if not user.is_active:
        raise InvalidCredentialsError()

    access_token = create_access_token(user_id=user.id, role=user.role)
    refresh_token, jti, expires_at = create_refresh_token(user_id=user.id)

    refresh_repository.create_refresh_token(
        db=db,
        user_id=user.id,
        jti=jti,
        expires_at=expires_at,
    )
    users_repository.update_last_login(db, user)

    await db.commit()

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


async def refresh_token(db: AsyncSession, token_data: RefreshTokenRequest) -> Token:
    payload = decode_token(token_data.refresh_token)
    if payload.get("type") != "refresh":
        raise InvalidCredentialsError()

    user_id = payload.get("sub")
    jti = payload.get("jti")
    if user_id is None or jti is None:
        raise InvalidCredentialsError()

    try:
        user_id_int = int(user_id)
    except (TypeError, ValueError):
        raise InvalidCredentialsError()

    token_db = await refresh_repository.get_by_jti(db, jti)

    # Неизвестный jti — просто 401, без массового отзыва
    if token_db is None:
        raise InvalidCredentialsError()

    # В2: сверка владельца
    if token_db.user_id != user_id_int:
        raise InvalidCredentialsError()

    # В1: повторное использование уже отозванного токена
    # → отзываем ВСЕ токены пользователя и коммитим ДО raise
    if token_db.revoked:
        await refresh_repository.revoke_all_for_user(db, token_db.user_id)
        await db.commit()
        raise InvalidCredentialsError()

    # Атомарный отзыв: если 0 строк — кто-то успел раньше (гонка)
    rowcount = await refresh_repository.revoke(db, token_db)
    if rowcount == 0:
        await refresh_repository.revoke_all_for_user(db, token_db.user_id)
        await db.commit()
        raise InvalidCredentialsError()

    user = await users_repository.get_user_by_id(db, user_id_int)
    if user is None:
        raise InvalidCredentialsError()

    if not user.is_active:
        raise InvalidCredentialsError()

    access_token = create_access_token(user_id=user.id, role=user.role)
    new_refresh_token, new_jti, expires_at = create_refresh_token(user_id=user.id)

    refresh_repository.create_refresh_token(
        db=db,
        user_id=user.id,
        jti=new_jti,
        expires_at=expires_at,
    )

    await db.commit()

    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
    )


async def logout(db: AsyncSession, token: RefreshTokenRequest):
    payload = decode_token(token.refresh_token)
    if payload.get("type") != "refresh":
        raise InvalidCredentialsError()

    jti = payload.get("jti")
    if jti is None:
        raise InvalidCredentialsError()

    token_db = await refresh_repository.get_by_jti(db, jti)
    if token_db is None:
        raise InvalidCredentialsError()

    # Идемпотентно: повторный logout не идёт в ветку mass-revoke
    await refresh_repository.revoke(db, token_db)
    await db.commit()


async def logout_all(db: AsyncSession, user: User):
    await refresh_repository.revoke_all_for_user(db, user.id)
    await db.commit()