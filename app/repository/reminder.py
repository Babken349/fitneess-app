from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.reminder import Reminder


class ReminderRepository:

    def create(
        self,
        db: Session,
        reminder: Reminder,
    ) -> Reminder:

        db.add(reminder)

        return reminder

    def update(
        self,
        reminder: Reminder,
    ) -> Reminder:

        return reminder

    def delete(
        self,
        db: Session,
        reminder: Reminder,
    ) -> None:

        db.delete(reminder)

    def get_by_id(
        self,
        db: Session,
        reminder_id: int,
    ) -> Reminder | None:

        stmt = select(Reminder).where(
            Reminder.id == reminder_id
        )

        return db.execute(stmt).scalar_one_or_none()

    def get_by_user(
        self,
        db: Session,
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

        return db.execute(stmt).scalars().all()

    def get_by_user_supplement(
        self,
        db: Session,
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

        return db.execute(stmt).scalars().all()

    def get_active_by_user(
        self,
        db: Session,
        user_id: int,
    ) -> list[Reminder]:

        stmt = (
            select(Reminder)
            .where(
                Reminder.user_id == user_id,
                Reminder.is_active.is_(True),
            )
        )

        return db.execute(stmt).scalars().all()

    def get_active_by_user_supplement(
        self,
        db: Session,
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

        return db.execute(stmt).scalars().all()

    def exists_duplicate(
    self,
    db: Session,
    user_id: int,
    user_supplement_id: int | None,
    day_of_week: int,
    time_of_day,
    exclude_id: int | None = None,
    ) -> bool:

        stmt = select(Reminder.id).where(
            Reminder.user_id == user_id,
            Reminder.user_supplement_id == user_supplement_id,
            Reminder.day_of_week == day_of_week,
            Reminder.time_of_day == time_of_day,
            Reminder.is_active.is_(True),
        )

        if exclude_id is not None:
            stmt = stmt.where(
                Reminder.id != exclude_id
            )

        return db.execute(stmt).scalar_one_or_none() is not None