import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.config import settings

from app.models.users import User
from app.models.password_reset_token import PasswordResetToken

from app.repository import refresh_tokens as refresh_repository
from app.repository import password_reset_tokens as reset_repository
from app.repository import users as users_repository

from app.exceptions import InvalidCredentialsError
from app.utils.password import password_manager
from app.services.email import EmailService


email_service = EmailService()


def request_password_reset(db: Session, email: str) -> dict:
    """
    Запрос на сброс пароля:
    - находит пользователя по email;
    - генерирует токен;
    - сохраняет токен в БД;
    - отправляет письмо со ссылкой на фронтенд;
    - возвращает нейтральное сообщение.
    """
    user = users_repository.get_user_by_identifier(db, email)

    # Защита от перебора: всегда одно и то же сообщение
    if user is None:
        return {"message": "Если почта верна, письмо отправлено"}

    # 1. Удаляем старые токены
    reset_repository.delete_user_tokens(db, user.id)

    # 2. Генерируем новый токен
    token_str = uuid.uuid4().hex
    token_model = PasswordResetToken(
        user_id=user.id,
        reset_token=token_str,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        used=False,
    )

    # 3. Сохраняем в базу
    reset_repository.create_reset_token(db, token_model)

    # 4. Формируем ссылку для сброса (на фронтенд)
    reset_link = (
        f"{settings.FRONTEND_URL}"
        f"/reset-password"
        f"?token={token_str}"
    )

    # 5. Отправляем письмо
    import resend
    from app.core.config import settings as app_settings

    resend.api_key = app_settings.RESEND_API_KEY

    resend.Emails.send({
        "from": f"Onboarding <{app_settings.EMAIL_FROM}>",
        "to": user.email,
        "subject": "Сброс пароля — Fitness App",
        "html": f"""
        <h1>Сброс пароля</h1>

        <p>Привет, {user.display_name}!</p>

        <p>
            Вы (или кто‑то другой) запросили сброс пароля.
            Нажмите на кнопку ниже, чтобы установить новый пароль.
        </p>

        <p>
            <a href="{reset_link}" style="
                display: inline-block;
                padding: 10px 20px;
                background-color: #dc2626;
                color: #ffffff;
                text-decoration: none;
                border-radius: 4px;
            ">
                Сбросить пароль
            </a>
        </p>

        <p>
            Ссылка действительна 1 час.
        </p>

        <p>
            Если вы не запрашивали сброс, просто проигнорируйте это письмо.
        </p>
        """,
    })

    # 6. Коммит
    db.commit()

    return {"message": "Если почта верна, письмо отправлено"}


def reset_password(db: Session, token: str, new_password: str) -> dict:
    """
    Сброс пароля по токену:
    - проверяет токен;
    - меняет пароль;
    - помечает токен как использованный;
    - отзывает все refresh‑токены.
    """
    token_db = reset_repository.get_by_token(db, token)

    if token_db is None:
        raise InvalidCredentialsError()

    if token_db.used:
        raise InvalidCredentialsError()

    if token_db.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise InvalidCredentialsError()

    user = users_repository.get_user_by_id(db=db, user_id=token_db.user_id)
    if user is None:
        raise InvalidCredentialsError()

    new_hashed = password_manager.hash(new_password)
    users_repository.update_password(db, user, new_hashed)

    reset_repository.mark_used(db, token_db)
    refresh_repository.revoke_all_for_user(db, user.id)

    db.commit()

    return {"message": "Пароль успешно изменен"}