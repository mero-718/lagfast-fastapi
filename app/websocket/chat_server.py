from fastapi import WebSocket, WebSocketDisconnect, HTTPException
from typing import Dict, List, Optional
import socketio
import asyncio
# from app.core.security import decode_access_token
# from app.models.user import User
# from app.models.chat import Message
# from app.database import SessionLocal
from ..models.chat import ChatMessage
from sqlalchemy.orm import Session
from datetime import datetime
from urllib.parse import parse_qs
from ..utils.auth import verify_token
from ..services.user_service import UserService
from ..utils.database import SessionLocal

# Create Socket.IO server
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
app = socketio.ASGIApp(sio)

# Store active connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Dict[str, List[socketio.AsyncServer]]] = {}
        self.user_connections: Dict[str, socketio.AsyncServer] = {}

    async def connect(self, sid: str, token: str):
        try:            
            # Decode token to get user_id
            user_name = verify_token(token).get('sub')
            db = SessionLocal()
            user_id = UserService.get_user_by_name(db, user_name).id
            if not user_id:
                raise HTTPException(status_code=401, detail="Invalid token")
            
            # Store the connection
            self.user_connections[sid] = user_id
            
            # Notify others about the new user
            await sio.emit('user_joined', {'user_id': user_id}, skip_sid=sid)
            
            # Send list of online users to the new connection
            online_users = [
                uid for uid in self.user_connections.values() if uid != user_id
            ]
            await sio.emit('online_users', online_users, room=sid)
            
        except Exception as e:
            print(f"Error in connect: {str(e)}")
            raise HTTPException(status_code=401, detail="Invalid token")

    async def disconnect(self, sid: str):
        if sid in self.user_connections:
            user_id = self.user_connections[sid]
            del self.user_connections[sid]
            
            # Notify others about the user leaving
            await sio.emit('user_left', {'user_id': user_id}, skip_sid=sid)

    async def join_room(self, sid: str, room_id: str):
        try:
            user_id = self.user_connections[sid]
            if not user_id:
                return

            # Initialize room if it doesn't exist
            if room_id not in self.active_connections:
                self.active_connections[room_id] = {}
            
            # Initialize user's connections in the room if they don't exist
            if user_id not in self.active_connections[room_id]:
                self.active_connections[room_id][user_id] = []
            
            # Add the connection to the room
            self.active_connections[room_id][user_id].append(sid)
            
            # Join Socket.IO room
            if sio is not None:
                print(f"Joining room {room_id} for user {self.active_connections[room_id]}")
                # await sio.enter_room(sid, room_id)
                
                # Notify others in the room
                await sio.emit('user_joined_room', 
                             {'user_id': user_id, 'room_id': room_id}, 
                             room=room_id, 
                             skip_sid=sid)
            else:
                print("Socket.IO server not initialized")
                
        except Exception as e:
            print(f"Error in join_room: {str(e)}")
            raise

    async def leave_room(self, sid: str, room_id: str):
        if sid in self.user_connections:
            user_id = self.user_connections[sid]
            if room_id in self.active_connections and user_id in self.active_connections[room_id]:
                self.active_connections[room_id][user_id].remove(sid)
                if not self.active_connections[room_id][user_id]:
                    del self.active_connections[room_id][user_id]
                if not self.active_connections[room_id]:
                    del self.active_connections[room_id]
            
            # Leave Socket.IO room
            await sio.leave_room(sid, room_id)
            
            # Notify others in the room
            await sio.emit('user_left_room', 
                         {'user_id': user_id, 'room_id': room_id}, 
                         room=room_id, 
                         skip_sid=sid)

    async def broadcast_to_room(self, room_id: str, message: dict, skip_sid: str = None):
        if room_id in self.active_connections:
            await sio.emit('message', message, room=room_id, skip_sid=skip_sid)

manager = ConnectionManager()

@sio.event
async def connect(sid, environ, auth):
    try:
        qs = parse_qs(environ.get("QUERY_STRING", ""))
        token = qs.get("token", [None])[0]
        if not token:
            raise Exception("No token provided")
        await manager.connect(sid, token)
    except Exception as e:
        print(f"Connection error: {str(e)}")
        return False

@sio.event
async def disconnect(sid):
    await manager.disconnect(sid)

@sio.event
async def join_room(sid, data):
    room_id = data.get('room_id')
    if room_id:
        await manager.join_room(sid, room_id)

@sio.event
async def leave_room(sid, data):
    room_id = data.get('room_id')
    if room_id:
        await manager.leave_room(sid, room_id)

@sio.event
async def message(sid, data):
    try:
        room_id = data.get('room_id')
        content = data.get('content')
        if not room_id or not content:
            return
        
        # Get user_id from connection
        user_id = manager.user_connections.get(sid)
        if not user_id:
            return
        
        # Save message to database
        db = SessionLocal()
        try:
            message = ChatMessage(
                room_id=room_id,
                receiver_id=room_id,
                sender_id=user_id,
                content=content,
                message_type='text',
                is_read=False,
                timestamp=datetime.utcnow()
            )
            db.add(message)
            db.commit()
            
            # Broadcast message to room
            await manager.broadcast_to_room(
                room_id,
                {
                    'room_id': room_id,
                    'receiver_id': user_id,
                    'content': content,
                    'timestamp': message.timestamp.isoformat()
                },
                skip_sid=sid
            )
        finally:
            db.close()
    except Exception as e:
        print(f"Error handling message: {str(e)}")

@sio.event
async def typing(sid, data):
    try:
        room_id = data.get('room_id')
        is_typing = data.get('is_typing')
        if not room_id:
            return
        
        # Get user_id from connection
        user_id = manager.user_connections.get(sid)
        if not user_id:
            return
        
        # Broadcast typing status to room
        await manager.broadcast_to_room(
            room_id,
            {
                'room_id': room_id,
                'user_id': user_id,
                'is_typing': is_typing
            },
            skip_sid=sid
        )
    except Exception as e:
        print(f"Error handling typing status: {str(e)}")

@sio.event
async def webrtc_signal(sid, data):
    try:
        target_user_id = data.get('target_user_id')
        signal = data.get('signal')
        if not target_user_id or not signal:
            return
        
        # Get user_id from connection
        user_id = manager.user_connections.get(sid)
        if not user_id:
            return
        
        # Find target user's connection
        target_sid = None
        for sid, uid in manager.user_connections.items():
            if uid == target_user_id:
                target_sid = sid
                break
        
        if target_sid:
            await sio.emit('webrtc_signal', {
                'from_user_id': user_id,
                'signal': signal
            }, room=target_sid)
    except Exception as e:
        print(f"Error handling WebRTC signal: {str(e)}") 