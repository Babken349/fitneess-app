from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.supplement_intake import SupplementIntake


class SupplementIntakeRepository:

    def create(
        self,
        db: AsyncSession,
        intake: SupplementIntake,
    ) -> SupplementIntake:
        db.add(intake)
        return intake

    def update(
        self,
        intake: SupplementIntake,
    ) -> SupplementIntake:
        return intake

    async def delete(
        self,
        db: AsyncSession,
        intake: SupplementIntake,
    ) -> None:
        await db.delete(intake)

    async def get_by_id(
        self,
        db: AsyncSession,
        intake_id: int,
    ) -> SupplementIntake | None:
        stmt = select(SupplementIntake).where(
            SupplementIntake.id == intake_id
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_user(
        self,
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
    ) -> list[SupplementIntake]:
        stmt = (
            select(SupplementIntake)
            .where(SupplementIntake.user_id == user_id)
            .order_by(SupplementIntake.taken_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_by_user_supplement(
        self,
        db: AsyncSession,
        user_supplement_id: int,
        skip: int = 0,
        limit: int = 20,
    ) -> list[SupplementIntake]:
        stmt = (
            select(SupplementIntake)
            .where(
                SupplementIntake.user_supplement_id
                == user_supplement_id
            )
            .order_by(SupplementIntake.taken_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_by_status(
        self,
        db: AsyncSession,
        user_id: int,
        status: str,
        skip: int = 0,
        limit: int = 20,
    ) -> list[SupplementIntake]:
        stmt = (
            select(SupplementIntake)
            .where(
                SupplementIntake.user_id == user_id,
                SupplementIntake.status == status,
            )
            .order_by(SupplementIntake.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_by_date_range(
        self,
        db: AsyncSession,
        user_id: int,
        start_at: datetime,
        end_at: datetime,
    ) -> list[SupplementIntake]:
        stmt = (
            select(SupplementIntake)
            .where(
                SupplementIntake.user_id == user_id,
                SupplementIntake.created_at >= start_at,
                SupplementIntake.created_at <= end_at,
            )
            .order_by(SupplementIntake.created_at.desc())
        )
        result = await db.execute(stmt)
        return result.scalars().all()