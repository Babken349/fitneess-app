"""sleep_analytics_service._correlation: идеальная корреляция, меньше 3 точек, константы дают None, сверка со scipy (sync-тесты)"""
import pytest
from scipy.stats import spearmanr

from app.services.sleep_analytics_service import SleepAnalyticsService

correlation = SleepAnalyticsService._correlation


def test_perfect_positive_correlation():
    result = correlation([300, 400, 500, 600], [1, 2, 3, 4])
    assert result.sample_size == 4
    assert result.rho == 1.0


def test_perfect_negative_correlation():
    result = correlation([300, 400, 500, 600], [4, 3, 2, 1])
    assert result.rho == -1.0


def test_matches_scipy():
    x = [360, 420, 480, 540, 450]
    y = [3, 5, 6, 8, 4]
    result = correlation(x, y)
    expected = spearmanr(x, y)
    assert result.rho == pytest.approx(expected.statistic, abs=1e-4)
    assert result.p_value == pytest.approx(expected.pvalue, abs=1e-4)


@pytest.mark.parametrize(
    "x, y",
    [
        ([300, 400], [1, 2]),            # меньше 3 точек
        ([400, 400, 400], [1, 2, 3]),    # сон постоянный
        ([300, 400, 500], [5, 5, 5]),    # результат постоянный
        ([300, 400, 500], [1, 2]),       # разная длина
    ],
)
def test_not_interpretable_returns_none(x, y):
    result = correlation(x, y)
    assert result.rho is None
    assert result.p_value is None