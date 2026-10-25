from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.friendship import Friendship


class FriendshipRepository:

    def create(self, db: AsyncSession, friendship: Friendship) -> Friendship:
        db.add(friendship)
        return friendship

    async def delete(self, db: AsyncSession, friendship: Friendship) -> None:
        await db.delete(friendship)

    def update(self, db: AsyncSession, friendship: Friendship) -> Friendship:
        return friendship

    async def get_by_id(self, db: AsyncSession, friendship_id: int) -> Friendship | None:
        stmt = select(Friendship).where(
            Friendship.id == friendship_id
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_between_users(
        self,
        db: AsyncSession,
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

        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_friends_by_user(
        self,
        db: AsyncSession,
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

        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_incoming_requests(
        self,
        db: AsyncSession,
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

        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_outgoing_requests(
        self,
        db: AsyncSession,
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

        result = await db.execute(stmt)
        return result.scalars().all()