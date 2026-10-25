from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependency import get_db

from app.schemas.supplements import (
    SupplementCreate,
    SupplementUpdate,
    SupplementResponse,
)

from app.services.supplement_service import SupplementService


router = APIRouter()
service = SupplementService()


@router.post(
    "/",
    response_model=SupplementResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_supplement(
    data: SupplementCreate,
    db: AsyncSession = Depends(get_db),
):
    return await service.create_supplement(
        db,
        data,
    )


@router.get(
    "/",
    response_model=list[SupplementResponse],
)
async def get_all_supplements(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    return await service.get_all(
        db,
        skip,
        limit,
    )


@router.get(
    "/{supplement_id}",
    response_model=SupplementResponse,
)
async def get_supplement_by_id(
    supplement_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await service.get_by_id(
        db,
        supplement_id,
    )


@router.patch(
    "/{supplement_id}",
    response_model=SupplementResponse,
)
async def update_supplement(
    supplement_id: int,
    data: SupplementUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await service.update_supplement(
        db,
        supplement_id,
        data,
    )


@router.delete(
    "/{supplement_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_supplement(
    supplement_id: int,
    db: AsyncSession = Depends(get_db),
):
    await service.delete_supplement(
        db,
        supplement_id,
    )

    return None