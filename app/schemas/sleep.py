from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict, Field, computed_field


class SleepCreate(BaseModel):
    sleep_date: date
    bedtime: time
    wake_time: time
    note: str | None = Field(default=None, max_length=500)


class SleepUpdate(BaseModel):
    # Все поля необязательны: PATCH меняет только переданные значения.
    bedtime: time | None = None
    wake_time: time | None = None
    note: str | None = Field(default=None, max_length=500)


class SleepRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    sleep_date: date
    bedtime: time
    wake_time: time
    duration_minutes: int
    note: str | None
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def duration_hours(self) -> float:
        return round(self.duration_minutes / 60, 2)


class SleepCorrelation(BaseModel):
    # Количество парных наблюдений, использованных в расчёте.
    sample_size: int

    # Коэффициент ранговой корреляции Спирмена.
    rho: float | None

    # p-value; отсутствует, если данных недостаточно для расчёта.
    p_value: float | None


class SleepAnalyticsRead(BaseModel):
    date_from: date
    date_to: date

    sleep_entries: int
    participants_with_sleep: int
    average_sleep_minutes: float | None

    concentration_pairs: int
    sleep_concentration: SleepCorrelation

    test_score_pairs: int
    sleep_test_score: SleepCorrelation