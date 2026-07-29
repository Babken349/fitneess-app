from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class SetLogCreate(BaseModel):
    exercise_id: int
    set_number: int = Field(..., ge=1)
    weight: float = Field(..., ge=0) # Вес не может быть отрицательным
    reps: int = Field(..., ge=0)
    rir: int | None = Field(None, ge=0) # Reps in Reserve (оставшиеся повт.)
    completed: bool = True

class SetLogUpdate(BaseModel):
    weight: float | None = Field(None, ge=0)
    reps: int | None = Field(None, ge=0)
    rir: int | None = Field(None, ge=0)
    completed: bool | None = None

class SetLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    workout_session_id: int
    exercise_id: int
    set_number: int
    weight: float
    reps: int
    rir: int | None
    completed: bool