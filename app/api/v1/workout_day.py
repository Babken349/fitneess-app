from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependency import get_db, get_current_user
from app.models.users import User
from app.schemas.workout_day import (
    WorkoutDayCreate,
    WorkoutDayUpdate,
    WorkoutDayResponse,
)
from app.services.workout_day import WorkoutDayService


router = APIRouter()

day_service = WorkoutDayService()


# =========================================================
# CREATE
# =========================================================

@router.post(
    "/programs/{program_id}/days",
    response_model=WorkoutDayResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_day(
    program_id: int,
    day_data: WorkoutDayCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return day_service.create_day(
        db=db,
        program_id=program_id,
        day_data=day_data,
        current_user=current_user,
    )


# =========================================================
# GET
# =========================================================

@router.get(
    "/programs/{program_id}/days",
    response_model=list[WorkoutDayResponse],
)
def get_days_by_program(
    program_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return day_service.get_days_by_program(
        db=db,
        program_id=program_id,
        current_user=current_user,
    )


@router.get(
    "/programs/{program_id}/days/active",
    response_model=list[WorkoutDayResponse],
)
def get_active_days_by_program(
    program_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return day_service.get_active_by_program(
        db=db,
        program_id=program_id,
        current_user=current_user,
    )


@router.get(
    "/programs/{program_id}/days/archived",
    response_model=list[WorkoutDayResponse],
)
def get_archived_days_by_program(
    program_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return day_service.get_archived_by_program(
        db=db,
        program_id=program_id,
        current_user=current_user,
    )


@router.get(
    "/days/{day_id}",
    response_model=WorkoutDayResponse,
)
def get_day_by_id(
    day_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return day_service.get_day_by_id(
        db=db,
        day_id=day_id,
        current_user=current_user,
    )


# =========================================================
# SEARCH
# =========================================================

@router.get(
    "/days/search",
    response_model=list[WorkoutDayResponse],
)
def search_days(
    name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return day_service.search_days(
        db=db,
        name=name,
        current_user=current_user,
    )


# =========================================================
# UPDATE
# =========================================================

@router.patch(
    "/days/{day_id}",
    response_model=WorkoutDayResponse,
)
def update_day(
    day_id: int,
    day_data: WorkoutDayUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return day_service.update_day(
        db=db,
        day_id=day_id,
        day_data=day_data,
        current_user=current_user,
    )


# =========================================================
# ARCHIVE / UNARCHIVE
# =========================================================

@router.patch(
    "/days/{day_id}/archive",
    response_model=WorkoutDayResponse,
)
def archive_day(
    day_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return day_service.archive_day(
        db=db,
        day_id=day_id,
        current_user=current_user,
    )


@router.patch(
    "/days/{day_id}/unarchive",
    response_model=WorkoutDayResponse,
)
def unarchive_day(
    day_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return day_service.unarchive_day(
        db=db,
        day_id=day_id,
        current_user=current_user,
    )


# =========================================================
# DELETE
# =========================================================

@router.delete(
    "/days/{day_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_day(
    day_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    day_service.delete_day(
        db=db,
        day_id=day_id,
        current_user=current_user,
    )

    return None