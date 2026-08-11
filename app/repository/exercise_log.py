# app/repository/exercise_log.py

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.exercise_log import ExerciseLog


class ExerciseLogRepository:

    def get_by_id(
        self,
        db: Session,
        exercise_log_id: int,
    ) -> ExerciseLog | None:

        stmt = select(ExerciseLog).where(
            ExerciseLog.id == exercise_log_id
        )

        return db.execute(stmt).scalar_one_or_none()

    def get_by_session(
        self,
        db: Session,
        workout_session_id: int,
    ) -> list[ExerciseLog]:

        stmt = (
            select(ExerciseLog)
            .where(
                ExerciseLog.workout_session_id == workout_session_id
            )
            .order_by(ExerciseLog.exercise_order)
        )

        return db.execute(stmt).scalars().all()

    def get_by_session_and_exercise(
        self,
        db: Session,
        workout_session_id: int,
        exercise_id: int,
    ) -> ExerciseLog | None:

        stmt = select(ExerciseLog).where(
            ExerciseLog.workout_session_id == workout_session_id,
            ExerciseLog.exercise_id == exercise_id,
        )

        return db.execute(stmt).scalar_one_or_none()

    def get_by_order_and_session(
        self,
        db: Session,
        workout_session_id: int,
        exercise_order: int,
    ) -> ExerciseLog | None:

        stmt = select(ExerciseLog).where(
            ExerciseLog.workout_session_id == workout_session_id,
            ExerciseLog.exercise_order == exercise_order,
        )

        return db.execute(stmt).scalar_one_or_none()

    def create(
        self,
        db: Session,
        exercise_log: ExerciseLog,
    ) -> ExerciseLog:

        db.add(exercise_log)
        return exercise_log

    def update(
        self,
        exercise_log: ExerciseLog,
    ) -> ExerciseLog:

        return exercise_log

    def delete(
        self,
        db: Session,
        exercise_log: ExerciseLog,
    ) -> None:

        db.delete(exercise_log)