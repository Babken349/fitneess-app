# app/api/v1/auth.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependency import get_db
from app.auth.dependencies import get_current_user

from app.schemas.auth import Token, RefreshTokenRequest
from app.schemas.users import UserLogin
from app.models.users import User

from app.services import auth


router = APIRouter()


@router.post(
    "/login",
    response_model=Token,
    summary="Вход в систему",
    description="Логин по email/паролю. Возвращает access + refresh токены.",
)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    return await auth.login(
        db,
        credentials,
    )


@router.post(
    "/refresh",
    response_model=Token,
    summary="Обновление токенов",
    description="Обновляет пару access/refresh токенов по refresh токену.",
)
async def refresh_token(
    data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    return await auth.refresh_token(
        db,
        data,
    )


@router.post(
    "/logout",
    summary="Выход из системы (текущее устройство)",
    description="Отзывает refresh‑токен (выход с текущего устройства).",
)
async def logout(
    data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    await auth.logout(
        db,
        data,
    )

    return {"message": "Вы вышли из системы"}


@router.post(
    "/logout-all",
    summary="Выход со всех устройств",
    description="Отзывает все refresh‑токены пользователя (выход со всех устройств).",
)
async def logout_all(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await auth.logout_all(
        db,
        current_user,
    )



    return {"message": "Вы вышли со всех устройств"}