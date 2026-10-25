from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class StudyStateCreate(BaseModel):
    concentration: int = Field(ge=1, le=5)
    energy: int | None = Field(default=None, ge=1, le=5)
    fatigue: int | None = Field(default=None, ge=1, le=5)
    motivation: int | None = Field(default=None, ge=1, le=5)

    subject: str = Field(default="", max_length=100)
    duration_minutes: int | None = Field(default=None, ge=1, le=720)

    notes: str | None = Field(default=None, max_length=1000)


class StudyStateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int

    concentration: int
    energy: int
    fatigue: int
    motivation: int

    subject: str
    duration_minutes: int | None

    notes: str | None
    recorded_at: datetime