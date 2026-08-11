from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from utils.validators import StrippedStr


class WorkoutDayCreate(BaseModel):
    name: StrippedStr = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    day_order: int = Field(
        ...,
        ge=1,
    )


class WorkoutDayUpdate(BaseModel):
    name: StrippedStr | None = Field(
        None,
        min_length=1,
        max_length=100,
    )

    day_order: int | None = Field(
        None,
        ge=1,
    )


class WorkoutDayResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    workout_program_id: int

    name: str
    day_order: int

    is_archived: bool

    created_at: datetime
    updated_at: datetime