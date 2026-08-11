from datetime import datetime

from sqlalchemy.orm import Session

from app.models.users import User
from app.models.workout_session import WorkoutSession
from app.repository.workout_session import WorkoutSessionRepository

from app.exceptions import (
    WorkoutSessionNotFoundError,
    WorkoutSessionAccessDeniedError,
    WorkoutSessionAlreadyFinishedError,
    ActiveWorkoutSessionAlreadyExistsError,
)


class WorkoutSessionService:

    def __init__(self):
        self.session_repo = WorkoutSessionRepository()

    # =========================
    # CREATE
    # =========================

    def create_session(
        self,
        db: Session,
        session_data,
        current_user: User,
    ) -> WorkoutSession:

        active_session = self.session_repo.get_active_by_user(
            db,
            current_user.id,
        )

        if active_session:
            raise ActiveWorkoutSessionAlreadyExistsError()

        session_db = WorkoutSession(
            user_id=current_user.id,
            workout_day_id=session_data.workout_day_id,
            notes=session_data.notes,
        )

        self.session_repo.create(
            db,
            session_db,
        )

        db.commit()
        db.refresh(session_db)

        return session_db

    # =========================
    # GET BY ID
    # =========================

    def get_by_id(
        self,
        db: Session,
        session_id: int,
        current_user: User,
    ) -> WorkoutSession:

        session_db = self.session_repo.get_by_id(
            db,
            session_id,
        )

        if not session_db:
            raise WorkoutSessionNotFoundError(
                session_id
            )

        if session_db.user_id != current_user.id:
            raise WorkoutSessionAccessDeniedError()

        return session_db

    # =========================
    # GET MY SESSIONS
    # =========================

    def get_my_sessions(
        self,
        db: Session,
        current_user: User,
        skip: int = 0,
        limit: int = 20,
    ) -> list[WorkoutSession]:

        return self.session_repo.get_by_user(
            db,
            current_user.id,
            skip,
            limit,
        )

    # =========================
    # GET BY DAY
    # =========================

    def get_by_day(
        self,
        db: Session,
        workout_day_id: int,
        current_user: User,
    ) -> list[WorkoutSession]:

        return self.session_repo.get_by_day(
            db,
            current_user.id,
            workout_day_id,
        )

    # =========================
    # GET ACTIVE
    # =========================

    def get_active_session(
        self,
        db: Session,
        current_user: User,
    ) -> WorkoutSession | None:

        return self.session_repo.get_active_by_user(
            db,
            current_user.id,
        )

    # =========================
    # UPDATE
    # =========================

    def update_session(
        self,
        db: Session,
        session_id: int,
        session_data,
        current_user: User,
    ) -> WorkoutSession:

        session_db = self.get_by_id(
            db,
            session_id,
            current_user,
        )

        if session_db.finished_at is not None:
            raise WorkoutSessionAlreadyFinishedError()

        update_data = session_data.model_dump(
            exclude_unset=True
        )

        for key, value in update_data.items():
            setattr(session_db, key, value)

        self.session_repo.update(
            session_db
        )

        db.commit()
        db.refresh(session_db)

        return session_db

    # =========================
    # FINISH
    # =========================

    def finish_session(
        self,
        db: Session,
        session_id: int,
        current_user: User,
    ) -> WorkoutSession:

        session_db = self.get_by_id(
            db,
            session_id,
            current_user,
        )

        if session_db.finished_at is not None:
            raise WorkoutSessionAlreadyFinishedError()

        session_db.finished_at = datetime.now()

        self.session_repo.update(
            session_db
        )

        db.commit()
        db.refresh(session_db)

        return session_db

    # =========================
    # DELETE
    # =========================

    def delete_session(
        self,
        db: Session,
        session_id: int,
        current_user: User,
    ) -> None:

        session_db = self.get_by_id(
            db,
            session_id,
            current_user,
        )

        self.session_repo.delete(
            db,
            session_db,
        )

        db.commit()