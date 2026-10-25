from datetime import date

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sleep import SleepEntry


class SleepRepository:

    def create(self, db: AsyncSession, entry: SleepEntry) -> SleepEntry:
        db.add(entry)
        return entry

    def update(self, entry: SleepEntry) -> SleepEntry:
        return entry

    async def delete(self, db: AsyncSession, entry: SleepEntry) -> None:
        await db.delete(entry)

    async def get_by_id_for_user(
        self,
        db: AsyncSession,
        sleep_id: int,
        user_id: int,
    ) -> SleepEntry | None:
        stmt = select(SleepEntry).where(
            SleepEntry.id == sleep_id,
            SleepEntry.user_id == user_id,
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_date_for_user(
        self,
        db: AsyncSession,
        sleep_date: date,
        user_id: int,
    ) -> SleepEntry | None:
        stmt = select(SleepEntry).where(
            SleepEntry.sleep_date == sleep_date,
            SleepEntry.user_id == user_id,
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_for_user(
        self,
        db: AsyncSession,
        user_id: int,
        date_from: date | None = None,
        date_to: date | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> list[SleepEntry]:
        stmt = select(SleepEntry).where(SleepEntry.user_id == user_id)

        if date_from is not None:
            stmt = stmt.where(SleepEntry.sleep_date >= date_from)

        if date_to is not None:
            stmt = stmt.where(SleepEntry.sleep_date <= date_to)

        stmt = (
            stmt.order_by(SleepEntry.sleep_date.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await db.execute(stmt)
        return list(result.scalars().all())


    async def count_for_user(
        self,
        db: AsyncSession,
        user_id: int,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> int:
        stmt = select(func.count()).select_from(SleepEntry).where(
            SleepEntry.user_id == user_id
        )

        if date_from is not None:
            stmt = stmt.where(SleepEntry.sleep_date >= date_from)

        if date_to is not None:
            stmt = stmt.where(SleepEntry.sleep_date <= date_to)

        result = await db.execute(stmt)
        return result.scalar_one()



    async def list_for_research(
        self,
        db: AsyncSession,
        date_from: date,
        date_to: date,
    ) -> list[SleepEntry]:
        stmt = (
            select(SleepEntry)
            .where(
                SleepEntry.sleep_date >= date_from,
                SleepEntry.sleep_date <= date_to,
            )
            .order_by(SleepEntry.sleep_date)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())