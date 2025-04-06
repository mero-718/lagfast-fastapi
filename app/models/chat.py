from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from ..utils.database import Base

# class ChatRoom(Base):
#     __tablename__ = "chat_rooms"

#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String, nullable=True)
#     is_group = Column(Boolean, default=False)
#     created_at = Column(DateTime, default=datetime.utcnow)
#     updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
#     # Relationships
#     participants = relationship("ChatParticipant", back_populates="room")
#     messages = relationship("ChatMessage", back_populates="room")

# class ChatParticipant(Base):
#     __tablename__ = "chat_participants"

#     id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, ForeignKey("users.id"))
#     room_id = Column(Integer, ForeignKey("chat_rooms.id"))
#     joined_at = Column(DateTime, default=datetime.utcnow)
#     is_online = Column(Boolean, default=False)
#     last_seen = Column(DateTime, nullable=True)
    
#     # Relationships
#     user = relationship("User", back_populates="chat_participations")
#     room = relationship("ChatRoom", back_populates="participants")

# class ChatMessage(Base):
#     __tablename__ = "chat_messages"

#     id = Column(Integer, primary_key=True, index=True)
#     room_id = Column(Integer, ForeignKey("chat_rooms.id"))
#     sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#     receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#     content = Column(Text, nullable=False)
#     message_type = Column(String, default="text", nullable=False)  # text, image, file, etc.
#     is_read = Column(Boolean, default=False, nullable=False)
#     timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
#     # Relationships
#     room = relationship("ChatRoom", back_populates="messages")
#     sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_messages")
#     receiver = relationship("User", foreign_keys=[receiver_id], back_populates="received_messages")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    message_type = Column(String, default="text", nullable=False)  # text, image, file, etc.
    is_read = Column(Boolean, default=False, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)