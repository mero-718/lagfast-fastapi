from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ChatRoomBase(BaseModel):
    name: Optional[str] = None
    is_group: bool = False

class ChatRoomCreate(ChatRoomBase):
    pass

class ChatRoomResponse(ChatRoomBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class MessageBase(BaseModel):
    content: str
    message_type: str = "text"

class MessageCreate(MessageBase):
    room_id: int

class MessageResponse(MessageBase):
    id: int
    room_id: int
    sender_id: int
    created_at: datetime
    is_read: bool

    class Config:
        from_attributes = True

class ParticipantBase(BaseModel):
    user_id: int
    room_id: int

class ParticipantResponse(ParticipantBase):
    id: int
    joined_at: datetime
    is_online: bool
    last_seen: Optional[datetime] = None

    class Config:
        from_attributes = True

class WebRTCSignal(BaseModel):
    type: str  # offer, answer, ice-candidate
    target_user_id: int
    data: dict 