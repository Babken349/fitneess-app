from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.exercise import MuscleGroup


class MuscleGroupRepository:
    
    async def get_by_id(self, db: AsyncSession, muscle_group_id: int) -> MuscleGroup | None:
        stmt = select(MuscleGroup).where(MuscleGroup.id == muscle_group_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_name(self, db: AsyncSession, name: str) -> MuscleGroup | None:
        stmt = select(MuscleGroup).where(MuscleGroup.name == name)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()