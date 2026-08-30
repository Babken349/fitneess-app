from sqlalchemy.orm import Session

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

    def create_reminder(
    self,
    db: Session,
    user_supplement_id: int,
    data: ReminderCreate,
    current_user: User,
    ) -> Reminder:

        user_supplement = self.user_supplement_repo.get_by_id(
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

        existing = self.reminder_repo.get_existing(
            db,
            current_user.id,
            user_supplement_id,
            data.day_of_week,
            data.time_of_day,
        )

        if existing and existing.is_active:
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

        db.commit()
        db.refresh(reminder)

        return reminder

    def get_by_id(
        self,
        db: Session,
        reminder_id: int,
        current_user: User,
    ) -> Reminder:

        reminder = self.reminder_repo.get_by_id(
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

    def get_my_reminders(
        self,
        db: Session,
        current_user: User,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Reminder]:

        return self.reminder_repo.get_by_user(
            db,
            current_user.id,
            skip,
            limit,
        )

    def get_by_user_supplement(
        self,
        db: Session,
        user_supplement_id: int,
        current_user: User,
    ) -> list[Reminder]:

        user_supplement = (
            self.user_supplement_repo.get_by_id(
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

        return self.reminder_repo.get_by_user_supplement(
            db,
            user_supplement_id,
        )

    def update_reminder(
        self,
        db: Session,
        reminder_id: int,
        data: ReminderUpdate,
        current_user: User,
    ) -> Reminder:

        reminder = self.get_by_id(
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

        db.commit()
        db.refresh(reminder)

        return reminder


    def activate_reminder(
        self,
        db: Session,
        reminder_id: int,
        current_user: User,
    ) -> Reminder:

        return self.update_reminder(
            db,
            reminder_id,
            ReminderUpdate(
                is_active=True,
            ),
            current_user,
        )


    def deactivate_reminder(
        self,
        db: Session,
        reminder_id: int,
        current_user: User,
    ) -> Reminder:

        return self.update_reminder(
            db,
            reminder_id,
            ReminderUpdate(
                is_active=False,
            ),
            current_user,
        )
    def delete_reminder(
        self,
        db: Session,
        reminder_id: int,
        current_user: User,
    ) -> None:

        reminder = self.get_by_id(
            db,
            reminder_id,
            current_user,
        )

        self.reminder_repo.delete(
            db,
            reminder,
        )

        db.commit()