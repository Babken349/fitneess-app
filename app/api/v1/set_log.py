# app/api/v1/set_log.py

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependency import get_db, get_current_user
from app.models.users import User

from app.schemas.set_log import (
    SetLogCreate,
    SetLogUpdate,
    SetLogResponse,
)

from app.services.set_log import SetLogService


router = APIRouter()

set_log_service = SetLogService()


@router.post(
    "/exercise-logs/{exercise_log_id}/sets",
    response_model=SetLogResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_set(
    exercise_log_id: int,
    data: SetLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return set_log_service.create_set(
        db=db,
        exercise_log_id=exercise_log_id,
        data=data,
        current_user=current_user,
    )


@router.get(
    "/exercise-logs/{exercise_log_id}/sets",
    response_model=list[SetLogResponse],
)
def get_sets(
    exercise_log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return set_log_service.get_by_exercise_log(
        db=db,
        exercise_log_id=exercise_log_id,
        current_user=current_user,
    )


@router.get(
    "/sets/{set_log_id}",
    response_model=SetLogResponse,
)
def get_set(
    set_log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return set_log_service.get_by_id(
        db=db,
        set_log_id=set_log_id,
        current_user=current_user,
    )


@router.patch(
    "/sets/{set_log_id}",
    response_model=SetLogResponse,
)
def update_set(
    set_log_id: int,
    data: SetLogUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return set_log_service.update_set(
        db=db,
        set_log_id=set_log_id,
        data=data,
        current_user=current_user,
    )


@router.delete(
    "/sets/{set_log_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_set(
    set_log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    set_log_service.delete_set(
        db=db,
        set_log_id=set_log_id,
        current_user=current_user,
    )

    return None