from hmac import new
from operator import ne
import uuid
from datetime import datetime, timedelta, timezone
from app.utils.password import password_manager
from sqlalchemy.orm import Session

from app.models.users import User
from app.models.password_reset_token import PasswordResetToken 
from app.repository import refresh_tokens as refresh_repository
from app.repository import password_reset_tokens as reset_repository
from app.repository import users as users_repository
from app.exceptions import InvalidCredentialsError


def request_password_reset(db: Session, email: str):
    user = users_repository.get_user_by_identifier(db, email)

    # Если юзера нет, тихо возвращаем сообщение (защита от перебора почты)
    if user is None:
        return {"message": "Если почта верна, письмо отправлено"}

    # 1. Удаляем старые токены
    reset_repository.delete_user_tokens(db, user.id)
    
    # 2. Генерируем новый
    token_str = uuid.uuid4().hex
    token_model = PasswordResetToken(
        user_id=user.id,
        reset_token=token_str,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        used=False
    )
    
    # 3. Сохраняем в базу
    reset_repository.create_reset_token(db, token_model)
    
    # 4. Выводим ссылку (пока без реальной почты)
    print(f"Ссылка для сброса: http://localhost:8000/reset-password?token={token_str}")
    
    # 5. Сохраняем изменения в БД (Unit of Work)
    db.commit()

    return {"message": "Если почта верна, письмо отправлено"}


def reset_password(db: Session, token: str, new_password: str):
    token_db = reset_repository.get_by_token(db, token)

    if token_db is None:
        raise InvalidCredentialsError()

    if token_db.used:
        raise InvalidCredentialsError()

    if token_db.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise InvalidCredentialsError()

    user = users_repository.get_user_by_id(db=db, user_id=token_db.user_id) 

    new_hashed = password_manager.hash(new_password)

    users_repository.update_password(db, user, new_hashed)

    reset_repository.mark_used(db, token_db)


    refresh_repository.revoke_all_for_user(db, user.id)

    db.commit()

    return {"message": "Пароль успешно изменен"}