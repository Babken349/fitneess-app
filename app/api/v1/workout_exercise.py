from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependency import get_db, get_current_user

from app.models.users import User

from app.schemas.workout_exercise import (
    WorkoutExerciseCreate,
    WorkoutExerciseUpdate,
    WorkoutExerciseResponse,
)

from app.services.workout_exercise import WorkoutExerciseService


router = APIRouter()

workout_exercise_service = WorkoutExerciseService()


# =========================================================
# CREATE
# =========================================================

@router.post(
    "/days/{workout_day_id}/exercises",
    response_model=WorkoutExerciseResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_workout_exercise(
    workout_day_id: int,
    data: WorkoutExerciseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return workout_exercise_service.create_workout_exercise(
        db=db,
        workout_day_id=workout_day_id,
        data=data,
        current_user=current_user,
    )


# =========================================================
# GET BY DAY
# =========================================================

@router.get(
    "/days/{workout_day_id}/exercises",
    response_model=list[WorkoutExerciseResponse],
)
def get_by_day(
    workout_day_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return workout_exercise_service.get_by_day(
        db=db,
        workout_day_id=workout_day_id,
        current_user=current_user,
    )


# =========================================================
# GET BY ID
# =========================================================

@router.get(
    "/workout-exercises/{workout_exercise_id}",
    response_model=WorkoutExerciseResponse,
)
def get_workout_exercise(
    workout_exercise_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return workout_exercise_service.get_by_id(
        db=db,
        workout_exercise_id=workout_exercise_id,
        current_user=current_user,
    )


# =========================================================
# UPDATE
# =========================================================

@router.patch(
    "/workout-exercises/{workout_exercise_id}",
    response_model=WorkoutExerciseResponse,
)
def update_workout_exercise(
    workout_exercise_id: int,
    data: WorkoutExerciseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return workout_exercise_service.update_workout_exercise(
        db=db,
        workout_exercise_id=workout_exercise_id,
        data=data,
        current_user=current_user,
    )


# =========================================================
# DELETE
# =========================================================

@router.delete(
    "/workout-exercises/{workout_exercise_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_workout_exercise(
    workout_exercise_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    workout_exercise_service.delete_workout_exercise(
        db=db,
        workout_exercise_id=workout_exercise_id,
        current_user=current_user,
    )

    return None