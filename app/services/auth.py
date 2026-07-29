# app/services/auth.py

from app.exceptions import InvalidCredentialsError, UserNotFoundError
from sqlalchemy.orm import Session

from app.schemas.auth import Token
from app.schemas.users import UserLogin
from app.repository import users as users_repository
from app.repository import refresh_tokens as refresh_repository
from app.auth.security import (
    create_access_token,
    create_refresh_token,
)

from app.utils.password import password_manager


def login(db: Session, credentials: UserLogin) -> Token:
    user = users_repository.get_user_by_identifier(db, credentials.identifier)


    if user is None:
        raise UserNotFoundError()

    
    if not  password_manager.verify(credentials.password, user.hashed_password):
        raise InvalidCredentialsError()

    access_token = create_access_token(user_id=user.id)

    refresh_token, jti, expires_at = create_refresh_token(user_id=user.id)

    refresh_repository.create_refresh_token(
    db=db,
    user_id=user.id,
    jti=jti,
    expires_at=expires_at
)

    users_repository.update_last_login(db, user)

    return Token(
    access_token=access_token,
    refresh_token=refresh_token,
    token_type="bearer"
)