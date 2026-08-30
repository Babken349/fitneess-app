from datetime import datetime

from app.utils.validators import StrippedStr
from pydantic import BaseModel, Field, ConfigDict


class SupplementIntakeCreate(BaseModel):
    user_supplement_id: int
    scheduled_at: datetime | None = None
    taken_at: datetime | None = None
    status: StrippedStr = Field(
        default="taken",
        max_length=20,
    )
    notes: StrippedStr | None = Field(
        None,
        max_length=500,
    )


class SupplementIntakeUpdate(BaseModel):
    scheduled_at: datetime | None = None
    taken_at: datetime | None = None
    status: StrippedStr | None = Field(
        None,
        max_length=20,
    )
    notes: StrippedStr | None = Field(
        None,
        max_length=500,
    )


class SupplementIntakeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    user_supplement_id: int
    scheduled_at: datetime | None
    taken_at: datetime | None
    status: str
    notes: str | None
    created_at: datetime