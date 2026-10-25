from typing import Annotated
from pydantic import StringConstraints

# Объявляем кастомный тип (это переменная, а не функция!)
StrippedStr = Annotated[str, StringConstraints(strip_whitespace=True)]

MIN_PASSWORD_LENGTH = 10
MAX_PASSWORD_LENGTH = 128

# Стартовый набор. Всё короче MIN_PASSWORD_LENGTH отсекается длиной,
# поэтому здесь только пароли от 10 символов. Для продакшена положи рядом
# файл с ~10 тыс. самых частых паролей и читай его один раз при импорте.
COMMON_PASSWORDS = frozenset({
    "password123", "passw0rd123", "qwerty12345", "qwertyuiop", "qwertyuiop1",
    "1234567890", "0123456789", "12345678910", "1q2w3e4r5t", "1qaz2wsx3edc",
    "qazwsxedcrfv", "iloveyou123", "letmein1234", "administrator", "welcome123",
    "йцукенгшщз", "йцукен1234", "парольпароль", "пароль1234", "привет12345",
})


def validate_new_password(value: str) -> str:
    if not value.strip():
        raise ValueError("Пароль не может быть пустым")

    if len(value) < MIN_PASSWORD_LENGTH:
        raise ValueError(
            f"Пароль должен быть не короче {MIN_PASSWORD_LENGTH} символов"
        )

    if len(value) > MAX_PASSWORD_LENGTH:
        raise ValueError(
            f"Пароль должен быть не длиннее {MAX_PASSWORD_LENGTH} символов"
        )

    if value.lower() in COMMON_PASSWORDS:
        raise ValueError("Этот пароль слишком распространён, выберите другой")

    return value