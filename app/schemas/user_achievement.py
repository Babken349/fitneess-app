from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserAchievementCreate(BaseModel):
    achievement_id: int


class UserAchievementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    achievement_id: int
    earned_at: datetime