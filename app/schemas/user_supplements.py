from datetime import datetime
from utils.validators import StrippedStr
from pydantic import BaseModel, Field, ConfigDict

class UserSupplementCreate(BaseModel):
    supplement_id: int
    dosage: StrippedStr = Field(..., max_length=50) # Например "2 таблетки"

class UserSupplementUpdate(BaseModel):
    dosage: StrippedStr | None = Field(None, max_length=50)

class UserSupplementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    supplement_id: int
    dosage: StrippedStr = Field(..., max_length=50)
    created_at: datetime
    updated_at: datetime