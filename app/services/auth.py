from app.exceptions import InvalidCredentialsError
from app.models.users import User
from sqlalchemy.orm import Session

from app.schemas.auth import Token, RefreshTokenRequest
from app.schemas.users import UserLogin
from app.repository import users as users_repository
from app.repository import refresh_tokens as refresh_repository
from app.auth.security import (
    create_access_token,
    create_refresh_token,
    decode_token
)
from app.utils.password import password_manager


def login(db: Session, credentials: UserLogin) -> Token:
    user = users_repository.get_user_by_identifier(db, credentials.identifier)
    if user is None:
        raise InvalidCredentialsError()
    
    if not password_manager.verify(credentials.password, user.hashed_password):
        raise InvalidCredentialsError()

    access_token = create_access_token(user_id=user.id, role=user.role)
    refresh_token, jti, expires_at = create_refresh_token(user_id=user.id)

    # Репозиторий только добавляет в сессию
    refresh_repository.create_refresh_token(
        db=db,
        user_id=user.id,
        jti=jti,
        expires_at=expires_at
    )
    users_repository.update_last_login(db, user)

    
    db.commit()
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


def refresh_token(db: Session, token_data: RefreshTokenRequest) -> Token:
    payload = decode_token(token_data.refresh_token)
    if payload.get("type") != "refresh":
        raise InvalidCredentialsError()
        
    user_id = payload.get("sub")
    jti = payload.get("jti")

    token_db = refresh_repository.get_by_jti(db, jti)
    if token_db is None or token_db.revoked:
        raise InvalidCredentialsError()

    # 1. Юзер для роли
    user = users_repository.get_user_by_id(db, int(user_id))
    if user is None:
        raise InvalidCredentialsError()

    # 2. Отзываем старый токен
    refresh_repository.revoke(db, token_db)

    # 3. Создаем новые токены, передавая роль юзера!
    access_token = create_access_token(user_id=user.id, role=user.role)
    new_refresh_token, new_jti, expires_at = create_refresh_token(user_id=user.id)

    refresh_repository.create_refresh_token(
        db=db,
        user_id=user.id,
        jti=new_jti,
        expires_at=expires_at
    )

    db.commit()

    return Token(access_token=access_token, refresh_token=new_refresh_token, token_type="bearer")


def logout(db: Session, token: RefreshTokenRequest):
    payload = decode_token(token.refresh_token)
    jti = payload.get("jti")
    token_db = refresh_repository.get_by_jti(db, jti)
    
    if token_db is None:
        raise InvalidCredentialsError()
    
    refresh_repository.revoke(db, token_db)
    
    db.commit()


def logout_all(db: Session, user: User):
    refresh_repository.revoke_all_for_user(db, user.id)
    db.commit() 
