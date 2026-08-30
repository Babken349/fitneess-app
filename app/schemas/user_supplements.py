from datetime import datetime

from app.utils.validators import StrippedStr
from pydantic import BaseModel, Field, ConfigDict


class UserSupplementCreate(BaseModel):
    supplement_id: int

    dosage: StrippedStr | None = Field(
        None,
        max_length=50,
    )

    frequency: StrippedStr | None = Field(
        None,
        max_length=50,
    )

    notes: StrippedStr | None = Field(
        None,
        max_length=255,
    )


class UserSupplementUpdate(BaseModel):
    dosage: StrippedStr | None = Field(
        None,
        max_length=50,
    )

    frequency: StrippedStr | None = Field(
        None,
        max_length=50,
    )

    notes: StrippedStr | None = Field(
        None,
        max_length=255,
    )

    is_active: bool | None = None


class UserSupplementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    supplement_id: int

    dosage: str | None
    frequency: str | None
    started_at: datetime
    notes: str | None
    is_active: bool