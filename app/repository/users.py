from pydantic import EmailStr
from sqlalchemy import select, or_
from sqlalchemy.orm import Session
from app.schemas.users import UserCreate, UserLogin, UserResponse, UserUpdate
from app.models import users
from app.models.users import User 
from datetime import datetime, timezone
from typing import Any


def create_user(db: Session, user: UserCreate, hashed_password: str) -> User:
    db_user = User(
        login=user.login,
        hashed_password=hashed_password,
        email=user.email
        )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

def get_user_by_identifier(db: Session, identifier: str) -> User | None:
    stmt  = select(User).where(or_(User.login == identifier,  User.email == identifier))
    result = db.execute(stmt)
    return result.scalar_one_or_none()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    stmt  = select(User).where(User.id == user_id)
    result  = db.execute(stmt)
    return result.scalar_one_or_none()

def update_user(db: Session, user_db: User, user_update: UserUpdate) -> User:
    # Берем только те поля, которые реально прислал клиент (не None)
    update_data = user_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
         setattr(user_db, key, value)
    db.commit()
    db.refresh(user_db)
    return user_db

def update_password(db: Session, user_db: User, new_hashed_password: str) -> User:
    user_db.hashed_password = new_hashed_password
    db.commit()
    db.refresh(user_db)
    return user_db

def update_email(db: Session, user_db: User, new_email: EmailStr) -> User:
    user_db.email = new_email
    db.commit()
    db.refresh(user_db)
    return user_db


def update_login(db: Session, user_db: User, new_login: str) -> User:
    user_db.login = new_login
    db.commit()
    db.refresh(user_db)
    return user_db


def update_last_login(db: Session, user_db: User) -> User:
    user_db.last_login = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user_db)
    return user_db


def delete_user(db: Session, user_db: User) -> bool:
    db.delete(user_db)
    db.commit()
    return True




def get_all_users(db: Session, skip: int = 0, limit: int = 20) -> list[User]:
    """Получить список всех пользователей (с пагинацией для админки)"""
    stmt = select(User).offset(skip).limit(limit)
    result = db.execute(stmt)
    return result.scalars().all()


def search_users(db: Session, query: str, limit: int = 10) -> list[User]:
    """Поиск пользователей по логину или имени (для фичи GymBro)"""
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
    """Получить список пользователей по их ID (например, для списка друзей)"""
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