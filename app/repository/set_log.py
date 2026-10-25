from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.set_log import SetLog


class SetLogRepository:

    async def get_by_id(
        self,
        db: AsyncSession,
        set_log_id: int,
    ) -> SetLog | None:

        stmt = select(SetLog).where(
            SetLog.id == set_log_id
        )

        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_exercise_log(
        self,
        db: AsyncSession,
        exercise_log_id: int,
    ) -> list[SetLog]:

        stmt = (
            select(SetLog)
            .where(
                SetLog.exercise_log_id == exercise_log_id
            )
            .order_by(SetLog.set_number)
        )

        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_by_number(
        self,
        db: AsyncSession,
        exercise_log_id: int,
        set_number: int,
    ) -> SetLog | None:

        stmt = select(SetLog).where(
            SetLog.exercise_log_id == exercise_log_id,
            SetLog.set_number == set_number,
        )

        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    def create(
        self,
        db: AsyncSession,
        set_log: SetLog,
    ) -> SetLog:

        db.add(set_log)
        return set_log

    def update(
        self,
        set_log: SetLog,
    ) -> SetLog:

        return set_log

    async def delete(
        self,
        db: AsyncSession,
        set_log: SetLog,
    ) -> None:

        await db.delete(set_log)