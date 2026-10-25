from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependency import get_db
from app.models.users import User
from app.schemas.study_state import StudyStateCreate, StudyStateResponse
from app.services.study_state import StudyStateService
from app.auth.dependencies import get_current_user


router = APIRouter()

study_state_service = StudyStateService()


@router.post(
    "",
    response_model=StudyStateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_study_state(
    data: StudyStateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await study_state_service.create(db, data, current_user)


@router.get(
    "",
    response_model=list[StudyStateResponse],
)
async def get_my_study_states(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await study_state_service.get_my_states(
        db,
        current_user,
        skip,
        limit,
    )


@router.get(
    "/{study_state_id}",
    response_model=StudyStateResponse,
)
async def get_study_state(
    study_state_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await study_state_service.get_by_id(
        db,
        study_state_id,
        current_user,
    )


@router.delete(
    "/{study_state_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_study_state(
    study_state_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await study_state_service.delete(
        db,
        study_state_id,
        current_user,
    )