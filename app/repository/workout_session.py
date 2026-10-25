from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.workout_session import WorkoutSession


class WorkoutSessionRepository:

    async def get_by_id(
        self,
        db: AsyncSession,
        session_id: int,
    ) -> WorkoutSession | None:
        stmt = select(WorkoutSession).where(
            WorkoutSession.id == session_id
        )

        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_user(
        self,
        db: AsyncSession,
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

        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_by_day(
        self,
        db: AsyncSession,
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

        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_active_by_user(
        self,
        db: AsyncSession,
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

        result = await db.execute(stmt)
        return result.scalars().first()

    def create(
        self,
        db: AsyncSession,
        session_db: WorkoutSession,
    ) -> WorkoutSession:
        db.add(session_db)
        return session_db

    def update(
        self,
        session_db: WorkoutSession,
    ) -> WorkoutSession:
        return session_db




    async def delete(
        self,
        db: AsyncSession,
        session_db: WorkoutSession,
    ) -> None:
        await db.delete(session_db)