from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.workout_session import WorkoutSession


class WorkoutSessionRepository:

    def get_by_id(
        self,
        db: Session,
        session_id: int,
    ) -> WorkoutSession | None:
        stmt = select(WorkoutSession).where(
            WorkoutSession.id == session_id
        )

        return db.execute(stmt).scalar_one_or_none()

    def get_by_user(
        self,
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
    ) -> list[WorkoutSession]:
        stmt = (
            select(WorkoutSession)
            .where(
                WorkoutSession.user_id == user_id
            )
            .order_by(WorkoutSession.started_at.desc())
            .offset(skip)
            .limit(limit)
        )

        return db.execute(stmt).scalars().all()

    def get_by_day(
        self,
        db: Session,
        user_id: int,
        workout_day_id: int,
    ) -> list[WorkoutSession]:
        stmt = (
            select(WorkoutSession)
            .where(
                WorkoutSession.user_id == user_id,
                WorkoutSession.workout_day_id == workout_day_id,
            )
            .order_by(WorkoutSession.started_at.desc())
        )

        return db.execute(stmt).scalars().all()

    def get_active_by_user(
        self,
        db: Session,
        user_id: int,
    ) -> WorkoutSession | None:
        stmt = (
            select(WorkoutSession)
            .where(
                WorkoutSession.user_id == user_id,
                WorkoutSession.finished_at.is_(None),
            )
            .order_by(WorkoutSession.started_at.desc())
        )

        return db.execute(stmt).scalars().first()

    def create(
        self,
        db: Session,
        session_db: WorkoutSession,
    ) -> WorkoutSession:
        db.add(session_db)
        return session_db

    def update(
        self,
        session_db: WorkoutSession,
    ) -> WorkoutSession:
        return session_db

    def delete(
        self,
        db: Session,
        session_db: WorkoutSession,
    ) -> None:
        db.delete(session_db)