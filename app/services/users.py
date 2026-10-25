from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.users import UserCreate, UserUpdate, ChangePassword, ChangeEmail, ChangeLogin
from app.models.users import User
from app.repository import users as users_repository
from app.utils.password import password_manager
from app.exceptions import (
    UserNotFoundError, EmailAlreadyExistsError,
    LoginAlreadyExistsError, InvalidPasswordError,
)


async def create_user(db: AsyncSession, user: UserCreate) -> User:
    if await users_repository.exists_by_email(db, user.email):
        raise EmailAlreadyExistsError(user.email)

    if await users_repository.exists_by_login(db, user.login):
        raise LoginAlreadyExistsError(user.login)

    hashed_password = await password_manager.hash(user.password)

    created_user = users_repository.create_user(
        db=db,
        user=user,
        hashed_password=hashed_password,
    )

    # СОХРАНЯЕМ В БАЗУ
    await db.commit()
    await db.refresh(created_user)
    return created_user


async def get_user_by_id(db: AsyncSession, user_id: int) -> User:
    user = await users_repository.get_user_by_id(db=db, user_id=user_id)
    if not user:
        raise UserNotFoundError(user_id=user_id)
    return user


async def update_profile(db: AsyncSession, user_db: User, user_update: UserUpdate) -> User:
    users_repository.update_user(db, user_db, user_update)
    # СОХРАНЯЕМ В БАЗУ
    await db.commit()
    await db.refresh(user_db)
    return user_db


async def change_password(db: AsyncSession, user_db: User, data: ChangePassword) -> User:
    if not await password_manager.verify(data.old_password, user_db.hashed_password):
        raise InvalidPasswordError()
    new_hashed = await password_manager.hash(data.new_password)
    users_repository.update_password(db, user_db, new_hashed)

    # СОХРАНЯЕМ В БАЗУ
    await db.commit()
    await db.refresh(user_db)
    return user_db


async def change_email(db: AsyncSession, user_db: User, data: ChangeEmail) -> User:
    if not await password_manager.verify(data.password, user_db.hashed_password):
        raise InvalidPasswordError()

    if await users_repository.exists_by_email(db, data.new_email):
        raise EmailAlreadyExistsError(data.new_email)

    users_repository.update_email(db, user_db, data.new_email)

    # СОХРАНЯЕМ В БАЗУ
    await db.commit()
    await db.refresh(user_db)
    return user_db


async def change_login(db: AsyncSession, user_db: User, data: ChangeLogin) -> User:
    if not await password_manager.verify(data.password, user_db.hashed_password):
        raise InvalidPasswordError()

    if await users_repository.exists_by_login(db, data.new_login):
        raise LoginAlreadyExistsError(data.new_login)

    users_repository.update_login(db, user_db, data.new_login)

    # СОХРАНЯЕМ В БАЗУ
    await db.commit()
    await db.refresh(user_db)
    return user_db


async def delete_account(db: AsyncSession, user_db: User, password: str) -> bool:
    if not await password_manager.verify(password, user_db.hashed_password):
        raise InvalidPasswordError()

    await users_repository.delete_user(db, user_db)
    # СОХРАНЯЕМ В БАЗУ
    await db.commit()
    return True