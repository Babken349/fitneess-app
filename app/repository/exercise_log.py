from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.exercise_log import ExerciseLog


class ExerciseLogRepository:

    async def get_by_id(
        self,
        db: AsyncSession,
        exercise_log_id: int,
    ) -> ExerciseLog | None:

        stmt = select(ExerciseLog).where(
            ExerciseLog.id == exercise_log_id
        )

        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_session(
        self,
        db: AsyncSession,
        workout_session_id: int,
    ) -> list[ExerciseLog]:

        stmt = (
            select(ExerciseLog)
            .where(
                ExerciseLog.workout_session_id == workout_session_id
            )
            .order_by(ExerciseLog.exercise_order)
        )

        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_by_session_and_exercise(
        self,
        db: AsyncSession,
        workout_session_id: int,
        exercise_id: int,
    ) -> ExerciseLog | None:

        stmt = select(ExerciseLog).where(
            ExerciseLog.workout_session_id == workout_session_id,
            ExerciseLog.exercise_id == exercise_id,
        )

        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_order_and_session(
        self,
        db: AsyncSession,
        workout_session_id: int,
        exercise_order: int,
    ) -> ExerciseLog | None:

        stmt = select(ExerciseLog).where(
            ExerciseLog.workout_session_id == workout_session_id,
            ExerciseLog.exercise_order == exercise_order,
        )

        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    def create(
        self,
        db: AsyncSession,
        exercise_log: ExerciseLog,
    ) -> ExerciseLog:

        db.add(exercise_log)
        return exercise_log

    def update(
        self,
        exercise_log: ExerciseLog,
    ) -> ExerciseLog:

        return exercise_log

    async def delete(
        self,
        db: AsyncSession,
        exercise_log: ExerciseLog,
    ) -> None:

        await db.delete(exercise_log)