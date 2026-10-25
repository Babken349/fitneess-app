from app.core.enums import UserRole
from datetime import datetime
from app.utils.validators import validate_new_password, StrippedStr  # <-- Импортируем тип отсюда!
from pydantic import BaseModel, Field, field_validator, EmailStr, ConfigDict, HttpUrl


# Создание пользователя
class UserCreate(BaseModel):
    login: StrippedStr = Field(..., min_length=4, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        return validate_new_password(value)


class UserLogin(BaseModel):
    identifier: StrippedStr = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=1, max_length=128)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    login: str
    email: EmailStr
    
    display_name: str | None = None
    avatar_url: HttpUrl | None = None
    bio: str | None = None
    
    is_active: bool
    is_verified: bool
    role: UserRole
    
    last_login: datetime | None = None
    premium_until: datetime | None = None
    
    created_at: datetime
    updated_at: datetime


class UserUpdate(BaseModel):
    display_name: StrippedStr | None = Field(default=None, max_length=100)
    avatar_url: HttpUrl | None = Field(default=None, max_length=255)
    bio: StrippedStr | None = Field(default=None, max_length=255)


class ChangePassword(BaseModel):
    old_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, value: str) -> str:
        return validate_new_password(value)


class ChangeEmail(BaseModel):
    new_email: EmailStr
    password: str = Field(..., min_length=1)


class ChangeLogin(BaseModel):
    new_login: StrippedStr = Field(..., min_length=4, max_length=50)
    password: str = Field(..., min_length=1)
