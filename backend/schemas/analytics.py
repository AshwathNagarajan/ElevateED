from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class CourseCompletionStats(BaseModel):
    """Statistics for a course's completion rate."""
    course_id: int
    course_title: str
    total_enrollments: int
    completed_count: int
    in_progress_count: int
    not_started_count: int
    completion_rate: float = Field(..., description="Percentage of students who completed the course")
    average_progress: float = Field(..., description="Average progress percentage across all students")

    class Config:
        from_attributes = True


class CourseCompletionRateResponse(BaseModel):
    """Overall course completion statistics."""
    total_courses: int
    total_enrollments: int
    overall_completion_rate: float
    courses: List[CourseCompletionStats]

    class Config:
        from_attributes = True


class QuizScoreStats(BaseModel):
    """Statistics for quiz scores."""
    quiz_id: int
    quiz_question: str
    total_attempts: int
    correct_count: int
    average_score: float
    success_rate: float = Field(..., description="Percentage of correct answers")

    class Config:
        from_attributes = True


class AverageQuizScoreResponse(BaseModel):
    """Overall quiz score statistics."""
    total_quizzes_taken: int
    overall_average_score: float
    overall_success_rate: float
    by_module: Optional[List[dict]] = Field(None, description="Average scores grouped by module")
    recent_quizzes: List[QuizScoreStats] = Field(..., description="Statistics for recent quizzes")

    class Config:
        from_attributes = True


class DailyActiveUser(BaseModel):
    """Daily active learner statistics."""
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    active_students: int = Field(..., description="Number of active learners on this date")
    lessons_completed: int = Field(..., description="Total lessons completed on this date")
    quizzes_taken: int = Field(..., description="Total quizzes taken on this date")

    class Config:
        from_attributes = True


class ActiveLearnersResponse(BaseModel):
    """Active learner statistics."""
    total_active_today: int = Field(..., description="Students active in last 24 hours")
    total_active_this_week: int = Field(..., description="Students active in last 7 days")
    total_active_this_month: int = Field(..., description="Students active in last 30 days")
    total_students: int = Field(..., description="Total number of students registered")
    engagement_rate: float = Field(..., description="Percentage of active students this month")
    daily_activity: List[DailyActiveUser] = Field(
        ...,
        description="Daily activity trend for the last 7 days"
    )
    top_active_modules: List[dict] = Field(
        ...,
        description="Most active modules based on lesson completions"
    )

    class Config:
        from_attributes = True


class LearnerEngagementStats(BaseModel):
    """Individual student engagement statistics."""
    student_id: int
    student_name: str
    lessons_completed: int
    quizzes_taken: int
    quiz_success_rate: float
    badges_earned: int
    courses_completed: int
    last_activity_at: Optional[datetime]

    class Config:
        from_attributes = True


class DetailedAnalyticsResponse(BaseModel):
    """Comprehensive analytics overview."""
    timestamp: datetime
    course_completions: CourseCompletionRateResponse
    quiz_scores: AverageQuizScoreResponse
    active_learners: ActiveLearnersResponse

    class Config:
        from_attributes = True
