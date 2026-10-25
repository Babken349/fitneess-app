from datetime import date

from sqlalchemy import Date, Float, cast, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sleep import SleepEntry
from app.models.study_state import StudyState
from app.models.study_test_result import StudyTestResult


class SleepAnalyticsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_sleep_entries(
        self,
        date_from: date,
        date_to: date,
    ) -> list[SleepEntry]:
        statement = select(SleepEntry).where(
            SleepEntry.sleep_date >= date_from,
            SleepEntry.sleep_date <= date_to,
        )
        result = await self.db.execute(statement)
        return list(result.scalars().all())

    async def get_study_data(
        self,
        date_from: date,
        date_to: date,
    ) -> list[tuple[int, date, float | None]]:
        study_date = cast(StudyState.recorded_at, Date)

        statement = select(
            StudyState.user_id,
            study_date,
            StudyState.concentration,
        ).where(
            study_date >= date_from,
            study_date <= date_to,
        )

        result = await self.db.execute(statement)
        return list(result.all())

    async def get_test_data(
        self,
        date_from: date,
        date_to: date,
    ) -> list[tuple[int, date, float | None]]:
        test_date = cast(StudyTestResult.tested_at, Date)
        score_percent = (
            cast(StudyTestResult.score, Float) * 100.0
            / StudyTestResult.max_score
        )

        statement = select(
            StudyTestResult.user_id,
            test_date,
            score_percent,
        ).where(
            test_date >= date_from,
            test_date <= date_to,
        )

        result = await self.db.execute(statement)
        return list(result.all())