from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from app.utils.validators import StrippedStr


class ExerciseCreate(BaseModel):
    name: StrippedStr = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    description: StrippedStr | None = Field(
        None,
        max_length=500,
    )

    muscle_group_id: int | None = None
    equipment_id: int | None = None


class ExerciseUpdate(BaseModel):
    name: StrippedStr | None = Field(
        None,
        min_length=1,
        max_length=100,
    )

    description: StrippedStr | None = Field(
        None,
        max_length=500,
    )

    muscle_group_id: int | None = None
    equipment_id: int | None = None


class ExerciseResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    name: str
    description: str | None

    muscle_group_id: int | None
    equipment_id: int | None

    is_archived: bool

    created_at: datetime
    updated_at: datetime