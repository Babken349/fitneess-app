from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from app.utils.validators import StrippedStr


class AchievementCreate(BaseModel):
    name: StrippedStr = Field(..., min_length=1, max_length=100)
    description: StrippedStr | None = Field(default=None, max_length=500)
    code: StrippedStr = Field(..., min_length=1, max_length=100)
    icon_url: str | None = None


class AchievementUpdate(BaseModel):
    name: StrippedStr | None = Field(default=None, min_length=1, max_length=100)
    description: StrippedStr | None = Field(default=None, max_length=500)
    code: StrippedStr | None = Field(default=None, min_length=1, max_length=100)
    icon_url: str | None = None
    is_active: bool | None = None


class AchievementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    code: str
    icon_url: str | None
    is_active: bool
    created_at: datetime