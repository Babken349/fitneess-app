from datetime import datetime

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.core.dependency import get_db
from app.models.users import User

from app.schemas.supplement_intake import (
    SupplementIntakeCreate,
    SupplementIntakeUpdate,
    SupplementIntakeResponse,
)

from app.services.supplement_intake import (
    SupplementIntakeService,
)


router = APIRouter()
service = SupplementIntakeService()


@router.post(
    "/supplement-intakes",
    response_model=SupplementIntakeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_intake(
    data: SupplementIntakeCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await service.create_intake(
        db,
        data,
        current_user,
    )


@router.get(
    "/supplement-intakes",
    response_model=list[SupplementIntakeResponse],
)
async def get_my_intakes(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await service.get_my_intakes(
        db,
        current_user,
        skip,
        limit,
    )


# Должен стоять ДО "/supplement-intakes/{intake_id}",
# иначе "date-range" попадёт в int-параметр и вернётся 422
@router.get(
    "/supplement-intakes/date-range",
    response_model=list[SupplementIntakeResponse],
)
async def get_intakes_by_date_range(
    start_at: datetime,
    end_at: datetime,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await service.get_my_intakes_by_date_range(
        db,
        start_at,
        end_at,
        current_user,
    )


@router.get(
    "/supplement-intakes/status/{intake_status}",
    response_model=list[SupplementIntakeResponse],
)
async def get_intakes_by_status(
    intake_status: str,
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await service.get_by_status(
        db,
        intake_status,
        current_user,
        skip,
        limit,
    )


@router.get(
    "/supplement-intakes/{intake_id}",
    response_model=SupplementIntakeResponse,
)
async def get_intake_by_id(
    intake_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await service.get_by_id(
        db,
        intake_id,
        current_user,
    )


@router.get(
    "/user-supplements/{user_supplement_id}/intakes",
    response_model=list[SupplementIntakeResponse],
)
async def get_intakes_by_user_supplement(
    user_supplement_id: int,
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await service.get_by_user_supplement(
        db,
        user_supplement_id,
        current_user,
        skip,
        limit,
    )


@router.patch(
    "/supplement-intakes/{intake_id}",
    response_model=SupplementIntakeResponse,
)
async def update_intake(
    intake_id: int,
    data: SupplementIntakeUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await service.update_intake(
        db,
        intake_id,
        data,
        current_user,
    )


@router.delete(
    "/supplement-intakes/{intake_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_intake(
    intake_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await service.delete_intake(
        db,
        intake_id,
        current_user,
    )

    return None