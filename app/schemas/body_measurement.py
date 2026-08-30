from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class BodyMeasurementCreate(BaseModel):
    chest: float | None = Field(None, gt=0)
    waist: float | None = Field(None, gt=0)
    hips: float | None = Field(None, gt=0)
    biceps: float | None = Field(None, gt=0)
    thigh: float | None = Field(None, gt=0)
    forearm: float | None = Field(None, gt=0)
    calf: float | None = Field(None, gt=0)


class BodyMeasurementUpdate(BaseModel):
    chest: float | None = Field(None, gt=0)
    waist: float | None = Field(None, gt=0)
    hips: float | None = Field(None, gt=0)
    biceps: float | None = Field(None, gt=0)
    thigh: float | None = Field(None, gt=0)
    forearm: float | None = Field(None, gt=0)
    calf: float | None = Field(None, gt=0)


class BodyMeasurementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    chest: float | None
    waist: float | None
    hips: float | None
    biceps: float | None
    thigh: float | None
    forearm: float | None
    calf: float | None
    recorded_at: datetime