from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reminder import Reminder
from app.models.users import User

from app.schemas.reminder import (
    ReminderCreate,
    ReminderUpdate,
)

from app.repository.reminder import ReminderRepository
from app.repository.user_supplements import (
    UserSupplementRepository,
)

from app.exceptions import (
    UserSupplementNotFoundError,
    UserSupplementAccessDeniedError,
    SupplementReminderNotFoundError,
    SupplementReminderAlreadyExistsError,
    SupplementReminderAccessDeniedError,
)


class ReminderService:

    def __init__(self):
        self.reminder_repo = ReminderRepository()
        self.user_supplement_repo = UserSupplementRepository()

    async def create_reminder(
        self,
        db: AsyncSession,
        user_supplement_id: int,
        data: ReminderCreate,
        current_user: User,
    ) -> Reminder:

        user_supplement = await self.user_supplement_repo.get_by_id(
            db,
            user_supplement_id,
        )

        if not user_supplement:
            raise UserSupplementNotFoundError(
                user_supplement_id
            )

        if user_supplement.user_id != current_user.id:
            raise UserSupplementAccessDeniedError(
                user_supplement_id
            )

        duplicate = await self.reminder_repo.exists_duplicate(
            db,
            current_user.id,
            user_supplement_id,
            data.day_of_week,
            data.time_of_day,
        )

        if duplicate:
            raise SupplementReminderAlreadyExistsError()

        reminder = Reminder(
            user_id=current_user.id,
            user_supplement_id=user_supplement_id,
            day_of_week=data.day_of_week,
            time_of_day=data.time_of_day,
            is_active=data.is_active,
        )

        self.reminder_repo.create(
            db,
            reminder,
        )

        await db.commit()
        await db.refresh(reminder)

        return reminder

    async def get_by_id(
        self,
        db: AsyncSession,
        reminder_id: int,
        current_user: User,
    ) -> Reminder:

        reminder = await self.reminder_repo.get_by_id(
            db,
            reminder_id,
        )

        if not reminder:
            raise SupplementReminderNotFoundError(
                reminder_id
            )

        if reminder.user_id != current_user.id:
            raise SupplementReminderAccessDeniedError(
                reminder_id
            )

        return reminder

    async def get_my_reminders(
        self,
        db: AsyncSession,
        current_user: User,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Reminder]:

        return await self.reminder_repo.get_by_user(
            db,
            current_user.id,
            skip,
            limit,
        )

    async def get_by_user_supplement(
        self,
        db: AsyncSession,
        user_supplement_id: int,
        current_user: User,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Reminder]:

        user_supplement = (
            await self.user_supplement_repo.get_by_id(
                db,
                user_supplement_id,
            )
        )

        if not user_supplement:
            raise UserSupplementNotFoundError(
                user_supplement_id
            )

        if user_supplement.user_id != current_user.id:
            raise UserSupplementAccessDeniedError(
                user_supplement_id
            )

        return await self.reminder_repo.get_by_user_supplement(
            db,
            user_supplement_id,
            skip,
            limit,
        )

    async def update_reminder(
        self,
        db: AsyncSession,
        reminder_id: int,
        data: ReminderUpdate,
        current_user: User,
    ) -> Reminder:

        reminder = await self.get_by_id(
            db,
            reminder_id,
            current_user,
        )

        update_data = data.model_dump(
            exclude_unset=True,
        )

        for key, value in update_data.items():
            setattr(
                reminder,
                key,
                value,
            )

        self.reminder_repo.update(
            reminder,
        )

        await db.commit()
        await db.refresh(reminder)

        return reminder

    async def activate_reminder(
        self,
        db: AsyncSession,
        reminder_id: int,
        current_user: User,
    ) -> Reminder:

        return await self.update_reminder(
            db,
            reminder_id,
            ReminderUpdate(
                is_active=True,
            ),
            current_user,
        )

    async def deactivate_reminder(
        self,
        db: AsyncSession,
        reminder_id: int,
        current_user: User,
    ) -> Reminder:

        return await self.update_reminder(
            db,
            reminder_id,
            ReminderUpdate(
                is_active=False,
            ),
            current_user,
        )

    async def delete_reminder(
        self,
        db: AsyncSession,
        reminder_id: int,
        current_user: User,
    ) -> None:

        reminder = await self.get_by_id(
            db,
            reminder_id,
            current_user,
        )

        await self.reminder_repo.delete(
            db,
            reminder,
        )

        await db.commit()

    async def get_active_reminders(
        self,
        db: AsyncSession,
        current_user: User,
    ) -> list[Reminder]:

        return await self.reminder_repo.get_active_by_user(
            db,
            current_user.id,
        )