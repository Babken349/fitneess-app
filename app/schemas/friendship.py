from datetime import datetime
from app.utils.validators import StrippedStr
from pydantic import BaseModel, Field, ConfigDict

class FriendshipCreate(BaseModel):
    addressee_id: int # Кому отправляем заявку

class FriendshipResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    requester_id: int
    addressee_id: int
    status: str # Например: 'pending', 'accepted', 'blocked'
    created_at: datetime