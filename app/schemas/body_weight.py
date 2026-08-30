from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class BodyWeightCreate(BaseModel):
    weight: float = Field(..., gt=0)


class BodyWeightUpdate(BaseModel):
    weight: float | None = Field(None, gt=0)


class BodyWeightResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    weight: float
    recorded_at: datetime