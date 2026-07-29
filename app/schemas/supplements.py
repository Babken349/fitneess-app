from datetime import datetime
from utils.validators import StrippedStr
from pydantic import BaseModel, Field, ConfigDict

class SupplementCreate(BaseModel):
    name: StrippedStr = Field(..., max_length=100)
    description: StrippedStr | None = Field(None, max_length=500)
    category: StrippedStr | None = Field(None, max_length=50)

class SupplementUpdate(BaseModel):
    name: StrippedStr | None = Field(None, max_length=100)
    description: StrippedStr | None = Field(None, max_length=500)
    category: StrippedStr | None = Field(None, max_length=50)

class SupplementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: StrippedStr = Field(..., max_length=100)
    description: StrippedStr | None = Field(None, max_length=500)
    category: StrippedStr | None = Field(None, max_length=50)
    created_at: datetime
    updated_at: datetime