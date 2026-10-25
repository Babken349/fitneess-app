from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user, require_admin, require_premium
from app.core.dependency import get_db
from app.models.users import User
from app.schemas.auth import Token, RefreshTokenRequest
from app.schemas.users import UserCreate, UserResponse
from app.services import users as users_service, auth


router = APIRouter()


@router.get("/me", response_model=UserResponse, status_code=200)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/register", response_model=UserResponse, status_code=201)
async def user_register(
    user_db: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    user = await users_service.create_user(db=db, user=user_db)

    return user


@router.get("/admin-panel", response_model=UserResponse, status_code=200)
async def get_admin_panel(current_user: User = Depends(require_admin)):
    return current_user


@router.get("/premium-content", response_model=UserResponse, status_code=200)
async def get_premium_status(current_user: User = Depends(require_premium)):
    return current_user


@router.post("/refresh", response_model=Token)
async def refresh_access_token(
    token_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    token = await auth.refresh_token(db, token_data)

    return token


@router.post("/logout")
async def logout_refresh_token(
    token_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    await auth.logout(db, token_data)
    return {"message": "Successfully logged out"}


@router.get("/{user_id}", response_model=UserResponse, status_code=200, dependencies=[Depends(require_admin)])
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    user = await users_service.get_user_by_id(db=db, user_id=user_id)
    return user