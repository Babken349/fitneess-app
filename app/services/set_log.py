# app/services/set_log.py

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.set_log import SetLog
from app.models.users import User

from app.schemas.set_log import (
    SetLogCreate,
    SetLogUpdate,
)

from app.repository.set_log import SetLogRepository
from app.repository.exercise_log import ExerciseLogRepository
from app.repository.workout_session import WorkoutSessionRepository

from app.exceptions import (
    SetLogNotFoundError,
    SetAlreadyExistsError,
    ExerciseLogNotFoundError,
    WorkoutSessionNotFoundError,
    ForbiddenError,
)


class SetLogService:

    def __init__(self):
        self.set_repo = SetLogRepository()
        self.exercise_log_repo = ExerciseLogRepository()
        self.session_repo = WorkoutSessionRepository()

    async def _get_owned_exercise_log(
        self,
        db: AsyncSession,
        exercise_log_id: int,
        current_user: User,
    ):

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

        if not session:
            raise WorkoutSessionNotFoundError(
                exercise_log.workout_session_id
            )

        if session.user_id != current_user.id:
            raise ForbiddenError()

        return exercise_log

    async def create_set(
        self,
        db: AsyncSession,
        exercise_log_id: int,
        data: SetLogCreate,
        current_user: User,
    ) -> SetLog:

        await self._get_owned_exercise_log(
            db,
            exercise_log_id,
            current_user,
        )

        existing = await self.set_repo.get_by_number(
            db,
            exercise_log_id,
            data.set_number,
        )

        if existing:
            raise SetAlreadyExistsError(
                data.set_number
            )

        set_log = SetLog(
            exercise_log_id=exercise_log_id,
            set_number=data.set_number,
            actual_reps=data.actual_reps,
            actual_weight=data.actual_weight,
            rir=data.rir,
            completed=data.completed,
        )

        self.set_repo.create(
            db,
            set_log,
        )

        await db.commit()
        await db.refresh(set_log)

        return set_log

    async def get_by_id(
        self,
        db: AsyncSession,
        set_log_id: int,
        current_user: User,
    ) -> SetLog:

        set_log = await self.set_repo.get_by_id(
            db,
            set_log_id,
        )

        if not set_log:
            raise SetLogNotFoundError(
                set_log_id
            )

        await self._get_owned_exercise_log(
            db,
            set_log.exercise_log_id,
            current_user,
        )

        return set_log

    async def get_by_exercise_log(
        self,
        db: AsyncSession,
        exercise_log_id: int,
        current_user: User,
    ) -> list[SetLog]:

        await self._get_owned_exercise_log(
            db,
            exercise_log_id,
            current_user,
        )

        return await self.set_repo.get_by_exercise_log(
            db,
            exercise_log_id,
        )

    async def update_set(
        self,
        db: AsyncSession,
        set_log_id: int,
        data: SetLogUpdate,
        current_user: User,
    ) -> SetLog:

        set_log = await self.set_repo.get_by_id(
            db,
            set_log_id,
        )

        if not set_log:
            raise SetLogNotFoundError(
                set_log_id
            )

        await self._get_owned_exercise_log(
            db,
            set_log.exercise_log_id,
            current_user,
        )

        update_data = data.model_dump(
            exclude_unset=True
        )

        if "set_number" in update_data:

            existing = await self.set_repo.get_by_number(
                db,
                set_log.exercise_log_id,
                update_data["set_number"],
            )

            if existing and existing.id != set_log_id:
                raise SetAlreadyExistsError(
                    update_data["set_number"]
                )

        for key, value in update_data.items():
            setattr(
                set_log,
                key,
                value,
            )

        self.set_repo.update(
            set_log
        )

        await db.commit()
        await db.refresh(set_log)

        return set_log

    async def delete_set(
        self,
        db: AsyncSession,
        set_log_id: int,
        current_user: User,
    ) -> None:

        set_log = await self.set_repo.get_by_id(
            db,
            set_log_id,
        )

        if not set_log:
            raise SetLogNotFoundError(
                set_log_id
            )

        await self._get_owned_exercise_log(
            db,
            set_log.exercise_log_id,
            current_user,
        )

        await self.set_repo.delete(
            db,
            set_log,
        )

        await db.commit()