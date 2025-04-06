from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from ..utils.database import get_db
from ..models.user import User
from ..schemas.user import User as UserSchema, Token, UserLogin
from ..utils.auth import (
    authenticate_user,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    SECRET_KEY,
    ALGORITHM,
    verify_token
)
from jose import jwt, JWTError

router = APIRouter()

def get_username_from_token(authorization: str = Header(...)) -> str:
    """
    Extract and verify username from the authorization token.
    
    Parameters:
    - authorization: Bearer token in the format 'Bearer <token>'
    
    Returns:
    - username: The username extracted from the token
    
    Raises:
    - HTTPException: If the token is invalid or expired
    """
    try:
        # Check if authorization header is in correct format
        if not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header format"
            )
            
        # Extract token
        token = authorization.split(" ")[1]
        
        # Verify and decode token
        try:
            payload = verify_token(token)
            username = payload.get("sub")
            if not username:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload"
                )
            return username
                
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e)
            )
            
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/auth/login", response_model=Token)
async def login_for_access_token(
    user: UserLogin,
    db: Session = Depends(get_db)
):
    # Authenticate user
    user = authenticate_user(db, user.username, user.password)
    if not user: 
        raise HTTPException(
            status_code=400,
            detail="Invalid username or password",
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me", response_model=UserSchema)
async def read_users_me(
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    """
    Get current user information using the access token.
    
    Parameters:
    - authorization: Bearer token in the format 'Bearer <token>'
    
    Returns:
    - User information if token is valid
    """
    try:
        username = get_username_from_token(authorization)
        
        # Get user from database
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
            
        return user
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 