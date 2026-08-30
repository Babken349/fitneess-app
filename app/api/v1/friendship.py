from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependency import get_db
from app.auth.dependencies import get_current_user

from app.models.users import User

from app.schemas.friendship import (
    FriendshipCreate,
    FriendshipResponse,
)

from app.services.friendship import FriendshipService


router = APIRouter()
service = FriendshipService()


# =========================
# SEND REQUEST
# =========================

@router.post(
    "/",
    response_model=FriendshipResponse,
    status_code=status.HTTP_201_CREATED,
)
def send_request(
    data: FriendshipCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.send_request(
        db,
        data,
        current_user,
    )


# =========================
# GET BY ID
# =========================

@router.get(
    "/{friendship_id}",
    response_model=FriendshipResponse,
)
def get_by_id(
    friendship_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.get_by_id(
        db,
        friendship_id,
        current_user,
    )


# =========================
# ACCEPT REQUEST
# =========================

@router.patch(
    "/{friendship_id}/accept",
    response_model=FriendshipResponse,
)
def accept_request(
    friendship_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.accept_request(
        db,
        friendship_id,
        current_user,
    )


# =========================
# REJECT REQUEST
# =========================

@router.delete(
    "/{friendship_id}/reject",
    status_code=status.HTTP_204_NO_CONTENT,
)
def reject_request(
    friendship_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service.reject_request(
        db,
        friendship_id,
        current_user,
    )


# =========================
# DELETE FRIEND
# =========================

@router.delete(
    "/{friendship_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_friend(
    friendship_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service.delete_friend(
        db,
        friendship_id,
        current_user,
    )


# =========================
# MY FRIENDS
# =========================

@router.get(
    "/me/friends",
    response_model=list[FriendshipResponse],
)
def get_friends(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.get_friends(
        db,
        current_user,
        skip,
        limit,
    )


# =========================
# INCOMING REQUESTS
# =========================

@router.get(
    "/me/requests/incoming",
    response_model=list[FriendshipResponse],
)
def get_incoming_requests(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.get_incoming_requests(
        db,
        current_user,
        skip,
        limit,
    )


# =========================
# OUTGOING REQUESTS
# =========================

@router.get(
    "/me/requests/outgoing",
    response_model=list[FriendshipResponse],
)
def get_outgoing_requests(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.get_outgoing_requests(
        db,
        current_user,
        skip,
        limit,
    )