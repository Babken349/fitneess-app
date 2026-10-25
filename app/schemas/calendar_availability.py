from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class CalendarAvailabilityCreate(BaseModel):
    date: date
    is_available: bool = True
    note: str | None = Field(
        default=None,
        max_length=255,
    )


class CalendarAvailabilityUpdate(BaseModel):
    is_available: bool | None = None
    note: str | None = Field(
        default=None,
        max_length=255,
    )


class CalendarAvailabilityResponse(BaseModel):
    id: int
    user_id: int
    date: date
    is_available: bool
    note: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )