from datetime import datetime
from utils.validators import StrippedStr
from pydantic import BaseModel, Field, ConfigDict

class FriendshipCreate(BaseModel):
    receiver_id: int # Кому отправляем заявку

class FriendshipResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    sender_id: int
    receiver_id: int
    status: str # Например: 'pending', 'accepted', 'blocked'
    created_at: datetime