from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users import User
from app.models.workout_exercise import WorkoutExercise

from app.repository.workout_exercise import WorkoutExerciseRepository
from app.repository.workout_day import WorkoutDayRepository
from app.repository.workout_program import WorkoutProgramRepository
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
        self.program_repo = WorkoutProgramRepository()
        self.exercise_repo = ExerciseRepository()

    # =========================================================
    # INTERNAL
    # =========================================================

    async def _check_day_access(
        self,
        db: AsyncSession,
        workout_day_id: int,
        current_user: User,
    ):
        # Связи day.program в async лениво не грузятся (MissingGreenlet),
        # поэтому владельца проверяем явными запросами.
        day = await self.workout_day_repo.get_by_id(
            db,
            workout_day_id,
        )

        if not day:
            raise WorkoutDayNotFoundError(workout_day_id)

        program = await self.program_repo.get_by_id(
            db,
            day.workout_program_id,
        )

        if not program or program.user_id != current_user.id:
            raise WorkoutDayAccessDeniedError()

        return day

    # =========================================================
    # CREATE
    # =========================================================

    async def create_workout_exercise(
        self,
        db: AsyncSession,
        workout_day_id: int,
        data: WorkoutExerciseCreate,
        current_user: User,
    ) -> WorkoutExercise:

        # 1-2. Проверяем день и владельца
        await self._check_day_access(
            db,
            workout_day_id,
            current_user,
        )

        # 3. Проверяем существование упражнения
        exercise = await self.exercise_repo.get_by_id(
            db,
            data.exercise_id,
        )

        if not exercise:
            raise ExerciseNotFoundError(data.exercise_id)

        # 4. Проверяем, нет ли уже этого упражнения
        # в данном дне
        existing = await self.workout_exercise_repo.get_by_exercise_and_day(
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
            await self.workout_exercise_repo.get_by_order_and_day(
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
        await db.commit()

        # 9. Refresh
        await db.refresh(workout_exercise)

        return workout_exercise

    # =========================================================
    # GET BY ID
    # =========================================================

    async def get_by_id(
        self,
        db: AsyncSession,
        workout_exercise_id: int,
        current_user: User,
    ) -> WorkoutExercise:

        workout_exercise = (
            await self.workout_exercise_repo.get_by_id(
                db,
                workout_exercise_id,
            )
        )

        if not workout_exercise:
            raise WorkoutExerciseNotFoundError(
                workout_exercise_id
            )

        await self._check_day_access(
            db,
            workout_exercise.workout_day_id,
            current_user,
        )

        return workout_exercise

    # =========================================================
    # GET BY DAY
    # =========================================================

    async def get_by_day(
        self,
        db: AsyncSession,
        workout_day_id: int,
        current_user: User,
    ) -> list[WorkoutExercise]:

        await self._check_day_access(
            db,
            workout_day_id,
            current_user,
        )

        return await self.workout_exercise_repo.get_by_day(
            db,
            workout_day_id,
        )

    # =========================================================
    # UPDATE
    # =========================================================

    async def update_workout_exercise(
        self,
        db: AsyncSession,
        workout_exercise_id: int,
        data: WorkoutExerciseUpdate,
        current_user: User,
    ) -> WorkoutExercise:

        workout_exercise = (
            await self.workout_exercise_repo.get_by_id(
                db,
                workout_exercise_id,
            )
        )

        if not workout_exercise:
            raise WorkoutExerciseNotFoundError(
                workout_exercise_id
            )

        await self._check_day_access(
            db,
            workout_exercise.workout_day_id,
            current_user,
        )

        update_data = data.model_dump(
            exclude_unset=True
        )

        # Если меняем exercise_id
        if "exercise_id" in update_data:

            exercise = await self.exercise_repo.get_by_id(
                db,
                update_data["exercise_id"],
            )

            if not exercise:
                raise ExerciseNotFoundError(
                    update_data["exercise_id"]
                )

            existing = (
                await self.workout_exercise_repo
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
                await self.workout_exercise_repo
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

        await db.commit()
        await db.refresh(workout_exercise)

        return workout_exercise

    # =========================================================
    # DELETE
    # =========================================================

    async def delete_workout_exercise(
        self,
        db: AsyncSession,
        workout_exercise_id: int,
        current_user: User,
    ) -> None:

        workout_exercise = (
            await self.workout_exercise_repo.get_by_id(
                db,
                workout_exercise_id,
            )
        )

        if not workout_exercise:
            raise WorkoutExerciseNotFoundError(
                workout_exercise_id
            )

        await self._check_day_access(
            db,
            workout_exercise.workout_day_id,
            current_user,
        )

        await self.workout_exercise_repo.delete(
            db,
            workout_exercise,
        )

        await db.commit()