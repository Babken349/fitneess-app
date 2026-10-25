from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.utils.validators import StrippedStr


ALLOWED_ICON_SCHEMES = ("http://", "https://")


def _validate_icon_url(value: str | None) -> str | None:
    if value is None:
        return None

    value = value.strip()

    if not value:
        raise ValueError("icon_url cannot be empty")

    if len(value) > 500:
        raise ValueError("icon_url is too long")

    if not value.lower().startswith(ALLOWED_ICON_SCHEMES):
        raise ValueError("icon_url must start with http:// or https://")

    return value


class AchievementCreate(BaseModel):
    name: StrippedStr = Field(..., min_length=1, max_length=100)
    description: StrippedStr | None = Field(default=None, max_length=500)
    code: StrippedStr = Field(..., min_length=1, max_length=100)
    icon_url: Annotated[str | None, Field(max_length=500)] = None

    @field_validator("icon_url")
    @classmethod
    def validate_icon_url(cls, value: str | None) -> str | None:
        return _validate_icon_url(value)


class AchievementUpdate(BaseModel):
    name: StrippedStr | None = Field(default=None, min_length=1, max_length=100)
    description: StrippedStr | None = Field(default=None, max_length=500)
    code: StrippedStr | None = Field(default=None, min_length=1, max_length=100)
    icon_url: Annotated[str | None, Field(max_length=500)] = None
    is_active: bool | None = None

    @field_validator("icon_url")
    @classmethod
    def validate_icon_url(cls, value: str | None) -> str | None:
        return _validate_icon_url(value)

    @field_validator("name", "code", "is_active", mode="before")
    @classmethod
    def reject_explicit_null(cls, value, info):
        if value is None:
            raise ValueError(f"Field '{info.field_name}' cannot be null")

        return value


class AchievementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    code: str
    icon_url: str | None
    is_active: bool
    created_at: datetime