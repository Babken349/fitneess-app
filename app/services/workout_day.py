from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users import User
from app.models.workout_day import WorkoutDay
from app.schemas.workout_day import WorkoutDayCreate, WorkoutDayUpdate

from app.repository.workout_day import WorkoutDayRepository
from app.repository.workout_program import WorkoutProgramRepository

from app.exceptions import (
    ProgramNotFoundError,
    DayNotFoundError,
    DayAlreadyExistsError,
    InvalidDayNameError,
    DayOrderAlreadyExistsError,
    DayAccessDeniedError,
    DayArchivedError,
    DayNotArchivedError,
)


class WorkoutDayService:

    def __init__(self):
        self.day_repo = WorkoutDayRepository()
        self.program_repo = WorkoutProgramRepository()


    async def _check_program_access(
        self,
        db: AsyncSession,
        program_id: int,
        current_user: User,
    ):
        program = await self.program_repo.get_by_id(
            db,
            program_id,
        )

        if not program:
            raise ProgramNotFoundError(program_id)

        if program.user_id != current_user.id:
            raise DayAccessDeniedError()

        return program


    async def create_day(
        self,
        db: AsyncSession,
        program_id: int,
        day_data: WorkoutDayCreate,
        current_user: User,
    ) -> WorkoutDay:

        # 1. Проверяем программу и владельца
        await self._check_program_access(
            db,
            program_id,
            current_user,
        )

        # 2. Проверяем название
        if not day_data.name.strip():
            raise InvalidDayNameError(day_data.name)

        # 3. Проверяем дубликат названия
        existing_day = await self.day_repo.get_by_name_and_program(
            db,
            day_data.name,
            program_id,
        )

        if existing_day:
            raise DayAlreadyExistsError(day_data.name)

        # 4. Проверяем day_order
        existing_order = await self.day_repo.get_by_order_and_program(
            db,
            day_data.day_order,
            program_id,
        )

        if existing_order:
            raise DayOrderAlreadyExistsError(
                day_data.day_order
            )

        # 5. Создаем объект
        day_db = WorkoutDay(
            workout_program_id=program_id,
            **day_data.model_dump(),
        )

        # 6. Repository
        new_day = self.day_repo.create(
            db,
            day_db,
        )

        # 7. Сохраняем
        await db.commit()
        await db.refresh(new_day)

        return new_day


    async def get_day_by_id(
        self,
        db: AsyncSession,
        day_id: int,
        current_user: User,
    ) -> WorkoutDay:

        day = await self.day_repo.get_by_id(
            db,
            day_id,
        )

        if not day:
            raise DayNotFoundError(day_id)

        # Проверяем владельца программы, к которой относится день
        await self._check_program_access(
            db,
            day.workout_program_id,
            current_user,
        )

        return day


    async def get_days_by_program(
        self,
        db: AsyncSession,
        program_id: int,
        current_user: User,
    ) -> list[WorkoutDay]:

        await self._check_program_access(
            db,
            program_id,
            current_user,
        )

        return await self.day_repo.get_active_by_program(
            db,
            program_id,
        )


    async def get_archived_days(
        self,
        db: AsyncSession,
        program_id: int,
        current_user: User,
    ) -> list[WorkoutDay]:

        await self._check_program_access(
            db,
            program_id,
            current_user,
        )

        return await self.day_repo.get_archived_by_program(
            db,
            program_id,
        )


    async def get_active_days(
        self,
        db: AsyncSession,
        program_id: int,
        current_user: User,
    ) -> list[WorkoutDay]:

        await self._check_program_access(
            db,
            program_id,
            current_user,
        )

        return await self.day_repo.get_active_by_program(
            db,
            program_id,
        )


    async def search_days(
        self,
        db: AsyncSession,
        name: str,
        current_user: User,
    ) -> list[WorkoutDay]:

        # Ищем только среди дней программ текущего пользователя
        return await self.day_repo.search_by_name(
            db,
            name,
            current_user.id,
        )


    async def update_day(
        self,
        db: AsyncSession,
        day_id: int,
        day_data: WorkoutDayUpdate,
        current_user: User,
    ) -> WorkoutDay:

        # 1-2. Получаем день и проверяем владельца программы
        day_db = await self.get_day_by_id(
            db,
            day_id,
            current_user,
        )

        # 3. Берем только переданные поля
        update_data = day_data.model_dump(
            exclude_unset=True
        )

        # 4. Проверяем название
        if "name" in update_data:

            if not update_data["name"].strip():
                raise InvalidDayNameError(
                    update_data["name"]
                )

            if update_data["name"] != day_db.name:

                existing_day = await self.day_repo.get_by_name_and_program(
                    db,
                    update_data["name"],
                    day_db.workout_program_id,
                )

                if (
                    existing_day
                    and existing_day.id != day_id
                ):
                    raise DayAlreadyExistsError(
                        update_data["name"]
                    )

        # 5. Проверяем day_order
        if (
            "day_order" in update_data
            and update_data["day_order"] != day_db.day_order
        ):

            existing_order = await self.day_repo.get_by_order_and_program(
                db,
                update_data["day_order"],
                day_db.workout_program_id,
            )

            if (
                existing_order
                and existing_order.id != day_id
            ):
                raise DayOrderAlreadyExistsError(
                    update_data["day_order"]
                )

        # 6. Обновляем через Repository
        self.day_repo.update(
            db,
            day_db,
            update_data,
        )

        # 7. Сохраняем
        await db.commit()
        await db.refresh(day_db)

        return day_db


    async def delete_day(
        self,
        db: AsyncSession,
        day_id: int,
        current_user: User,
    ) -> None:

        # 1-2. Получаем день и проверяем владельца
        day_db = await self.get_day_by_id(
            db,
            day_id,
            current_user,
        )

        # 3. Удаляем
        await self.day_repo.delete(
            db,
            day_db,
        )

        # 4. Commit
        await db.commit()


    async def archive_day(
        self,
        db: AsyncSession,
        day_id: int,
        current_user: User,
    ) -> WorkoutDay:

        # 1-2. Получаем день и проверяем владельца
        day_db = await self.get_day_by_id(
            db,
            day_id,
            current_user,
        )

        # 3. Проверяем, не архивирован ли уже
        if day_db.is_archived:
            raise DayArchivedError()

        # 4. Архивируем
        self.day_repo.archive(
            db,
            day_db,
        )

        # 5. Сохраняем
        await db.commit()
        await db.refresh(day_db)

        return day_db


    async def unarchive_day(
        self,
        db: AsyncSession,
        day_id: int,
        current_user: User,
    ) -> WorkoutDay:

        # 1-2. Получаем день и проверяем владельца
        day_db = await self.get_day_by_id(
            db,
            day_id,
            current_user,
        )

        # 3. Проверяем, действительно ли он архивирован
        if not day_db.is_archived:
            raise DayNotArchivedError()

        # 4. Восстанавливаем
        self.day_repo.unarchive(
            db,
            day_db,
        )

        # 5. Сохраняем
        await db.commit()
        await db.refresh(day_db)

        return day_db