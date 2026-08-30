from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

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
def create_supplement(
    data: SupplementCreate,
    db: Session = Depends(get_db),
):
    return service.create_supplement(
        db,
        data,
    )


@router.get(
    "/",
    response_model=list[SupplementResponse],
)
def get_all_supplements(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    return service.get_all(
        db,
        skip,
        limit,
    )


@router.get(
    "/{supplement_id}",
    response_model=SupplementResponse,
)
def get_supplement_by_id(
    supplement_id: int,
    db: Session = Depends(get_db),
):
    return service.get_by_id(
        db,
        supplement_id,
    )


@router.patch(
    "/{supplement_id}",
    response_model=SupplementResponse,
)
def update_supplement(
    supplement_id: int,
    data: SupplementUpdate,
    db: Session = Depends(get_db),
):
    return service.update_supplement(
        db,
        supplement_id,
        data,
    )


@router.delete(
    "/{supplement_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_supplement(
    supplement_id: int,
    db: Session = Depends(get_db),
):
    service.delete_supplement(
        db,
        supplement_id,
    )

    return None