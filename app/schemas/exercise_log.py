from pydantic import BaseModel, Field, ConfigDict
from app.utils.validators import StrippedStr


class ExerciseLogCreate(BaseModel):
    exercise_id: int
    exercise_order: int = Field(..., ge=1)
    notes: StrippedStr | None = Field(
        None,
        max_length=255,
    )


class ExerciseLogUpdate(BaseModel):
    exercise_order: int | None = Field(
        None,
        ge=1,
    )

    notes: StrippedStr | None = Field(
        None,
        max_length=255,
    )


class ExerciseLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    workout_session_id: int
    exercise_id: int
    exercise_order: int
    notes: str | None