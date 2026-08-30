from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth.dependencies import require_admin
from app.core.dependency import get_db
from app.models.users import User
from app.schemas.achievement import AchievementCreate, AchievementUpdate, AchievementResponse
from app.services.achievement import AchievementService

router = APIRouter()
service = AchievementService()


@router.get("/", response_model=list[AchievementResponse])
def get_all_achievements(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    return service.get_all(db, skip, limit)


@router.get("/{achievement_id}", response_model=AchievementResponse)
def get_achievement_by_id(
    achievement_id: int,
    db: Session = Depends(get_db),
):
    return service.get_by_id(db, achievement_id)


@router.post("/", response_model=AchievementResponse, status_code=status.HTTP_201_CREATED)
def create_achievement(
    data: AchievementCreate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return service.create_achievement(db, data)


@router.patch("/{achievement_id}", response_model=AchievementResponse)
def update_achievement(
    achievement_id: int,
    data: AchievementUpdate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return service.update_achievement(db, achievement_id, data)


@router.delete("/{achievement_id}", response_model=AchievementResponse)
def deactivate_achievement(
    achievement_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return service.deactivate_achievement(db, achievement_id)