from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.workout_program import WorkoutProgram


class WorkoutProgramRepository:
    def __init__(self):
        pass

    async def get_by_id(self, db: AsyncSession, program_id: int) -> WorkoutProgram | None:
        stmt = select(WorkoutProgram).where(WorkoutProgram.id == program_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_public(self, db: AsyncSession, skip: int, limit: int) -> list[WorkoutProgram]:
        stmt = (
            select(WorkoutProgram)
            .where(
                WorkoutProgram.is_public.is_(True),
                WorkoutProgram.is_archived.is_(False),
            )
            .order_by(WorkoutProgram.id)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    async def search_by_name(
        self, db: AsyncSession, name: str, user_id: int
    ) -> list[WorkoutProgram]:
        stmt = (
            select(WorkoutProgram)
            .where(
                WorkoutProgram.name.ilike(f"%{name}%"),
                WorkoutProgram.is_archived.is_(False),
                or_(
                    WorkoutProgram.is_public.is_(True),
                    WorkoutProgram.user_id == user_id,
                ),
            )
            .order_by(WorkoutProgram.id)
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    def create(self, db: AsyncSession, program_db: WorkoutProgram) -> WorkoutProgram:
        db.add(program_db)
        return program_db

    def update(self, db: AsyncSession, program_db: WorkoutProgram) -> WorkoutProgram:
        return program_db

    async def delete(self, db: AsyncSession, program_db: WorkoutProgram) -> None:
        await db.delete(program_db)

    async def get_active_by_user(
        self, db: AsyncSession, user_id: int
    ) -> list[WorkoutProgram]:
        stmt = (
            select(WorkoutProgram)
            .where(
                WorkoutProgram.user_id == user_id,
                WorkoutProgram.is_archived.is_(False),
            )
            .order_by(WorkoutProgram.id)
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_archived_by_user(
        self, db: AsyncSession, user_id: int
    ) -> list[WorkoutProgram]:
        stmt = (
            select(WorkoutProgram)
            .where(
                WorkoutProgram.user_id == user_id,
                WorkoutProgram.is_archived.is_(True),
            )
            .order_by(WorkoutProgram.id)
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_by_user(
        self,
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
    ) -> list[WorkoutProgram]:
        stmt = (
            select(WorkoutProgram)
            .where(WorkoutProgram.user_id == user_id)
            .order_by(WorkoutProgram.id)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return result.scalars().all()


    async def count_by_user(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> int:
        stmt = select(func.count()).select_from(WorkoutProgram).where(
            WorkoutProgram.user_id == user_id
        )
        result = await db.execute(stmt)
        return result.scalar_one()

    async def count_public(
        self,
        db: AsyncSession,
    ) -> int:
        stmt = select(func.count()).select_from(WorkoutProgram).where(
            WorkoutProgram.is_public.is_(True),
            WorkoutProgram.is_archived.is_(False),
        )
        result = await db.execute(stmt)
        return result.scalar_one()

        
    async def get_by_name_and_user(
        self, db: AsyncSession, name: str, user_id: int
    ) -> WorkoutProgram | None:
        stmt = select(WorkoutProgram).where(
            WorkoutProgram.name == name,
            WorkoutProgram.user_id == user_id,
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()