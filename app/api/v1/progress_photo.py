from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.core.dependency import get_db
from app.models.users import User
from app.schemas.progress_photo import (
    ProgressPhotoCreate,
    ProgressPhotoUpdate,
    ProgressPhotoResponse,
)
from app.services.progress_photo import ProgressPhotoService

router = APIRouter()
service = ProgressPhotoService()


@router.post("/photos", response_model=ProgressPhotoResponse, status_code=201)
def create_photo(
    data: ProgressPhotoCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.create_photo(db, data, current_user)


@router.get("/photos", response_model=list[ProgressPhotoResponse])
def get_my_photos(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.get_my_photos(db, current_user, skip, limit)


@router.get("/photos/{photo_id}", response_model=ProgressPhotoResponse)
def get_photo_by_id(
    photo_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.get_by_id(db, photo_id, current_user)


@router.patch("/photos/{photo_id}", response_model=ProgressPhotoResponse)
def update_photo(
    photo_id: int,
    data: ProgressPhotoUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.update_photo(db, photo_id, data, current_user)


@router.delete("/photos/{photo_id}", status_code=204)
def delete_photo(
    photo_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service.delete_photo(db, photo_id, current_user)