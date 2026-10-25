from datetime import date

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.core.dependency import get_db
from app.models.users import User
from app.schemas.calendar_availability import (
    CalendarAvailabilityCreate,
    CalendarAvailabilityResponse,
    CalendarAvailabilityUpdate,
)
from app.services.calendar_availability import (
    CalendarAvailabilityService,
)


router = APIRouter()

service = CalendarAvailabilityService()


@router.post(
    "/availability",
    response_model=CalendarAvailabilityResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_or_update_availability(
    data: CalendarAvailabilityCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await service.create_or_update(
        db=db,
        current_user=current_user,
        data=data,
    )


@router.patch(
    "/availability/{availability_id}",
    response_model=CalendarAvailabilityResponse,
)
async def update_availability(
    availability_id: int,
    data: CalendarAvailabilityUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await service.update(
        db=db,
        current_user=current_user,
        availability_id=availability_id,
        data=data,
    )


@router.delete(
    "/availability/{availability_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_availability(
    availability_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await service.delete(
        db=db,
        current_user=current_user,
        availability_id=availability_id,
    )


@router.get(
    "/availability/me",
    response_model=list[CalendarAvailabilityResponse],
)
async def get_my_calendar(
    start_date: date,
    end_date: date,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await service.get_my_calendar(
        db=db,
        current_user=current_user,
        start_date=start_date,
        end_date=end_date,
    )


@router.get(
    "/availability/friend/{friend_id}",
    response_model=list[CalendarAvailabilityResponse],
)
async def get_friend_calendar(
    friend_id: int,
    start_date: date,
    end_date: date,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await service.get_friend_calendar(
        db=db,
        current_user=current_user,
        friend_id=friend_id,
        start_date=start_date,
        end_date=end_date,
    )