from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class LessonProgressCreate(BaseModel):
    """Schema for creating a new lesson progress entry"""
    student_id: int
    lesson_id: int
    completed: bool = False


class LessonProgressUpdate(BaseModel):
    """Schema for updating lesson progress"""
    completed: bool
    completion_date: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class LessonProgressResponse(BaseModel):
    """Schema for lesson progress response"""
    id: int
    student_id: int
    lesson_id: int
    completed: bool
    completion_date: Optional[datetime]
    started_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class LessonProgressWithDetailsResponse(BaseModel):
    """Schema for lesson progress response with lesson details"""
    id: int
    student_id: int
    lesson_id: int
    completed: bool
    completion_date: Optional[datetime]
    started_at: datetime
    
    # Nested lesson details
    lesson_title: Optional[str] = None
    lesson_duration: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)


class StudentLessonProgressResponse(BaseModel):
    """Schema for listing a student's lesson progress"""
    id: int
    lesson_id: int
    completed: bool
    completion_date: Optional[datetime]
    started_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ModuleLessonProgressResponse(BaseModel):
    """Schema for module progress overview"""
    module_id: int
    module_title: str
    total_lessons: int
    completed_lessons: int
    completion_percentage: float
    
    model_config = ConfigDict(from_attributes=True)


class ProgressStatisticsResponse(BaseModel):
    """Schema for student progress statistics"""
    total_lessons_started: int
    total_lessons_completed: int
    overall_completion_percentage: float
    modules_progress: list = []
    
    model_config = ConfigDict(from_attributes=True)
