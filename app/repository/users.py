from pydantic import EmailStr
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.users import UserCreate, UserUpdate
from app.models.users import User
from datetime import datetime, timezone


def create_user(db: AsyncSession, user: UserCreate, hashed_password: str) -> User:
    db_user = User(
        login=user.login,
        hashed_password=hashed_password,
        email=user.email
    )
    db.add(db_user)
    # commit и refresh убраны!
    return db_user


async def get_user_by_identifier(db: AsyncSession, identifier: str) -> User | None:
    stmt = select(User).where(or_(User.login == identifier, User.email == identifier))
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


def update_user(db: AsyncSession, user_db: User, user_update: UserUpdate) -> User:
    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user_db, key, value)
    # commit и refresh убраны!
    return user_db


def update_password(db: AsyncSession, user_db: User, new_hashed_password: str) -> User:
    user_db.hashed_password = new_hashed_password
    return user_db


def update_email(db: AsyncSession, user_db: User, new_email: EmailStr) -> User:
    user_db.email = new_email
    return user_db


def update_login(db: AsyncSession, user_db: User, new_login: str) -> User:
    user_db.login = new_login
    return user_db


def update_last_login(db: AsyncSession, user_db: User) -> User:
    user_db.last_login = datetime.now(timezone.utc)
    return user_db


async def delete_user(db: AsyncSession, user_db: User) -> None:
    await db.delete(user_db)
    # commit убран!


async def get_all_users(db: AsyncSession, skip: int = 0, limit: int = 20) -> list[User]:
    stmt = select(User).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


async def search_users(db: AsyncSession, query: str, limit: int = 10) -> list[User]:
    search_pattern = f"%{query}%"
    stmt = select(User).where(
        or_(
            User.login.ilike(search_pattern),
            User.display_name.ilike(search_pattern)
        )
    ).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_users_by_ids(db: AsyncSession, user_ids: list[int]) -> list[User]:
    stmt = select(User).where(User.id.in_(user_ids))
    result = await db.execute(stmt)
    return result.scalars().all()


async def exists_by_email(db: AsyncSession, email: EmailStr) -> bool:
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    return result.scalar_one_or_none() is not None


async def exists_by_login(db: AsyncSession, login: str) -> bool:
    stmt = select(User).where(User.login == login)
    result = await db.execute(stmt)
    return result.scalar_one_or_none() is not None