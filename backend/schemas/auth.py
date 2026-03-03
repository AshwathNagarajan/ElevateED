from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class TokenResponse(BaseModel):
    """Schema for token response"""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Schema for token data"""
    user_id: int
    role: str

class UserLogin(BaseModel):
    """Schema for user login"""
    email: str
    password: str

class UserBase(BaseModel):
    """Base schema for user"""
    email: str
    full_name: str
    role: str = "student"  # student, mentor, admin

class UserCreate(UserBase):
    """Schema for creating a user"""
    password: str

class UserResponse(UserBase):
    """Schema for user response"""
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
