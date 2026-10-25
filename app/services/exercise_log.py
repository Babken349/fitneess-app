# app/services/exercise_log.py

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.exercise_log import ExerciseLog
from app.models.users import User

from app.schemas.exercise_log import (
    ExerciseLogCreate,
    ExerciseLogUpdate,
)

from app.repository.exercise_log import ExerciseLogRepository
from app.repository.workout_session import WorkoutSessionRepository
from app.repository.exercise import ExerciseRepository

from app.exceptions import (
    ExerciseNotFoundError,
    WorkoutSessionNotFoundError,
    ExerciseLogNotFoundError,
    ExerciseLogAlreadyExistsError,
    ExerciseOrderAlreadyExistsError,
    ForbiddenError,
)


class ExerciseLogService:

    def __init__(self):
        self.exercise_log_repo = ExerciseLogRepository()
        self.session_repo = WorkoutSessionRepository()
        self.exercise_repo = ExerciseRepository()

    async def create_exercise_log(
        self,
        db: AsyncSession,
        workout_session_id: int,
        data: ExerciseLogCreate,
        current_user: User,
    ) -> ExerciseLog:

        session = await self.session_repo.get_by_id(
            db,
            workout_session_id,
        )

        if not session:
            raise WorkoutSessionNotFoundError(
                workout_session_id
            )

        if session.user_id != current_user.id:
            raise ForbiddenError()

        exercise = await self.exercise_repo.get_by_id(
            db,
            data.exercise_id,
        )

        if not exercise:
            raise ExerciseNotFoundError(
                data.exercise_id
            )

        existing_exercise = (
            await self.exercise_log_repo.get_by_session_and_exercise(
                db,
                workout_session_id,
                data.exercise_id,
            )
        )

        if existing_exercise:
            raise ExerciseLogAlreadyExistsError(
                data.exercise_id
            )

        existing_order = (
            await self.exercise_log_repo.get_by_order_and_session(
                db,
                workout_session_id,
                data.exercise_order,
            )
        )

        if existing_order:
            raise ExerciseOrderAlreadyExistsError(
                data.exercise_order
            )

        exercise_log = ExerciseLog(
            workout_session_id=workout_session_id,
            exercise_id=data.exercise_id,
            exercise_order=data.exercise_order,
            notes=data.notes,
        )

        self.exercise_log_repo.create(
            db,
            exercise_log,
        )

        await db.commit()
        await db.refresh(exercise_log)

        return exercise_log

    async def get_by_id(
        self,
        db: AsyncSession,
        exercise_log_id: int,
        current_user: User,
    ) -> ExerciseLog:

        exercise_log = await self.exercise_log_repo.get_by_id(
            db,
            exercise_log_id,
        )

        if not exercise_log:
            raise ExerciseLogNotFoundError(
                exercise_log_id
            )

        session = await self.session_repo.get_by_id(
            db,
            exercise_log.workout_session_id,
        )

        if not session or session.user_id != current_user.id:
            raise ForbiddenError()

        return exercise_log

    async def get_by_session(
        self,
        db: AsyncSession,
        workout_session_id: int,
        current_user: User,
    ) -> list[ExerciseLog]:

        session = await self.session_repo.get_by_id(
            db,
            workout_session_id,
        )

        if not session:
            raise WorkoutSessionNotFoundError(
                workout_session_id
            )

        if session.user_id != current_user.id:
            raise ForbiddenError()

        return await self.exercise_log_repo.get_by_session(
            db,
            workout_session_id,
        )

    async def update_exercise_log(
        self,
        db: AsyncSession,
        exercise_log_id: int,
        data: ExerciseLogUpdate,
        current_user: User,
    ) -> ExerciseLog:

        exercise_log = await self.exercise_log_repo.get_by_id(
            db,
            exercise_log_id,
        )

        if not exercise_log:
            raise ExerciseLogNotFoundError(
                exercise_log_id
            )

        session = await self.session_repo.get_by_id(
            db,
            exercise_log.workout_session_id,
        )

        if not session or session.user_id != current_user.id:
            raise ForbiddenError()

        update_data = data.model_dump(
            exclude_unset=True
        )

        if "exercise_order" in update_data:
            existing = (
                await self.exercise_log_repo.get_by_order_and_session(
                    db,
                    exercise_log.workout_session_id,
                    update_data["exercise_order"],
                )
            )

            if existing and existing.id != exercise_log_id:
                raise ExerciseOrderAlreadyExistsError(
                    update_data["exercise_order"]
                )

        for key, value in update_data.items():
            setattr(
                exercise_log,
                key,
                value,
            )

        self.exercise_log_repo.update(
            exercise_log
        )

        await db.commit()
        await db.refresh(exercise_log)

        return exercise_log

    async def delete_exercise_log(
        self,
        db: AsyncSession,
        exercise_log_id: int,
        current_user: User,
    ) -> None:

        exercise_log = await self.exercise_log_repo.get_by_id(
            db,
            exercise_log_id,
        )

        if not exercise_log:
            raise ExerciseLogNotFoundError(
                exercise_log_id
            )

        session = await self.session_repo.get_by_id(
            db,
            exercise_log.workout_session_id,
        )

        if not session or session.user_id != current_user.id:
            raise ForbiddenError()

        await self.exercise_log_repo.delete(
            db,
            exercise_log,
        )

        await db.commit()