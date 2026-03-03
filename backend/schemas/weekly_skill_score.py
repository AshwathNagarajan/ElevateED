from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional


class WeeklySkillScoreCreate(BaseModel):
    """Schema for creating a weekly skill score"""
    student_id: int
    quiz_score: float = Field(..., ge=0, le=100, description="Quiz score (0-100)")
    project_score: float = Field(..., ge=0, le=100, description="Project score (0-100)")
    attendance_score: float = Field(..., ge=0, le=100, description="Attendance score (0-100)")
    mentor_rating: float = Field(..., ge=0, le=100, description="Mentor rating (0-100)")
    week_ending: datetime = Field(..., description="End date of the week")


class WeeklySkillScoreResponse(BaseModel):
    """Schema for weekly skill score response"""
    id: int
    student_id: int
    quiz_score: float
    project_score: float
    attendance_score: float
    mentor_rating: float
    skill_score: float
    created_at: datetime
    week_ending: datetime
    
    model_config = ConfigDict(from_attributes=True)


class SkillScoreUpdate(BaseModel):
    """Schema for updating skill score components"""
    quiz_score: Optional[float] = Field(None, ge=0, le=100)
    project_score: Optional[float] = Field(None, ge=0, le=100)
    attendance_score: Optional[float] = Field(None, ge=0, le=100)
    mentor_rating: Optional[float] = Field(None, ge=0, le=100)
