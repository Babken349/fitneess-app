from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.core.dependency import get_db
from app.models.users import User

from app.schemas.exercise_log import (
    ExerciseLogCreate,
    ExerciseLogUpdate,
    ExerciseLogResponse,
)

from app.services.exercise_log import ExerciseLogService


router = APIRouter()

exercise_log_service = ExerciseLogService()


@router.post(
    "/workout-sessions/{session_id}/exercises",
    response_model=ExerciseLogResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_exercise_log(
    session_id: int,
    data: ExerciseLogCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await exercise_log_service.create_exercise_log(
        db=db,
        workout_session_id=session_id,
        data=data,
        current_user=current_user,
    )


@router.get(
    "/workout-sessions/{session_id}/exercises",
    response_model=list[ExerciseLogResponse],
)
async def get_session_exercises(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await exercise_log_service.get_by_session(
        db=db,
        workout_session_id=session_id,
        current_user=current_user,
    )


@router.get(
    "/exercise-logs/{exercise_log_id}",
    response_model=ExerciseLogResponse,
)
async def get_exercise_log(
    exercise_log_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await exercise_log_service.get_by_id(
        db=db,
        exercise_log_id=exercise_log_id,
        current_user=current_user,
    )


@router.patch(
    "/exercise-logs/{exercise_log_id}",
    response_model=ExerciseLogResponse,
)
async def update_exercise_log(
    exercise_log_id: int,
    data: ExerciseLogUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await exercise_log_service.update_exercise_log(
        db=db,
        exercise_log_id=exercise_log_id,
        data=data,
        current_user=current_user,
    )


@router.delete(
    "/exercise-logs/{exercise_log_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_exercise_log(
    exercise_log_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await exercise_log_service.delete_exercise_log(
        db=db,
        exercise_log_id=exercise_log_id,
        current_user=current_user,
    )

    return None