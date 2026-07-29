from datetime import date
from signal import raise_signal

from app.models import users
from sqlalchemy.orm import Session

from app.schemas.users import UserCreate, UserUpdate, ChangePassword, ChangeEmail, ChangeLogin
from app.models.users import User
from app.repository import users as users_repository
from app.utils.password import password_manager
from app.exceptions import (
    UserNotFoundError, EmailAlreadyExistsError,
    LoginAlreadyExistsError, InvalidPasswordError,
)


def create_user(db: Session, user: UserCreate) -> User:
    if users_repository.exists_by_email(db, user.email):
        raise EmailAlreadyExistsError(user.email)

    if users_repository.exists_by_login(db, user.login):
        raise LoginAlreadyExistsError(user.login)

    hashed_password = password_manager.hash(user.password)

    return users_repository.create_user(
        db=db,
        user=user,
        hashed_password=hashed_password,
    )


def get_user_by_id(db: Session, user_id: int) -> User:
    user = users_repository.get_user_by_id(db=db, user_id=user_id)
    if not user:
        raise UserNotFoundError(user_id=user_id)
    return user

def update_profile(db: Session, user_db: User, user_update: UserUpdate) -> User:
    return users_repository.update_user(db, user_db, user_update)

def change_password(db: Session, user_db: User, data: ChangePassword) -> User:
    if not password_manager.verify(data.old_password, user_db.hashed_password):
        raise InvalidPasswordError()
    new_hashed = password_manager.hash(data.new_password)
    return users_repository.update_password(db, user_db, new_hashed)

def change_email(db: Session, user_db: User, data: ChangeEmail) -> User:
    if not password_manager.verify(data.password, user_db.hashed_password):
        raise InvalidPasswordError()

    if users_repository.exists_by_email(db, data.new_email):
        raise EmailAlreadyExistsError(data.new_email)

    return users_repository.update_email(db, user_db, data.new_email)


def change_login(db: Session, user_db: User, data: ChangeLogin) -> User:
    if not password_manager.verify(data.password, user_db.hashed_password):
        raise InvalidPasswordError()

    if users_repository.exists_by_login(db, data.new_login):
        raise LoginAlreadyExistsError(data.new_login)

    return users_repository.update_login(db, user_db, data.new_login)


def delete_account(db: Session, user_db: User, password: str) -> bool:
    if not password_manager.verify(password, user_db.hashed_password):
        raise InvalidPasswordError()

    return users_repository.delete_user(db, user_db)