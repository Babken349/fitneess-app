from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.set_log import SetLog


class SetLogRepository:

    def get_by_id(
        self,
        db: Session,
        set_log_id: int,
    ) -> SetLog | None:

        stmt = select(SetLog).where(
            SetLog.id == set_log_id
        )

        return db.execute(stmt).scalar_one_or_none()

    def get_by_exercise_log(
        self,
        db: Session,
        exercise_log_id: int,
    ) -> list[SetLog]:

        stmt = (
            select(SetLog)
            .where(
                SetLog.exercise_log_id == exercise_log_id
            )
            .order_by(SetLog.set_number)
        )

        return db.execute(stmt).scalars().all()

    def get_by_number(
        self,
        db: Session,
        exercise_log_id: int,
        set_number: int,
    ) -> SetLog | None:

        stmt = select(SetLog).where(
            SetLog.exercise_log_id == exercise_log_id,
            SetLog.set_number == set_number,
        )

        return db.execute(stmt).scalar_one_or_none()

    def create(
        self,
        db: Session,
        set_log: SetLog,
    ) -> SetLog:

        db.add(set_log)
        return set_log

    def update(
        self,
        set_log: SetLog,
    ) -> SetLog:

        return set_log

    def delete(
        self,
        db: Session,
        set_log: SetLog,
    ) -> None:

        db.delete(set_log)