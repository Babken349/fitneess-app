from datetime import datetime
from utils.validators import StrippedStr
from pydantic import BaseModel, Field, ConfigDict

class WorkoutSessionCreate(BaseModel):
    workout_day_id: int | None = None # Может быть null, если юзер тренируется без плана
    notes: StrippedStr | None = Field(None, max_length=1000)

class WorkoutSessionUpdate(BaseModel):
    finished_at: datetime | None = None # Тренировка заканчивается проставлением времени конца
    notes: StrippedStr | None = Field(None, max_length=1000)

class WorkoutSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    workout_day_id: int | None
    started_at: datetime
    finished_at: datetime | None
    notes: StrippedStr | None = Field(None, max_length=1000)