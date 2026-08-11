from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependency import get_db
from app.auth.dependencies import get_current_user

from app.schemas.workout_program import (
    CreateWorkoutProgram,
    WorkoutProgramUpdate,
    WorkoutSessionResponse,
)
from app.models.users import User
from app.services.workout_program import ProgramService

router = APIRouter()

workout_program_service = ProgramService()


@router.post("/workout-programs")
def create_program(
    program_data: CreateWorkoutProgram,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return workout_program_service.create_program(
        db=db,
        program_data=program_data,
        current_user=current_user,
    )


@router.put("/workout-programs/{program_id}")
def update_program(
    program_id: int,
    program_data: WorkoutProgramUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return workout_program_service.update_program(
        db=db,
        program_id=program_id,
        program_data=program_data,
        current_user=current_user,
    )


@router.get("/workout-programs/{program_id}")
def get_program_by_id(
    program_id: int,
    db: Session = Depends(get_db),
):
    return workout_program_service.get_program_by_id(
        db=db,
        program_id=program_id,
    )


@router.get("/workout-programs/me")
def get_my_programs(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return workout_program_service.get_my_programs(
        db=db,
        current_user=current_user,
        skip=skip,
        limit=limit,
    )


@router.get("/workout-programs/public")
def get_public_programs(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    return workout_program_service.get_public_programs(
        db=db,
        skip=skip,
        limit=limit,
    )


@router.get("/workout-programs/search")
def search_programs(
    name: str,
    db: Session = Depends(get_db),
):
    return workout_program_service.search_programs(
        db=db,
        name=name,
    )


@router.patch("/workout-programs/{program_id}/archive")
def archive_program(
    program_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return workout_program_service.archive_program(
        db=db,
        program_id=program_id,
        current_user=current_user,
    )


@router.patch("/workout-programs/{program_id}/unarchive")
def unarchive_program(
    program_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return workout_program_service.unarchive_program(
        db=db,
        program_id=program_id,
        current_user=current_user,
    )


@router.delete("/workout-programs/{program_id}")
def delete_program(
    program_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    workout_program_service.delete_program(
        db=db,
        program_id=program_id,
        current_user=current_user,
    )
    return {"detail": "Program deleted successfully"}


@router.patch("/workout-programs/{program_id}/public")
def make_public(
    program_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return workout_program_service.make_public(
        db=db,
        program_id=program_id,
        current_user=current_user,
    )


@router.patch("/workout-programs/{program_id}/private")
def make_private(
    program_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return workout_program_service.make_private(
        db=db,
        program_id=program_id,
        current_user=current_user,
    )


@router.get("/workout-programs/me/{program_id}")
def get_my_program(
    program_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return workout_program_service.get_my_program(
        db=db,
        program_id=program_id,
        current_user=current_user,
    )


@router.get("/workout-programs/me/archived")
def get_archived_by_user(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return workout_program_service.get_archived_by_user(
        db=db,
        user_id=current_user.id,
    )


@router.get("/workout-programs/me/active")
def get_active_by_user(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return workout_program_service.get_active_by_user(
        db=db,
        user_id=current_user.id,
    )