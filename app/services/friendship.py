from sqlalchemy.orm import Session

from app.models.friendship import Friendship
from app.models.users import User

from app.schemas.friendship import FriendshipCreate

from app.repository.friendship import FriendshipRepository

from app.exceptions import (
    FriendshipNotFoundError,
    FriendshipAlreadyExistsError,
    FriendshipRequestAlreadyExistsError,
    FriendshipRequestNotFoundError,
    FriendshipAccessDeniedError,
    CannotFriendYourselfError,
    InvalidFriendshipStatusError,
)


class FriendshipService:

    def __init__(self):
        self.friendship_repo = FriendshipRepository()

    # =========================
    # INTERNAL
    # =========================

    def _get_user_friendship(
        self,
        db: Session,
        friendship_id: int,
        current_user: User,
    ) -> Friendship:

        friendship = self.friendship_repo.get_by_id(
            db,
            friendship_id,
        )

        if not friendship:
            raise FriendshipNotFoundError(
                friendship_id
            )

        if (
            friendship.requester_id != current_user.id
            and
            friendship.addressee_id != current_user.id
        ):
            raise FriendshipAccessDeniedError()

        return friendship

    # =========================
    # SEND REQUEST
    # =========================

    def send_request(
        self,
        db: Session,
        data: FriendshipCreate,
        current_user: User,
    ) -> Friendship:

        if data.addressee_id == current_user.id:
            raise CannotFriendYourselfError()

        existing = self.friendship_repo.get_between_users(
            db,
            current_user.id,
            data.addressee_id,
        )

        if existing:

            if existing.status == "pending":
                raise FriendshipRequestAlreadyExistsError()

            if existing.status == "accepted":
                raise FriendshipAlreadyExistsError()

            raise FriendshipAlreadyExistsError()

        friendship = Friendship(
            requester_id=current_user.id,
            addressee_id=data.addressee_id,
            status="pending",
        )

        self.friendship_repo.create(
            db,
            friendship,
        )

        db.commit()
        db.refresh(friendship)

        return friendship

    # =========================
    # ACCEPT REQUEST
    # =========================

    def accept_request(
        self,
        db: Session,
        friendship_id: int,
        current_user: User,
    ) -> Friendship:

        friendship = self._get_user_friendship(
            db,
            friendship_id,
            current_user,
        )

        if friendship.addressee_id != current_user.id:
            raise FriendshipAccessDeniedError()

        if friendship.status != "pending":
            raise InvalidFriendshipStatusError()

        friendship.status = "accepted"

        self.friendship_repo.update(db, friendship)

        db.commit()
        db.refresh(friendship)

        return friendship

    # =========================
    # REJECT REQUEST
    # =========================

    def reject_request(
        self,
        db: Session,
        friendship_id: int,
        current_user: User,
    ) -> None:

        friendship = self._get_user_friendship(
            db,
            friendship_id,
            current_user,
        )

        if friendship.addressee_id != current_user.id:
            raise FriendshipAccessDeniedError()

        if friendship.status != "pending":
            raise InvalidFriendshipStatusError()

        self.friendship_repo.delete(
            db,
            friendship,
        )

        db.commit()

    # =========================
    # DELETE FRIEND
    # =========================

    def delete_friend(
        self,
        db: Session,
        friendship_id: int,
        current_user: User,
    ) -> None:

        friendship = self._get_user_friendship(
            db,
            friendship_id,
            current_user,
        )

        if friendship.status != "accepted":
            raise InvalidFriendshipStatusError()

        self.friendship_repo.delete(
            db,
            friendship,
        )

        db.commit()

    # =========================
    # GET BY ID
    # =========================

    def get_by_id(
        self,
        db: Session,
        friendship_id: int,
        current_user: User,
    ) -> Friendship:

        return self._get_user_friendship(
            db,
            friendship_id,
            current_user,
        )

    # =========================
    # GET FRIENDS
    # =========================

    def get_friends(
        self,
        db: Session,
        current_user: User,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Friendship]:

        return self.friendship_repo.get_friends_by_user(
            db,
            current_user.id,
            skip,
            limit,
        )

    # =========================
    # INCOMING REQUESTS
    # =========================

    def get_incoming_requests(
        self,
        db: Session,
        current_user: User,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Friendship]:

        return self.friendship_repo.get_incoming_requests(
            db,
            current_user.id,
            skip,
            limit,
        )

    # =========================
    # OUTGOING REQUESTS
    # =========================

    def get_outgoing_requests(
        self,
        db: Session,
        current_user: User,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Friendship]:

        return self.friendship_repo.get_outgoing_requests(
            db,
            current_user.id,
            skip,
            limit,
        )