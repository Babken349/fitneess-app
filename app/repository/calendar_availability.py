from datetime import date
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.calendar_availability import CalendarAvailability


class CalendarAvailabilityRepository:

    def create(
        self,
        db: AsyncSession,
        availability: CalendarAvailability,
    ) -> CalendarAvailability:
        db.add(availability)
        return availability

    async def get_by_id(
        self,
        db: AsyncSession,
        availability_id: int,
    ) -> CalendarAvailability | None:
        stmt = select(CalendarAvailability).where(
            CalendarAvailability.id == availability_id
        )

        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_user_and_date(
        self,
        db: AsyncSession,
        user_id: int,
        target_date: date,
    ) -> CalendarAvailability | None:
        stmt = select(CalendarAvailability).where(
            CalendarAvailability.user_id == user_id,
            CalendarAvailability.date == target_date,
        )

        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_calendar(
        self,
        db: AsyncSession,
        user_id: int,
        start_date: date,
        end_date: date,
    ) -> list[CalendarAvailability]:
        stmt = (
            select(CalendarAvailability)
            .where(
                CalendarAvailability.user_id == user_id,
                CalendarAvailability.date >= start_date,
                CalendarAvailability.date <= end_date,
            )
            .order_by(CalendarAvailability.date)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    def update(
        self,
        availability: CalendarAvailability,
    ) -> CalendarAvailability:
        return availability

    async def delete(
        self,
        db: AsyncSession,
        availability: CalendarAvailability,
    ) -> None:
        await db.delete(availability)