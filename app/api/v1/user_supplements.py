from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session


from app.auth.dependencies import get_current_user
from app.core.dependency import get_db
from app.models.users import User
from app.schemas.user_supplements import (
    UserSupplementCreate,
    UserSupplementUpdate,
    UserSupplementResponse,
)
from app.services.user_supplements import UserSupplementService


router = APIRouter()
service = UserSupplementService()


@router.post(
    "/user-supplements",
    response_model=UserSupplementResponse,
    status_code=201,
)
def create_user_supplement(
    data: UserSupplementCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.create_user_supplement(
        db,
        data,
        current_user,
    )


@router.get(
    "/user-supplements",
    response_model=list[UserSupplementResponse],
)
def get_my_supplements(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.get_my_supplements(
        db,
        current_user,
        skip,
        limit,
    )


@router.get(
    "/user-supplements/{user_supplement_id}",
    response_model=UserSupplementResponse,
)
def get_user_supplement_by_id(
    user_supplement_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.get_by_id(
        db,
        user_supplement_id,
        current_user,
    )


@router.patch(
    "/user-supplements/{user_supplement_id}",
    response_model=UserSupplementResponse,
)
def update_user_supplement(
    user_supplement_id: int,
    data: UserSupplementUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.update_user_supplement(
        db,
        user_supplement_id,
        data,
        current_user,
    )


@router.delete(
    "/user-supplements/{user_supplement_id}",
    status_code=204,
)
def delete_user_supplement(
    user_supplement_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service.delete_user_supplement(
        db,
        user_supplement_id,
        current_user,
    )