from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.achievement import Achievement


class AchievementRepository:
    def __init__(self):
        pass

    async def get_by_id(self, db: AsyncSession, achievement_id: int) -> Achievement | None:
        stmt = select(Achievement).where(Achievement.id == achievement_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_code(self, db: AsyncSession, code: str) -> Achievement | None:
        stmt = select(Achievement).where(Achievement.code == code)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_name(self, db: AsyncSession, name: str) -> Achievement | None:
        stmt = select(Achievement).where(Achievement.name == name)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, db: AsyncSession, skip: int = 0, limit: int = 20) -> list[Achievement]:
        stmt = select(Achievement).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_all_active(self, db: AsyncSession, skip: int = 0, limit: int = 20) -> list[Achievement]:
        stmt = (
            select(Achievement)
            .where(Achievement.is_active.is_(True))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    def create(self, db: AsyncSession, achievement_db: Achievement) -> Achievement:
        db.add(achievement_db)
        return achievement_db

    def update(self, achievement_db: Achievement) -> Achievement:
        return achievement_db

    async def exists_by_code(self, db: AsyncSession, code: str) -> bool:
        stmt = select(Achievement).where(Achievement.code == code)
        result = await db.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def exists_by_name(self, db: AsyncSession, name: str) -> bool:
        stmt = select(Achievement).where(Achievement.name == name)
        result = await db.execute(stmt)
        return result.scalar_one_or_none() is not None