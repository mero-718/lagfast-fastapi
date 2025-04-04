from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List
from ..utils.database import get_db
from ..models.user import User
from ..schemas.user import User as UserSchema, UserCreate, UserUpdate
from ..services.user_service import UserService
from ..utils.auth import get_current_active_user
from ..utils.file_upload import save_upload_file
import os

router = APIRouter()

@router.post("/users/", response_model=UserSchema)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    db_user = UserService.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    return UserService.create_user(db=db, user=user)

@router.get("/users/", response_model=List[UserSchema])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)    
):
    users = UserService.get_users(db, skip=skip, limit=limit)
    return users

@router.get("/users/{user_id}", response_model=UserSchema)
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
):
    db_user = UserService.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put("/users/{user_id}", response_model=UserSchema)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
):
    db_user = UserService.update_user(db, user_id=user_id, user_update=user_update)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
):
    success = UserService.delete_user(db, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}

@router.post("/users/{user_id}/photo", response_model=UserSchema)
async def upload_user_photo(
    user_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    try:
        # Save the uploaded file
        photo_url = save_upload_file(file, user_id)
        
        # Update user with new photo URL
        user_update = UserUpdate(photo_url=photo_url)
        updated_user = UserService.update_user(db, user_id=user_id, user_update=user_update)
        
        if updated_user is None:
            raise HTTPException(status_code=404, detail="User not found")
            
        return updated_user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to upload photo") 