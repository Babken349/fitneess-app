from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.core.dependency import get_db
from app.models.users import User

from app.schemas.reminder import (
    ReminderCreate,
    ReminderUpdate,
    ReminderResponse,
)

from app.services.reminder import ReminderService


router = APIRouter()
service = ReminderService()


@router.post(
    "/user-supplements/{user_supplement_id}/reminders",
    response_model=ReminderResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_reminder(
    user_supplement_id: int,
    data: ReminderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.create_reminder(
        db,
        user_supplement_id,
        data,
        current_user,
    )


@router.get(
    "/user-supplements/{user_supplement_id}/reminders",
    response_model=list[ReminderResponse],
)
def get_reminders_by_user_supplement(
    user_supplement_id: int,
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.get_by_user_supplement(
        db,
        user_supplement_id,
        current_user,
        skip,
        limit,
    )


@router.get(
    "/supplement-reminders",
    response_model=list[ReminderResponse],
)
def get_my_reminders(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.get_my_reminders(
        db,
        current_user,
        skip,
        limit,
    )


@router.get(
    "/supplement-reminders/active",
    response_model=list[ReminderResponse],
)
def get_active_reminders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.get_active_reminders(
        db,
        current_user,
    )


@router.get(
    "/supplement-reminders/{reminder_id}",
    response_model=ReminderResponse,
)
def get_reminder_by_id(
    reminder_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.get_by_id(
        db,
        reminder_id,
        current_user,
    )


@router.patch(
    "/supplement-reminders/{reminder_id}",
    response_model=ReminderResponse,
)
def update_reminder(
    reminder_id: int,
    data: ReminderUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.update_reminder(
        db,
        reminder_id,
        data,
        current_user,
    )


@router.post(
    "/supplement-reminders/{reminder_id}/activate",
    response_model=ReminderResponse,
)
def activate_reminder(
    reminder_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.activate_reminder(
        db,
        reminder_id,
        current_user,
    )


@router.post(
    "/supplement-reminders/{reminder_id}/deactivate",
    response_model=ReminderResponse,
)
def deactivate_reminder(
    reminder_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.deactivate_reminder(
        db,
        reminder_id,
        current_user,
    )


@router.delete(
    "/supplement-reminders/{reminder_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_reminder(
    reminder_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service.delete_reminder(
        db,
        reminder_id,
        current_user,
    )

    return None