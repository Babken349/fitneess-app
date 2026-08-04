

from fastapi import APIRouter, Depends
from app.auth.dependencies import get_current_user
from app.services.exercise import ExerciseService
from app.models.users import User
from sqlalchemy.orm import Session
from app.core.dependency import get_db
from app.schemas.exercise import ExerciseCreate, ExerciseResponse, ExerciseUpdate

router = APIRouter()

@router.post("/", response_model=ExerciseResponse)
def create_exercise( exercise_data: ExerciseCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    exercise_service = ExerciseService()
    return exercise_service.create_exercise(db=db, exercise_data=exercise_data, current_user=current_user)


@router.delete("/{exercise_id}")
def delete_exercise(exercise_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    exercise_service = ExerciseService()
    return exercise_service.delete_exercise(db=db, exercise_id=exercise_id, current_user=current_user)

@router.patch("/{exercise_id}/archive")
def archive_exercise(exercise_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    exercise_service = ExerciseService()
    return exercise_service.archive_exercise(db=db, exercise_id=exercise_id, current_user=current_user)

@router.patch("/{exercise_id}")
def update_exercise(exercise_data: ExerciseUpdate, exercise_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    exercise_service = ExerciseService()
    return exercise_service.update_exercise(db=db, exercise_id=exercise_id, exercise_data=exercise_data, current_user=current_user)

@router.get("/")
def get_all_exercises(skip: int = 0, limit: int = 20, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    exercise_service = ExerciseService()
    return exercise_service.get_all_exercises(db=db, skip=skip, limit=limit)

@router.get("/{exercise_id}", response_model=ExerciseResponse)
def get_exercise_by_id(exercise_id: int, db: Session = Depends(get_db)):
    exercise_service = ExerciseService()
    return exercise_service.get_exercise_by_id(db=db, exercise_id=exercise_id)