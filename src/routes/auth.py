from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import timedelta

from src.database.config import get_db
from src.models.user import User
from src.auth.jwt_handler import (
    create_access_token,
    get_current_active_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

router = APIRouter()


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: Optional[str] = None


class UserResponse(BaseModel):
    id: Optional[int] = None
    email: str
    full_name: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str
    success: bool
    profile: UserResponse


@router.post("/login", response_model=Token)
async def login(login_data: UserLoginRequest, db: Session = Depends(get_db)):
    """Login user and return JWT tokens using email."""
    user = db.query(User).filter(User.email == login_data.email.lower()).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "profile": {"id": user.id, "email": user.email, "full_name": user.full_name},
        "token_type": "bearer",
        "success": True,
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current authenticated user information."""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
    }
