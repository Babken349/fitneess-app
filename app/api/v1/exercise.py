from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import require_admin
from app.core.dependency import get_db
from app.schemas.exercise import (
    ExerciseCreate,
    ExerciseResponse,
    ExerciseUpdate,
)
from app.services.exercise import ExerciseService

router = APIRouter()

exercise_service = ExerciseService()


@router.post("/", response_model=ExerciseResponse)
def create_exercise(
    exercise_data: ExerciseCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    return exercise_service.create_exercise(
        db=db,
        exercise_data=exercise_data,
    )


@router.patch("/{exercise_id}", response_model=ExerciseResponse)
def update_exercise(
    exercise_id: int,
    exercise_data: ExerciseUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    return exercise_service.update_exercise(
        db=db,
        exercise_id=exercise_id,
        exercise_data=exercise_data,
    )


@router.patch("/{exercise_id}/archive", response_model=ExerciseResponse)
def archive_exercise(
    exercise_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    return exercise_service.archive_exercise(
        db=db,
        exercise_id=exercise_id,
    )


@router.delete("/{exercise_id}")
def delete_exercise(
    exercise_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    exercise_service.delete_exercise(
        db=db,
        exercise_id=exercise_id,
    )
    return {"detail": "Exercise deleted successfully"}


@router.get("/", response_model=list[ExerciseResponse])
def get_all_exercises(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    return exercise_service.get_all_exercises(
        db=db,
        skip=skip,
        limit=limit,
    )


@router.get("/{exercise_id}", response_model=ExerciseResponse)
def get_exercise_by_id(
    exercise_id: int,
    db: Session = Depends(get_db),
):
    return exercise_service.get_exercise_by_id(
        db=db,
        exercise_id=exercise_id,
    )


@router.get("/search", response_model=list[ExerciseResponse])
def search_exercises(
    name: str,
    db: Session = Depends(get_db),
):
    return exercise_service.search_exercises(
        db=db,
        name_substring=name,
    )