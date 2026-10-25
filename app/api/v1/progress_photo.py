from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

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
async def create_photo(
    data: ProgressPhotoCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await service.create_photo(db, data, current_user)


@router.get("/photos", response_model=list[ProgressPhotoResponse])
async def get_my_photos(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await service.get_my_photos(db, current_user, skip, limit)


@router.get("/photos/{photo_id}", response_model=ProgressPhotoResponse)
async def get_photo_by_id(
    photo_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await service.get_by_id(db, photo_id, current_user)


@router.patch("/photos/{photo_id}", response_model=ProgressPhotoResponse)
async def update_photo(
    photo_id: int,
    data: ProgressPhotoUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await service.update_photo(db, photo_id, data, current_user)


@router.delete("/photos/{photo_id}", status_code=204)
async def delete_photo(
    photo_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await service.delete_photo(db, photo_id, current_user)