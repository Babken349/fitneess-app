from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

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
def create_measurement(
    data: BodyMeasurementCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.create_measurement(db, data, current_user)


@router.get("/measurements", response_model=list[BodyMeasurementResponse])
def get_my_measurements(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.get_my_measurements(db, current_user, skip, limit)


@router.get("/measurements/{measurement_id}", response_model=BodyMeasurementResponse)
def get_measurement_by_id(
    measurement_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.get_by_id(db, measurement_id, current_user)


@router.patch("/measurements/{measurement_id}", response_model=BodyMeasurementResponse)
def update_measurement(
    measurement_id: int,
    data: BodyMeasurementUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.update_measurement(db, measurement_id, data, current_user)


@router.delete("/measurements/{measurement_id}", status_code=204)
def delete_measurement(
    measurement_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service.delete_measurement(db, measurement_id, current_user)