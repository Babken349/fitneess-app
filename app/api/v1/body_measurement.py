from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.core.dependency import get_db
from app.models.users import User
from app.schemas.body_measurement import (
    BodyMeasurementCreate,
    BodyMeasurementUpdate,
    BodyMeasurementResponse,
)
from app.services.body_measurement import BodyMeasurementService

router = APIRouter()
service = BodyMeasurementService()


@router.post("/measurements", response_model=BodyMeasurementResponse, status_code=201)
async def create_measurement(
    data: BodyMeasurementCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await service.create_measurement(db, data, current_user)


@router.get("/measurements", response_model=list[BodyMeasurementResponse])
async def get_my_measurements(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await service.get_my_measurements(db, current_user, skip, limit)


@router.get("/measurements/{measurement_id}", response_model=BodyMeasurementResponse)
async def get_measurement_by_id(
    measurement_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await service.get_by_id(db, measurement_id, current_user)


@router.patch("/measurements/{measurement_id}", response_model=BodyMeasurementResponse)
async def update_measurement(
    measurement_id: int,
    data: BodyMeasurementUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await service.update_measurement(db, measurement_id, data, current_user)


@router.delete("/measurements/{measurement_id}", status_code=204)
async def delete_measurement(
    measurement_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await service.delete_measurement(db, measurement_id, current_user)