from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.common import PaginatedResponse
from app.auth.dependencies import get_current_user
from app.core.dependency import get_db
from app.models.users import User
from app.schemas.body_weight import (
    BodyWeightCreate,
    BodyWeightUpdate,
    BodyWeightResponse,
)
from app.services.body_weight import BodyWeightService

router = APIRouter()
service = BodyWeightService()


@router.post("/weights", response_model=BodyWeightResponse, status_code=201)
async def create_weight(
    data: BodyWeightCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await service.create_weight(db, data, current_user)


@router.get("/weights", response_model=PaginatedResponse[BodyWeightResponse])
async def get_my_weights(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    items, total = await service.get_my_weights(db, current_user, skip, limit)
    return PaginatedResponse[BodyWeightResponse](
        items=[BodyWeightResponse.model_validate(x) for x in items],
        total=total,
        skip=skip,
        limit=limit,
    )

@router.get("/weights/{weight_id}", response_model=BodyWeightResponse)
async def get_weight_by_id(
    weight_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await service.get_by_id(db, weight_id, current_user)


@router.patch("/weights/{weight_id}", response_model=BodyWeightResponse)
async def update_weight(
    weight_id: int,
    data: BodyWeightUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await service.update_weight(db, weight_id, data, current_user)


@router.delete("/weights/{weight_id}", status_code=204)
async def delete_weight(
    weight_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await service.delete_weight(db, weight_id, current_user)