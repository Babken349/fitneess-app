from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from utils.validators import StrippedStr


class WorkoutProgramCreate(BaseModel):
    name: StrippedStr = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    description: StrippedStr | None = Field(
        None,
        max_length=255,
    )

    is_public: bool = False


class WorkoutProgramUpdate(BaseModel):
    name: StrippedStr | None = Field(
        None,
        min_length=1,
        max_length=100,
    )

    description: StrippedStr | None = Field(
        None,
        max_length=255,
    )

    is_public: bool | None = None


class WorkoutProgramResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    user_id: int

    name: str
    description: str | None

    is_public: bool
    is_archived: bool

    created_at: datetime
    updated_at: datetime