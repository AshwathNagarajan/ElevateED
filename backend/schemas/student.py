from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class StudentCreate(BaseModel):
    """Schema for creating a new student"""
    name: str
    age: int
    guardian_contact: str
    interest_track: Optional[str] = None
    predicted_track: Optional[str] = None

class StudentResponse(BaseModel):
    """Schema for student response"""
    id: int
    name: str
    age: int
    guardian_contact: str
    interest_track: Optional[str] = None
    predicted_track: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class StudentUpdate(BaseModel):
    """Schema for updating a student"""
    name: Optional[str] = None
    age: Optional[int] = None
    guardian_contact: Optional[str] = None
    interest_track: Optional[str] = None
    predicted_track: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)
