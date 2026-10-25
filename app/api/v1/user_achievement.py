from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.core.dependency import get_db
from app.models.users import User
from app.schemas.user_achievement import UserAchievementResponse
from app.services.user_achievement import UserAchievementService

router = APIRouter()
service = UserAchievementService()


@router.get("/me", response_model=list[UserAchievementResponse])
async def get_my_achievements(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await service.get_my_achievements(db, current_user, skip, limit)


@router.get("/{user_achievement_id}", response_model=UserAchievementResponse)
async def get_my_achievement_by_id(
    user_achievement_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await service.get_by_id(db, user_achievement_id, current_user)