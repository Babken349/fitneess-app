# app/api/v1/exercise_log.py

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependency import get_db, get_current_user
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
def create_exercise_log(
    session_id: int,
    data: ExerciseLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return exercise_log_service.create_exercise_log(
        db=db,
        workout_session_id=session_id,
        data=data,
        current_user=current_user,
    )


@router.get(
    "/workout-sessions/{session_id}/exercises",
    response_model=list[ExerciseLogResponse],
)
def get_session_exercises(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return exercise_log_service.get_by_session(
        db=db,
        workout_session_id=session_id,
        current_user=current_user,
    )


@router.get(
    "/exercise-logs/{exercise_log_id}",
    response_model=ExerciseLogResponse,
)
def get_exercise_log(
    exercise_log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return exercise_log_service.get_by_id(
        db=db,
        exercise_log_id=exercise_log_id,
        current_user=current_user,
    )


@router.patch(
    "/exercise-logs/{exercise_log_id}",
    response_model=ExerciseLogResponse,
)
def update_exercise_log(
    exercise_log_id: int,
    data: ExerciseLogUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return exercise_log_service.update_exercise_log(
        db=db,
        exercise_log_id=exercise_log_id,
        data=data,
        current_user=current_user,
    )


@router.delete(
    "/exercise-logs/{exercise_log_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_exercise_log(
    exercise_log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    exercise_log_service.delete_exercise_log(
        db=db,
        exercise_log_id=exercise_log_id,
        current_user=current_user,
    )

    return None