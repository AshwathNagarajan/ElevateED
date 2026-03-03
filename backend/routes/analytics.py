from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from database import get_db
from models import Course, Enrollment, QuizSubmission, Quiz, Lesson, Module, LessonProgress, Student
from models.user import User
from routes.auth import get_current_user, require_admin
from schemas.analytics import (
    CourseCompletionRateResponse,
    CourseCompletionStats,
    AverageQuizScoreResponse,
    QuizScoreStats,
    ActiveLearnersResponse,
    DailyActiveUser,
)
from datetime import datetime, timedelta
from typing import List

router = APIRouter(
    prefix="/analytics",
    tags=["analytics"],
)


@router.get("/course-completion-rate", response_model=CourseCompletionRateResponse)
def get_course_completion_rate(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Get course completion rate statistics for all courses (admin only).
    
    Returns:
        - total_courses: Number of courses in the system
        - total_enrollments: Total number of enrollments
        - overall_completion_rate: Overall completion percentage
        - courses: List of per-course statistics with:
          - course_id, course_title
          - total_enrollments, completed_count, in_progress_count, not_started_count
          - completion_rate, average_progress
    """
    # Get all courses
    courses = db.query(Course).all()
    
    if not courses:
        return CourseCompletionRateResponse(
            total_courses=0,
            total_enrollments=0,
            overall_completion_rate=0.0,
            courses=[]
        )
    
    course_stats = []
    total_enrollments = 0
    total_completed = 0
    
    for course in courses:
        # Get enrollment counts for this course
        enrollments = db.query(Enrollment).filter(Enrollment.course_id == course.id).all()
        total_course_enrollments = len(enrollments)
        
        if total_course_enrollments == 0:
            continue
        
        # Count students by status
        completed = sum(1 for e in enrollments if e.completed)
        in_progress = sum(1 for e in enrollments if not e.completed and e.progress_percentage > 0)
        not_started = sum(1 for e in enrollments if e.progress_percentage == 0)
        
        # Calculate completion rate
        completion_rate = (completed / total_course_enrollments * 100) if total_course_enrollments > 0 else 0
        
        # Calculate average progress
        average_progress = sum(e.progress_percentage for e in enrollments) / total_course_enrollments
        
        course_stats.append(CourseCompletionStats(
            course_id=course.id,
            course_title=course.title,
            total_enrollments=total_course_enrollments,
            completed_count=completed,
            in_progress_count=in_progress,
            not_started_count=not_started,
            completion_rate=round(completion_rate, 2),
            average_progress=round(average_progress, 2)
        ))
        
        total_enrollments += total_course_enrollments
        total_completed += completed
    
    # Calculate overall completion rate
    overall_completion_rate = (total_completed / total_enrollments * 100) if total_enrollments > 0 else 0
    
    return CourseCompletionRateResponse(
        total_courses=len(course_stats),
        total_enrollments=total_enrollments,
        overall_completion_rate=round(overall_completion_rate, 2),
        courses=course_stats
    )


@router.get("/average-quiz-score", response_model=AverageQuizScoreResponse)
def get_average_quiz_score(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Get average quiz score statistics (admin only).
    
    Returns:
        - total_quizzes_taken: Total number of quiz submissions
        - overall_average_score: Average score across all quizzes
        - overall_success_rate: Percentage of correct answers
        - by_module: Average scores grouped by module
        - recent_quizzes: Statistics for the 10 most recent quizzes
    """
    # Get all quiz submissions
    submissions = db.query(QuizSubmission).all()
    
    if not submissions:
        return AverageQuizScoreResponse(
            total_quizzes_taken=0,
            overall_average_score=0.0,
            overall_success_rate=0.0,
            by_module=[],
            recent_quizzes=[]
        )
    
    # Calculate overall statistics
    total_attempts = len(submissions)
    correct_count = sum(1 for s in submissions if s.is_correct)
    overall_average_score = sum(s.score for s in submissions) / total_attempts if total_attempts > 0 else 0
    overall_success_rate = (correct_count / total_attempts * 100) if total_attempts > 0 else 0
    
    # Get statistics grouped by module
    module_stats = db.query(
        Module.title,
        func.count(QuizSubmission.id).label('attempts'),
        func.avg(QuizSubmission.score).label('avg_score'),
        func.sum(func.cast(QuizSubmission.is_correct, func.Integer)).label('correct_count')
    ).join(
        Quiz, QuizSubmission.quiz_id == Quiz.id
    ).join(
        Lesson, Quiz.lesson_id == Lesson.id
    ).join(
        Module, Lesson.module_id == Module.id
    ).group_by(Module.title).all()
    
    module_data = [
        {
            "module_name": stat[0],
            "attempts": stat[1],
            "average_score": round(stat[2], 2) if stat[2] else 0,
            "success_rate": round((stat[3] / stat[1] * 100), 2) if stat[1] and stat[3] else 0
        }
        for stat in module_stats
    ]
    
    # Get recent quiz statistics
    recent_quizzes = db.query(
        Quiz.id,
        Quiz.question,
        func.count(QuizSubmission.id).label('total_attempts'),
        func.sum(func.cast(QuizSubmission.is_correct, func.Integer)).label('correct_count'),
        func.avg(QuizSubmission.score).label('avg_score')
    ).join(
        QuizSubmission, Quiz.id == QuizSubmission.quiz_id
    ).group_by(Quiz.id, Quiz.question).order_by(desc(Quiz.id)).limit(10).all()
    
    recent_quiz_stats = [
        QuizScoreStats(
            quiz_id=quiz[0],
            quiz_question=quiz[1][:100],  # Truncate long questions
            total_attempts=quiz[2],
            correct_count=quiz[3] or 0,
            average_score=round(quiz[4], 2) if quiz[4] else 0,
            success_rate=round((quiz[3] / quiz[2] * 100), 2) if quiz[2] and quiz[3] else 0
        )
        for quiz in recent_quizzes
    ]
    
    return AverageQuizScoreResponse(
        total_quizzes_taken=total_attempts,
        overall_average_score=round(overall_average_score, 2),
        overall_success_rate=round(overall_success_rate, 2),
        by_module=module_data,
        recent_quizzes=recent_quiz_stats
    )


@router.get("/active-learners", response_model=ActiveLearnersResponse)
def get_active_learners(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Get active learner statistics (admin only).
    
    Returns:
        - total_active_today: Students active in last 24 hours
        - total_active_this_week: Students active in last 7 days
        - total_active_this_month: Students active in last 30 days
        - total_students: Total registered students
        - engagement_rate: Percentage of active students this month
        - daily_activity: Activity trend for last 7 days
        - top_active_modules: Most active modules
    """
    now = datetime.utcnow()
    today = now.date()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    
    # Get total students
    total_students = db.query(Student).count()
    
    # Get active students in different time periods
    active_today = db.query(LessonProgress.student_id).filter(
        func.date(LessonProgress.started_at) == today
    ).distinct().count()
    
    active_week = db.query(LessonProgress.student_id).filter(
        LessonProgress.started_at >= week_ago
    ).distinct().count()
    
    active_month = db.query(LessonProgress.student_id).filter(
        LessonProgress.started_at >= month_ago
    ).distinct().count()
    
    engagement_rate = (active_month / total_students * 100) if total_students > 0 else 0
    
    # Get daily activity for last 7 days
    daily_activity = []
    for i in range(6, -1, -1):  # Last 7 days
        date = today - timedelta(days=i)
        next_date = date + timedelta(days=1)
        
        active_students = db.query(LessonProgress.student_id).filter(
            and_(
                func.date(LessonProgress.started_at) == date
            )
        ).distinct().count()
        
        lessons_completed = db.query(LessonProgress).filter(
            and_(
                func.date(LessonProgress.completion_date) == date,
                LessonProgress.completed == True
            )
        ).count()
        
        quizzes_taken = db.query(QuizSubmission).filter(
            and_(
                func.date(QuizSubmission.submitted_at) == date
            )
        ).count()
        
        daily_activity.append(DailyActiveUser(
            date=str(date),
            active_students=active_students,
            lessons_completed=lessons_completed,
            quizzes_taken=quizzes_taken
        ))
    
    # Get top active modules
    top_modules = db.query(
        Module.id,
        Module.title,
        func.count(LessonProgress.id).label('completions')
    ).join(
        Lesson, Module.id == Lesson.module_id
    ).join(
        LessonProgress, Lesson.id == LessonProgress.lesson_id
    ).filter(
        LessonProgress.completed == True
    ).group_by(Module.id, Module.title).order_by(desc('completions')).limit(5).all()
    
    top_active_modules = [
        {
            "module_id": module[0],
            "module_name": module[1],
            "completions": module[2]
        }
        for module in top_modules
    ]
    
    return ActiveLearnersResponse(
        total_active_today=active_today,
        total_active_this_week=active_week,
        total_active_this_month=active_month,
        total_students=total_students,
        engagement_rate=round(engagement_rate, 2),
        daily_activity=daily_activity,
        top_active_modules=top_active_modules
    )
