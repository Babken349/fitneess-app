from pydantic import EmailStr
from sqlalchemy import select, or_
from sqlalchemy.orm import Session
from app.schemas.users import UserCreate, UserUpdate
from app.models.users import User 
from datetime import datetime, timezone


def create_user(db: Session, user: UserCreate, hashed_password: str) -> User:
    db_user = User(
        login=user.login,
        hashed_password=hashed_password,
        email=user.email
    )
    db.add(db_user)
    # commit и refresh убраны!
    return db_user


def get_user_by_identifier(db: Session, identifier: str) -> User | None:
    stmt = select(User).where(or_(User.login == identifier, User.email == identifier))
    result = db.execute(stmt)
    return result.scalar_one_or_none()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    stmt = select(User).where(User.id == user_id)
    result = db.execute(stmt)
    return result.scalar_one_or_none()


def update_user(db: Session, user_db: User, user_update: UserUpdate) -> User:
    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user_db, key, value)
    # commit и refresh убраны!
    return user_db


def update_password(db: Session, user_db: User, new_hashed_password: str) -> User:
    user_db.hashed_password = new_hashed_password
    return user_db


def update_email(db: Session, user_db: User, new_email: EmailStr) -> User:
    user_db.email = new_email
    return user_db


def update_login(db: Session, user_db: User, new_login: str) -> User:
    user_db.login = new_login
    return user_db


def update_last_login(db: Session, user_db: User) -> User:
    user_db.last_login = datetime.now(timezone.utc)
    return user_db


def delete_user(db: Session, user_db: User) -> None:
    db.delete(user_db)
    # commit убран!


def get_all_users(db: Session, skip: int = 0, limit: int = 20) -> list[User]:
    stmt = select(User).offset(skip).limit(limit)
    result = db.execute(stmt)
    return result.scalars().all()


def search_users(db: Session, query: str, limit: int = 10) -> list[User]:
    search_pattern = f"%{query}%"
    stmt = select(User).where(
        or_(
            User.login.ilike(search_pattern),
            User.display_name.ilike(search_pattern)
        )
    ).limit(limit)
    result = db.execute(stmt)
    return result.scalars().all()


def get_users_by_ids(db: Session, user_ids: list[int]) -> list[User]:
    stmt = select(User).where(User.id.in_(user_ids))
    result = db.execute(stmt)
    return result.scalars().all()


def exists_by_email(db: Session, email: EmailStr) -> bool:
    stmt = select(User).where(User.email == email)
    result = db.execute(stmt)
    return result.scalar_one_or_none() is not None


def exists_by_login(db: Session, login: str) -> bool:
    stmt = select(User).where(User.login == login)
    result = db.execute(stmt)
    return result.scalar_one_or_none() is not None