from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class StudyTestResultCreate(BaseModel):
    exam_type: str = Field(
        min_length=1,
        max_length=20,
    )

    subject: str = Field(
        min_length=1,
        max_length=100,
    )

    score: int = Field(
        ge=0,
    )

    max_score: int = Field(
        gt=0,
    )

    duration_minutes: int | None = Field(
        default=None,
        gt=0,
    )

    notes: str | None = Field(
        default=None,
        max_length=1000,
    )


class StudyTestResultResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    user_id: int

    exam_type: str
    subject: str

    score: int
    max_score: int

    duration_minutes: int | None

    notes: str | None
    tested_at: datetime