from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.exercise import Equipment


class EquipmentRepository:
    
    async def get_by_id(self, db: AsyncSession, equipment_id: int) -> Equipment | None:
        stmt = select(Equipment).where(Equipment.id == equipment_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_name(self, db: AsyncSession, name: str) -> Equipment | None:
        stmt = select(Equipment).where(Equipment.name == name)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()