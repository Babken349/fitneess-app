from pydantic import BaseModel, Field, ConfigDict
from app.utils.validators import StrippedStr


class WorkoutExerciseCreate(BaseModel):
    exercise_id: int
    exercise_order: int = Field(..., ge=1)
    note: StrippedStr | None = Field(
        None,
        max_length=255,
    )


class WorkoutExerciseUpdate(BaseModel):
    exercise_order: int | None = Field(
        None,
        ge=1,
    )

    note: StrippedStr | None = Field(
        None,
        max_length=255,
    )


class WorkoutExerciseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    workout_day_id: int
    exercise_id: int
    exercise_order: int
    note: str | None