from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class RecommendationResponse(BaseModel):
    """Schema for a single recommendation."""
    type: str = Field(
        ...,
        description="Type of recommendation: 'revision', 'next_level', or 'foundational_review'"
    )
    module_id: int
    module_name: str
    message: str
    reason: str
    score: float = Field(..., description="Student's success percentage in this module")
    generated_at: datetime
    failed_count: Optional[int] = Field(None, description="Number of failed quizzes (for revision)")
    passed_count: Optional[int] = Field(None, description="Number of passed quizzes (for next_level)")

    class Config:
        from_attributes = True


class ModuleStatistics(BaseModel):
    """Schema for per-module quiz statistics."""
    module_id: int
    module_name: str
    total: int = Field(..., description="Total quizzes attempted")
    passed: int = Field(..., description="Number of quizzes passed")
    failed: int = Field(..., description="Number of quizzes failed")
    success_percentage: float = Field(..., description="Success rate percentage")
    average_score: float = Field(..., description="Average score in this module")

    class Config:
        from_attributes = True


class StudentPerformanceResponse(BaseModel):
    """Schema for overall student quiz performance."""
    total_quizzes: int = Field(..., description="Total number of quizzes attempted")
    passed: int = Field(..., description="Total quizzes passed")
    failed: int = Field(..., description="Total quizzes failed")
    success_percentage: float = Field(..., description="Overall success rate")
    average_score: float = Field(..., description="Overall average score")
    module_stats: List[ModuleStatistics] = Field(
        ...,
        description="Per-module performance breakdown"
    )

    class Config:
        from_attributes = True


class NextModuleInfo(BaseModel):
    """Schema for next module information."""
    id: int
    title: str
    order: int

    class Config:
        from_attributes = True


class NextLevelResponse(BaseModel):
    """Schema for next level unlock check response."""
    unlocked: bool = Field(..., description="Whether the next level is unlocked")
    message: str = Field(..., description="Human-readable message about the result")
    reason: Optional[str] = Field(None, description="Reason if not unlocked")
    next_module: Optional[NextModuleInfo] = Field(None, description="Details of next module if unlocked")

    class Config:
        from_attributes = True


class RevisionLessonResponse(BaseModel):
    """Schema for revision lesson recommendation."""
    lesson_id: int
    lesson_title: str
    lesson_content: Optional[str]
    video_url: Optional[str]
    duration_minutes: Optional[int]
    recommendation: str
    module_id: int
    module_name: str

    class Config:
        from_attributes = True


class PracticeRecommendation(BaseModel):
    """Schema for practice recommendation."""
    module_id: int
    module_name: str
    message: str
    focus_area: str = Field(
        ...,
        description="Focus area: 'Conceptual Understanding' or 'Applied Skills'"
    )
    difficulty: str = Field(
        ...,
        description="Suggested difficulty level: 'Beginner', 'Intermediate', or 'Advanced'"
    )
    priority: str = Field(
        ...,
        description="Priority level: 'High', 'Medium', or 'Low'"
    )
    success_rate: float = Field(..., description="Current success rate in this module")
    recommendation_type: str = Field(
        ...,
        description="Type of recommendation: 'revision' or 'foundational_review'"
    )

    class Config:
        from_attributes = True
