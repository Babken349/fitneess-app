from pydantic import BaseModel, Field, ConfigDict


class SetLogCreate(BaseModel):
    set_number: int = Field(..., ge=1)

    actual_weight: float = Field(
        ...,
        ge=0,
    )

    actual_reps: int = Field(
        ...,
        ge=0,
    )

    rir: int | None = Field(
        None,
        ge=0,
    )

    completed: bool = True


class SetLogUpdate(BaseModel):
    set_number: int | None = Field(
        None,
        ge=1,
    )

    actual_weight: float | None = Field(
        None,
        ge=0,
    )

    actual_reps: int | None = Field(
        None,
        ge=0,
    )

    rir: int | None = Field(
        None,
        ge=0,
    )

    completed: bool | None = None


class SetLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    exercise_log_id: int
    set_number: int
    actual_weight: float
    actual_reps: int
    rir: int | None
    completed: bool