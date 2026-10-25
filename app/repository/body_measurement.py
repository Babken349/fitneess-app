from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.body_measurement import BodyMeasurement


class BodyMeasurementRepository:
    def __init__(self):
        pass

    async def get_by_id(self, db: AsyncSession, measurement_id: int) -> BodyMeasurement | None:
        stmt = select(BodyMeasurement).where(BodyMeasurement.id == measurement_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_user(
        self,
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
    ) -> list[BodyMeasurement]:
        stmt = (
            select(BodyMeasurement)
            .where(BodyMeasurement.user_id == user_id)
            .order_by(BodyMeasurement.recorded_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    def create(self, db: AsyncSession, measurement_db: BodyMeasurement) -> BodyMeasurement:
        db.add(measurement_db)
        return measurement_db

    def update(self, db: AsyncSession, measurement_db: BodyMeasurement) -> BodyMeasurement:
        return measurement_db

    async def delete(self, db: AsyncSession, measurement_db: BodyMeasurement) -> None:
        await db.delete(measurement_db)