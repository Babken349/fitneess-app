from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

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

    async def create_session(
        self,
        db: AsyncSession,
        session_data,
        current_user: User,
    ) -> WorkoutSession:

        active_session = await self.session_repo.get_active_by_user(
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

        await db.commit()
        await db.refresh(session_db)

        return session_db

    # =========================
    # GET BY ID
    # =========================

    async def get_by_id(
        self,
        db: AsyncSession,
        session_id: int,
        current_user: User,
    ) -> WorkoutSession:

        session_db = await self.session_repo.get_by_id(
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

    async def get_my_sessions(
        self,
        db: AsyncSession,
        current_user: User,
        skip: int = 0,
        limit: int = 20,
    ) -> list[WorkoutSession]:

        return await self.session_repo.get_by_user(
            db,
            current_user.id,
            skip,
            limit,
        )

    # =========================
    # GET BY DAY
    # =========================

    async def get_by_day(
        self,
        db: AsyncSession,
        workout_day_id: int,
        current_user: User,
    ) -> list[WorkoutSession]:

        return await self.session_repo.get_by_day(
            db,
            current_user.id,
            workout_day_id,
        )

    # =========================
    # GET ACTIVE
    # =========================

    async def get_active_session(
        self,
        db: AsyncSession,
        current_user: User,
    ) -> WorkoutSession | None:

        return await self.session_repo.get_active_by_user(
            db,
            current_user.id,
        )

    # =========================
    # UPDATE
    # =========================

    async def update_session(
        self,
        db: AsyncSession,
        session_id: int,
        session_data,
        current_user: User,
    ) -> WorkoutSession:

        session_db = await self.get_by_id(
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

        await db.commit()
        await db.refresh(session_db)

        return session_db

    # =========================
    # FINISH
    # =========================

    async def finish_session(
        self,
        db: AsyncSession,
        session_id: int,
        current_user: User,
    ) -> WorkoutSession:

        session_db = await self.get_by_id(
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

        await db.commit()
        await db.refresh(session_db)

        return session_db

    # =========================
    # DELETE
    # =========================

    async def delete_session(
        self,
        db: AsyncSession,
        session_id: int,
        current_user: User,
    ) -> None:

        session_db = await self.get_by_id(
            db,
            session_id,
            current_user,
        )

        await self.session_repo.delete(
            db,
            session_db,
        )

        await db.commit()