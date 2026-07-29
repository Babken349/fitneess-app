import string
from typing import Annotated
from pydantic import StringConstraints

# Объявляем кастомный тип (это переменная, а не функция!)
StrippedStr = Annotated[str, StringConstraints(strip_whitespace=True)]


def validate_new_password(value: str) -> str:
    if not value:
        raise ValueError('New password cannot be empty or whitespace')
    
    if not any(v.isdigit() for v in value):
        raise ValueError(f"Password must contain at least one digit")
    
    if not any(v.isupper() for v in value):
        raise ValueError(f"Password must contain at least one uppercase letter")
    
    if not any(v.islower() for v in value):
        raise ValueError(f"Password must contain at least one lowercase letter")
    
    if not any(v in string.punctuation for v in value):
        raise ValueError(f"Password must contain at least one special character")

    return value