from sqlalchemy.orm import Session

from app.models.users import User
from app.models.workout_exercise import WorkoutExercise

from app.repository.workout_exercise import WorkoutExerciseRepository
from app.repository.workout_day import WorkoutDayRepository
from app.repository.exercise import ExerciseRepository

from app.schemas.workout_exercise import (
    WorkoutExerciseCreate,
    WorkoutExerciseUpdate,
)

from app.exceptions import (
    WorkoutExerciseNotFoundError,
    WorkoutDayNotFoundError,
    ExerciseNotFoundError,
    WorkoutExerciseAlreadyExistsError,
    WorkoutExerciseOrderAlreadyExistsError,
    WorkoutDayAccessDeniedError,
)


class WorkoutExerciseService:

    def __init__(self):
        self.workout_exercise_repo = WorkoutExerciseRepository()
        self.workout_day_repo = WorkoutDayRepository()
        self.exercise_repo = ExerciseRepository()

    # =========================================================
    # CREATE
    # =========================================================

    def create_workout_exercise(
        self,
        db: Session,
        workout_day_id: int,
        data: WorkoutExerciseCreate,
        current_user: User,
    ) -> WorkoutExercise:

        # 1. Проверяем, существует ли тренировочный день
        day = self.workout_day_repo.get_by_id(
            db,
            workout_day_id,
        )

        if not day:
            raise WorkoutDayNotFoundError(workout_day_id)

        # 2. Проверяем, принадлежит ли день пользователю
        # Здесь предполагается, что WorkoutDay -> WorkoutProgram
        # и у программы есть user_id.
        if day.program.user_id != current_user.id:
            raise WorkoutDayAccessDeniedError()

        # 3. Проверяем существование упражнения
        exercise = self.exercise_repo.get_by_id(
            db,
            data.exercise_id,
        )

        if not exercise:
            raise ExerciseNotFoundError(data.exercise_id)

        # 4. Проверяем, нет ли уже этого упражнения
        # в данном дне
        existing = self.workout_exercise_repo.get_by_exercise_and_day(
            db,
            data.exercise_id,
            workout_day_id,
        )

        if existing:
            raise WorkoutExerciseAlreadyExistsError(
                data.exercise_id,
                workout_day_id,
            )

        # 5. Проверяем свободен ли порядок
        existing_order = (
            self.workout_exercise_repo.get_by_order_and_day(
                db,
                data.exercise_order,
                workout_day_id,
            )
        )

        if existing_order:
            raise WorkoutExerciseOrderAlreadyExistsError(
                data.exercise_order,
                workout_day_id,
            )

        # 6. Создаем связующую запись
        workout_exercise = WorkoutExercise(
            workout_day_id=workout_day_id,
            exercise_id=data.exercise_id,
            exercise_order=data.exercise_order,
            note=data.note,
        )

        # 7. Repository
        self.workout_exercise_repo.create(
            db,
            workout_exercise,
        )

        # 8. Commit
        db.commit()

        # 9. Refresh
        db.refresh(workout_exercise)

        return workout_exercise

    # =========================================================
    # GET BY ID
    # =========================================================

    def get_by_id(
        self,
        db: Session,
        workout_exercise_id: int,
        current_user: User,
    ) -> WorkoutExercise:

        workout_exercise = (
            self.workout_exercise_repo.get_by_id(
                db,
                workout_exercise_id,
            )
        )

        if not workout_exercise:
            raise WorkoutExerciseNotFoundError(
                workout_exercise_id
            )

        if (
            workout_exercise.workout_day.program.user_id
            != current_user.id
        ):
            raise WorkoutDayAccessDeniedError()

        return workout_exercise

    # =========================================================
    # GET BY DAY
    # =========================================================

    def get_by_day(
        self,
        db: Session,
        workout_day_id: int,
        current_user: User,
    ) -> list[WorkoutExercise]:

        day = self.workout_day_repo.get_by_id(
            db,
            workout_day_id,
        )

        if not day:
            raise WorkoutDayNotFoundError(
                workout_day_id
            )

        if day.program.user_id != current_user.id:
            raise WorkoutDayAccessDeniedError()

        return self.workout_exercise_repo.get_by_day(
            db,
            workout_day_id,
        )

    # =========================================================
    # UPDATE
    # =========================================================

    def update_workout_exercise(
        self,
        db: Session,
        workout_exercise_id: int,
        data: WorkoutExerciseUpdate,
        current_user: User,
    ) -> WorkoutExercise:

        workout_exercise = (
            self.workout_exercise_repo.get_by_id(
                db,
                workout_exercise_id,
            )
        )

        if not workout_exercise:
            raise WorkoutExerciseNotFoundError(
                workout_exercise_id
            )

        if (
            workout_exercise.workout_day.program.user_id
            != current_user.id
        ):
            raise WorkoutDayAccessDeniedError()

        update_data = data.model_dump(
            exclude_unset=True
        )

        # Если меняем exercise_id
        if "exercise_id" in update_data:

            exercise = self.exercise_repo.get_by_id(
                db,
                update_data["exercise_id"],
            )

            if not exercise:
                raise ExerciseNotFoundError(
                    update_data["exercise_id"]
                )

            existing = (
                self.workout_exercise_repo
                .get_by_exercise_and_day(
                    db,
                    update_data["exercise_id"],
                    workout_exercise.workout_day_id,
                )
            )

            if (
                existing
                and existing.id != workout_exercise_id
            ):
                raise WorkoutExerciseAlreadyExistsError(
                    update_data["exercise_id"],
                    workout_exercise.workout_day_id,
                )

        # Если меняем порядок
        if "exercise_order" in update_data:

            existing_order = (
                self.workout_exercise_repo
                .get_by_order_and_day(
                    db,
                    update_data["exercise_order"],
                    workout_exercise.workout_day_id,
                )
            )

            if (
                existing_order
                and existing_order.id != workout_exercise_id
            ):
                raise WorkoutExerciseOrderAlreadyExistsError(
                    update_data["exercise_order"],
                    workout_exercise.workout_day_id,
                )

        # Обновляем поля
        for key, value in update_data.items():
            setattr(
                workout_exercise,
                key,
                value,
            )

        self.workout_exercise_repo.update(
            workout_exercise
        )

        db.commit()
        db.refresh(workout_exercise)

        return workout_exercise

    # =========================================================
    # DELETE
    # =========================================================

    def delete_workout_exercise(
        self,
        db: Session,
        workout_exercise_id: int,
        current_user: User,
    ) -> None:

        workout_exercise = (
            self.workout_exercise_repo.get_by_id(
                db,
                workout_exercise_id,
            )
        )

        if not workout_exercise:
            raise WorkoutExerciseNotFoundError(
                workout_exercise_id
            )

        if (
            workout_exercise.workout_day.program.user_id
            != current_user.id
        ):
            raise WorkoutDayAccessDeniedError()

        self.workout_exercise_repo.delete(
            db,
            workout_exercise,
        )

        db.commit()