from datetime import datetime
from utils.validators import StrippedStr
from pydantic import BaseModel, Field, ConfigDict

class WorkoutExerciseCreate(BaseModel):
    exercise_id: int
    exercise_order: int = Field(..., ge=1)
    note: StrippedStr | None = Field(None, max_length=255)

class WorkoutExerciseUpdate(BaseModel):
    exercise_id: int | None = None
    exercise_order: int | None = Field(None, ge=1)
    note: StrippedStr | None = Field(None, max_length=255)

class WorkoutExerciseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    workout_day_id: int
    exercise_id: int
    exercise_order: int
    note: StrippedStr | None = Field(None, max_length=255)
    created_at: datetime
    updated_at: datetime