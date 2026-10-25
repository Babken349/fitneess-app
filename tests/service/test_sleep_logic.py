"""sleep_service.calculate_duration: переход через полночь, равные времена, границы 1 и 1080 минут (sync-тесты)"""
from datetime import time

import pytest

from app.services.sleep_service import InvalidSleepDurationError, SleepService

calculate = SleepService.calculate_duration


@pytest.mark.parametrize(
    "bedtime, wake_time, expected",
    [
        (time(23, 0), time(7, 0), 480),    # через полночь
        (time(22, 30), time(6, 15), 465),
        (time(1, 0), time(8, 0), 420),     # без перехода через полночь
        (time(23, 59), time(0, 0), 1),     # минимум: 1 минута
        (time(0, 0), time(18, 0), 1080),   # максимум: 18 часов
        (time(22,0,0),time(5, 30, 30), 450), # с секундами
    ],
)
def test_duration(bedtime, wake_time, expected):
    assert calculate(bedtime, wake_time) == expected


@pytest.mark.parametrize(
    "bedtime, wake_time",
    [
        (time(7, 0), time(7, 0)),    # одинаковое время
        (time(0, 0), time(18, 1)),   # больше 18 часов
    ],
)
def test_invalid_duration(bedtime, wake_time):
    with pytest.raises(InvalidSleepDurationError):
        calculate(bedtime, wake_time)