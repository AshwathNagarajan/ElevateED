from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List


class LessonCreate(BaseModel):
    """Schema for creating a new lesson"""
    title: str
    content: Optional[str] = None
    video_url: Optional[str] = None
    duration_minutes: Optional[int] = None


class LessonResponse(BaseModel):
    """Schema for lesson response"""
    id: int
    module_id: int
    title: str
    content: Optional[str] = None
    video_url: Optional[str] = None
    duration_minutes: Optional[int] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ModuleCreate(BaseModel):
    """Schema for creating a new module"""
    title: str
    order_number: int


class ModuleResponse(BaseModel):
    """Schema for module response"""
    id: int
    course_id: int
    title: str
    order_number: int
    lessons: List[LessonResponse] = []
    
    model_config = ConfigDict(from_attributes=True)


class ModuleWithLessonsResponse(BaseModel):
    """Schema for module response with full lessons"""
    id: int
    course_id: int
    title: str
    order_number: int
    lessons: List[LessonResponse] = []
    
    model_config = ConfigDict(from_attributes=True)


class CourseCreate(BaseModel):
    """Schema for creating a new course"""
    title: str
    description: Optional[str] = None
    track_type: str
    level: str
    duration_hours: Optional[float] = 0.0
    instructor: Optional[str] = "ElevateED Instructor"
    thumbnail_url: Optional[str] = None


class CourseResponse(BaseModel):
    """Schema for course response"""
    id: int
    title: str
    description: Optional[str] = None
    track_type: str
    level: str
    duration_hours: Optional[float] = 0.0
    instructor: Optional[str] = "ElevateED Instructor"
    rating: Optional[float] = 0.0
    thumbnail_url: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class CourseDetailResponse(BaseModel):
    """Schema for course response with modules and lessons"""
    id: int
    title: str
    description: Optional[str] = None
    track_type: str
    level: str
    created_at: datetime
    modules: List[ModuleWithLessonsResponse] = []
    
    model_config = ConfigDict(from_attributes=True)


class CourseUpdate(BaseModel):
    """Schema for updating a course"""
    title: Optional[str] = None
    description: Optional[str] = None
    track_type: Optional[str] = None
    level: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class CourseFilters(BaseModel):
    """Schema for applied filters"""
    track_type: Optional[str] = None
    level: Optional[str] = None


class CoursePaginatedResponse(BaseModel):
    """Schema for paginated course list response"""
    skip: int
    limit: int
    total: int
    count: int
    page: int
    pages: int
    filters: CourseFilters
    items: List[CourseResponse]
    
    model_config = ConfigDict(from_attributes=True)
