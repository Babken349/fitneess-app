from typing_extensions import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_admin
from app.core.dependency import get_db
from app.models.users import User
from app.schemas.achievement import AchievementCreate, AchievementUpdate, AchievementResponse
from app.services.achievement import AchievementService

router = APIRouter()
service = AchievementService()


@router.get("/", response_model=list[AchievementResponse])
async def get_all_achievements(
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    db: AsyncSession = Depends(get_db),
):
    return await service.get_all(db, skip, limit)


@router.get("/{achievement_id}", response_model=AchievementResponse)
async def get_achievement_by_id(
    achievement_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await service.get_by_id(db, achievement_id)


@router.post("/", response_model=AchievementResponse, status_code=status.HTTP_201_CREATED)
async def create_achievement(
    data: AchievementCreate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    return await service.create_achievement(db, data)


@router.patch("/{achievement_id}", response_model=AchievementResponse)
async def update_achievement(
    achievement_id: int,
    data: AchievementUpdate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    return await service.update_achievement(db, achievement_id, data)


@router.delete("/{achievement_id}", response_model=AchievementResponse)
async def deactivate_achievement(
    achievement_id: int,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    return await service.deactivate_achievement(db, achievement_id)