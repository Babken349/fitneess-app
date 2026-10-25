from collections import defaultdict
from datetime import date
from statistics import mean

from scipy.stats import spearmanr
from sqlalchemy.ext.asyncio import AsyncSession

from app.repository.sleep_analytics_repository import (
    SleepAnalyticsRepository,
)
from app.schemas.sleep import SleepAnalyticsRead, SleepCorrelation


class SleepAnalyticsService:
    def __init__(self, db: AsyncSession):
        self.repository = SleepAnalyticsRepository(db)

    @staticmethod
    def _correlation(
        sleep_minutes: list[float],
        outcomes: list[float],
    ) -> SleepCorrelation:
        n = len(sleep_minutes)

        # Для очень маленькой выборки или постоянных значений
        # коэффициент и p-value не интерпретируем.
        if (
            n < 3
            or len(outcomes) != n
            or len(set(sleep_minutes)) < 2
            or len(set(outcomes)) < 2
        ):
            return SleepCorrelation(
                sample_size=n,
                rho=None,
                p_value=None,
            )

        result = spearmanr(sleep_minutes, outcomes)

        return SleepCorrelation(
            sample_size=n,
            rho=round(float(result.statistic), 4),
            p_value=round(float(result.pvalue), 4),
        )

    async def get_analytics(
        self,
        date_from: date,
        date_to: date,
    ) -> SleepAnalyticsRead:
        if date_from > date_to:
            raise ValueError(
                "date_from не может быть позже date_to."
            )

        sleep_entries = await self.repository.get_sleep_entries(
            date_from,
            date_to,
        )
        study_data = await self.repository.get_study_data(
            date_from,
            date_to,
        )
        test_data = await self.repository.get_test_data(
            date_from,
            date_to,
        )

        # По каждой паре (участник, дата) собираем показатели.
        sleep_by_key = {
            (entry.user_id, entry.sleep_date): entry.duration_minutes
            for entry in sleep_entries
        }

        concentration_by_key: dict[tuple[int, date], list[float]] = (
            defaultdict(list)
        )
        for user_id, study_date, score in study_data:
            if score is not None:
                concentration_by_key[(user_id, study_date)].append(
                    float(score)
                )

        test_score_by_key: dict[tuple[int, date], list[float]] = (
            defaultdict(list)
        )
        for user_id, test_date, score in test_data:
            if score is not None:
                test_score_by_key[(user_id, test_date)].append(
                    float(score)
                )

        # Если за день несколько учебных сессий или тестов,
        # берём среднее значение за этот день.
        sleep_concentration_x = []
        sleep_concentration_y = []

        sleep_test_x = []
        sleep_test_y = []

        for key, duration in sleep_by_key.items():
            if key in concentration_by_key:
                sleep_concentration_x.append(duration)
                sleep_concentration_y.append(
                    mean(concentration_by_key[key])
                )

            if key in test_score_by_key:
                sleep_test_x.append(duration)
                sleep_test_y.append(mean(test_score_by_key[key]))

        return SleepAnalyticsRead(
            date_from=date_from,
            date_to=date_to,
            sleep_entries=len(sleep_entries),
            participants_with_sleep=len({
                entry.user_id for entry in sleep_entries
            }),
            average_sleep_minutes=(
                round(mean([
                    entry.duration_minutes
                    for entry in sleep_entries
                ]), 1)
                if sleep_entries
                else None
            ),
            concentration_pairs=len(sleep_concentration_x),
            sleep_concentration=self._correlation(
                sleep_concentration_x,
                sleep_concentration_y,
            ),
            test_score_pairs=len(sleep_test_x),
            sleep_test_score=self._correlation(
                sleep_test_x,
                sleep_test_y,
            ),
        )