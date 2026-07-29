from datetime import datetime, time
from pydantic import BaseModel, Field, ConfigDict

class ReminderCreate(BaseModel):
    user_supplement_id: int | None = None
    day_of_week: int = Field(..., ge=0, le=6) # 0=понедельник ... 6=воскресенье
    time_of_day: time
    is_active: bool = True

class ReminderUpdate(BaseModel):
    day_of_week: int | None = Field(None, ge=0, le=6)
    time_of_day: time | None = None
    is_active: bool | None = None

class ReminderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    user_supplement_id: int | None
    day_of_week: int
    time_of_day: time
    is_active: bool
    created_at: datetime