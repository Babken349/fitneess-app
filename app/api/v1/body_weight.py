from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

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
def create_weight(
    data: BodyWeightCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.create_weight(db, data, current_user)


@router.get("/weights", response_model=list[BodyWeightResponse])
def get_my_weights(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.get_my_weights(db, current_user, skip, limit)


@router.get("/weights/{weight_id}", response_model=BodyWeightResponse)
def get_weight_by_id(
    weight_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.get_by_id(db, weight_id, current_user)


@router.patch("/weights/{weight_id}", response_model=BodyWeightResponse)
def update_weight(
    weight_id: int,
    data: BodyWeightUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.update_weight(db, weight_id, data, current_user)


@router.delete("/weights/{weight_id}", status_code=204)
def delete_weight(
    weight_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service.delete_weight(db, weight_id, current_user)