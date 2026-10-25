from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.exercise import Exercise


class ExerciseRepository:

    async def get_by_id(
        self,
        db: AsyncSession,
        exercise_id: int,
    ) -> Exercise | None:
        stmt = select(Exercise).where(
            Exercise.id == exercise_id
        )

        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_name(
        self,
        db: AsyncSession,
        name: str,
    ) -> Exercise | None:
        stmt = select(Exercise).where(
            Exercise.name == name
        )

        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Exercise]:
        stmt = (
            select(Exercise)
            .where(Exercise.is_archived.is_(False))
            .offset(skip)
            .limit(limit)
        )

        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_archived(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Exercise]:
        stmt = (
            select(Exercise)
            .where(Exercise.is_archived.is_(True))
            .offset(skip)
            .limit(limit)
        )

        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_active(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Exercise]:
        stmt = (
            select(Exercise)
            .where(Exercise.is_archived.is_(False))
            .offset(skip)
            .limit(limit)
        )

        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_by_muscle_group(
        self,
        db: AsyncSession,
        muscle_group_id: int,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Exercise]:
        stmt = (
            select(Exercise)
            .where(
                Exercise.muscle_group_id == muscle_group_id,
                Exercise.is_archived.is_(False),
            )
            .offset(skip)
            .limit(limit)
        )

        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_by_equipment(
        self,
        db: AsyncSession,
        equipment_id: int,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Exercise]:
        stmt = (
            select(Exercise)
            .where(
                Exercise.equipment_id == equipment_id,
                Exercise.is_archived.is_(False),
            )
            .offset(skip)
            .limit(limit)
        )

        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_by_muscle_group_and_equipment(
        self,
        db: AsyncSession,
        muscle_group_id: int,
        equipment_id: int,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Exercise]:
        stmt = (
            select(Exercise)
            .where(
                Exercise.muscle_group_id == muscle_group_id,
                Exercise.equipment_id == equipment_id,
                Exercise.is_archived.is_(False),
            )
            .offset(skip)
            .limit(limit)
        )

        result = await db.execute(stmt)
        return result.scalars().all()

    async def search_by_name(
        self,
        db: AsyncSession,
        name: str,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Exercise]:
        stmt = (
            select(Exercise)
            .where(
                Exercise.name.ilike(f"%{name}%"),
                Exercise.is_archived.is_(False),
            )
            .offset(skip)
            .limit(limit)
        )

        result = await db.execute(stmt)
        return result.scalars().all()

    async def exists_by_name(
        self,
        db: AsyncSession,
        name: str,
    ) -> bool:
        stmt = select(Exercise).where(
            Exercise.name == name
        )

        result = await db.execute(stmt)
        return result.scalar_one_or_none() is not None

    def create(
        self,
        db: AsyncSession,
        exercise_db: Exercise,
    ) -> Exercise:
        db.add(exercise_db)
        return exercise_db

    def update(
        self,
        exercise_db: Exercise,
    ) -> Exercise:
        return exercise_db

    async def delete(
        self,
        db: AsyncSession,
        exercise_db: Exercise,
    ) -> None:
        await db.delete(exercise_db)

    def archive(
        self,
        exercise_db: Exercise,
    ) -> Exercise:
        exercise_db.is_archived = True
        return exercise_db

    def unarchive(
        self,
        exercise_db: Exercise,
    ) -> Exercise:
        exercise_db.is_archived = False
        return exercise_db