from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional


class EnrollmentCreate(BaseModel):
    """Schema for creating a new enrollment"""
    student_id: int
    course_id: int
    progress_percentage: float = Field(default=0.0, ge=0.0, le=100.0)
    completed: bool = Field(default=False)


class EnrollmentCreateRequest(BaseModel):
    """Schema for enrollment request from frontend (just course_id)"""
    course_id: int


class EnrollmentUpdate(BaseModel):
    """Schema for updating an enrollment"""
    progress_percentage: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    completed: Optional[bool] = None
    
    model_config = ConfigDict(from_attributes=True)


class EnrollmentResponse(BaseModel):
    """Schema for enrollment response"""
    id: int
    student_id: int
    course_id: int
    progress_percentage: float
    completed: bool
    enrolled_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class EnrollmentDetailResponse(BaseModel):
    """Schema for enrollment response with student and course details"""
    id: int
    student_id: int
    course_id: int
    progress_percentage: float
    completed: bool
    enrolled_at: datetime
    
    # Nested details
    student: Optional[dict] = None
    course: Optional[dict] = None
    
    model_config = ConfigDict(from_attributes=True)


class CourseBasicInfo(BaseModel):
    """Basic course information for embedding in enrollments"""
    id: int
    title: str
    description: Optional[str] = None
    track_type: str
    level: str
    duration_hours: Optional[float] = 0.0
    instructor: Optional[str] = "ElevateED Instructor"
    rating: Optional[float] = 0.0
    thumbnail_url: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class StudentEnrollmentsResponse(BaseModel):
    """Schema for student's list of enrollments"""
    id: int
    progress_percentage: float
    completed: bool
    enrolled_at: datetime
    course_id: int
    course: Optional[CourseBasicInfo] = None
    
    model_config = ConfigDict(from_attributes=True)


class CourseEnrollmentsResponse(BaseModel):
    """Schema for course's list of enrolled students"""
    id: int
    student_id: int
    progress_percentage: float
    completed: bool
    enrolled_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
