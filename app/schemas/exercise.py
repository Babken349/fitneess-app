from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.utils.validators import StrippedStr



class ExerciseCreate(BaseModel):
    name: StrippedStr = Field(..., max_length=100)
    description: StrippedStr | None = Field(None, max_length=500)
    muscle_group_id: int | None = Field(None)
    equipment_id: int | None = Field(None)

class ExerciseUpdate(BaseModel):
    name: StrippedStr | None = Field(None, max_length=100)
    description: StrippedStr | None = Field(None, max_length=500)
    muscle_group_id: int | None = Field(None)
    equipment_id: int | None = Field(None)


class ExerciseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: StrippedStr = Field(..., max_length=100)
    description: StrippedStr | None = Field(None, max_length=500)
    muscle_group_id: int | None = Field(None)
    equipment_id: int | None = Field(None)
    created_at: datetime
    updated_at: datetime