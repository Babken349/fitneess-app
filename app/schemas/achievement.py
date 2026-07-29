from datetime import datetime
from utils.validators import StrippedStr
from pydantic import BaseModel, Field, ConfigDict

class AchievementCreate(BaseModel):
    title: StrippedStr = Field(..., max_length=100)
    description: StrippedStr | None = Field(None, max_length=255)
    icon: StrippedStr | None = Field(None, max_length=255)

class AchievementUpdate(BaseModel):
    title: StrippedStr | None = Field(None, max_length=100)
    description: StrippedStr | None = Field(None, max_length=255)
    icon: StrippedStr | None = Field(None, max_length=255)

class AchievementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    title: StrippedStr = Field(..., max_length=100)
    description: StrippedStr | None = Field(None, max_length=255)
    icon: StrippedStr | None = Field(None, max_length=255)
    created_at: datetime
    updated_at: datetime