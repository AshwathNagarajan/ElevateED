from routes.student import router as student_router
from routes.auth import router as auth_router
from routes.predict import router as predict_router
from routes.skill import router as skill_router
from routes.attendance import router as attendance_router
from routes.course import router as course_router
from routes.enrollment import router as enrollment_router
from routes.lesson import router as lesson_router
from routes.quiz import router as quiz_router
from routes.recommendation import router as recommendation_router
from routes.analytics import router as analytics_router

__all__ = [
    "student_router",
    "auth_router",
    "predict_router",
    "skill_router",
    "attendance_router",
    "course_router",
    "enrollment_router",
    "lesson_router",
    "quiz_router",
    "recommendation_router",
    "analytics_router",
]
