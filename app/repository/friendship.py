from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.friendship import Friendship


class FriendshipRepository:

    def create(self, db: Session, friendship: Friendship) -> Friendship:
        db.add(friendship)
        return friendship

    def delete(self, db: Session, friendship: Friendship) -> None:
        db.delete(friendship)

    def update(self, db: Session, friendship: Friendship) -> Friendship:
        return friendship

    def get_by_id(self, db: Session, friendship_id: int) -> Friendship | None:
        stmt = select(Friendship).where(
            Friendship.id == friendship_id
        )
        return db.execute(stmt).scalar_one_or_none()

    def get_between_users(
        self,
        db: Session,
        user_id: int,
        other_user_id: int,
    ) -> Friendship | None:
        stmt = select(Friendship).where(
            (
                (Friendship.requester_id == user_id)
                & (Friendship.addressee_id == other_user_id)
            )
            |
            (
                (Friendship.requester_id == other_user_id)
                & (Friendship.addressee_id == user_id)
            )
        )

        return db.execute(stmt).scalar_one_or_none()

    def get_friends_by_user(
        self,
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Friendship]:
        stmt = (
            select(Friendship)
            .where(
                (
                    (Friendship.requester_id == user_id)
                    | (Friendship.addressee_id == user_id)
                ),
                Friendship.status == "accepted",
            )
            .offset(skip)
            .limit(limit)
        )

        return db.execute(stmt).scalars().all()

    def get_incoming_requests(
        self,
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Friendship]:
        stmt = (
            select(Friendship)
            .where(
                Friendship.addressee_id == user_id,
                Friendship.status == "pending",
            )
            .offset(skip)
            .limit(limit)
        )

        return db.execute(stmt).scalars().all()

    def get_outgoing_requests(
        self,
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Friendship]:
        stmt = (
            select(Friendship)
            .where(
                Friendship.requester_id == user_id,
                Friendship.status == "pending",
            )
            .offset(skip)
            .limit(limit)
        )

        return db.execute(stmt).scalars().all()