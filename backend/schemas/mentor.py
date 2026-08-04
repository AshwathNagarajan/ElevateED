from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime


class MentorBase(BaseModel):
    """Base schema for mentor"""
    name: str
    phone: Optional[str] = None
    qualification: str = Field(..., description="e.g., M.Tech, PhD, B.E.")
    specialization: str = Field(..., description="e.g., Data Science, Web Development")
    experience_years: int = Field(..., ge=0, description="Years of teaching/industry experience")
    bio: Optional[str] = None
    linkedin_url: Optional[str] = None


class MentorCreate(MentorBase):
    """Schema for creating a mentor (registration)"""
    email: str
    password: str
    full_name: str  # For user account


class MentorUpdate(BaseModel):
    """Schema for updating mentor profile"""
    name: Optional[str] = None
    phone: Optional[str] = None
    qualification: Optional[str] = None
    specialization: Optional[str] = None
    experience_years: Optional[int] = None
    bio: Optional[str] = None
    linkedin_url: Optional[str] = None
    profile_image_url: Optional[str] = None


class MentorResponse(MentorBase):
    """Schema for mentor response"""
    id: int
    user_id: int
    profile_image_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class MentorWithUserResponse(MentorResponse):
    """Schema for mentor response with user info"""
    email: str
    
    model_config = ConfigDict(from_attributes=True)
