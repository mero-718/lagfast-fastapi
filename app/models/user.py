from sqlalchemy import Boolean, Column, Integer, String, DateTime, func
from sqlalchemy.sql import func
from ..utils.database import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 

    # chat_participations = relationship("ChatParticipant", back_populates="user")
    # sent_messages = relationship("ChatMessage", foreign_keys="[ChatMessage.sender_id]", back_populates="sender")
    # received_messages = relationship("ChatMessage", foreign_keys="[ChatMessage.receiver_id]", back_populates="receiver")