from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reminder import Reminder


class ReminderRepository:

    def create(
        self,
        db: AsyncSession,
        reminder: Reminder,
    ) -> Reminder:

        db.add(reminder)

        return reminder

    def update(
        self,
        reminder: Reminder,
    ) -> Reminder:

        return reminder

    async def delete(
        self,
        db: AsyncSession,
        reminder: Reminder,
    ) -> None:

        await db.delete(reminder)

    async def get_by_id(
        self,
        db: AsyncSession,
        reminder_id: int,
    ) -> Reminder | None:

        stmt = select(Reminder).where(
            Reminder.id == reminder_id
        )

        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_user(
        self,
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Reminder]:

        stmt = (
            select(Reminder)
            .where(
                Reminder.user_id == user_id
            )
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
    ) -> list[Reminder]:

        stmt = (
            select(Reminder)
            .where(
                Reminder.user_supplement_id
                == user_supplement_id
            )
            .offset(skip)
            .limit(limit)
        )

        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_active_by_user(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> list[Reminder]:

        stmt = (
            select(Reminder)
            .where(
                Reminder.user_id == user_id,
                Reminder.is_active.is_(True),
            )
        )

        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_active_by_user_supplement(
        self,
        db: AsyncSession,
        user_supplement_id: int,
    ) -> list[Reminder]:

        stmt = (
            select(Reminder)
            .where(
                Reminder.user_supplement_id
                == user_supplement_id,
                Reminder.is_active.is_(True),
            )
        )

        result = await db.execute(stmt)
        return result.scalars().all()

    async def exists_duplicate(
        self,
        db: AsyncSession,
        user_id: int,
        user_supplement_id: int | None,
        day_of_week: int,
        time_of_day: str,
        exclude_id: int | None = None,
    ) -> bool:

        stmt = select(Reminder.id).where(
            Reminder.user_id == user_id,
            Reminder.user_supplement_id == user_supplement_id,
            Reminder.day_of_week == day_of_week,
            Reminder.time_of_day == time_of_day,
            Reminder.is_active.is_(True),
        ).limit(1)

        if exclude_id is not None:
            stmt = stmt.where(Reminder.id != exclude_id)

        result = await db.execute(stmt)
        return result.first() is not None