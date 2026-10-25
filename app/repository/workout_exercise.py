from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.workout_exercise import WorkoutExercise


class WorkoutExerciseRepository:

    async def get_by_id(
        self,
        db: AsyncSession,
        workout_exercise_id: int,
    ) -> WorkoutExercise | None:
        stmt = select(WorkoutExercise).where(
            WorkoutExercise.id == workout_exercise_id
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_day(
        self,
        db: AsyncSession,
        workout_day_id: int,
    ) -> list[WorkoutExercise]:
        stmt = (
            select(WorkoutExercise)
            .where(
                WorkoutExercise.workout_day_id == workout_day_id
            )
            .order_by(WorkoutExercise.exercise_order)
        )

        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_by_order_and_day(
        self,
        db: AsyncSession,
        exercise_order: int,
        workout_day_id: int,
    ) -> WorkoutExercise | None:
        stmt = select(WorkoutExercise).where(
            WorkoutExercise.exercise_order == exercise_order,
            WorkoutExercise.workout_day_id == workout_day_id,
        )

        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_exercise_and_day(
        self,
        db: AsyncSession,
        exercise_id: int,
        workout_day_id: int,
    ) -> WorkoutExercise | None:
        stmt = select(WorkoutExercise).where(
            WorkoutExercise.exercise_id == exercise_id,
            WorkoutExercise.workout_day_id == workout_day_id,
        )

        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    def create(
        self,
        db: AsyncSession,
        workout_exercise: WorkoutExercise,
    ) -> WorkoutExercise:
        db.add(workout_exercise)
        return workout_exercise

    def update(
        self,
        workout_exercise: WorkoutExercise,
    ) -> WorkoutExercise:
        return workout_exercise

    async def delete(
        self,
        db: AsyncSession,
        workout_exercise: WorkoutExercise,
    ) -> None:
        await db.delete(workout_exercise)