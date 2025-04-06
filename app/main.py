from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .controllers import auth_controller, user_controller
from .routers import chat_router
from .models import user, chat
from .utils.database import engine
from .websocket.chat_server import app as socket_app
from socketio import ASGIApp
from .websocket.chat_server import sio

# Create database tables
user.Base.metadata.create_all(bind=engine)
chat.Base.metadata.create_all(bind=engine)

app = FastAPI(title="LabFast API")

sio_app = ASGIApp(sio)
app.mount("/ws", sio_app)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_controller.router, tags=["auth"])
app.include_router(user_controller.router, tags=["users"])
app.include_router(chat_router.router, tags=["chat"])

# Mount Socket.IO app
app.mount("/socket.io", socket_app)

@app.get("/")
async def root():
    return {"message": "Welcome to LabFast API"} 