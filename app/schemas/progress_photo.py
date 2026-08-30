from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from app.utils.validators import StrippedStr


class ProgressPhotoCreate(BaseModel):
    image_url: str = Field(..., min_length=1, max_length=500)
    notes: StrippedStr | None = Field(default=None, max_length=255)


class ProgressPhotoUpdate(BaseModel):
    image_url: str | None = Field(default=None, min_length=1, max_length=500)
    notes: StrippedStr | None = Field(default=None, max_length=255)


class ProgressPhotoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    image_url: str
    recorded_at: datetime
    notes: str | None