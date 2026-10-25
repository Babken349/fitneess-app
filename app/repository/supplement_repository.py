from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.supplements import Supplement


class SupplementRepository:

    def create(
        self,
        db: AsyncSession,
        supplement: Supplement,
    ) -> Supplement:
        db.add(supplement)
        return supplement

    def update(
        self,
        supplement: Supplement,
    ) -> Supplement:
        return supplement

    async def delete(
        self,
        db: AsyncSession,
        supplement: Supplement,
    ) -> None:
        await db.delete(supplement)

    async def get_by_id(
        self,
        db: AsyncSession,
        supplement_id: int,
    ) -> Supplement | None:
        stmt = select(Supplement).where(
            Supplement.id == supplement_id
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_name(
        self,
        db: AsyncSession,
        name: str,
    ) -> Supplement | None:
        stmt = select(Supplement).where(
            Supplement.name == name
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def exists_by_name(
        self,
        db: AsyncSession,
        name: str,
    ) -> bool:
        stmt = select(Supplement.id).where(
            Supplement.name == name
        ).limit(1)
        result = await db.execute(stmt)
        return result.first() is not None

    async def get_all(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Supplement]:
        stmt = (
            select(Supplement)
            .order_by(Supplement.id)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return result.scalars().all()