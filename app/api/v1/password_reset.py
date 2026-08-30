from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependency import get_db

from app.schemas.auth import ForgotPassword, ResetPassword

from app.services import password_reset_service


router = APIRouter()


@router.post(
    "/forgot-password",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Запрос на сброс пароля",
    description=(
        "Отправляет письмо со ссылкой для сброса пароля. "
        "Всегда возвращает одно и то же сообщение, чтобы не светить наличие почты."
    ),
)
def forgot_password(
    data: ForgotPassword,
    db: Session = Depends(get_db),
):
    """
    Пользователь вводит email → бэкенд:
    - находит пользователя;
    - генерирует токен;
    - сохраняет токен в БД;
    - отправляет письмо со ссылкой на фронтенд;
    - возвращает нейтральное сообщение.
    """
    return password_reset_service.request_password_reset(
        db,
        data.email,
    )


@router.post(
    "/reset-password",
    summary="Сброс пароля по токену",
    description=(
        "Устанавливает новый пароль, если токен валиден, не использован и не просрочен. "
        "После успешного сброса все refresh‑токены пользователя отзываются."
    ),
)
def reset_password(
    data: ResetPassword,
    db: Session = Depends(get_db),
):
    """
    Фронтенд вызывает этот эндпоинт после того, как пользователь:
    - перешёл по ссылке из письма;
    - ввёл новый пароль.

    Тело запроса:
    {
        "token": "...",
        "new_password": "..."
    }
    """
    return password_reset_service.reset_password(
        db,
        data.token,
        data.new_password,
    )