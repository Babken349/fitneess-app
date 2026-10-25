from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.study_test_result import StudyTestResult


class StudyTestResultRepository:

    async def create(
        self,
        db: AsyncSession,
        result: StudyTestResult,
    ) -> StudyTestResult:
        db.add(result)
        await db.flush()
        return result

    async def get_by_id(
        self,
        db: AsyncSession,
        result_id: int,
    ) -> StudyTestResult | None:
        stmt = select(StudyTestResult).where(
            StudyTestResult.id == result_id
        )
        query_result = await db.execute(stmt)
        return query_result.scalar_one_or_none()

    async def get_by_user(
        self,
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
    ) -> list[StudyTestResult]:
        stmt = (
            select(StudyTestResult)
            .where(StudyTestResult.user_id == user_id)
            .order_by(StudyTestResult.tested_at.desc())
            .offset(skip)
            .limit(limit)
        )
        query_result = await db.execute(stmt)
        return list(query_result.scalars().all())

    async def delete(
        self,
        db: AsyncSession,
        result: StudyTestResult,
    ) -> None:
        await db.delete(result)