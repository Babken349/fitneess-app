from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from fitness.app.utils.validators import StrippedStr


class ExerciseCreate(BaseModel):
    name: StrippedStr = Field(..., max_length=100)
    description: StrippedStr | None = Field(None, max_length=500)
    muscle_group: StrippedStr | None = Field(None, max_length=50)
    equipment: StrippedStr | None = Field(None, max_length=50)


class ExerciseUpdate(BaseModel):
    name: StrippedStr | None = Field(None, max_length=100)
    description: StrippedStr | None = Field(None, max_length=500)
    muscle_group: StrippedStr | None = Field(None, max_length=50)
    equipment: StrippedStr | None = Field(None, max_length=50)


class ExerciseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: StrippedStr = Field(..., max_length=100)
    description: StrippedStr | None = Field(None, max_length=500)
    muscle_group: StrippedStr | None = Field(None, max_length=50)
    equipment: StrippedStr | None = Field(None, max_length=50)
    created_at: datetime
    updated_at: datetime