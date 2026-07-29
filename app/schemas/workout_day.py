from datetime import datetime
from utils.validators import StrippedStr
from pydantic import BaseModel, Field, ConfigDict

class WorkoutDayCreate(BaseModel):
    name: StrippedStr = Field(..., max_length=100)
    day_order: int = Field(..., ge=1) # ge=1 значит "greater or equal" (номер дня не может быть 0 или отрицательным)

class WorkoutDayUpdate(BaseModel):
    name: StrippedStr | None = Field(None, max_length=100)
    day_order: int | None = Field(None, ge=1)

class WorkoutDayResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    workout_program_id: int
    name: StrippedStr = Field(..., max_length=100)
    day_order: int
    created_at: datetime
    updated_at: datetime