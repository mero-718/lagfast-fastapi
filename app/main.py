from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .utils.database import engine
from .models import user
from .controllers import auth_controller, user_controller

# Create database tables
user.Base.metadata.create_all(bind=engine)

app = FastAPI(title="LabFast API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include routers
@app.get("/")
async def root():
    return {"message": "This is FastAPI Backend for LabFast"}

app.include_router(auth_controller.router, tags=["auth"])
app.include_router(user_controller.router, tags=["users"]) 