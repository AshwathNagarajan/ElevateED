from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class BadgeConditionType(str, Enum):
    """Badge condition types."""
    COMPLETE_COURSE = "complete_course"
    LEARNING_STREAK = "learning_streak"
    HIGH_SCORE = "high_score"
    QUIZ_MASTER = "quiz_master"
    ATTENDANCE_PERFECT = "attendance_perfect"
    FIRST_LESSON = "first_lesson"
    MODULE_COMPLETION = "module_completion"
    PRACTICE_DEDICATION = "practice_dedication"


class BadgeCreate(BaseModel):
    """Schema for creating a badge (admin only)."""
    name: str = Field(..., max_length=100, description="Unique badge name")
    description: str = Field(..., description="Badge description and earning criteria")
    condition_type: BadgeConditionType
    icon_url: Optional[str] = Field(None, max_length=500)
    color: str = Field(default="primary")
    points: int = Field(default=10, ge=0)


class BadgeResponse(BaseModel):
    """Schema for badge response."""
    id: int
    name: str
    description: str
    condition_type: BadgeConditionType
    icon_url: Optional[str]
    color: str
    points: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class BadgeDetailResponse(BadgeResponse):
    """Detailed badge response with student count."""
    earned_count: int = Field(
        default=0,
        description="Number of students who earned this badge"
    )

    class Config:
        from_attributes = True


class StudentBadgeCreate(BaseModel):
    """Schema for awarding a badge to a student."""
    badge_id: int
    context_data: Optional[str] = Field(None, max_length=500)


class StudentBadgeResponse(BaseModel):
    """Schema for student badge (badge earned by student)."""
    id: int
    badge_id: int
    earned_at: datetime
    context_data: Optional[str]

    class Config:
        from_attributes = True


class StudentBadgeDetailResponse(BaseModel):
    """Detailed student badge response with full badge details."""
    id: int
    badge_id: int
    badge: BadgeResponse
    earned_at: datetime
    context_data: Optional[str]

    class Config:
        from_attributes = True


class StudentBadgesResponse(BaseModel):
    """Schema for a student's badges collection."""
    student_id: int
    total_badges: int = Field(..., description="Total badges earned")
    total_points: int = Field(..., description="Total points from badges")
    badges: List[StudentBadgeDetailResponse] = Field(
        ...,
        description="List of earned badges"
    )

    class Config:
        from_attributes = True
