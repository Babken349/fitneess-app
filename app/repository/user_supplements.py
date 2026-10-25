from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_supplements import UserSupplement


class UserSupplementRepository:

    def create(
        self,
        db: AsyncSession,
        user_supplement: UserSupplement,
    ) -> UserSupplement:
        db.add(user_supplement)
        return user_supplement

    def update(
        self,
        user_supplement: UserSupplement,
    ) -> UserSupplement:
        return user_supplement

    async def delete(
        self,
        db: AsyncSession,
        user_supplement: UserSupplement,
    ) -> None:
        await db.delete(user_supplement)

    async def get_by_id(
        self,
        db: AsyncSession,
        user_supplement_id: int,
    ) -> UserSupplement | None:
        stmt = select(UserSupplement).where(
            UserSupplement.id == user_supplement_id
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_user_and_supplement(
        self,
        db: AsyncSession,
        user_id: int,
        supplement_id: int,
    ) -> UserSupplement | None:
        stmt = select(UserSupplement).where(
            UserSupplement.user_id == user_id,
            UserSupplement.supplement_id == supplement_id,
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_user(
        self,
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
    ) -> list[UserSupplement]:
        stmt = (
            select(UserSupplement)
            .where(UserSupplement.user_id == user_id)
            .order_by(UserSupplement.id)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return result.scalars().all()