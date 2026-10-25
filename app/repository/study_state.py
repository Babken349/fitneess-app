from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.study_state import StudyState


class StudyStateRepository:

    async def create(
        self,
        db: AsyncSession,
        study_state: StudyState,
    ) -> StudyState:
        db.add(study_state)
        await db.flush()
        return study_state

    async def get_by_id(
        self,
        db: AsyncSession,
        study_state_id: int,
    ) -> StudyState | None:
        stmt = select(StudyState).where(
            StudyState.id == study_state_id
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_user(
        self,
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
    ) -> list[StudyState]:
        stmt = (
            select(StudyState)
            .where(StudyState.user_id == user_id)
            .order_by(StudyState.recorded_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def delete(
        self,
        db: AsyncSession,
        study_state: StudyState,
    ) -> None:
        await db.delete(study_state)