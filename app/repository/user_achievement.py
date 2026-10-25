from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_achievement import UserAchievement


class UserAchievementRepository:
    def __init__(self):
        pass

    async def get_by_id(
        self, db: AsyncSession, user_achievement_id: int
    ) -> UserAchievement | None:
        stmt = select(UserAchievement).where(UserAchievement.id == user_achievement_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_user_and_achievement(
        self, db: AsyncSession, user_id: int, achievement_id: int
    ) -> UserAchievement | None:
        stmt = select(UserAchievement).where(
            UserAchievement.user_id == user_id,
            UserAchievement.achievement_id == achievement_id,
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_user(
        self, db: AsyncSession, user_id: int, skip: int = 0, limit: int = 20
    ) -> list[UserAchievement]:
        stmt = (
            select(UserAchievement)
            .where(UserAchievement.user_id == user_id)
            .order_by(UserAchievement.earned_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_by_achievement(
        self, db: AsyncSession, achievement_id: int, skip: int = 0, limit: int = 20
    ) -> list[UserAchievement]:
        stmt = (
            select(UserAchievement)
            .where(UserAchievement.achievement_id == achievement_id)
            .order_by(UserAchievement.id)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    def create(
        self, db: AsyncSession, user_achievement_db: UserAchievement
    ) -> UserAchievement:
        db.add(user_achievement_db)
        return user_achievement_db

    async def delete(
        self, db: AsyncSession, user_achievement_db: UserAchievement
    ) -> None:
        await db.delete(user_achievement_db)

    async def exists(self, db: AsyncSession, user_id: int, achievement_id: int) -> bool:
        stmt = (
            select(UserAchievement.id)
            .where(
                UserAchievement.user_id == user_id,
                UserAchievement.achievement_id == achievement_id,
            )
            .limit(1)
        )
        result = await db.execute(stmt)
        return result.first() is not None