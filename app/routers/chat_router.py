from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..utils.database import get_db
from ..models.chat import ChatMessage
from ..schemas.chat import ChatRoomCreate, ChatRoomResponse, MessageResponse, MessageCreate

router = APIRouter()

@router.get("/messages/{user_id}", response_model=List[MessageResponse])
async def get_messages(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all messages between the current user and another user.
    """
    try:
        # Get all messages where either user is the sender or receiver
        messages = db.query(ChatMessage).filter(
            (
                (ChatMessage.sender_id == user_id) & 
                (ChatMessage.receiver_id == user_id)
            ) | (
                (ChatMessage.sender_id == user_id) & 
                (ChatMessage.receiver_id == user_id)
            )
        ).order_by(ChatMessage.timestamp.asc()).all()

        # Format messages for response
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                "id": msg.id,
                "content": msg.content,
                "sender_id": msg.sender_id,
                "receiver_id": msg.receiver_id,
                "timestamp": msg.timestamp.isoformat(),
                "is_read": msg.is_read
            })

        return formatted_messages

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching messages: {str(e)}"
        ) 
