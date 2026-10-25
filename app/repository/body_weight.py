from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.body_weight import BodyWeight


class BodyWeightRepository:
    def __init__(self):
        pass

    async def get_by_id(self, db: AsyncSession, weight_id: int) -> BodyWeight | None:
        stmt = select(BodyWeight).where(BodyWeight.id == weight_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_user(
        self,
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
    ) -> list[BodyWeight]:
        stmt = (
            select(BodyWeight)
            .where(BodyWeight.user_id == user_id)
            .order_by(BodyWeight.recorded_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    async def count_by_user(
        self,
        db:AsyncSession,
        user_id:int,    
    ) -> int:
        stmt = select(func.count()).select_from(BodyWeight).where(
            BodyWeight.user_id == user_id
        )
        result = await db.execute(stmt)
        return result.scalar_one()

    def create(self, db: AsyncSession, weight_db: BodyWeight) -> BodyWeight:
        db.add(weight_db)
        return weight_db

    def update(self, db: AsyncSession, weight_db: BodyWeight) -> BodyWeight:
        return weight_db

    async def delete(self, db: AsyncSession, weight_db: BodyWeight) -> None:
        await db.delete(weight_db)