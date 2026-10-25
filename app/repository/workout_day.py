from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.workout_day import WorkoutDay
from app.models.workout_program import WorkoutProgram


class WorkoutDayRepository:

    async def get_by_id(self, db: AsyncSession, day_id: int) -> WorkoutDay | None:
        stmt = select(WorkoutDay).where(WorkoutDay.id == day_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active_by_program(self, db: AsyncSession, program_id: int) -> list[WorkoutDay]:
        stmt = (
            select(WorkoutDay)
            .where(
                WorkoutDay.workout_program_id == program_id,
                WorkoutDay.is_archived.is_(False),
            )
            .order_by(WorkoutDay.day_order)
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_archived_by_program(self, db: AsyncSession, program_id: int) -> list[WorkoutDay]:
        stmt = (
            select(WorkoutDay)
            .where(
                WorkoutDay.workout_program_id == program_id,
                WorkoutDay.is_archived.is_(True),
            )
            .order_by(WorkoutDay.day_order)
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_by_order_and_program(
        self, db: AsyncSession, day_order: int, program_id: int
    ) -> WorkoutDay | None:
        stmt = select(WorkoutDay).where(
            WorkoutDay.day_order == day_order,
            WorkoutDay.workout_program_id == program_id,
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_name_and_program(
        self, db: AsyncSession, name: str, program_id: int
    ) -> WorkoutDay | None:
        stmt = select(WorkoutDay).where(
            WorkoutDay.name == name,
            WorkoutDay.workout_program_id == program_id,
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def search_by_name(
        self, db: AsyncSession, name: str, user_id: int
    ) -> list[WorkoutDay]:
        stmt = (
            select(WorkoutDay)
            .join(
                WorkoutProgram,
                WorkoutDay.workout_program_id == WorkoutProgram.id,
            )
            .where(
                WorkoutProgram.user_id == user_id,
                WorkoutDay.name.ilike(f"%{name}%"),
                WorkoutDay.is_archived.is_(False),
            )
            .order_by(WorkoutDay.day_order)
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    def create(self, db: AsyncSession, day_db: WorkoutDay) -> WorkoutDay:
        db.add(day_db)
        return day_db

    def update(
        self,
        db: AsyncSession,
        day_db: WorkoutDay,
        update_data: dict,
    ) -> WorkoutDay:
        for key, value in update_data.items():
            setattr(day_db, key, value)

        return day_db

    async def delete(self, db: AsyncSession, day_db: WorkoutDay) -> None:
        await db.delete(day_db)

    def archive(self, db: AsyncSession, day_db: WorkoutDay) -> WorkoutDay:
        day_db.is_archived = True
        return day_db

    def unarchive(self, db: AsyncSession, day_db: WorkoutDay) -> WorkoutDay:
        day_db.is_archived = False
        return day_db