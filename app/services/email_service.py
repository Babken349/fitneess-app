import uuid
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users import User
from app.models.email_verification_token import EmailVerificationToken
from app.repository import email_verification_token as email_repository
from app.repository import users as users_repository
from app.exceptions import InvalidCredentialsError


async def request_verification_token(db: AsyncSession, user: User) -> EmailVerificationToken:
    # 1. Репозиторий удаляет старые токены (без коммита)
    await email_repository.delete_user_tokens(db=db, user_id=user.id)

    token_str = uuid.uuid4().hex

    token_model = EmailVerificationToken(
        user_id=user.id,
        verification_token=token_str,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        used=False
    )

    # 2. Репозиторий добавляет объект в сессию (без коммита)
    saved_token = email_repository.create_verification_token(db=db, token_model=token_model)

    # 3. СЕРВИС ДЕЛАЕТ COMMIT! (Unit of Work)
    await db.commit()
    await db.refresh(saved_token)

    print(f"Отправлено письмо! Ссылка: http://localhost:8000/api/v1/auth/verify-email?token={saved_token.verification_token}")

    return saved_token


async def verify_email(db: AsyncSession, token_string: str) -> dict:

    # 1. Ищем токен
    token_db = await email_repository.get_by_token(db=db, token_string=token_string)
    if token_db is None:
        raise InvalidCredentialsError()

    # 2. Pythonic style: пишем просто if token_db.used, без == True
    if token_db.used:
        raise InvalidCredentialsError()

    if token_db.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise InvalidCredentialsError()

    # 3. Находим юзера и меняем его
    user = await users_repository.get_user_by_id(db=db, user_id=token_db.user_id)
    if user is None:
        raise InvalidCredentialsError()

    user.is_verified = True

    # 4. Помечаем токен как использованный
    email_repository.mark_used(db=db, token_db=token_db)

    # 5. СЕРВИС ДЕЛАЕТ COMMIT! Все изменения сохраняются разом.
    await db.commit()
    await db.refresh(user)

    return {"message": "Email успешно подтвержден"}