"""Тесты validate_new_password: длина, пустой, common-password."""
import pytest

from app.utils.validators import (
    COMMON_PASSWORDS,
    MAX_PASSWORD_LENGTH,
    MIN_PASSWORD_LENGTH,
    validate_new_password,
)


def test_valid_password_is_returned_unchanged():
    pwd = "Tractor-Blue-42x"
    assert validate_new_password(pwd) == pwd


def test_exactly_min_length_is_valid():
    pwd = "a" * MIN_PASSWORD_LENGTH
    assert validate_new_password(pwd) == pwd


def test_exactly_max_length_is_valid():
    pwd = "a" * MAX_PASSWORD_LENGTH
    assert validate_new_password(pwd) == pwd


@pytest.mark.parametrize("password", ["", "   ", "\t\n"])
def test_empty_or_whitespace_only_is_rejected(password):
    with pytest.raises(ValueError, match="пустым"):
        validate_new_password(password)


def test_too_short_is_rejected():
    pwd = "a" * (MIN_PASSWORD_LENGTH - 1)
    with pytest.raises(ValueError, match="короче"):
        validate_new_password(pwd)


def test_too_long_is_rejected():
    pwd = "a" * (MAX_PASSWORD_LENGTH + 1)
    with pytest.raises(ValueError, match="длиннее"):
        validate_new_password(pwd)


def test_common_password_is_rejected():
    # Берём первый элемент из списка — гарантированно common
    common = next(iter(COMMON_PASSWORDS))
    with pytest.raises(ValueError, match="распространён"):
        validate_new_password(common)


def test_common_password_case_insensitive():
    common = next(iter(COMMON_PASSWORDS))
    with pytest.raises(ValueError, match="распространён"):
        validate_new_password(common.upper())