from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import (
    FriendshipAccessDeniedError,
    CalendarAvailabilityNotFoundError,
)
from app.models.calendar_availability import CalendarAvailability
from app.models.users import User
from app.repository.calendar_availability import (
    CalendarAvailabilityRepository,
)
from app.repository.friendship import FriendshipRepository
from app.schemas.calendar_availability import (
    CalendarAvailabilityCreate,
    CalendarAvailabilityUpdate,
)


class CalendarAvailabilityService:

    def __init__(self):
        self.calendar_repo = CalendarAvailabilityRepository()
        self.friendship_repo = FriendshipRepository()

    async def _check_friendship(
        self,
        db: AsyncSession,
        current_user_id: int,
        friend_id: int,
    ) -> None:
        friendship = await self.friendship_repo.get_between_users(
            db,
            current_user_id,
            friend_id,
        )

        if friendship is None or friendship.status != "accepted":
            raise FriendshipAccessDeniedError()

    async def create_or_update(
        self,
        db: AsyncSession,
        current_user: User,
        data: CalendarAvailabilityCreate,
    ) -> CalendarAvailability:

        existing = await self.calendar_repo.get_by_user_and_date(
            db,
            current_user.id,
            data.date,
        )

        if existing:
            existing.is_available = data.is_available
            existing.note = data.note

            self.calendar_repo.update(existing)

            await db.commit()
            await db.refresh(existing)

            return existing

        availability = CalendarAvailability(
            user_id=current_user.id,
            date=data.date,
            is_available=data.is_available,
            note=data.note,
        )

        self.calendar_repo.create(
            db,
            availability,
        )

        await db.commit()
        await db.refresh(availability)

        return availability

    async def update(
        self,
        db: AsyncSession,
        current_user: User,
        availability_id: int,
        data: CalendarAvailabilityUpdate,
    ) -> CalendarAvailability:

        availability = await self.calendar_repo.get_by_id(
            db,
            availability_id,
        )

        if availability is None:
            raise CalendarAvailabilityNotFoundError()

        if availability.user_id != current_user.id:
            raise FriendshipAccessDeniedError()

        update_data = data.model_dump(
            exclude_unset=True,
        )

        for key, value in update_data.items():
            setattr(availability, key, value)

        self.calendar_repo.update(availability)

        await db.commit()
        await db.refresh(availability)

        return availability

    async def delete(
        self,
        db: AsyncSession,
        current_user: User,
        availability_id: int,
    ) -> None:

        availability = await self.calendar_repo.get_by_id(
            db,
            availability_id,
        )

        if availability is None:
            raise CalendarAvailabilityNotFoundError()

        if availability.user_id != current_user.id:
            raise FriendshipAccessDeniedError()

        await self.calendar_repo.delete(
            db,
            availability,
        )

        await db.commit()

    async def get_my_calendar(
        self,
        db: AsyncSession,
        current_user: User,
        start_date: date,
        end_date: date,
    ) -> list[CalendarAvailability]:

        return await self.calendar_repo.get_user_calendar(
            db,
            current_user.id,
            start_date,
            end_date,
        )

    async def get_friend_calendar(
        self,
        db: AsyncSession,
        current_user: User,
        friend_id: int,
        start_date: date,
        end_date: date,
    ) -> list[CalendarAvailability]:

        await self._check_friendship(
            db,
            current_user.id,
            friend_id,
        )

        return await self.calendar_repo.get_user_calendar(
            db,
            friend_id,
            start_date,
            end_date,
        )