from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.core.dependency import get_db

from app.models.users import User

from app.schemas.workout_session import (
    WorkoutSessionCreate,
    WorkoutSessionUpdate,
    WorkoutSessionResponse,
)

from app.services.workout_session import WorkoutSessionService


router = APIRouter()

session_service = WorkoutSessionService()


@router.post(
    "",
    response_model=WorkoutSessionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_session(
    session_data: WorkoutSessionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await session_service.create_session(
        db=db,
        session_data=session_data,
        current_user=current_user,
    )


@router.get(
    "/me",
    response_model=list[WorkoutSessionResponse],
)
async def get_my_sessions(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await session_service.get_my_sessions(
        db=db,
        current_user=current_user,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/active",
    response_model=WorkoutSessionResponse | None,
)
async def get_active_session(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await session_service.get_active_session(
        db=db,
        current_user=current_user,
    )


@router.get(
    "/{session_id}",
    response_model=WorkoutSessionResponse,
)
async def get_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await session_service.get_by_id(
        db=db,
        session_id=session_id,
        current_user=current_user,
    )


@router.get(
    "/day/{workout_day_id}",
    response_model=list[WorkoutSessionResponse],
)
async def get_sessions_by_day(
    workout_day_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await session_service.get_by_day(
        db=db,
        workout_day_id=workout_day_id,
        current_user=current_user,
    )


@router.patch(
    "/{session_id}",
    response_model=WorkoutSessionResponse,
)
async def update_session(
    session_id: int,
    session_data: WorkoutSessionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await session_service.update_session(
        db=db,
        session_id=session_id,
        session_data=session_data,
        current_user=current_user,
    )


@router.patch(
    "/{session_id}/finish",
    response_model=WorkoutSessionResponse,
)
async def finish_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await session_service.finish_session(
        db=db,
        session_id=session_id,
        current_user=current_user,
    )


@router.delete(
    "/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await session_service.delete_session(
        db=db,
        session_id=session_id,
        current_user=current_user,
    )

    return None