from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.workout_exercise import WorkoutExercise


class WorkoutExerciseRepository:

    def get_by_id(
        self,
        db: Session,
        workout_exercise_id: int,
    ) -> WorkoutExercise | None:
        stmt = select(WorkoutExercise).where(
            WorkoutExercise.id == workout_exercise_id
        )
        return db.execute(stmt).scalar_one_or_none()

    def get_by_day(
        self,
        db: Session,
        workout_day_id: int,
    ) -> list[WorkoutExercise]:
        stmt = (
            select(WorkoutExercise)
            .where(
                WorkoutExercise.workout_day_id == workout_day_id
            )
            .order_by(WorkoutExercise.exercise_order)
        )

        return db.execute(stmt).scalars().all()

    def get_by_order_and_day(
        self,
        db: Session,
        exercise_order: int,
        workout_day_id: int,
    ) -> WorkoutExercise | None:
        stmt = select(WorkoutExercise).where(
            WorkoutExercise.exercise_order == exercise_order,
            WorkoutExercise.workout_day_id == workout_day_id,
        )

        return db.execute(stmt).scalar_one_or_none()

    def get_by_exercise_and_day(
        self,
        db: Session,
        exercise_id: int,
        workout_day_id: int,
    ) -> WorkoutExercise | None:
        stmt = select(WorkoutExercise).where(
            WorkoutExercise.exercise_id == exercise_id,
            WorkoutExercise.workout_day_id == workout_day_id,
        )

        return db.execute(stmt).scalar_one_or_none()

    def create(
        self,
        db: Session,
        workout_exercise: WorkoutExercise,
    ) -> WorkoutExercise:
        db.add(workout_exercise)
        return workout_exercise

    def update(
        self,
        workout_exercise: WorkoutExercise,
    ) -> WorkoutExercise:
        return workout_exercise

    def delete(
        self,
        db: Session,
        workout_exercise: WorkoutExercise,
    ) -> None:
        db.delete(workout_exercise)