from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class StudyStateCreate(BaseModel):
    concentration: int = Field(ge=1, le=10)
    energy: int = Field(ge=1, le=10)
    fatigue: int = Field(ge=1, le=10)
    motivation: int = Field(ge=1, le=10)

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